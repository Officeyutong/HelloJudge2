from main import config, redis_connection_pool, background_task_queue
import redis
import time
import json

"""

负责发送并维护短信验证码
"""


def make_code_key(phone: str) -> str:
    return f"hj2-phoneauth-code-{phone}"


def make_time_key(phone: str) -> str:
    return f"hj2-phoneauth-jointime-{phone}"


def get_send_time(phone: str) -> int:
    """
    查询验证码的发送时间
    如果已超期，则返回0

    """
    key = make_time_key(phone)
    client = redis.Redis(connection_pool=redis_connection_pool)
    if not client.exists(key):
        return 0
    else:
        return int(client.get(key).decode())


def send_sms_code(phone: str, code: str, expire_after: int):
    """
    发送短信验证码
    @param phone: 目标手机号
    @param code: 短信验证码
    @param expire_after: 超时时间(秒)
    """
    redis_key = make_code_key(phone)

    client = redis.Redis(connection_pool=redis_connection_pool)
    client.set(redis_key, code, ex=config.CODE_VALIDITY)
    client.set(make_time_key(phone), str(
        int(time.time())), ex=config.CODE_VALIDITY)
    # print(f"Sending {code=} to {phone=}")
    # user.last_auth_code = code
    # user.last_send_time = datetime.datetime.now()
    # user.phone_number = phone
    # db.session.commit()
    # print("db commited")
    # background_task_queue.send_task("qbxtoj.send_sms_code", [{
    #     "access_key": config.ALIYUN_ACCESS_KEY_ID,
    #     "access_secret": config.ALIYUN_ACCESS_SECRET,
    #     "region": config.ALIYUN_REGION,
    #     "sign_name": config.ALIYUN_SIGN_NAME,
    #     "template_code": config.ALIYUN_TEMPLATE_CODE,
    #     "target_phone": phone,
    #     "code": code
    # }])
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    client = AcsClient(config.ALIYUN_ACCESS_KEY_ID,
                       config.ALIYUN_ACCESS_SECRET, config.ALIYUN_REGION)
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')
    request.add_query_param("RegionId", config.ALIYUN_REGION)
    request.add_query_param("PhoneNumbers", phone)
    request.add_query_param("SignName", config.ALIYUN_SIGN_NAME)
    request.add_query_param("TemplateCode", config.ALIYUN_TEMPLATE_CODE)
    request.add_query_param("TemplateParam", json.dumps({
        "code": code
    }))
    response = client.do_action(request).decode()
    return response

def validate_sms_code(phone: str, code: str) -> bool:
    """
    校验短信验证码，返回是否成功
    @param phone: 目标手机号
    @param code: 验证码
    """
    redis_key = make_code_key(phone)
    client = redis.Redis(
        connection_pool=redis_connection_pool, decode_responses=False)
    if not client.exists(redis_key):
        return False
    if client.get(redis_key) != code.encode():
        return False
    return True


def remove_auth(phone: str):
    """
    手动移除验证码
    """
    redis_key = make_code_key(phone)
    client = redis.Redis(
        connection_pool=redis_connection_pool, decode_responses=False)
    if client.exists(redis_key):
        client.delete(redis_key)
    if client.exists(make_time_key(phone)):
        client.delete(make_time_key(phone))


def check_already_send(phone: str):
    """
    查询是否已验证
    """
    return redis.Redis(connection_pool=redis_connection_pool).exists(make_code_key(phone))
