from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import *
from models.problem import *
from models.submission import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename


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
            "userid":-1//如果已登录则表示用户ID
        }

    """
    result = {
        "result": session.get("userid") is not None
    }
    if session.get("userid"):
        user: User = db.session.query(User).filter(
            User.id == session.get("userid")).one()
        result["userid"] = user.id
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
    if session.get("userid") is not None:
        return make_response(-1, message="你已经登录了！")
    query = db.session.query(User).filter(or_(
        User.email == request.form["identifier"], User.username == request.form["identifier"])).filter(User.password == request.form["password"])
    if query.count() == 0:
        return make_response(-1, message="用户名或密码错误")
    session["userid"] = query.one().id
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
    if session.get("userid") is not None:
        return make_response(-1, message="你已经登录了！")
    import re
    if re.match(config.USRENAME_REGEX, request.form["username"]) is None:
        return make_response(-1, message="用户名必须满足以下正则表达式:"+config.USRENAME_REGEX)
    query = db.session.query(User).filter(or_(
        User.email == request.form["email"], User.username == request.form["username"]))
    if query.count():
        return make_response(-1, message="此用户名或邮箱已被用于注册账号")
    user = User(username=request.form["username"],
                email=request.form["email"], password=request.form["password"])
    db.session.add(user)
    db.session.commit()
    session.permanment = True
    session["userid"] = user.id
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
    if session.get("userid") is None:
        return make_response(-1, message="你尚未登录!")
    session.pop("userid")
    return make_response(0)


@app.route("/api/get_user_profile", methods=["POST"])
def get_user_profile():
    """
    获取用户个人信息
    参数:
        user_id:int 用户ID
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
            "data":{
                "username":"用户名",
                "email":"邮箱",
                "description":"描述",
                "is_admin":"是否为管理员"
            }
        }
    """
    user = db.session.query(User).filter(User.id == request.form["user_id"])
    if user.count() == 0:
        return make_response(-1, message="未知用户ID")
    user: User = user.one()
    ret = user.as_dict()
    del ret["password"]
    del ret["reset_token"]
    return make_response(0, data=ret)
