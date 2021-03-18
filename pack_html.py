import ast
import pathlib
import os
import dataclasses
import jinja2
import shutil
import asyncio
import aiofiles
import re
from io import StringIO
from typing import Any, List, Dict
try:
    import config
except ModuleNotFoundError:
    import config_default as config

local_dir = pathlib.Path(os.getcwd())
templates = local_dir/"templates"
view_file_name = local_dir/"routes"/"view.py"
output_dir = local_dir/"pack_output"

MINIFIER_CMD = """
html-minifier --collapse-whitespace --remove-comments --remove-optional-tags 
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
    expr = re.compile(r"<(.+):(.+)>")
    return expr.sub("(.+)", route)


async def render_and_minify(template: jinja2.Template, info: ExtractResult, mixin: Dict[str, Any], config_buf: StringIO):
    string = await template.render_async(**mixin)
    output_file = output_dir/"pages"/info.template_name
    if not os.path.exists(output_file.parent):
        os.makedirs(output_file.parent)
    minifier = await asyncio.create_subprocess_shell(
        """html-minifier --collapse-whitespace --remove-comments --remove-redundant-attributes --remove-script-type-attributes --remove-tag-whitespace --use-short-doctype --minify-css true --minify-js true""", asyncio.subprocess.PIPE, asyncio.subprocess.PIPE, asyncio.subprocess.STDOUT
    )
    minifier.stdin.write(string.encode())
    minifier.stdin.write_eof()
    out_data = await minifier.stdout.read()
    async with aiofiles.open(output_file, "wb") as f:
        await f.write(out_data)
    await minifier.wait()
    for route in info.routes:
        config_buf.write(f"""
        location ~ ^{process_route(route)}$ {{
            try_files /pages/{info.template_name} = 404;
        }}    
        """)
    print(info.template_name, "OK!")


def main():

    with open(view_file_name, "r", encoding="utf-8") as f:
        parse_result = ast.parse(f.read())
    items: List[ExtractResult] = []
    for x in parse_result.body:
        if type(x) is ast.FunctionDef:
            try:
                items.append(extract_info(x))
            except Exception as e:
                print(x.name, "failed")
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
    config_buf.write(f"""
    location ^~ /static {{
        try_files $uri = 404;
    }}
    """)
    config_buf.write(f"""
    location ^~ /api {{
        proxy_pass http://127.0.0.1:8095;
    }}
    """)
    config_buf.write(f"""
    location / {{
        proxy_pass http://127.0.0.1:8095;
    }}
    """)
    
    shutil.rmtree(output_dir/"static", True)
    shutil.copytree("static", output_dir/"static")
    with open(output_dir/"nginx.conf", "w", encoding="utf-8") as f:
        f.write(config_buf.getvalue())
    print("OK!")


if __name__ == "__main__":
    main()
