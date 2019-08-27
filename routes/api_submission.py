from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import *
from models.problem import *
from models.submission import *
from models import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename


@app.route("/api/rejudge", methods=["POST"])
def rejudge():
    """ 
    重测提交
    参数:
    submission_id:int 提交ID
    {
        "code","message"
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    if not user.is_admin:
        return make_response(-1, message="你没有权限这样做")
    submit: Submission = Submission.by_id(request.form["submission_id"])
    if not submit:
        return make_response(-1, message="提交不存在")
    from api.judge import push_to_queue
    submit.status = "waiting"
    db.session.commit()
    push_to_queue(submit.id)
    return make_response(0, message="ok")


@app.route("/api/submit", methods=["POST"])
def submit():
    """
    提交代码\答案
    参数:
        problem_id:int 题目ID
        code:str 代码
        language:str 语言ID
        contest_id:int 比赛ID,设置为-1表示非比赛提交//目前尚未处理
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//调用失败时的信息
            "submission_id":-1//调用成功时的提交ID
        }
    """
    problem = db.session.query(Problem).filter(
        Problem.id == request.form["problem_id"])
    if problem.count() == 0:
        return make_response(-1, message="题目ID不存在")
    problem: Problem = problem.one()
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    if not problem.public:
        if not user.is_admin and user.id != problem.writer_id:
            return make_response(-1, message="你没有权限执行此操作")
    import importlib
    try:
        importlib.import_module("langs."+request.form["language"])
    except:
        return make_response(-1, message="不支持的语言ID")

    import datetime
    submit = Submission(uid=user.id, language=request.form["language"], problem_id=problem.id, submit_time=datetime.datetime.now(), public=True, contest_id=request.form["contest_id"],
                        code=request.form["code"], status="waiting")
    db.session.add(submit)
    db.session.commit()
    from api.judge import push_to_queue
    push_to_queue(submit.id)
    return make_response(0, submission_id=submit.id)


@app.route("/api/get_submission_info", methods=["POST"])
def get_submission_info():
    """
    获取提交信息
    参数
    submission_id:int 提交ID
    {
        "code":0,//非0表示调用成功
        "message":"qwq",//调用失败时的信息
        "data":{
            "id":-1,//提交ID
            "uid":-1,//用户ID
            "language":"qwq",//语言ID
            "language_name":"语言名",
            "problem_id":-1,//题目ID
            "submit_time":"提交时间",
            "public":"是否公开",
            "contest_id":"比赛ID",
            "code":"代码",
            "judge_result":{
                "subtask":{"score":100,"status":"WA","testcases":
                    [{"input":"xxx","output":"xxx","score":0,"status":"WA"}]
                    }
            },
            "status":"状态",
            "message":"附加信息",
            "judger":"评测机名，非UUID",
            "score":"总分",
            "ace_mode":"ACE.js语言ID"
        }
    }
    """
    if db.session.query(Submission).filter(Submission.id == request.form["submission_id"]).count() == 0:
        return "提交ID不存在", 404
    submit: Submission = db.session.query(Submission).filter(
        Submission.id == request.form["submission_id"]).one()
    if not submit.public and not session.get("uid"):
        return "你没有权限查看此提交", 403
    if session.get("uid"):
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        if not submit.public and not user.is_admin and not user.id == submit.uid:
            return make_response(-1, message="你没有权限查看此提交")
    ret = submit.to_dict()

    ret["score"] = submit.get_total_score()
    ret["submit_time"] = str(ret["submit_time"])
    if submit.contest_id != -1:
        contest: Contest = Contest.by_id(submit.contest_id)
        if not contest.judge_result_visible and contest.running() and user.id != contest.owner_id and not user.is_admin:
            ret["judge_result"] = {}
            ret["status"] = "invisible"
            ret["score"] = 0
        for i, x in enumerate(contest.problems):
            if x["id"] == ret["problem_id"]:
                ret["problem_id"] = f"contest:{contest.id},{i}"
                break

    import importlib
    ret["ace_mode"] = importlib.import_module(
        "langs."+submit.language).ACE_MODE
    ret["language_name"] = importlib.import_module(
        "langs."+ret["language"]).DISPLAY
    return make_response(0, data=ret)


@app.route("/api/submission_list", methods=["POST"])
def submission_list():
    """
    获取提交列表
    参数:
    page:int 页数
    filter:str 过滤器
    过滤器格式:
    若干个形如K=V的条件以逗号分隔，条件之间关系为与
    比如uid=1,status=accepted
    支持以下Key值
    uid:用户ID
    status:评测状态,accepted,unaccepted,judging,waiting
    min_score:分数下界
    max_score:分数下界
    problem:题目ID
    contest:比赛ID
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//调用失败时的信息
            "data":[
                {"id":-1,"problem_id":123,"problem_title":"qwq","status":"judging","score":-1,"contest":-1,"total_score":123}
            ],
            "total_pages":总页数,
            "current_page":当前页(根据URL分析)
        }
    """
    page = int(request.form.get("page", 1))
    result = None
    if not session.get("uid"):
        result = db.session.query(Submission).filter(Submission.public == True)
    else:
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        if user.is_admin:
            result = db.session.query(Submission)
        else:
            result = db.session.query(Submission).filter(
                or_(Submission.public == True, Submission.uid == user.id))
    filter = request.form["filter"].split(",")
    filters = {
        "uid": lambda x, y: x.filter(Submission.uid == y),
        "status": lambda x, y: x.filter(Submission.status == y),
        "min_score": lambda x, y: x.filter(Submission.score >= int(y)),
        "max_score": lambda x, y: x.filter(Submission.score <= int(y)),
        "problem": lambda x, y: x.filter(Submission.problem_id == y),
        "contest": lambda x, y: x.filter(Submission.contest_id == y),

    }

    for f in filter:
        if not f:
            continue
        # print(f)
        key, value = f.split("=")
        key = key.strip()
        if not key:
            continue
        if key not in filters:
            return make_response(-1, message=f"过滤器{key}={value}未知")
        result = filters[key](result, value)
    result = result.order_by(Submission.id.desc())
    count = result.count()
    import math
    pages = int(math.ceil(count/config.SUBMISSIONS_PER_PAGE))
    result = result.slice(
        (page-1)*config.SUBMISSIONS_PER_PAGE, (page)*config.SUBMISSIONS_PER_PAGE).all()
    ret = []
    for submit in result:
        obj = {
            "id": submit.id,
            "status": submit.status,
            "score": submit.get_total_score(),
            "contest": submit.contest_id,
            "uid": submit.uid,
            "username": User.by_id(submit.uid).username,
            "submit_time": str(submit.submit_time)
        }
        if submit.contest_id != -1:
            contest: Contest = Contest.by_id(submit.contest_id)
            if not contest.can_see_judge_result(session.get("uid")):
                obj["status"] = "invisible"
                obj["score"] = 0

        problem: Problem = db.session.query(Problem).filter(
            Problem.id == submit.problem_id).one()
        obj["problem_id"] = problem.id
        obj["problem_title"] = problem.title
        obj["total_score"] = problem.get_total_score()
        ret.append(obj)
    return make_response(0, data=ret, page_count=pages, current_page=page)
