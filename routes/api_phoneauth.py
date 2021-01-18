"""
此文件为旧式手机验证相关路由
新式路由见phoneutil
"""

from time import sleep
from models.submission import Submission
import typing

from main import background_task_queue, db, config, permission_manager
from main import web_app as app
from common.permission import require_permission
from common.utils import unpack_argument
from flask_sqlalchemy import BaseQuery
from flask import session
import flask
from utils import make_response
from models.user import User
import sqlalchemy.sql.expression as expr
from sqlalchemy.sql import func

import datetime
import random

from aliyunsdkcore import client
from aliyunsdkafs.request.v20180112 import AuthenticateSigRequest
from aliyunsdkcore.profile import region_provider

from xml.dom import minidom

region_provider.add_endpoint('afs', 'cn-hangzhou', 'afs.aliyuncs.com')

aliyun_client = client.AcsClient(config.ALIYUN_ACCESS_KEY_ID,
                                 config.ALIYUN_ACCESS_SECRET, 'cn-hangzhou')


@app.route("/api/phoneauth/preparation", methods=["POST"])
def api_phoneauth_preparation():
    return make_response(0, data={
        "appKey": config.ALIYUN_CAPTCHA_APP_KEY
    })


@app.route("/api/phoneauth/sendcode", methods=["POST"])
@unpack_argument
def api_phoneauth_sendcode(phone: str, noCaptcha: dict):
    """
    用户请求发送短信
    noCaptcha:{
        "nc_token",
        "csessionid",
        "sig"
    }
    """
    if not session.get("uid", None):
        return make_response(-1, message="请先登录")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    if user.phone_verified:
        return make_response(-1, message="您已验证过手机号")
    if user.last_send_time:
        if (((datetime.datetime.now()-user.last_send_time)).total_seconds()) < config.MIN_SEND_GAP:
            return make_response(-1, message=f"两次发送验证码的最短间隔为{config.MIN_SEND_GAP}秒")
    already_used_user = db.session.query(User.id).filter(
        User.phone_number == phone).one_or_none()
    if already_used_user and already_used_user.id != user.id:
        return make_response(-1, message="此号码已由他人使用")
    request = AuthenticateSigRequest.AuthenticateSigRequest()
    request.set_AppKey(config.ALIYUN_CAPTCHA_APP_KEY)
    request.set_RemoteIp(flask.request.remote_addr)
    request.set_Scene("nc_message")
    request.set_Token(noCaptcha["nc_token"])
    request.set_SessionId(noCaptcha["csessionid"])
    request.set_Sig(noCaptcha["sig"])
    # print("before making req")
    result = aliyun_client.do_action(request)
    # print("resp got")
    tree = minidom.parseString(result.decode())
    resp_code = tree.getElementsByTagName("Code")[0].firstChild.data
    if resp_code != '100':
        return make_response(-1, message=f"请完成滑块验证")
    code = "".join(str(random.randint(0, 9)) for x in range(6))
    # print(f"Sending {code=} to {phone=}")
    user.last_auth_code = code
    user.last_send_time = datetime.datetime.now()
    user.phone_number = phone
    db.session.commit()
    # print("db commited")
    background_task_queue.send_task("qbxtoj.send_sms_code", [{
        "access_key": config.ALIYUN_ACCESS_KEY_ID,
        "access_secret": config.ALIYUN_ACCESS_SECRET,
        "region": config.ALIYUN_REGION,
        "sign_name": config.ALIYUN_SIGN_NAME,
        "template_code": config.ALIYUN_TEMPLATE_CODE,
        "target_phone": phone,
        "code": code
    }])
    print("task pushed")
    return make_response(0, message=f"短信已加入发送队列(验证码有效期 {config.CODE_VALIDITY}s)，请注意查收")


@app.route("/api/phoneauth/auth", methods=["POST"])
@unpack_argument
def api_phoneauth_auth(code: str):
    """
    校验短信验证码
    """
    if not session.get("uid", None):
        return make_response(-1, message="请先登录")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    if user.phone_verified:
        return make_response(-1, message="您已验证过手机号")
    if not user.last_auth_code:
        return make_response(-1, message="请先发送验证码")
    if code != user.last_auth_code:
        return make_response(-1, message="验证码错误")
    if (datetime.datetime.now()-user.last_send_time).seconds > config.CODE_VALIDITY:
        return make_response(-1, message="验证码已过期,请重新发送")
    user.phone_verified = True
    db.session.commit()
    return make_response(0, message="验证成功，请稍等跳转")
