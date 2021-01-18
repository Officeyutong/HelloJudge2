from flask import Blueprint, request
from main import redis_connection_pool, config
from common.utils import unpack_argument
from utils import make_response
from flask import request
import redis
router = Blueprint("log", __name__)


@router.route("/update", methods=["POST"])
@unpack_argument
def log_update(logid: str, log: str, expireAfter: int = config.DEFAULT_LOG_EXPIRE):
    if request.headers.get("log-token", "") != config.LOG_TOKEN:
        return make_response(-1, message="Invalid log token")
    client = redis.Redis(connection_pool=redis_connection_pool)
    client.set(
        f"hj2-log-{logid}",
        log,
        ex=expireAfter
    )
    return make_response(0, message="ok")


@router.route("/get", methods=["POST"])
@unpack_argument
def log_get(logid: str):
    """
    获取日志
    {
        "content":"日志内容"
    }
    """
    client = redis.Redis(connection_pool=redis_connection_pool)
    key = f"hj2-log-{logid}"
    if not client.exists(key):
        return make_response(-1, message="ID不存在")

    return make_response(0, content=client.get(key).decode())
