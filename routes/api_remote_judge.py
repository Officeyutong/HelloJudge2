from main import web_app as app
from main import db, config, basedir, permission_manager, redis_connection_pool, csrf, socket
from common.utils import unpack_argument
from flask import session, request, send_file, send_from_directory
from utils import make_response
from flask_socketio import emit, join_room
import uuid


@socket.on("init", namespace="/ws/remote_judge")
def remote_judge_socketio(data):
    """
    客户端连接，生成一个UUID作为客户端标识符
    """
    uid = str(uuid.uuid1())
    join_room(room=uid)
    emit("set_client_session_id", {"client_session_id": uid}, room=uid)

@socket.on("submit", namespace="/ws/remote_judge")
def remote_judge_submit(data):
    """
    客户端提交代码
    {
        "problem_id":hj2题目ID,
        "remote_user_id":"远程用户ID",
        "code":"用户代码",
        "language":"用户选择的语言",
        "login_captcha":"登录验证码",
        "submit_captcha":"提交验证码"
    }
    """



@app.route("/api/judge/remote_judge/update", methods=["POST"])
@csrf.exempt
@unpack_argument
def remote_judge_update(ok: bool, data: dict, uuid: str, client_session_id: str):
    if uuid not in config.JUDGERS:
        return make_response(-1, message="未认证评测机")
    emit("server_response", {"ok": ok, "data": data}, room=client_session_id)
    return make_response(0, message="done")
