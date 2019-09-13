from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *

from models import *
from sqlalchemy.sql.expression import *
# from werkzeug.utils import secure_filename
from typing import Tuple


@app.before_request
def banned_check():
    if session.get("uid"):
        user: User = User.by_id(session.get("uid"))
        if user.banned:
            session.pop("uid")


@app.route("/api/query_login_state", methods=["POST"])
def query_login_state():
    """
    查询登录状态。
    参数:
        无
    返回:
        {
            "code":0,//0表示调用成功
            "result": true,//表示是否已登录
            "uid":-1//如果已登录则表示用户ID,
            "is_admin":"是否是管理员"
        }

    """
    result = {
        "result": session.get("uid") is not None
    }
    if session.get("uid"):
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        result["uid"] = user.id
        result["is_admin"] = user.is_admin
    return make_response(0, **result)


@app.route("/api/login", methods=["POST"])
def login():
    """
    登录
    参数:
        identifier:str 用户名或者邮箱
        password:str 密码的加盐md5
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    if session.get("uid") is not None:
        return make_response(-1, message="你已经登录了！")
    query = db.session.query(User).filter(or_(
        User.email == request.form["identifier"], User.username == request.form["identifier"])).filter(User.password == request.form["password"])
    if query.count() == 0:
        return make_response(-1, message="用户名或密码错误")
    user: User = query.one()
    if user.banned:
        return make_response(-1, message="此账户已被封禁.")
    if user.auth_token != "":
        return make_response(-1, message="请点击您邮箱内的激活邮件验证您的账号。如果没有收到或者想要更改邮箱请使用您的用户名重新注册")
    session["uid"] = query.one().id
    session.permanment = True
    return make_response(0)


@app.route("/api/auth_email", methods=["POST"])
def auth_email():
    """
    验证用户邮箱
    username: 用户名
    token: 验证密钥

    """
    user: User = db.session.query(User).filter(and_(
        User.username == request.form["username"], User.auth_token == request.form["token"])).one_or_none()
    if not user:
        return make_response(-1, message="用户名或token错误")
    user.auth_token = ""
    db.session.commit()
    return make_response(0, message="ok")


@app.route("/api/register", methods=["POST"])
def register():
    """
    注册账号
    参数:
        username:str 用户名
        email:str 邮箱
        password:str 密码
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    if session.get("uid") is not None:
        return make_response(-1, message="你已经登录了！")
    import re
    import utils
    if re.match(config.USERNAME_REGEX, request.form["username"]) is None:
        return make_response(-1, message="用户名必须满足以下正则表达式:"+config.USERNAME_REGEX)
    if config.REQUIRE_REGISTER_AUTH:
        user = db.session.query(User).filter(
            User.username == request.form["username"])
        if user.count():
            user: User = user.one()
            next_query = db.session.query(User).filter(
                User.email == request.form["email"])
            if next_query.count() != 0 and next_query.one().username != request.form["username"]:
                return make_response(-1, message="此邮箱已被使用")
            if user.auth_token != "":
                import uuid
                user.auth_token = str(uuid.uuid1())
                send_mail(config.REGISTER_AUTH_EMAIL.format(
                    auth_token=user.auth_token), "验证邮件", request.form["email"])
                user.email = request.form["email"]
                db.session.commit()
                return make_response(-1, message=f"验证邮件已经发送到您的新邮箱{request.form['email']}")

    query = db.session.query(User).filter(or_(
        User.email == request.form["email"], User.username == request.form["username"]))
    if query.count():
        return make_response(-1, message="此用户名或邮箱已被用于注册账号")
    from datetime import datetime
    user = User(username=request.form["username"],
                email=request.form["email"], password=request.form["password"], register_time=datetime.now())
    import uuid
    if config.REQUIRE_REGISTER_AUTH:
        user.auth_token = str(uuid.uuid1())
        send_mail(config.REGISTER_AUTH_EMAIL.format(
            auth_token=user.auth_token), "验证邮件", request.form["email"])
        db.session.add(user)
        db.session.commit()
        return make_response(-1, message="验证邮件已经发送到您邮箱的垃圾箱，请注意查收")
    db.session.add(user)
    db.session.commit()
    session.permanment = True
    session["uid"] = user.id
    return make_response(0)


@app.route("/api/logout", methods=["POST"])
def logout():
    """
    登出账号
    参数:
        无
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    if session.get("uid") is None:
        return make_response(-1, message="你尚未登录!")
    session.pop("uid")
    return make_response(0)


@app.route("/api/require_reset_password", methods=["POST"])
def require_reset_password():
    """
    请求重设密码
    参数:
        {
            "identifier":"用户识别符"
        }
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    import uuid
    query = db.session.query(User).filter(or_(
        User.email == request.form["identifier"], User.username == request.form["identifier"]))
    if query.count() == 0:
        return make_response(-1, message="用户名或邮箱错误")
    user: User = query.one()
    user.reset_token = str(uuid.uuid1())
    from utils import send_mail
    try:
        send_mail(config.RESET_PASSWORD_EMAIL.format(
            reset_token=user.reset_token), "重置密码", user.email)
    except Exception as ex:
        import traceback
        return make_response(-1, message=traceback.format_exc())
    db.session.commit()
    return make_response(0, message="重置密码的邮件已经发送到您邮箱的垃圾箱，请注意查收")


@app.route("/api/reset_password", methods=["POST"])
def reset_password():
    """
    重设密码
    参数:
        {
            "identifier":"用户识别符",
            "reset_token":"重置密钥",
            "password":"新密码"
        }
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    query = db.session.query(User).filter(or_(
        User.email == request.form["identifier"], User.username == request.form["identifier"]))
    if query.count() == 0:
        return make_response(-1, message="用户名或邮箱错误")
    user: User = query.one()
    if user.reset_token != request.form["reset_token"]:
        return make_response(-1, message="Bad reset token")
    user.password = request.form["password"]
    user.reset_token = ""
    db.session.commit()
    return make_response(0, message="密码重置完成，请使用新密码登录。")


@app.route("/api/get_user_profile", methods=["POST"])
def get_user_profile():
    """
    获取用户个人信息
    参数:
        uid:int 用户ID
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
            "data":{
                "id":"用户ID"
                "username":"用户名",
                "email":"邮箱",
                "description":"描述",
                "is_admin":"是否为管理员",
                "ac_problems":"通过题目",
                "rating_history":[],
                "joined_teams":[
                    {"name":"团队名","id":"团队ID"}
                ],
                "banned":"是否已封禁"
            }
        }
    """
    user = db.session.query(User).filter(User.id == request.form["uid"])
    if user.count() == 0:
        return make_response(-1, message="未知用户ID")
    user: User = user.one()
    ret = user.as_dict()
    del ret["password"]
    del ret["reset_token"]
    problems = db.session.query(Submission.problem_id).filter(and_(Submission.uid == user.id, Submission.status == "accepted")
                                                              ).distinct().all()
    ret["ac_problems"] = [x[0] for x in problems]
    ret["rating"] = user.get_rating()
    ret["register_time"] = str(ret["register_time"])
    joined_teams = []
    for item in user.joined_teams:
        team = Team.by_id(item)
        joined_teams.append({"id": team.id, "name": team.name})
    ret["joined_teams"] = joined_teams
    for item in ret["rating_history"]:
        contest_name: Tuple[str] = db.session.query(Contest.name).filter(
            Contest.id == item["contest_id"]).one_or_none()
        if not contest_name:
            contest_name = "比赛不存在"
        # print(contest_name)
        item["contest_name"] = contest_name.name
    return make_response(0, data=ret)


@app.route("/api/update_profile", methods=["POST"])
def update_profile():
    """
    更新个人信息
    {
        "uid":"用户ID",
        "data":{
            "username":"用户名",
            "email":"电子邮件",
            "description":"个人简介",
            "changePassword":"是否更改密码",
            "newPassword":"新密码",
            "banned":"是否已封禁"
        }
    }
    {
        "code":0,"message":"qwq"
    }
    """
    import re
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    operator: User = User.by_id(session.get("uid"))
    user: User = User.by_id(request.form["uid"])
    if user.id != operator.id and not operator.is_admin:
        return make_response(-1, message="你无权进行此操作")
    data: dict = decode_json(request.form["data"])
    regex = re.compile(config.USERNAME_REGEX)
    if not regex.search(data["username"]):
        return make_response(-1, message="用户名必须符合以下正则表达式: {}".format(config.USERNAME_REGEX))
    if not re.compile(r"(.+)@(.+)").search(data["email"]):
        return make_response(-1, message="请输入合法的邮箱")
    user.username = data["username"]
    user.email = data["email"]
    user.description = data["description"]
    if data["changePassword"]:
        user.password = data["newPassword"]
    if data["banned"] != user.banned and not operator.is_admin:
        return make_response(-1, message="你没有权限封禁\解封此用户")
    user.banned = data["banned"]
    db.session.commit()
    return make_response(0, message="操作完成")
