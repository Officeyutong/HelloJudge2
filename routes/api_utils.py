from main import web_app as app
from main import db, config, basedir, permission_manager
from flask import session, request, send_file, send_from_directory
from utils import *
from models import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename


@app.route("/api/home_page", methods=["POST"])
def home_page():
    """
    返回主页数据
    {
        "data":{
            "broadcasts":[
                {
                    "title":"xxx",
                    "id":"xxx",
                    "time":'xxx'
                }
            ],
            "ranklist":[
                "username":"xxx",
                "uid":-1,
                "description":"xxx"
            ],
            "recent_problems":[
                "title":"xxx",
                "id":"xxx",
                "create_time":"xxx"
            ],
            "discussions":[
                "title":"xxx",
                "id":-1,
                "time":""
            ],
            "friend_links":[
                {
                    "name":"qwq","url":"qwq"
                }
            ]
        }
    }
    """
    result = {"broadcasts": [], "ranklist": [],
              "recent_problems": [], "app_name": config.APP_NAME, "discussions": [], "friend_links": config.FRIEND_LINKS}
    broadcasts = db.session.query(Discussion.title, Discussion.time, Discussion.id).filter(or_(Discussion.path == "broadcast", Discussion.path.like("broadcast.%"))).order_by(
        Discussion.id.desc()).limit(config.HOMEPAGE_BROADCAST).all()
    for item in broadcasts:
        result["broadcasts"].append({
            "title": item.title, "id": item.id, "time": str(item.time)
        })
    ranklist = db.session.query(User.id, User.description, User.username, User.rating).order_by(
        User.rating.desc()).order_by(User.id.asc()).limit(config.HOMEPAGE_RANKLIST).all()
    for item in ranklist:
        result["ranklist"].append({
            "username": item.username, "id": item.id, "description": item.description, "rating": item.rating
        })
    problems = db.session.query(Problem.title, Problem.id, Problem.create_time).filter(Problem.public == True).order_by(
        Problem.create_time.desc()).limit(config.HOMEPAGE_PROBLEMS).all()
    for item in problems:
        result["recent_problems"].append({
            "title": item.title, "id": item.id, "create_time": str(item.create_time)
        })
    discussions = db.session.query(Discussion.title, Discussion.time, Discussion.id).filter(Discussion.path.like("discussion.%")).order_by(Discussion.top.desc()).order_by(
        Discussion.time.desc()).limit(config.HOMEPAGE_DISCUSSIONS).all()
    for item in discussions:
        result["discussions"].append({
            "title": item.title, "id": item.id, "time": str(item.time)
        })
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
            "id": file.replace(".py", ""), "display": module.DISPLAY, "version": module.VERSION, "ace_mode": module.ACE_MODE
        })
    result.sort(key=lambda x: x["id"])
    return make_response(0, list=result)


@app.route("/api/import_from_syzoj", methods=["POST"])
def import_from_syzoj():
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

        with requests.get(f"{request.form['url']}/export") as urlf:
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
        if request.form["willPublic"].lower() == "true":
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
        with requests.get(f"{request.form['url']}/testdata/download") as urlf:
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
        return encode_json({
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
            "example": "\n\n".join((f"#### 样例{index} 输入\n{item['input']}\n\n#### 样例{index} 输出\n{item['output']}" for item, index in enumerate(problem.example))),
            "limit_and_hint": problem.hint,
            "time_limit": max((item["time_limit"] for item in problem.subtasks)),
            "memory_limit": max((item["memory_limit"] for item in problem.subtasks)),
            "file_io": problem.using_file_io, "file_io_input_name": problem.input_file_name, "file_io_output_name": problem.output_file_name,
            "type": problem.problem_type, "tags": []
        }
    }
    return encode_json(result)


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
