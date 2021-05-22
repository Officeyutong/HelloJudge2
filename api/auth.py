from main import config, redis_connection_pool, background_task_queue
import redis


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
    import time
    client.set(make_time_key(phone), str(
        int(time.time())), ex=config.CODE_VALIDITY)
    # print(f"Sending {code=} to {phone=}")
    # user.last_auth_code = code
    # user.last_send_time = datetime.datetime.now()
    # user.phone_number = phone
    # db.session.commit()
    # print("db commited")
    background_task_queue.send_task("hj2.send_sms_code", [{
        "access_key": config.ALIYUN_ACCESS_KEY_ID,
        "access_secret": config.ALIYUN_ACCESS_SECRET,
        "region": config.ALIYUN_REGION,
        "sign_name": config.ALIYUN_SIGN_NAME,
        "template_code": config.ALIYUN_TEMPLATE_CODE,
        "target_phone": phone,
        "code": code
    }])


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
