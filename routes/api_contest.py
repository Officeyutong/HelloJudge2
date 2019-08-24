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


@app.route("/api/contest/show", methods=["POST"])
def show_contest():
    """
    参数:
    {
        "contest_id"
    }
    {
        "code":0,
        "message":"",
        "data":{
            "name":"比赛名",
            "description":"说明",
            "id":"比赛ID",
            "owner_id":"所有者ID",
            "owner_username":"所有者用户名",
            "start_time":"开始时间(timestampm,s)",
            "end_time":"结束时间",
            "ranklist_visible":false,
            "judge_result_visible":false,
            "rank_criterion":"",
            "problems":[
                {
                    "weight":"题目权值,
                    "title":"题目标题",
                    "id":"题目ID(比赛中的)"
                    "total_submit":"总提交数",//-1表示不可见
                    "accepted_submit":"通过提交数",//-1表示不可见
                    "my_submit":"我的提交最高分提交",
                    "status":"我的状态"
                }
            ]
        }
    }
    """
    import time
    can_see_ranks = False
    contest: Contest = Contest.by_id(request.form["contest_id"])
    if not contest:
        return make_response(-1, message="未知题目ID")
    can_see_ranks = can_see_ranks or contest.ranklist_visible
    has_login = False
    if session.get("uid"):
        has_login = True
        user: User = User.by_id(session.get("uid"))
        if user.is_admin or user.id == contest.owner_id:
            can_see_ranks = True
    user: User = User.by_id(contest.owner_id)

    result = {
        "id": contest.id,
        "name": contest.name,
        "description": contest.description,
        "owner_id": user.id,
        "owner_username": user.username,
        "start_time": int(time.mktime(contest.start_time.timetuple())),
        "end_time": int(time.mktime(contest.end_time.timetuple())),
        "problems": [],
        "ranklist_visible": contest.ranklist_visible,
        "judge_result_visible": contest.judge_result_visible,
        "rank_criterion": contest.rank_criterion,
    }
    problems = result["problems"]
    for i, problem_data in enumerate(contest.problems):
        problem: Problem = Problem.by_id(problem_data["id"])
        current = {
            "title": problem.title,
            "id": i,
            "total_submit": -1,
            "accepted_submit": -1,
            "my_submit": -1,
            "status": "unknown", "weight": problem_data["weight"]
        }
        if can_see_ranks:
            submit_query = db.session.query(Submission).filter(
                Submission.contest_id == contest.id)
            current["total_submit"] = submit_query.count()
            current["accepted_submit"] = submit_query.filter(
                Submission.status == "accepted").count()
        if has_login:
            my_best_submit: Submission = db.session.query(Submission.id, Submission.status).filter(
                Submission.contest_id == contest.id).filter(Submission.uid == user.id).order_by(Submission.status.desc()).one_or_none()
            if my_best_submit:
                current["my_submit"] = my_best_submit.id
                current["status"] = my_best_submit.status
        problems.append(current)
    return make_response(0, data=result)


@app.route("/api/contest/raw_data", methods=["POST"])
def contest_raw_data():
    """
    contest_id
    {
                "id": contest.id,
        "name": contest.name,
        "description": contest.description,
        "start_time": int(time.mktime(contest.start_time.timetuple())),
        "end_time": int(time.mktime(contest.end_time.timetuple())),
        "problems": contest.problems,
        "ranklist_visible": contest.ranklist_visible,
        "judge_result_visible": contest.judge_result_visible,
        "rank_criterion": contest.rank_criterion,
    }
    """
    if not session.get("uid"):
        return "你没有权限这样做", 403
    user: User = User.by_id(session.get("uid"))
    contest: Contest = Contest.by_id(request.form["contest_id"])
    if not user.is_admin and user.id != contest.owner_id:
        return "你没有权限这样做", 403
    import time
    result = {
        "id": contest.id,
        "name": contest.name,
        "description": contest.description,
        "start_time": int(time.mktime(contest.start_time.timetuple())),
        "end_time": int(time.mktime(contest.end_time.timetuple())),
        "problems": contest.problems,
        "ranklist_visible": contest.ranklist_visible,
        "judge_result_visible": contest.judge_result_visible,
        "rank_criterion": contest.rank_criterion,
    }
    return make_response(0, data=result)


@app.route("/api/contest/update", methods=["POST"])
def contest_update():
    """
    更新比赛信息
    {
        contest_id:比赛ID,
        data:数据字典
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    contest: Contest = Contest.by_id(request.form["contest_id"])
    if not user.is_admin and user.id != contest.owner_id:
        return make_response(-1, message="请先登录")
    data: dict = decode_json(request.form["data"])
    print(data)
    for k, v in data.items():
        setattr(contest, k, v)

    def from_second_to_datetime(seconds):
        import time
        import datetime
        time_struct = time.localtime(seconds) 
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        print(time_str)
        return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    contest.start_time = from_second_to_datetime(data["start_time"])
    contest.end_time = from_second_to_datetime(data["end_time"])
    print(contest.start_time, contest.end_time)
    db.session.commit()
    return make_response(0, message="完成")
