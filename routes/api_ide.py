from main import web_app as app
from main import db, config, basedir, csrf, redis_connection_pool
from flask import session, request, send_file, send_from_directory
from utils import *
from models import *
from sqlalchemy.sql.expression import *
from api.ide_run import push_into_queue
from werkzeug.utils import secure_filename
import redis
from common.utils import unpack_argument
import json
import flask_socketio
import os
@app.route("/api/ide/submit", methods=["POST"])
def submit_ide_run():
    """
    提交IDE运行申请
    code: 代码
    input: 输入
    lang: 语言ID
    parameter: 附加参数
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    code, input, lang, parameter = request.form["code"], request.form[
        "input"], request.form["lang"], request.form["parameter"]
    if len(code) > config.MAX_CODE_LENGTH:
        return make_response(-1, message="提交代码过长")
    if len(input) > config.MAX_CODE_LENGTH:
        return make_response(-1, message="输入文件过长")
    if len(parameter) > config.IDE_RUN_COMPILE_PARAMETER_LENGTH_LIMIT:
        return make_response(-1, message="编译参数过长")
    if not os.path.exists(os.path.join("langs", lang+".py")):
        return make_response(-1, message="语言ID不存在")
    run_id = push_into_queue(code, input, lang, parameter)
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
    data = {
        "run_id": request.form["run_id"],
        "message": request.form["message"],
        "status": request.form["status"]
    }
    print(f"Updating...{request.form['run_id']}")
    flask_socketio.emit("update", data, room="iderun",
                        namespace="/ws/iderun", broadcast=True)

    if request.form.get("status", "") == "done":
        conn = redis.Redis(connection_pool=redis_connection_pool)
        conn.set(
            name=f"hj2-iderun-result-{request.form['run_id']}",
            value=json.dumps(data).encode(),
            ex=60  # 60s后自动过期
        )

    return make_response(0, message="ok")


@app.route("/api/ide/fetch_status", methods=["POST", "GET"])
@unpack_argument
def iderun_fetch_status(run_id: str):
    """
    {
        "run_id":"运行ID",
        "message":"消息",
        "status":"done/running"
    }
    """
    key = f"hj2-iderun-result-{run_id}"
    conn = redis.Redis(connection_pool=redis_connection_pool)
    if not conn.exists(key):
        return make_response(0, data={
            "run_id": run_id,
            "message": "运行中",
            "status": "running"
        })
    else:
        value = conn.get(key).decode()
        conn.delete(key)
        return make_response(0, data=json.loads(value))


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
