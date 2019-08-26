from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import *
from models.problem import *
from models.submission import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename


@app.route("/api/get_judge_status", methods=["POST", "GET"])
def get_judge_status():
    """
    获取评测状态列表
    参数:无
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//调用失败时的信息
            "data":{
                "accepted":{"icon":"xxx","text":"xxx"}
            }
        }
    """
    ret = {
        "waiting": {"icon": "notched circle loading icon", "text": "等待评测中", "color": "blue"},
        "judging": {"icon": "notched circle loading icon", "text": "评测中", "color": "blue"},
        "accepted": {"icon": "check icon", "text": "通过", "color": "green"},
        "unaccepted": {"icon": "times icon", "text": "未通过", "color": "red"},
        "wrong_answer": {"icon": "x icon", "text": "答案错误", "color": "red"},
        "time_limit_exceed": {"icon": "clock outline icon", "text": "超出时限", "color": "red"},
        "runtime_error": {"icon": "exclamation circle icon", "text": "运行时错误", "color": "red"},
        "skipped": {"icon": "cog icon", "text": "跳过", "color": "blue"},
        "unknown": {"icon": "question circle icon", "text": "未知", "color": "black"},
        "invisible": {"icon": "times icon", "text": "不可见", "color": "black"},
        "unsubmitted": {"icon": "notched circle loading icon", "text": "未提交", "color": "red"}
    }
    return make_response(0, data=ret)


@app.route("/api/get_supported_langs", methods=["POST", "GET"])
def get_supported_lang():
    """
    获取支持的语言列表
    参数:
        无
    返回:
        {
            "code":0,//非0表示调用成功
            "list":[
                {"id":"c++11","display":"C++ 11","version":"G++ 8.3"}
            ]
        }
    """
    result = []
    import os
    import importlib
    for file in filter(lambda x: x.endswith(".py"), os.listdir("langs")):
        module = importlib.import_module("langs."+file.replace(".py", ""))
        result.append({
            "id": file.replace(".py", ""), "display": module.DISPLAY, "version": module.VERSION, "ace_mode": module.ACE_MODE
        })
    return make_response(0, list=result)
