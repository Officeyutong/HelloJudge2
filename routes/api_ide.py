from main import web_app as app
from main import db, config, basedir, csrf
from flask import session, request, send_file, send_from_directory
from utils import *
from models import *
from sqlalchemy.sql.expression import *
from api.ide_run import push_into_queue
from werkzeug.utils import secure_filename


@app.route("/api/ide/submit", methods=["POST"])
def submit_ide_run():
    """
    提交IDE运行申请
    code: 代码
    input: 输入
    lang: 语言ID
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    code, input, lang = request.form["code"], request.form["input"], request.form["lang"]
    if len(code) > config.MAX_CODE_LENGTH:
        return make_response(-1, message="提交代码过长")
    if len(input) > config.MAX_CODE_LENGTH:
        return make_response(-1, message="输入文件过长")
    import os
    if not os.path.exists(os.path.join("langs", lang+".py")):
        return make_response(-1, message="语言ID不存在")
    run_id = push_into_queue(code, input, lang)
    return make_response(0, data={
        "run_id": run_id
    })


@csrf.exempt
@app.route("/api/ide/update", methods=["POST"])
def iderun_update():
    """
    更新在线IDE提交状态
    uuid: 评测机UUID
    run_id: 运行ID
    message: 消息
    status: done/running运行状态
    """
    if request.form.get("uuid") not in config.JUDGERS:
        return make_response(-1, message="未认证评测机")
    import flask_socketio
    # print(f"Updating...{request.form['run_id']}")
    flask_socketio.emit("update", {
        "run_id": request.form["run_id"],
        "message": request.form["message"],
        "status": request.form["status"]
    }, room="iderun", namespace="/ws/iderun", broadcast=True)
    return make_response(0, message="ok")


# @csrf.exempt
# @app.route("update", namespace="/ws/ide/update")
# def ws_iderun_update(state: dict):
#     """
#     更新在线IDE提交状态
#     uuid: 评测机UUID
#     run_id: 运行ID
#     message: 消息
#     status: done/running运行状态
#     """
#     if state.get("uuid") not in config.JUDGERS:
#         return
#     import flask_socketio
#     # print(f"Updating...{request.form['run_id']}")
#     flask_socketio.emit("update", {
#         "run_id": state["run_id"],
#         "message": state["message"],
#         "status": state["status"]
#     }, room="iderun", namespace="/ws/iderun", broadcast=True)
