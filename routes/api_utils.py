from main import web_app as app
from main import db, config, basedir, permission_manager
from flask import session, request, send_file, send_from_directory

from werkzeug.utils import secure_filename
from common.utils import unpack_argument
from common.permission import require_permission
import requests
from urllib.parse import urljoin

from common.utils import make_json_response as make_response
from sqlalchemy.sql import expression as expr
from models.user import User
from models.problem import Problem
from utils import generate_file_list
import ujson
from io import StringIO
import pathlib
import shutil
import os
import time
import datetime


@app.route("/api/home_page", methods=["POST"])
def api_home_page():
    """
    返回主页数据
    {
        "data":{
            "appName":config.APP_NAME,
            "friendLinks":[
                {
                    "name":"qwq",
                    "url":"qwq"
                }
            ], //信息流单独加载
            "swipers":[{
                "image":"图片URL",
                "url":"链接URL"
            }],
            "toolbox":[{
                "color":"semantic ui颜色",
                "name":"显示名",
                "url":"跳转链接"
            }],
            "swiperInterval":"轮播切换间隔(ms)",
            "showRanklist":false
        }
    }
    """
    result = {
        "appName": config.APP_NAME,
        "friendLinks": config.FRIEND_LINKS,
        "swipers": config.HOMEPAGE_SWIPER,
        "toolbox": config.HOMEPAGE_TOOLBOX,
        "swiperInterval": config.SWIPER_SWITCH_INTERVAL,
        "showRanklist": config.SHOW_RANKLIST_ON_HOMEPAGE
    }

    return make_response(0, data=result)


@app.route("/api/get_judge_status", methods=["POST", "GET"])
def get_judge_status():
    """
    获取评测状态列表
    参数:无
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//调用失败时的信息
            "data":{
                "accepted":{"icon":"xxx","text":"xxx"}
            }
        }
    """
    ret = config.JUDGE_STATUS
    return make_response(0, data=ret)


@app.route("/api/get_supported_langs", methods=["POST", "GET"])
def get_supported_lang():
    """
    获取支持的语言列表
    参数:
        无
    返回:
        {
            "code":0,//非0表示调用成功
            "list":[
                {"id":"c++11","display":"C++ 11","version":"G++ 8.3"}
            ]
        }
    """
    result = []
    import os
    import importlib
    for file in filter(lambda x: x.endswith(".py"), os.listdir("langs")):
        module = importlib.import_module("langs."+file.replace(".py", ""))
        result.append({
            "id": file.replace(".py", ""),
            "display": module.DISPLAY,
            "version": module.VERSION,
            "ace_mode": module.ACE_MODE,
            "hljs_mode": module.HLJS_MODE
        })
    result.sort(key=lambda x: x["id"])
    return make_response(0, list=result, data=result)


@app.route("/api/utils/import_from_syzoj_ng", methods=["POST"])
@unpack_argument
@require_permission(permission_manager, "problem.manage")
def api_utils_import_from_syzoj_ng(api_server: str, problem_id: str, public: bool, locale: str = "zh_CN"):
    def make_url(url: str):
        # print(url, "to", urljoin(api_server, url))
        return urljoin(api_server, url)
    problem_data = requests.post(make_url("/api/problem/getProblem"), json={
        "testData": True,
        "displayId": problem_id,
        "judgeInfo": True,
        "samples": True,
        "localizedContentsOfLocale": locale,
        "judgeInfoToBePreprocessed": True
    }).json()
    print(problem_data)
    real_problem_id = problem_data["meta"]["id"]
    stmt = StringIO()
    examples = []
    for item in problem_data["localizedContentsOfLocale"]["contentSections"]:
        if item["type"] == "Text":
            stmt.write(f"### {item['sectionTitle']}\n\n{item['text']}\n\n")
        elif item["type"] == "Sample":
            curr = problem_data["samples"]
            id = item["sampleId"]
            examples.append({
                "input": curr[id]["inputData"],
                "output": curr[id]["outputData"],
            })
    judge_info = problem_data["judgeInfo"]
    print(judge_info)
    time_limit = judge_info["timeLimit"]
    memory_limit = judge_info["memoryLimit"]
    score = 100//(len(judge_info["subtasks"]))
    last_score = 100 - score * len(judge_info["subtasks"])
    subtasks = [
        {
            "name": f"Subtask{i+1}",
            "score": score + (last_score if i == len(judge_info["subtasks"])-1 else 0),
            "method": {"groupmin": "min", "sum": "sum", "groupmul": "min"}[subtask["scoringType"].lower()],
            "testcases":[
                    {
                        "input": testcase["inputFile"],
                        "output":testcase["outputFile"]
                    } for testcase in subtask["testcases"]
            ],
            "time_limit":time_limit,
            "memory_limit":memory_limit
        } for i, subtask in enumerate(judge_info["subtasks"])
    ]
    for subtask in subtasks:
        score = subtask["score"]
        score_per_case = score//len(subtask["testcases"])
        last_score - score - score_per_case*len(subtask["testcases"])
        for item in subtask["testcases"]:
            item["full_score"] = score_per_case
        subtask["testcases"][-1]["full_score"] += last_score
    problem = Problem(
        uploader_id=session.get("uid"),
        title=problem_data["localizedContentsOfLocale"]["title"],
        content=stmt.getvalue(),
        example=examples,
        files=[{
            "name": item["filename"],
            "size":item["size"],
        } for item in problem_data["testData"]],
        subtasks=subtasks,
        public=public,
        create_time=datetime.datetime.now()
    )
    db.session.add(problem)
    db.session.commit()
    working_dir = pathlib.Path(config.UPLOAD_DIR)/str(problem.id)
    shutil.rmtree(working_dir, ignore_errors=True)
    os.mkdir(working_dir) 
    file_links = requests.post(make_url("/api/problem/downloadProblemFiles"), json={
        "filenameList": [item["filename"] for item in problem_data["testData"]],
        "problemId": real_problem_id,
        "type": "TestData"
    }).json()
    print(file_links)
    current_time = str(time.time())
    for file in file_links["downloadInfo"]:
        print(f"Downloading {file['filename']}")
        with requests.get(file["downloadUrl"]) as resp:
            with open(working_dir/file["filename"], "wb") as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            with open(working_dir/(file["filename"]+".lock"), "w") as f:
                f.write(current_time)
    return make_response(0, problem_id=problem.id)


@app.route("/api/import_from_syzoj", methods=["POST"])
@unpack_argument
def import_from_syzoj(url: str, willPublic: bool):
    """
    从SYZOJ导入题目
    参数:
    url:str SYZOJ题目URL
    willPublic:int 新题目是否公开
    返回
    {
        "code":0,
        "uuid":'用于websocket的uuid',
        "message":""
    }
    """
    import urllib
    import tempfile
    import pathlib
    import traceback
    import zipfile
    import shutil
    import os
    import yaml
    import requests
    from io import BytesIO
    from utils import decode_json
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    if not permission_manager.has_any_permission(user.id, "problem.create", "problem.manage"):
        return make_response(-1, message="你没有权限执行此操作")
    try:

        with requests.get(f"{url}/export") as urlf:
            data = decode_json(urlf.content.decode())["obj"]
        print("JSON data: {}".format(data))
        import datetime
        problem = Problem(uploader_id=user.id,
                          title=data["title"],
                          content=data["description"],
                          input_format=data["input_format"],
                          output_format=data["output_format"],
                          hint=data["limit_and_hint"],
                          using_file_io=data["file_io"],
                          input_file_name=data["file_io_input_name"],
                          output_file_name=data["file_io_output_name"],
                          create_time=datetime.datetime.now()
                          )
        if willPublic:
            if not permission_manager.has_any_permission(user.id, "problem.publicize", "problem.manage"):
                return make_response(-1, message="你没有权限公开题目")
            problem.public = True
        problem.example = []
        problem.hint = "### 样例\n" + \
            data["example"]+"\n\n### Hint\n"+problem.hint
        time_limit = int(data["time_limit"])
        memory_limit = int(data["memory_limit"])
        db.session.add(problem)
        db.session.commit()

        work_dir = pathlib.PurePath(tempfile.mkdtemp())
        with requests.get(f"{url}/testdata/download") as urlf:
            pack = zipfile.ZipFile(BytesIO(urlf.content))
            pack.extractall(work_dir)
            pack.close()
        problem_data_dir = pathlib.PurePath(
            f"{config.UPLOAD_DIR}/{problem.id}")
        shutil.rmtree(problem_data_dir, ignore_errors=True)
        shutil.copytree(work_dir, problem_data_dir)
        shutil.rmtree(work_dir)
        # 更换新的word_dir
        work_dir = problem_data_dir
        for file in filter(lambda x: x.endswith(".lock"), os.listdir(work_dir)):
            os.remove(work_dir/file)
        file_list = []
        for file in filter(lambda x: not x.endswith(".lock"), os.listdir(work_dir)):
            with open(work_dir/(file+".lock"), "w") as f:
                import time
                last_modified_time = time.time()
                f.write(str(last_modified_time))
            file_list.append({
                "name": file, "size": os.path.getsize(work_dir/file), "last_modified_time": last_modified_time
            })
        problem.files = file_list
        pure_file_list = list(map(lambda x: x["name"], file_list))

        for x in pure_file_list:
            if x.startswith("spj_"):
                problem.spj_filename = x
                break
        auto_generate = True
        subtasks = []
        if os.path.exists(work_dir/"data.yml"):
            # 存在data.yml
            with open(work_dir/"data.yml", "r", encoding="utf-8") as f:
                data_obj = yaml.safe_load(f)
                # data.yml中钦定spj

                if "specialJudge" in data_obj:
                    new_spj_filename = work_dir/(
                        "spj_"+data_obj["specialJudge"]["language"]+"."+data_obj["specialJudge"]["fileName"].split(".")[-1])
                    print(new_spj_filename)
                    print(work_dir/data_obj["specialJudge"]["fileName"])
                    shutil.move(
                        work_dir/data_obj["specialJudge"]["fileName"], new_spj_filename)
                    problem.spj_filename = new_spj_filename.name
                if "subtasks" in data_obj:
                    auto_generate = False

                    def make_input(x):
                        return data_obj["inputFile"].replace("#", str(x))

                    def make_output(x):
                        return data_obj["outputFile"].replace("#", str(x))

                    for i, subtask in enumerate(data_obj["subtasks"]):
                        print(subtask)
                        subtasks.append({
                            "name": f"Subtask{i+1}",
                            "score": int(subtask["score"]),
                            "method": subtask["type"],
                            "time_limit": time_limit,
                            "memory_limit": memory_limit,
                            "testcases": []
                        })
                        testcases = subtasks[-1]["testcases"]
                        score = subtasks[-1]["score"]//len(subtask["cases"])
                        for testcase in subtask["cases"]:
                            testcases.append({
                                "input": make_input(testcase),
                                "output": make_output(testcase),
                                "full_score": score
                            })
                        testcases[-1]["full_score"] = subtasks[-1]["score"] - \
                            score*(len(testcases)-1)
        if auto_generate:
            # 不存在data.yml，直接生成子任务
            input_files = list(
                filter(lambda x: x.endswith(".in"), pure_file_list))
            output_files = list(
                filter(lambda x: x.endswith(".out") or x.endswith(".ans"), pure_file_list))
            if len(input_files) == len(output_files):
                pass
            for i, file in enumerate(input_files):
                pure_file_name = file[:file.rindex(".")]
                subtasks.append({
                    "name": f"Subtask{i+1}",
                    "score": 100//len(input_files),
                    "method": "sum",
                    "time_limit": time_limit,
                    "memory_limit": memory_limit,
                    "testcases": [{"full_score": 100//len(input_files), "input": file, "output": f"{pure_file_name}.ans" if f"{pure_file_name}.ans" in output_files else f"{pure_file_name}.out"}],
                    "comment": ""
                })
            diff = 100-sum(map(lambda x: x["score"], subtasks))
            subtasks[-1]["score"] += diff
            subtasks[-1]["testcases"][0]["full_score"] += diff
        for file in filter(lambda x: x.endswith(".lock"), os.listdir(work_dir)):
            os.remove(work_dir/file)
        for file in filter(lambda x: not x.endswith(".lock"), os.listdir(work_dir)):
            with open(work_dir/(file+".lock"), "w") as f:
                import time
                last_modified_time = time.time()
                f.write(str(last_modified_time))
        problem.files = generate_file_list(problem.id)
        problem.subtasks = subtasks
        db.session.commit()
    except Exception:
        print(traceback.format_exc())
        return make_response(-1, message=traceback.format_exc())
    return make_response(0, problem_id=problem.id)


@app.route("/api/get_help_markdown", methods=["POST", "GET"])
def get_help_markdown():
    return send_file("help.md")


@app.route("/show_problem/<int:id>/export", methods=["POST", "GET"])
def export_problem(id):
    """
    SYZOJ式的导出题目
    """
    problem: Problem = Problem.by_id(id)
    if not problem or not problem.public:
        return ujson.dumps({
            "success": False, "error": {
                "message": "无此题目", "nextUrls": {}
            }
        })
    result = {
        "success": True,
        "obj": {
            "title": problem.title,
            "description": problem.background+"\n"+problem.content,
            "input_format": problem.input_format,
            "output_format": problem.output_format,
            "example": "\n\n".join((f"#### 样例{index} 输入\n{item['input']}\n\n#### 样例{index} 输出\n{item['output']}" for index, item in enumerate(problem.example))),
            "limit_and_hint": problem.hint,
            "time_limit": max((item["time_limit"] for item in problem.subtasks)),
            "memory_limit": max((item["memory_limit"] for item in problem.subtasks)),
            "file_io": problem.using_file_io, "file_io_input_name": problem.input_file_name, "file_io_output_name": problem.output_file_name,
            "type": problem.problem_type, "tags": []
        }
    }
    return ujson.dumps(result)


@app.route("/show_problem/<int:id>/testdata/download", methods=["GET", "POST"])
def testdata_download(id):
    problem: Problem = Problem.by_id(id)
    if not problem or not problem.public:
        return 404
    import pathlib
    import zipfile
    import tempfile
    import flask
    problem_path = pathlib.Path(config.UPLOAD_DIR)/str(problem.id)
    zip_file = tempfile.mktemp("zip")
    zipf = zipfile.ZipFile(zip_file, "w")
    for publicized_file in problem.downloads:
        zipf.write(problem_path/publicized_file, arcname=publicized_file)
    zipf.close()
    return flask.send_file(zip_file, as_attachment=True, attachment_filename="testdata.zip")
