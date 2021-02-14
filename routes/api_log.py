from flask import Blueprint, request
from main import redis_connection_pool, config, log_manager
from common.utils import unpack_argument, require_header
from utils import make_response
from flask import request
import redis
router = Blueprint("log", __name__)


@router.route("/update", methods=["POST"])
@require_header("log-token", config.LOG_TOKEN)
@unpack_argument
def log_update(log_key: str, log: str):
    log_manager.set_log(log_key, log)
    return make_response(0, message="ok")


@router.route("/get", methods=["POST"])
@unpack_argument
def log_get(log_key: str):
    """
    获取日志
    {
        "content":"日志内容"
    }
    """

    return make_response(0, content=log_manager.get_log(log_key))
