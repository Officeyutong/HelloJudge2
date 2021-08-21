from main import config, db, redis_connection_pool, web_app, background_task_queue
from flask import Blueprint, session, request
import flask
from utils import make_response
from common.utils import unpack_argument
from models.user import User
import redis
import datetime
import random
import requests
from api import auth as phoneauth
from typing import Dict, Any
router = Blueprint("phoneutil", __name__)


@router.route("/preparation", methods=["POST"])
def api_preparation():
    return make_response(0, data={
        "site_key": config.RECAPTCHA_SITE_KEY
    })


@router.route("/sendcode", methods=["POST"])
@unpack_argument
def api_sendcode(phone: str, client_response: Any, must_not_use: bool = False):
    """
    用户请求发送短信
    client_response: 客户端从验证端拿到的response
    must_not_use: 这个手机号不得被他人使用
    """
    # 不需要登录就能发验证码
    # if not session.get("uid", None):
    #     return make_response(-1, message="请先登录")
    resp = requests.post("https://www.recaptcha.net/recaptcha/api/siteverify", data={
        "secret": config.RECAPTCHA_SECRET,
        "response": client_response
    }).json()
    import time
    ok = resp["success"]
    if must_not_use:
        if db.session.query(User).filter_by(phone_number=phone).count():
            return make_response(-1, message="该手机号已被使用")
    if not ok:
        print(f"reCaptcha auth error {phone=}: {resp['error-codes']}")
        return make_response(-1, message=f"请完成验证")
    if time.time()-phoneauth.get_send_time(phone) < config.MIN_SEND_GAP:
        return make_response(-1, message=f"两次发送验证码的最短间隔为{config.MIN_SEND_GAP}秒")

    code = "".join(str(random.randint(0, 9)) for x in range(6))
    send_resp = phoneauth.send_sms_code(phone, code, config.CODE_VALIDITY)
    print(f"Code to {phone}", send_resp)
    return make_response(0, message=f"短信已加入发送队列(验证码有效期 {config.CODE_VALIDITY}s)，请注意查收")
