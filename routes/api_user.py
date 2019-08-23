from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *

from models import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename
from typing import Tuple


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
            "uid":-1//如果已登录则表示用户ID
        }

    """
    result = {
        "result": session.get("uid") is not None
    }
    if session.get("uid"):
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        result["uid"] = user.id
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
    session["uid"] = query.one().id
    session.permanment = True
    return make_response(0)


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
    if re.match(config.USRENAME_REGEX, request.form["username"]) is None:
        return make_response(-1, message="用户名必须满足以下正则表达式:"+config.USRENAME_REGEX)
    query = db.session.query(User).filter(or_(
        User.email == request.form["email"], User.username == request.form["username"]))
    if query.count():
        return make_response(-1, message="此用户名或邮箱已被用于注册账号")
    from datetime import datetime
    user = User(username=request.form["username"],
                email=request.form["email"], password=request.form["password"], register_time=datetime.now())
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

    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    content = MIMEText(config.RESET_PASSWORD_EMAIL.format(
        reset_token=user.reset_token), "plain", "utf-8")
    content["From"] = Header("HelloJudgeV2", "utf-8")
    content["Subject"] = Header("重置密码", "utf-8")
    smtp_client = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
    smtp_client.login(config.SMTP_USER, config.SMTP_PASSWORD)
    smtp_client.sendmail(config.EMAIL_SENDER, user.email,
                         content.as_string())
    smtp_client.close()
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
                "username":"用户名",
                "email":"邮箱",
                "description":"描述",
                "is_admin":"是否为管理员",
                "ac_problems":"通过题目",
                "rating_history":"rating历史",
                "joined_teams":[
                    {"name":"团队名","id":"团队ID"}
                ]
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
    problems = db.session.query(Submission.problem_id).filter(
        Submission.uid == user.id and Submission.status == "AC").distinct().all()
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
        item["contest_name"] = contest_name
    return make_response(0, data=ret)
