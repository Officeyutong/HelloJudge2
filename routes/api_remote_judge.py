from main import web_app as app
from main import db, config, basedir, permission_manager, redis_connection_pool, csrf, socket
from main import remote_judge_queue
from common.utils import unpack_argument
from common.permission import require_permission
from flask import session, request, send_file, send_from_directory
from utils import make_response, decode_json, encode_json
from flask_socketio import emit, join_room
from models import RemoteAccount, User, Problem, Submission, Discussion
from typing import List, Dict
from sqlalchemy.sql.expression import and_
import uuid


@socket.on("submit", namespace="/ws/remote_judge")
def remote_judge_submit(data):
    """
    客户端提交代码
    {
        "problemID":hj2题目ID,
        "remoteAccountID":"远程用户ID",
        "code":"用户代码",
        "language":"用户选择的语言",
        "loginCaptcha":"登录验证码",
        "submitCaptcha":"提交验证码"
    }
    """
    if not permission_manager.has_permission(session.get("uid"), "remote_judge.use"):
        emit("server_response", {"ok": False,
                                 "message": "你没有权限这样做"}, room=request.sid)
        return
    problem: Problem = Problem.by_id(data["problemID"])
    if not problem.public and int(session.get("uid")) != problem.uploader_id and not permission_manager.has_permission(session.get("uid"), "problem.manage"):
        emit("server_response", {"ok": False,
                                 "message": "你没有权限使用此题目"}, room=request.sid)
        return
    if len(data["code"]) > config.MAX_CODE_LENGTH:
        emit("server_response", {"ok": False,
                                 "message": "代码过长"}, room=request.sid)
        return
    remote_account: RemoteAccount = db.session.query(RemoteAccount).filter(
        RemoteAccount.account_id == data["remoteAccountID"]).one_or_none()
    if not remote_account or remote_account.uid != int(session.get("uid")):
        emit("server_response", {"ok": False,
                                 "message": "非法账户ID"}, room=request.sid)
        return
    if data["language"] not in config.REMOTE_JUDGE_OJS[problem.remote_judge_oj]["availableLanguages"]:
        emit("server_response", {"ok": False,
                                 "message": "非法语言"}, room=request.sid)
        return

    remote_judge_queue.send_task("judgers.remote.submit", [
        problem.remote_judge_oj,
        decode_json(remote_account.session),
        remote_account.account_id,
        problem.remote_problem_id,
        data["language"],
        data["code"],
        data["loginCaptcha"],
        data["submitCaptcha"],
        request.sid,
        remote_account.username,
        remote_account.password,
        problem.id,
        int(session.get("uid")),
        problem.public,
        list(reversed(config.TRACK_DELAY_INTERVAL))
    ])
    emit("message", {"message": "提交中..."}, room=request.sid)


@socket.on("fetch_problem", namespace="/ws/remote_judge")
def remote_judge_add_remote_problem(data: dict):
    """
    客户端发送添加题目请求
    """
    import datetime
    from flask import request
    oj, remoteProblemID = data["oj"], data["remoteProblemID"]
    if oj not in config.REMOTE_JUDGE_OJS:
        return make_response(-1, message="不合法的OJ")
    if not permission_manager.has_permission(session.get("uid"), "problem.create"):
        emit("server_response", {
             "message": "你没有权限这样做", "ok": False}, room=request.sid)
        return
    problem = Problem(create_time=datetime.datetime.now())
    problem.uploader_id = int(session.get("uid"))
    db.session.add(problem)
    db.session.commit()
    print("Fetching: ", [
        oj,
        remoteProblemID,
        str(problem.id),
        request.sid
    ])
    remote_judge_queue.send_task("judgers.remote.fetch_problem", [
        oj,
        remoteProblemID,
        str(problem.id),
        request.sid
    ])
    emit("message", {"message": "正在爬取"}, room=request.sid)


@app.route("/api/remote_judge/get_available_ojs", methods=["POST"])
def remote_judge_get_available_ojs():
    return make_response(0, data=config.REMOTE_JUDGE_OJS)


@app.route("/api/judge/remote_judge/create_submission", methods=["POST"])
@csrf.exempt
@unpack_argument
def remote_judge_create_submission(
    uuid: str,
    client_session_id: str,
    code: str,
    language: str,
    uid: int,
    hj2_problem_id: str,
    public: bool,
    message: str
):
    """
    评测端向远程OJ提交代码成功后，创建相应的提交记录
    """
    if uuid not in config.JUDGERS:
        return make_response(-1, message="未认证评测机")
    import datetime
    submission: Submission = Submission(
        uid=uid,
        language=language,
        problem_id=hj2_problem_id,
        submit_time=datetime.datetime.now(),
        public=public,
        code=code,
        status="waiting",
    )
    db.session.add(submission)
    db.session.commit()
    print("Submit done. ", submission.id)
    emit("server_response", {"ok": True, "data": {"submission_id": submission.id}},
         room=client_session_id, namespace="/ws/remote_judge")
    return make_response(0, data={"submission_id": submission.id})


@app.route("/api/judge/remote_judge/update_submit_status", methods=["POST"])
@csrf.exempt
@unpack_argument
def remote_judge_update(ok: bool, data: dict, uuid: str, client_session_id: str):
    """
    提交时状态更新,评测端调用
    """
    if uuid not in config.JUDGERS:
        return make_response(-1, message="未认证评测机")
    emit("server_response", {"ok": ok, "data": data},
         room=client_session_id, namespace="/ws/remote_judge")
    return make_response(0, message="done")


@app.route("/api/judge/remote_judge/update_session", methods=["POST"])
@csrf.exempt
@unpack_argument
def remote_judge_update_session(uuid: str, account_id: str, session: dict):
    """
    登录后更新session
    """
    print(locals())
    # print(kwargs)
    if uuid not in config.JUDGERS:
        return make_response(-1, message="未认证评测机")
    account: RemoteAccount = db.session.query(RemoteAccount).filter(
        RemoteAccount.account_id == account_id).one()
    account.session = encode_json(session)
    db.session.commit()
    return make_response(0, message="done")


@app.route("/api/judge/remote_judge/update_fetch", methods=["POST"])
@csrf.exempt
@unpack_argument
def remote_judge_update_fetch(ok: bool,  uuid: str, client_session_id: str, hj2_problem_id: str, result: dict = None, message: str = ""):
    """
    更新添加题目状态,评测端调用
    """
    if uuid not in config.JUDGERS:
        return make_response(-1, message="未认证评测机")
    if not ok:
        emit("server_response", {"ok": False,
                                 "message": message}, room=client_session_id, namespace="/ws/remote_judge")
        db.session.query(Problem).filter(Problem.id == hj2_problem_id).delete()
        return make_response(0, message="done")
    problem: Problem = db.session.query(Problem).filter(
        Problem.id == hj2_problem_id).one()
    # print(result)
    problem.title = result["title"]
    problem.background = "内存限制: {} MB\n\n时间限制: {} ms\n\n".format(
        result["memoryLimit"], result["timeLimit"])+result["background"]
    problem.content = result["content"]
    problem.hint = result["hint"]
    problem.input_format = result["inputFormat"]
    problem.output_format = result["outputFormat"]
    problem.remote_judge_oj = result["remoteOJ"]
    problem.remote_problem_id = result["remoteProblemID"]
    problem.example = result["examples"]
    problem.problem_type = "remote_judge"
    problem.downloads = []
    problem.extra_parameter = []
    problem.files = []
    problem.provides = []
    problem.subtasks = []
    db.session.commit()
    emit("server_response", {
         "ok": ok, "problemID": hj2_problem_id, "message": "添加成功"}, room=client_session_id, namespace="/ws/remote_judge")
    return make_response(0, message="done")


@app.route("/api/remote_judge/get_problem_info", methods=["POST"])
@require_permission(permission_manager, "remote_judge.use")
@unpack_argument
def remote_judge_get_problem_info(problem_id: str):
    """
    {
        "code":0,
        "data":{
            "problemData":{
                "title":"题目名",
                "content":"题目内容",
                "background":"题目背景",
                "inputFormat":"输入格式",
                "outputFormat":'输出格式',
                "examples":[{"input":"样例输入","output":"样例输出"}],
                "createTime":"创建时间",
                "uploaderProfile":{
                    "uid":"用户ID",
                    "username":"用户名"
                },
                "remoteProblemID":"远程题目ID",
                "remoteOJ":{
                    "id":"远程OJID",
                    "display":"远程OJ显示名",
                    "availableLanguages":[
                        {"id":"0","display":"C++"}
                    ]
                },
                "public":"是否公开",
                "hint":"提示",
                "recentDiscussions":[
                    {
                        "id":123,
                        "title":"qw"
                    }
                ],
                "acceptedCount":"",
                "submissionCount":""
            },
            "userData":{
                "lastCode":"上次提交的代码",
                "lastLanguage":"上次选择的语言",
                "status":"qwq",
                "id":"",
                "accounts":{
                    "id":{
                        "username":"用户名",
                        "oj":"OJ",
                        "accountID":"ID"
                    }
                }
            }
        }

    }
    """
    problem: Problem = db.session.query(Problem).filter(
        Problem.id == problem_id).one_or_none()
    if not problem:
        return make_response(-1, message="未知题目ID")
    if problem.problem_type != "remote_judge":
        return make_response(-1, message="此题目非远程评测题目")
    if not permission_manager.has_permission(session.get("uid"), "remote_judge.use") and problem.uploader_id != int(session.get("uid")):
        return make_response(-1, message="你没有权限查看该题目")
    uploader: User = db.session.query(User.id, User.username).filter(
        User.id == problem.uploader_id).one()
    last_submission: Submission = db.session.query(Submission).filter(and_(
        Submission.problem_id == problem.id,
        Submission.uid == session.get("uid")
    )).order_by(Submission.score.desc()).order_by(Submission.id.desc())
    last_code, last_language, submission_id, status = "", next(iter(
        config.REMOTE_JUDGE_OJS[problem.remote_judge_oj]["availableLanguages"].keys())), -1, None
    if last_submission.count():
        last_submission = last_submission.first()
        last_code = last_submission.code
        last_language = last_submission.language
        status = last_submission.status
        submission_id = last_submission.id
    discussions = [

    ]
    discussions_query = db.session.query(Discussion.id, Discussion.title).filter(
        Discussion.path == f"discussion.problem.{problem.id}").order_by(Discussion.id.desc()).limit(5)
    for item in discussions_query:
        discussions.append({
            "id": item.id,
            "title": item.title
        })
    accounts = {}
    for item in db.session.query(RemoteAccount.account_id, RemoteAccount.username, RemoteAccount.oj).filter(
        and_(
            RemoteAccount.uid == session.get("uid", -1),
            RemoteAccount.oj == problem.remote_judge_oj
        )
    ):
        accounts[item.account_id] = {
            "username": item.username,
            "oj": config.REMOTE_JUDGE_OJS[item.oj]["display"],
            "accountID": item.account_id
        }
    return make_response(0, data={
        "problemData": {
            "title": problem.title,
            "content": problem.content,
            "background": problem.background,
            "inputFormat": problem.input_format,
            "outputFormat": problem.output_format,
            "examples": problem.example,
            "createTime": problem.create_time,
            "uploaderProfile": {
                "uid": uploader.id,
                "username": uploader.username
            },
            "remoteProblemID": problem.remote_problem_id,
            "remoteOJ": {
                "id": problem.remote_judge_oj,
                **config.REMOTE_JUDGE_OJS[problem.remote_judge_oj]
            },
            "public": problem.public,
            "hint": problem.hint,
            "recentDiscussions": discussions,
            "acceptedCount": db.session.query(Submission).filter(Submission.problem_id == problem.id).filter(Submission.status == "accepted").count(),
            "submissionCount": db.session.query(Submission).filter(Submission.problem_id == problem.id).count(),
            "id": problem.id

        },
        "userData": {
            "lastCode": last_code,
            "lastLanguage": last_language,
            "status": status,
            "id": submission_id,
            "managable": permission_manager.has_permission(
                session.get("uid", None), "problem.manage"),
            "accounts": accounts
        }
    })


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
        current_account.session = "{}"
    db.session.commit()
    return make_response(0, message="更新完成")
