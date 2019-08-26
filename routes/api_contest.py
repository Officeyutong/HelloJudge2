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
    can_see_judge_result = False
    contest: Contest = Contest.by_id(request.form["contest_id"])
    if not contest:
        return make_response(-1, message="未知题目ID")
    can_see_ranks = can_see_ranks or contest.ranklist_visible
    can_see_judge_result = can_see_judge_result or contest.judge_result_visible
    has_login = False
    if session.get("uid"):
        has_login = True
        user: User = User.by_id(session.get("uid"))
        if user.is_admin or user.id == contest.owner_id:
            can_see_ranks = True
            can_see_judge_result = True
    owner: User = User.by_id(contest.owner_id)

    result = {
        "id": contest.id,
        "name": contest.name,
        "description": contest.description,
        "owner_id": owner.id,
        "owner_username": owner.username,
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
            "status": "unsubmitted", "weight": problem_data["weight"]
        }
        if can_see_ranks:
            submit_query = db.session.query(Submission).filter(
                Submission.contest_id == contest.id).filter(Submission.problem_id == problem.id)
            current["total_submit"] = submit_query.count()
            current["accepted_submit"] = submit_query.filter(
                Submission.status == "accepted").count()
        if has_login:
            my_best_submit: Submission = db.session.query(Submission.id, Submission.status).filter(
                Submission.contest_id == contest.id).filter(and_(Submission.uid == user.id, Submission.problem_id == problem.id)).order_by(Submission.status.desc()).first()
            if my_best_submit:
                current["my_submit"] = my_best_submit.id
                current["status"] = my_best_submit.status
                if not can_see_judge_result:
                    current["status"] = "invisible"  
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
    # print(data)
    for k, v in data.items():
        setattr(contest, k, v)

    def from_second_to_datetime(seconds):
        import time
        import datetime
        time_struct = time.localtime(seconds)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        # print(time_str)
        return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    contest.start_time = from_second_to_datetime(data["start_time"])
    contest.end_time = from_second_to_datetime(data["end_time"])
    # print(contest.start_time, contest.end_time)
    db.session.commit()
    return make_response(0, message="完成")


@app.route("/api/contest/problem/show", methods=["POST"])
def contest_show_problem():
    """
    获取比赛题目信息
    参数:
        problem_id:int 题目ID(比赛中的)
        contest_id:int 比赛ID
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//code非0的时候表示错误信息
            "data":{
                "title":"qwq",//题目名
                "backcground":"qwq",//题目背景
                "content":"题目内容",
                "input_format":"输入格式",
                "output_format":"输出格式",
                "hint":"数据范围与提示",
                "example":"样例,形如[{'input':'xxx','output':'xxx'}]",
                "files":["a.in","a.out"],//不包括具体的二进制数据！
                "subtasks":[
                         {"name": "Subtask1", "score": 40, "method": "min", "files": [], "time_limit":1000, "memory_limit":512}].
                "last_code":"qwq",//上一次提交的代码,
                "last_lang":"qwq",//上一次选择的语言ID
                "score":题目总分,
                "extra_compile_parameter":"附加编译参数"
            }
        }
    """
    contest: Contest = Contest.by_id(request.form["contest_id"])
    if not contest.running():
        if not session.get("uid"):
            return make_response(-1, message="你没有权限跟我说话")
        user: User = User.by_id(session.get("uid"))
        if not user.is_admin and user.id != contest.owner_id:
            return make_response(-1, message="你没有权限跟我说话")
    problem: Problem = Problem.by_id(
        contest.problems[int(request.form["problem_id"])]["id"])
    result = problem.as_dict()
    last_submission = db.session.query(Submission).filter(and_(
        Submission.problem_id == problem.id, Submission.uid == session.get("uid"))).filter(Submission.contest_id == contest.id).order_by(Submission.submit_time.desc())
    if last_submission.count():
        submit = last_submission.first()
        result["last_code"] = submit.code
        result["last_lang"] = submit.language
    else:
        result["last_lang"] = result["last_code"] = ""
    result["id"] = int(request.form["problem_id"])
    del result["uploader_id"]
    result["score"] = problem.get_total_score()
    return make_response(0, data=result)


@app.route("/api/contest/submit", methods=["POST"])
def contest_submit():
    """
    提交代码\答案
    参数:

        problem_id:int 题目ID
        code:str 代码
        language:str 语言ID
        contest_id:int 比赛ID
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//调用失败时的信息
            "submission_id":-1//调用成功时的提交ID
        }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    contest: Contest = Contest.by_id(request.form["contest_id"])
    problem: Problem = Problem.by_id(
        contest.problems[int(request.form["problem_id"])]["id"])
    if not contest.running():
        return make_response(-1, message="比赛未在进行！")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    import importlib
    try:
        importlib.import_module("langs."+request.form["language"])
    except:
        return make_response(-1, message="不支持的语言ID")

    import datetime
    submit = Submission(uid=user.id, language=request.form["language"], problem_id=problem.id, submit_time=datetime.datetime.now(), public=False, contest_id=request.form["contest_id"],
                        code=request.form["code"], status="waiting")
    db.session.add(submit)
    db.session.commit()
    from api.judge import push_to_queue
    push_to_queue(submit.id)
    return make_response(0, submission_id=submit.id)


@app.route("/api/contest/ranklist", methods=["POST"])
def contest_ranklist():
    """
    获取比赛的排行榜
    {
        contest_id:比赛ID
    }
    返回值:
    {
        "code":0,
        "data":{
            "ranklist":[
                {
                    "uid":"用户ID",
                    "username":"用户名",
                    "scores":[
                        {
                            "score":"题目得分",
                            "submit_count":1,//AC前的提交次数,
                            "ac_time":"AC时间(分钟)",//
                            "penalty":"罚时"//AC时间+config.FAIL_SUBMIT_PENALTY*提交次数
                            "submit_id":"提交ID",
                            "status":"题目状态",
                            "first_blood":True//一血
                        }
                    ],
                    "total":{
                        "score":"分数",
                        "penalty":"总罚时",
                        "ac_count":"总通过数"
                    }
                }        
            ],
            "problems":[
                {
                    "name":"题目名",
                    "id":"题目ID",//比赛中的
                    "accepted_submit":"通过数量",
                    "total_submit":"总提交数量"
                }
            ]
        }
    }
    """
    contest: Contest = Contest.by_id(request.form['contest_id'])
    can_see_ranklist = False
    if session.get("uid"):
        userx: User = User.by_id(session.get("uid"))
        if userx.is_admin or userx.id == contest.owner_id:
            can_see_ranklist = True
    if contest.ranklist_visible:
        can_see_ranklist = True
    users = db.session.query(Submission.uid).filter(
        Submission.contest_id == contest.id).distinct().all()
    ranklist = []
    for submission in users:
        user: User = User.by_id(submission.uid)
        current = {
            "uid": user.id,
            "username": user.username,
            "scores": [],
            "total": {}
        }
        ranklist.append(current)
        scores = current["scores"]
        # 处理用户user在problem下的结果
        for problem_obj in contest.problems:
            id, weight = problem_obj["id"], problem_obj["weight"]
            # 获取分数最高中，最早的提交
            if contest.rank_criterion != "last_submit":
                # ACM赛制和IOI赛制，获取分数最高且最靠前的提交
                best_submit = db.session.query(Submission.status,
                                               Submission.score,
                                               Submission.submit_time,
                                               Submission.id).order_by(Submission.score.desc()).order_by(Submission.id.asc()).filter(and_(Submission.uid == user.id, Submission.contest_id == contest.id, Submission.problem_id == id))

            else:
                # NOI赛制，获取最后一次提交
                best_submit = db.session.query(Submission.status,
                                               Submission.score,
                                               Submission.submit_time,
                                               Submission.id).order_by(Submission.id.desc()).filter(and_(Submission.uid == user.id, Submission.contest_id == contest.id, Submission.problem_id == id))

            if best_submit.count() == 0:
                scores.append({
                    "score": 0,
                    "submit_count": -1,
                    "ac_time": -1,
                    "penalty": 0,
                    "submit_id": -1,
                    "status": "unknown"
                })
                continue
            best_submit = best_submit.first()

            import time
            if best_submit.status == "accepted":
                last = {
                    "score": best_submit.acore*weight,
                    "submit_count": db.session.query(Submission.id).filter(Submission.contest_id == contest.id).filter(Submission.uid == user.id).filter(Submission.status != "accepted").filter(Submission.id < best_submit.id).count(),
                    "ac_time": int((best_submit.submit_time-contest.start_time).total_seconds()/60),
                    "submit_id": best_submit.id,
                    "status": best_submit.status
                }
                last["penalty"] = last["ac_time"] + \
                    last["submit_count"]*config.FAIL_SUBMIT_PENALTY
                if db.session.query(Submission.id).filter(Submission.contest_id == contest.id and Submission.id < best_submit.id and Submission.problem_id == id and Submission.status == "accepted").count() == 0:
                    last["first_blood"] = True
            else:
                last = {
                    "score": best_submit.score*weight,
                    "submit_count": db.session.query(Submission.id).filter(Submission.contest_id == contest.id).filter(Submission.uid == user.id).filter(Submission.status != "accepted").filter(Submission.id <= best_submit.id).count(),
                    "ac_time": -1,
                    "submit_id": best_submit.id,
                    "status": best_submit.status
                }
                last["penalty"] = last["submit_count"] * \
                    config.FAIL_SUBMIT_PENALTY
                last["first_blood"] = False
            scores.append(last)
        # 处理用户的total
        total = {
            "score": sum(map(lambda x: x["score"], scores)),
            "penalty": sum(map(lambda x: x["penalty"], scores)),
            "ac_count": sum(map(lambda x: 1 if x["status"] == "accepted" else 0, scores))
        }
        current["total"] = total
    if contest.rank_criterion == "penalty":
        ranklist.sort(
            key=lambda x: (-x["total"]["ac_count"], x["total"]["penalty"]))
    else:
        ranklist.sort(key=lambda x: x["total"]["score"], reverse=True)
    problems = []
    result = {"ranklist": ranklist, "problems": problems}
    for i, x in enumerate(contest.problems):
        problem: Problem = Problem.by_id(x["id"])
        problems.append({
            "name": problem.title,
            "id": i,
            "accepted_submit": db.session.query(Submission.id).filter(Submission.contest_id == contest.id and Submission.status == "accepted" and Submission.problem_id == problem.id).count(),
            "total_submit": db.session.query(Submission.id).filter(Submission.contest_id == contest.id and Submission.problem_id == problem.id).count()
        })
    return make_response(0, data=result)
