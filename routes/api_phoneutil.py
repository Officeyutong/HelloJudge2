from main import config, db, redis_connection_pool, web_app, background_task_queue
from flask import Blueprint, session, request
import flask
from utils import make_response
from common.utils import unpack_argument
from models.user import User
from xml.dom import minidom
import redis
import datetime
import random
from aliyunsdkcore import client
from aliyunsdkafs.request.v20180112 import AuthenticateSigRequest
from aliyunsdkcore.profile import region_provider
from api import auth as phoneauth
router = Blueprint("phoneutil", __name__)
region_provider.add_endpoint('afs', 'cn-hangzhou', 'afs.aliyuncs.com')

aliyun_client = client.AcsClient(config.ALIYUN_ACCESS_KEY_ID,
                                 config.ALIYUN_ACCESS_SECRET, 'cn-hangzhou')


@router.route("/preparation", methods=["POST"])
def api_preparation():
    return make_response(0, data={
        "appKey": config.ALIYUN_CAPTCHA_APP_KEY
    })


@router.route("/sendcode", methods=["POST"])
@unpack_argument
def api_sendcode(phone: str, noCaptcha: dict, must_not_use: bool = False):
    """
    用户请求发送短信
    noCaptcha:{
        "nc_token",
        "csessionid",
        "sig"
    }
    must_not_use: 这个手机号不得被他人使用
    """
    # 不需要登录就能发验证码
    # if not session.get("uid", None):
    #     return make_response(-1, message="请先登录")
    import time

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
    if must_not_use:
        if db.session.query(User).filter_by(phone_number=phone).count():
            return make_response(-1, message="该手机号已被使用")
    if resp_code != '100':
        return make_response(-1, message=f"请完成滑块验证")
    if time.time()-phoneauth.get_send_time(phone) < config.MIN_SEND_GAP:
        return make_response(-1, message=f"两次发送验证码的最短间隔为{config.MIN_SEND_GAP}秒")

    code = "".join(str(random.randint(0, 9)) for x in range(6))
    phoneauth.send_sms_code(phone, code, config.CODE_VALIDITY)
    print("task pushed")
    return make_response(0, message=f"短信已加入发送队列(验证码有效期 {config.CODE_VALIDITY}s)，请注意查收")
