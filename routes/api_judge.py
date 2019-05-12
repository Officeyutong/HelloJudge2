from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import *
from models.problem import *
from models.submission import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename


@app.route("/api/judge/get_file_list")
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


@app.route("/api/judge/download_file")
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
    path = os.path.join(basedir, f"uploads/{problem.id}")
    file = os.path.join(path, request.form["filename"])
    if not os.path.exists(file):
        import flask
        flask.abort(404)
    return flask.send_file(file)


@app.route("/api/judge/download_file")
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
    return make_response(0, data=problem.as_dict())
