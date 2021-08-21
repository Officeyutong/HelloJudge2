"""
注册时不使用手机号，注册后使用手机号的，使用这个路由
"""

from main import db
from main import web_app as app
from common.utils import unpack_argument
from flask import session
from utils import make_response
from models.user import User
import api.auth as phoneapi

@app.route("/api/phoneauth/auth", methods=["POST"])
@unpack_argument
def api_phoneauth_auth(code: str, phone: str):
    """
    校验短信验证码
    """
    if not session.get("uid", None):
        return make_response(-1, message="请先登录")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    if user.phone_verified:
        return make_response(-1, message="您已验证过手机号")
    if db.session.query(User).filter_by(phone_number=phone).count():
        return make_response(-1, message="此号码已被别人使用")
    if not phoneapi.validate_sms_code(phone, code):
        return make_response(-1, message="验证码错误")
    user.phone_verified = True
    user.phone_number = phone
    db.session.commit()
    return make_response(0, message="验证成功，请稍等跳转")
