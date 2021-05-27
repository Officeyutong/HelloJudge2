import ast
import pathlib
import os
import dataclasses
import jinja2
import shutil
import asyncio
import aiofiles
import re
import bs4
import aiohttp
from urllib.parse import urlparse
import hashlib
import argparse
from io import StringIO, BytesIO

from typing import Any, List, Dict, Set
try:
    import config
except ModuleNotFoundError:
    import config_default as config

CACHE_IGNORE = {
    "katex.min.css",
    "katex.css",
    "semantic.min.css",
    "semantic.css"
}

local_dir = pathlib.Path(os.getcwd())
templates = local_dir/"templates"
view_file_name = local_dir/"routes"/"view.py"
output_dir = local_dir/"pack_output"

MINIFIER_CMD = """
html-minifier --collapse-whitespace --conservative-collapse --remove-comments --remove-optional-tags 
--remove-redundant-attributes --remove-script-type-attributes --remove-tag-whitespace --use-short-doctype --minify-css true --minify-js true --input-dir {INPUT_DIR} --output-dir {OUTPUT_DIR}
"""


@dataclasses.dataclass
class ExtractResult:
    func_name: str
    template_name: str
    routes: List[str]


def extract_info(func: ast.FunctionDef) -> ExtractResult:
    exc = ValueError(f"{func.name} is not a view route!")
    if len(func.body) != 1:
        raise exc
    return_call: ast.Return = func.body[0]
    if type(return_call) is not ast.Return:
        raise exc from TypeError("This function doesn's have a return call")
    call_val = return_call.value
    if type(call_val) is not ast.Call:
        raise exc
    call_val: ast.Call
    if call_val.func.id != "render_template":
        raise exc
    arg = call_val.args[0]
    if type(arg) is not ast.Constant:
        raise exc
    arg: ast.Constant
    template_file = arg.value
    decorators = func.decorator_list
    decs = [
        x.args[0].value for x in decorators
    ]
    return ExtractResult(
        func.name,
        template_file.strip("/"),
        decs
    )


def process_route(route: str) -> str:
    if "int" in route:
        expr = re.compile(r"<int:([a-zA-Z0-9_]+)>")
        route = expr.sub("([0-9]+)", route)
    if "string" in route:
        route = re.compile(r"<string:([a-zA-Z0-9_]+)>").sub("([^/]+)", route)
    return route


async def render_and_minify(template: jinja2.Template, info: ExtractResult, mixin: Dict[str, Any], config_buf: StringIO):
    string = await template.render_async(**mixin)
    output_file = output_dir/"pages"/info.template_name
    if not os.path.exists(output_file.parent):
        os.makedirs(output_file.parent)
    async with aiofiles.open(output_file, "wb") as f:
        await f.write(string.encode())
    for route in info.routes:
        config_buf.write(f"""
        location ~ ^{process_route(route)}$ {{
            try_files /pages/{info.template_name} = 404;
        }}    
        """)
    print(info.template_name, "render OK!")


async def minify(file):
    async with aiofiles.open(file, "rb") as f:
        data = await f.read()
    minifier = await asyncio.create_subprocess_shell(
        """html-minifier --collapse-whitespace --remove-comments --remove-redundant-attributes --remove-script-type-attributes --remove-tag-whitespace --use-short-doctype --minify-css true --minify-js true""", asyncio.subprocess.PIPE, asyncio.subprocess.PIPE, asyncio.subprocess.STDOUT
    )
    minifier.stdin.write(data)
    minifier.stdin.write_eof()
    out_data = await minifier.stdout.read()
    async with aiofiles.open(file, "wb") as f:
        await f.write(out_data)
    await minifier.wait()
    print(file, "minified!")


def save_static_files(html_list: List[str]):
    files: Set[str] = set()
    files_url_mapper: Dict[str, str] = {}
    for item in html_list:
        file_path = output_dir/"pages"/item
        print("Processing", file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f.read(), "lxml")
        elems = soup.select("script")
        for item in elems:
            if "src" in item.attrs:
                src = item.attrs["src"]
                if not src.startswith("/static"):
                    files.add(src)
        styles = soup.select("link[rel=stylesheet]")
        for item in styles:
            if "href" in item.attrs:
                href = item.attrs["href"]
                if not href.startswith("/static"):
                    files.add(href)
    print(files)
    print(len(files), "in total")
    cache_dir = output_dir/"cache"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.mkdir(cache_dir)

    async def download_one(url: str):
        new_url = url
        if url.startswith("//"):
            new_url = "http:"+url
        buf = BytesIO()
        hasher = hashlib.sha256()
        print("Start download", new_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(new_url) as resp:
                curr = await resp.read()
                filename = ""
                if "Content-Disposition" in resp.headers:
                    for x in resp.headers['Content-Disposition'].split(";"):
                        if "=" in x and x.strip().startswith("filename") and not x.strip().startswith("filename*"):
                            filename = ast.literal_eval(x.split("=")[1])
                if filename == "":
                    parse_result = urlparse(new_url)
                    filename = parse_result.path.split("/")[-1]
                if filename in CACHE_IGNORE:
                    files_url_mapper[url] = url
                    return
                hasher.update(curr)
                *prev, ext = filename.split(".")
                filename = ".".join([*prev, hasher.hexdigest()[:8], ext])
                buf.write(curr)
        async with aiofiles.open(output_dir/"cache"/filename, "wb") as f:
            await f.write(buf.getvalue())
        files_url_mapper[url] = "/cache/"+filename
        print(new_url, "to", filename, "download ok")
    asyncio.get_event_loop().run_until_complete(asyncio.wait([
        download_one(url) for url in files
    ]))
    # print(files_url_mapper)
    for item in html_list:
        html_path = output_dir/"pages"/item
        with open(html_path, "r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f.read(), "lxml")
        for script_tag in soup.select("script"):
            if "src" in script_tag.attrs:
                src = script_tag.attrs["src"]
                if not src.startswith("/static"):
                    script_tag.attrs["src"] = files_url_mapper[script_tag.attrs["src"]]
        for link_tag in soup.select("link[rel=stylesheet]"):
            if "href" in link_tag.attrs:
                href = link_tag.attrs["href"]
                if not href.startswith("/static"):
                    link_tag.attrs["href"] = files_url_mapper[link_tag.attrs["href"]]
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(html_path, "replaced.")


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--api-server", help="API服务器地址(默认为http://127.0.0.1:8095)", default="http://127.0.0.1:8095", required=False, type=str)
    arg_parser.add_argument(
        "--cache-static", help="缓存静态文件", action="store_true")
    arg_parse_result = arg_parser.parse_args()
    api_server = arg_parse_result.api_server
    cache_static = arg_parse_result.cache_static
    print(api_server, cache_static)
    # return
    with open(view_file_name, "r", encoding="utf-8") as f:
        parse_result = ast.parse(f.read())
    items: List[ExtractResult] = []
    for x in parse_result.body:
        if type(x) is ast.FunctionDef:
            try:
                items.append(extract_info(x))
            except Exception as e:
                print(x.name, "failed")
    html_list = [item.template_name for item in items]
    print(items)
    mixin = {
        "DEBUG": False,
        "APP_NAME": config.APP_NAME,
        "SALT": config.PASSWORD_SALT,
        "USING_CSRF_TOKEN": False
    }
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=jinja2.select_autoescape(["html"]),
        enable_async=True
    )
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)
    config_buf = StringIO()
    asyncio.get_event_loop().run_until_complete(asyncio.wait(
        [render_and_minify(env.get_template(item.template_name),
                           item, mixin, config_buf) for item in items]
    ))
    if cache_static:
        save_static_files(html_list)
    # return
    asyncio.get_event_loop().run_until_complete(asyncio.wait(
        [minify(output_dir/"pages"/item) for item in html_list]
    ))

    config_buf.write(f"""
    location ^~ /static {{
        try_files $uri = 404;
    }}
    """)
    config_buf.write(f"""
    location ^~ /cache {{
        try_files $uri = 404;
    }}
    """)
    config_buf.write(f"""
    location ^~ /api {{
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass {api_server};
    }}
    """)
    config_buf.write(f"""
    location / {{
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass {api_server};
    }}
    """)

    shutil.rmtree(output_dir/"static", True)
    shutil.copytree("static", output_dir/"static")
    with open(output_dir/"nginx.conf", "w", encoding="utf-8") as f:
        f.write(config_buf.getvalue())
    print("OK!")


if __name__ == "__main__":
    main()
