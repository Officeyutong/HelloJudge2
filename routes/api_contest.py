from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename
import datetime
import math
import re
from typing import Iterable


@app.route("/api/contest/create", methods=["POST"])
def create_contest():
    """
    参数:
    {
        ""
    }
    {
        "code":0,
        "message":"",
        "contest_id":1
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    if not user.is_admin:
        return make_response(-1, message="只有管理员才可进行此操作")
    import datetime
    contest = Contest(owner_id=user.id,
                      start_time=datetime.datetime.now(),
                      end_time=datetime.datetime.now()+datetime.timedelta(hours=3)
                      )
    db.session.add(contest)
    db.session.commit()
    return make_response(0, contest_id=contest.id)


@app.route("/api/contest/list", methods=["POST"])
def contest_list():
    """
    {
        "page":"切换到的页面",
    }
    {
        "code":0,
        "data":{
            "page_count":"页面总数",
            "list":[
                {
                    "id":"比赛ID",
                    "name":"比赛名",
                    "owner_id":"所有者用户ID",
                    "owner_username":"所有者用户名",
                    "begin_time":"开始毫秒数",
                    "end_time":"结束毫秒数"
                }
            ]
        }
    }
    """
    page = int(request.form.get("page", 1))
    result = db.session.query(Contest).order_by(Contest.id.desc())
    count = result.count()
    import math
    pages = int(math.ceil(count/config.CONTESTS_PER_PAGE))
    result: Iterable[Contest] = result.slice(
        (page-1)*config.CONTESTS_PER_PAGE, (page)*config.CONTESTS_PER_PAGE).all()
    ret = {"page_count": int(math.ceil(count/config.CONTESTS_PER_PAGE)), "list": [

    ]}
    import time
    for contest in result:
        user: User = User.by_id(contest.owner_id)
        ret["list"].append({
            "id": contest.id,
            "name": contest.name,
            "owner_id": user.id,
            "owner_username": user.username,
            "start_time": int(time.mktime(contest.start_time.timetuple())),
            "end_time": int(time.mktime(contest.end_time.timetuple())),

        })
    return make_response(0, data=ret)
