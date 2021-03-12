"""
这个路由用以处理使用手机号的用户操作（例如登录，注册，找回密码）
"""
from api import auth
from flask import Blueprint, session
from common.utils import unpack_argument
from utils import make_response
from main import config, db, web_app
from models.user import User
from api import auth as phoneauth
import sqlalchemy.sql.expression as expr
import re
import datetime
import time
import argon2
router = Blueprint("phoneuser", __name__)


@router.route("/reset_password", methods=["POST"])
@unpack_argument
def api_resetpassword(
    phone: str,
    password: str,
    authcode: str
):
    """
    重置密码
    """
    if not phoneauth.validate_sms_code(phone, authcode):
        return make_response(-1, message="验证码错误")
    user: User = db.session.query(User).filter_by(phone_number=phone).one()
    hasher = argon2.PasswordHasher()
    user.password = hasher.hash(password)
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/check_phone", methods=["POST"])
@unpack_argument
def api_checkphone(phone: str):
    """
    检测手机号是不是正在使用
    """
    return make_response(0, data={
        "using": db.session.query(User).filter_by(phone_number=phone).count() != 0
    })


@router.route("/register", methods=["POST"])
@unpack_argument
def api_register(
    username: str,
    password: str,
    email: str,
    phone: str,
    authcode: str
):
    """
    使用手机号注册
    """
    if not config.USE_PHONE_WHEN_REGISTER_AND_RESETPASSWD:
        return make_response(-1, message="不使用手机号注册用户")
    if session.get("uid", None):
        return make_response(-1, message="你已登录")
    if not re.match(config.USERNAME_REGEX, username):
        return make_response(-1, message=f"用户名必须符合正则表达式: {config.USERNAME_REGEX}")
    used = db.session.query(User).filter(
        expr.or_(
            User.username == username,
            User.email == email,
            User.phone_number == phone
        )
    ).count()
    if used:
        return make_response(-1, message="当前用户名或邮箱或手机号已被他人使用!")
    if not phoneauth.validate_sms_code(phone, authcode):
        return make_response(-1, message="验证码校验失败")
    hasher = argon2.PasswordHasher()
    user = User(
        username=username,
        email=email,
        password=hasher.hash(password),
        register_time=datetime.datetime.now(),
        phone_number=phone,
        phone_verified=True
    )
    db.session.add(user)
    db.session.commit()
    session.permanent = True
    session["uid"] = user.id
    session["login_time"] = str(int(time.time()))
    return make_response(0, message="操作完成")
