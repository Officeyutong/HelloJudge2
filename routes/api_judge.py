from main import web_app as app
from main import db, config, basedir, csrf
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import *
from models.problem import *
from models.submission import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename


@csrf.exempt
@app.route("/api/judge/get_file_list", methods=["POST"])
def judge_get_file_list():
    """
    获取题目的文件列表
    参数:
    problem_id:int 题目ID
    uuid:str 评测机uuid
    返回
    {
        "code":-1,//0表示调用成功
        "message":"qwq",
        "data":[
            {"name":"1.in","size":12345,"last_modified_time":1234}
        ]
    }
    """
    if request.form['uuid'] not in config.JUDGERS:
        return make_response(-1, message="该评测机未认证")
    problem = db.session.query(Problem).filter(
        Problem.id == request.form["problem_id"])
    if problem.count() == 0:
        return make_response(-1, message="题目不存在")
    return make_response(0, data=generate_file_list(request.form["problem_id"]))


@csrf.exempt
@app.route("/api/judge/download_file", methods=["POST"])
def judge_download_file():
    """
    下载题目文件
    参数:
    problem_id:int 题目ID
    filename:str 文件名
    uuid:str 评测机uuid
    返回
        文件内容
    """
    if request.form['uuid'] not in config.JUDGERS:
        return make_response(-1, message="该评测机未认证")
    problem = db.session.query(Problem).filter(
        Problem.id == request.form["problem_id"])
    if problem.count() == 0:
        return make_response(-1, message="题目不存在")
    import os
    problem: Problem = problem.one()
    path = os.path.join(basedir, f"{config.UPLOAD_DIR}/{problem.id}")
    file = os.path.join(path, request.form["filename"])
    import flask
    if not os.path.exists(file):
        flask.abort(404)
    return flask.send_file(file)


@csrf.exempt
@app.route("/api/judge/get_problem_info", methods=["POST"])
def judge_get_problem_info():
    """
    获取题目信息
    参数:
    problem_id:int 题目ID
    uuid:str 评测机uuid
    返回
    {
        "code":-1,//0表示调用成功
        "message":"qwq",
        "data":{

        }
    }
    """
    if request.form['uuid'] not in config.JUDGERS:
        return make_response(-1, message="该评测机未认证")
    problem = db.session.query(Problem).filter(
        Problem.id == request.form["problem_id"])
    if problem.count() == 0:
        return make_response(-1, message="题目不存在")
    problem: Problem = problem.one()
    result = problem.as_dict()
    result["create_time"] = str(result["create_time"])
    return make_response(0, data=result)


@csrf.exempt
@app.route("/api/judge/update", methods=["POST"])
def judge_update():
    """
    更新评测状态
    参数:
    submission_id:int 提交ID
    uuid:str 评测机uuid
    judge_result:dict 评测结果
    message:str 附加信息
    返回
    {
        "code":-1,//0表示调用成功
        "message":"qwq"
    }
    """
    if request.form['uuid'] not in config.JUDGERS:
        return make_response(-1, message="该评测机未认证")
    from api.judge import update_status
    update_status(int(request.form["submission_id"]), decode_json(request.form["judge_result"]),
                  str(config.JUDGERS[request.form["uuid"]]), request.form.get("message", ""))
    return make_response(0)


@csrf.exempt
@app.route("/api/judge/get_lang_config", methods=["POST"])
def get_lang_config():
    """
    获取语言配置文件
    参数:
    lang_id:str 语言ID
    uuid:str 评测机uuid
    返回
    对应的文件
    """
    import os
    if request.form['uuid'] not in config.JUDGERS:
        return make_response(-1, message="该评测机未认证")
    return send_file(os.path.join(basedir, "langs", request.form["lang_id"]+".py"))
