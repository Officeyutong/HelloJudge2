from main import web_app as app
from main import db, config, basedir, permission_manager, redis_connection_pool, csrf, socket
from main import queue
from common.utils import unpack_argument
from common.permission import require_permission
from flask import session, request, send_file, send_from_directory
from utils import make_response
from flask_socketio import emit, join_room
from models import RemoteAccount
from typing import List, Dict
from models import Problem
import uuid


@socket.on("connect", namespace="/ws/remote_judge")
def remote_judge_socketio():
    """
    客户端连接，生成一个UUID作为客户端标识符
    """
    print("Connected...")
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


@socket.on("fetch_problem", namespace="/ws/remote_judge")
def remote_judge_add_remote_problem(data: dict):
    oj, remoteProblemID = data["oj"], data["remoteProblemID"]
    if oj not in config.REMOTE_JUDGE_OJS:
        return make_response(-1, message="不合法的OJ")
    import datetime
    problem = Problem(create_time=datetime.datetime.now())
    problem.uploader_id = int(session.get("uid"))
    db.session.add(problem)
    db.session.commit()
    queue.send_task("judgers.remote.fetch_problem", [
        oj,
        remoteProblemID,
        str(problem.id),
        data["sessionID"]
    ])
    emit("message", {"message": "正在爬取"}, room=data["sessionID"])


@app.route("/api/remote_judge/get_available_ojs", methods=["POST"])
def remote_judge_get_available_ojs():
    return make_response(0, data=config.REMOTE_JUDGE_OJS)


@app.route("/api/judge/remote_judge/update_submit", methods=["POST"])
@csrf.exempt
@unpack_argument
def remote_judge_update(ok: bool, data: dict, uuid: str, client_session_id: str):
    if uuid not in config.JUDGERS:
        return make_response(-1, message="未认证评测机")
    emit("server_response", {"ok": ok, "data": data},
         room=client_session_id, namespace="/ws/remote_judge")
    return make_response(0, message="done")


@app.route("/api/judge/remote_judge/update_fetch", methods=["POST"])
@csrf.exempt
@unpack_argument
def remote_judge_update_fetch(ok: bool,  uuid: str, client_session_id: str, hj2_problem_id: str, result: dict = None, message: str = ""):
    """
    更新爬取题目状态
    """
    if uuid not in config.JUDGERS:
        return make_response(-1, message="未认证评测机")
    if not ok:
        emit("server_response", {"ok": False,
                                 "message": message}, room=client_session_id)
        db.session.query(Problem).filter(Problem.id == hj2_problem_id).delete()
        return
    problem: Problem = db.session.query(Problem).filter(
        Problem.id == hj2_problem_id).one()
    # print(result)
    problem.title = result["title"]
    problem.background = "内存限制: {} MB\n\n时间限制: {} ms".format(
        result["memoryLimit"], result["timeLimit"])+result["background"]
    problem.content = result["content"]
    problem.hint = result["hint"]
    problem.input_format = result["inputFormat"]
    problem.output_format = result["outputFormat"]
    problem.remote_judge_oj = result["remoteOJ"]
    problem.remote_problem_id = result["remoteProblemID"]
    problem.example = result["examples"]

    db.session.commit()
    emit("server_response", {
         "ok": ok, "problemID": hj2_problem_id}, room=client_session_id, namespace="/ws/remote_judge")
    return make_response(0, message="done")


@app.route("/api/remote_judge/get_accounts", methods=["POST"])
@require_permission(permission_manager, "remote_judge.use")
def remote_judge_get_accounts():
    accounts = db.session.query(RemoteAccount).filter(
        RemoteAccount.uid == session.get("uid")).all()
    result = {
        "availableOJs": config.REMOTE_JUDGE_OJS,
        "accounts": []
    }
    for item in accounts:
        result["accounts"].append({
            "accountID": item.account_id,
            "username": item.username,
            "password": item.password,
            "oj": item.oj
        })
    return make_response(0, data=result)


@app.route("/api/remote_judge/add_account", methods=["POST"])
@require_permission(permission_manager, "remote_judge.use")
def remote_judge_add_account():
    account_id = str(uuid.uuid1())
    db.session.add(RemoteAccount(
        account_id=account_id,
        username="",
        password="",
        oj=next(iter(config.REMOTE_JUDGE_OJS.keys())),
        uid=int(session.get("uid"))
    ))
    db.session.commit()
    return make_response(0, data={
        "accountID": account_id
    })


@app.route("/api/remote_judge/remove_account", methods=["POST"])
@require_permission(permission_manager, "remote_judge.use")
@unpack_argument
def remote_judge_remove_account(accountID: str):
    remote_account: RemoteAccount = db.session.query(RemoteAccount).filter(
        RemoteAccount.account_id == accountID).one_or_none()
    if not remote_account:
        return make_response(-1, message="错误的用户ID")
    if remote_account.uid != int(session.get("uid")):
        return make_response(-1, message="你只能更改自己的Remote Judge账户")
    db.session.delete(remote_account)
    db.session.commit()
    return make_response(0, message="删除成功")


@app.route("/api/remote_judge/update_accounts", methods=["POST"])
@require_permission(permission_manager, "remote_judge.use")
@unpack_argument
def remote_judge_update_accounts(accounts: List[Dict[str, str]]):
    for item in accounts:
        current_account: RemoteAccount = db.session.query(RemoteAccount).filter(
            RemoteAccount.account_id == item["accountID"]).one_or_none()
        if not current_account:
            return make_response(-1, message=f"未知账户ID {item['accountID']}")
        if current_account.uid != int(session.get("uid")):
            return make_response(-1, message=f"账户 {item['accountID']} 不属于你")
        if item['oj'] not in config.REMOTE_JUDGE_OJS:
            return make_response(-1, message=f"账户 {item['accountID']} 的OJ {item['oj']} 不合法")
        current_account.oj = item['oj']
        current_account.password = item['password']
        current_account.username = item['username']
    db.session.commit()
    return make_response(0, message="更新完成")
