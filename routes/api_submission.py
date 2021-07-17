from sqlalchemy.sql import expression as expr
from main import web_app as app
from main import db, config, basedir, permission_manager
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import *
from models.problem import *
from models.submission import *
from models import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename
from common.permission import require_permission
from common.utils import unpack_argument
from typing import Dict, Any


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
    # user: User = User.by_id(session.get("uid"))
    if not permission_manager.has_any_permission(session.get("uid", None), "submission.manage", "submission.rejudge"):
        return make_response(-1, message="你没有权限这样做")
    submit: Submission = Submission.by_id(request.form["submission_id"])
    problem: Problem = db.session.query(
        Problem.problem_type).filter_by(id=submit.problem_id).one()
    if problem.problem_type == "submit_answer":
        return make_response(-1, message="提交答案题不能重测")
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
    提交代码/答案
    参数:
        problem_id:int 题目ID
        code:str 代码
        language:str 语言ID
        contest_id:int 比赛ID,设置为-1表示非比赛提交,如果非-1，那么problem_id为比赛中的题目ID
        usedParameters:str [1,2,3] 使用到了的附加编译选项ID
        virtualID: 虚拟比赛ID
        answerData: 提交答案题答案数据
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//调用失败时的信息
            "submission_id":-1//调用成功时的提交ID
        }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()

    using_contest = int(request.form["contest_id"]) != -1
    virtual_id = int(request.form.get("virtualID", -1))
    using_virtual = (virtual_id != -1)
    virtual_contest: VirtualContest = db.session.query(
        VirtualContest).filter_by(id=virtual_id).one_or_none()
    if using_contest:
        contest: Contest = Contest.by_id(request.form["contest_id"])
        if using_virtual:
            if (not virtual_contest) or virtual_contest. contest_id != contest.id:
                return make_response(-1, message="此虚拟比赛不对应于此实际比赛")
            if not virtual_contest.running():
                return make_response(-1, message="虚拟比赛未在进行")
            problem: Problem = Problem.by_id(
                contest.problems[int(request.form["problem_id"])]["id"])
        else:

            if not contest.running():
                return make_response(-1, message="比赛未在进行！")
            if contest.private_contest and not permission_manager.has_permission(session.get("uid", -1), f"contest.use.{contest.id}"):
                return make_response(-1, message="你没有权限查看该比赛")
            problem: Problem = Problem.by_id(
                contest.problems[int(request.form["problem_id"])]["id"])

    else:
        problem = db.session.query(Problem).filter(
            Problem.id == request.form["problem_id"])
        if problem.count() == 0:
            return make_response(-1, message="题目ID不存在")
        problem: Problem = problem.one()
        if not problem.public:
            if not permission_manager.has_any_permission(user.id, f"problem.use.{problem.id}") and user.id != problem.uploader_id:
                return make_response(-1, message="你没有权限执行此操作")
    from typing import Set
    if problem.problem_type != "submit_answer":
        parameters: Set[int] = set(decode_json(request.form["usedParameters"]))
        import importlib
        import re

        for i, item in enumerate(problem.extra_parameter):
            if re.compile(item["lang"]).match(request.form["language"]) and item["force"] and i not in parameters:
                parameters.add(i)

        try:
            importlib.import_module("langs."+request.form["language"])
        except:
            return make_response(-1, message="不支持的语言ID")
        parameter_string = " ".join(
            (problem.extra_parameter[i]["parameter"] for i in parameters if i < len(
                problem.extra_parameter) and re.compile(problem.extra_parameter[i]["lang"]).match(request.form["language"]))
        )

        import datetime
        submit = Submission(uid=user.id,
                            language=request.form["language"],
                            problem_id=problem.id,
                            submit_time=datetime.datetime.now(),
                            public=problem.public,
                            contest_id=request.form["contest_id"],
                            virtual_contest_id=virtual_id if using_virtual else None,
                            code=request.form["code"],
                            status="waiting",
                            extra_compile_parameter=parameter_string,
                            selected_compile_parameters=list(parameters)
                            )
    else:
        import base64
        import datetime
        encoded = base64.encodebytes(
            request.files["answerData"].stream.read()).decode().replace("\n", "")

        submit = Submission(uid=user.id,
                            language="cpp",
                            problem_id=problem.id,
                            submit_time=datetime.datetime.now(),
                            public=problem.public,
                            contest_id=request.form["contest_id"],
                            virtual_contest_id=virtual_id if using_virtual else None,
                            code=encoded,
                            status="waiting",
                            extra_compile_parameter="",
                            selected_compile_parameters=[]
                            )
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
            "usePolling":"是否使用轮询",
            "managable":"是否可管理",
            "id":-1,//提交ID
            "uid":-1,//用户ID
            "language":"qwq",//语言ID
            "language_name":"语言名",
            "submit_time":"提交时间",
            "public":"是否公开",
            "contest":{
                "id":"ID",
                "name":"名称",
                "isContest":"是否在比赛中"
            },
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
            "ace_mode":"ACE.js语言ID",
            "time_cost":"时间开销",
            "memory_cost":"内存开销",
            "extra_compile_parameter":"附加编译参数",
            "isRemoteSubmission":"是否为远程提交",
            "problem":{
                "id":"题目ID",
                "title":"题目名",
            },
            "user":{
                "uid":"提交者ID",
                "username":"提交者用户名"
            },
            "virtualContestID":"虚拟比赛ID"
        }
    }
    """
    if db.session.query(Submission).filter(Submission.id == request.form["submission_id"]).count() == 0:
        return "提交ID不存在", 404
    submit: Submission = db.session.query(Submission).filter(
        Submission.id == request.form["submission_id"]).one()
    if not submit.public and not session.get("uid"):
        return "你没有权限查看此提交", 403
    problem: Problem = db.session.query(
        Problem).filter(Problem.id == submit.problem_id).one()
    # has_perm_to_use_problem = problem.public or ((not problem.public) and permission_manager.has_permission(
    #     session.get("uid", -1), f"problem.use.{problem.id}")) or permission_manager.has_permission(session.get("uid", -1), "problem.manage")
    have_permission_to_use_problem = (problem.public or (permission_manager.has_permission(
        session.get("uid", -1), f"problem.use.{problem.id}") and not problem.public and problem.submission_visible)) and (
            submit.contest_id < 0
            or (
                (
                    permission_manager.has_permission(session.get(
                        "uid", -1), f"contest.use.{submit.contest_id}")
                    or
                    db.session.query(Contest.id).filter(
                        Contest.id == submit.contest_id, Contest.private_contest == False).count() > 0
                ) and
                db.session.query(Contest.id).filter(
                    Contest.id == submit.contest_id, Contest.closed == True).count() > 0
            )
    )
    # print("cansee = ",have_permission_to_use_problem)
    if session.get("uid"):
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        if not submit.public and not permission_manager.has_permission(user.id, "submission.manage") and not user.id == submit.uid and not have_permission_to_use_problem:
            return make_response(-1, message="你没有权限查看此提交")
    ret = submit.to_dict()

    ret["score"] = submit.get_total_score()
    ret["submit_time"] = str(ret["submit_time"])

    if submit.contest_id != -1:
        contest: Contest = Contest.by_id(submit.contest_id)
        using_virtual = submit.virtual_contest_id is not None
        virtual_contest = db.session.query(
            VirtualContest).filter_by(id=submit.virtual_contest_id).one_or_none()

        if not contest.judge_result_visible and (virtual_contest.running() if using_virtual else contest.running()) and user.id != contest.owner_id and not permission_manager.has_permission(user.id, "contest.manage"):
            ret["judge_result"] = {}
            ret["status"] = ret["status"] if ret["status"] in {
                "compile_error"} else "invisible"
            ret["score"] = 0
            ret["time_cost"] = -1
            ret["memory_cost"] = -1
            ret["message"] = ""
        for i, x in enumerate(contest.problems):
            if x["id"] == ret["problem_id"]:
                # ret["problem_id"] = f"contest:{contest.id},{i}"
                ret["problem"] = {
                    "id": i,
                    "title": db.session.query(
                        Problem.title).filter(Problem.id == x["id"]).one().title
                }
                break
        ret["contest"] = {
            "id": contest.id,
            "name": contest.name,
            "isContest": True
        }
    else:
        ret["contest"] = {
            "isContest": False
        }
        ret["problem"] = {
            "id": problem.id,
            "title": problem.title
        }
    ret["problem"]["score"] = problem.get_total_score()
    ret["problem"]["subtasks"] = problem.subtasks
    import importlib
    try:
        try:
            lang_module = importlib.import_module(
                "langs."+submit.language)
            ret["ace_mode"] = lang_module.ACE_MODE
            ret["language_name"] = lang_module.DISPLAY
        except Exception as ex:
            pass

    except Exception as ex:
        import traceback
        traceback.print_exc()
        ret["ace_mode"] = ret["language_name"] = ""

    ret["managable"] = permission_manager.has_permission(
        session.get("uid", None), "submission.manage")
    ret["isRemoteSubmission"] = problem.problem_type == "remote_judge"
    ret["user"] = {
        "uid": submit.uid,
        "username": db.session.query(User.username).filter(User.id == submit.uid).one().username
    }
    ret["usePolling"] = config.USE_POLLING
    ret["virtualContestID"] = submit.virtual_contest_id
    if problem.problem_type == "submit_answer":
        ret["code"] = "提交答案题不提供用户答案下载"
    del ret["problem_id"]
    del ret["uid"]
    return make_response(0, data=ret)


@app.route("/api/submission_list", methods=["POST"])
@unpack_argument
def submission_list(page: int = 1, filter: Dict[str, Any] = {}):
    """
    获取提交列表
    参数:
    page:int 页数
    filter:str 过滤器
    过滤器格式:
    {K1:V1,K2:V2...}
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
    result = None
    if not session.get("uid"):
        result = db.session.query(Submission).filter(Submission.public == True)
    else:
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        if permission_manager.has_permission(user.id, "submission.manage"):
            result = db.session.query(Submission)
        else:
            result = db.session.query(Submission).filter(
                or_(Submission.public == True, Submission.uid == user.id))
    filters = {
        "uid": lambda x, y: x.filter(Submission.uid == y) if y.isnumeric() else x.filter(Submission.user.has(User.username == y)),
        "status": lambda x, y: x.filter(Submission.status == y),
        "min_score": lambda x, y: x.filter(Submission.score >= int(y)),
        "max_score": lambda x, y: x.filter(Submission.score <= int(y)),
        "problem": lambda x, y: x.filter(Submission.problem_id == y),
        "contest": lambda x, y: x.filter(Submission.contest_id == y),
    }
    if "problem" in filter:
        value = filter["problem"]
        # 如果题目允许查看提交且用户具有权限
        problem = db.session.query(Problem).filter_by(
            id=value).one_or_none()
        if not problem:
            return make_response(-1, message="未知题目ID")
        # print("testing")
        result = result.filter(Submission.problem_id == value)
        if (not problem.public) and problem.submission_visible and permission_manager.has_permission(session.get("uid", -1), f"problem.use.{problem.id}"):
            visible_contests = {
                contest.id
                for contest in db.session.query(Contest.id, Contest.private_contest).filter(Contest.closed == True).all()
                if not contest.private_contest or permission_manager.has_permission(session.get("uid", -1), f"contest.use.{contest.id}")
            }
            print(visible_contests)
            # print("tested")
            result = result.union(
                db.session.query(Submission).filter(expr.and_(
                    Submission.problem_id == problem.id,
                    expr.or_(
                        Submission.contest_id == -1,
                        Submission.contest_id.in_(visible_contests)
                    )
                ))
            )
    for key, value in filter.items():
        # print(key, value)
        if not key:
            continue
        if key not in filters:
            return make_response(-1, message=f"过滤器{key}={value}未知")
        if key == "problem":
            continue
        if key in {"min_score", "max_score", "status"}:
            if "contest" in filter:
                curr_contest: Contest = db.session.query(
                    Contest).filter_by(id=filter["contest"]).one_or_none()
                if not curr_contest:
                    continue
                if (not permission_manager.has_permission(session.get("uid", -1), "contest.manage")) and curr_contest.running():
                    return make_response(-1, message="比赛进行时不可筛选分数边界或提交状态")

        result = filters[key](result, value)

    result = result.order_by(Submission.id.desc())
    count = result.count()
    import math
    pages = int(math.ceil(count/config.SUBMISSIONS_PER_PAGE))
    result = result.slice(
        (page-1)*config.SUBMISSIONS_PER_PAGE, (page)*config.SUBMISSIONS_PER_PAGE).all()
    ret = []
    for submit in result:
        submit: Submission
        obj = {
            "id": submit.id,
            "status": submit.status,
            "score": submit.get_total_score(),
            "contest": submit.contest_id,
            "uid": submit.uid,
            "username": User.by_id(submit.uid).username,
            "submit_time": str(submit.submit_time),
            "memory_cost": submit.memory_cost,
            "time_cost": submit.time_cost
        }
        if submit.contest_id != -1:
            contest: Contest = Contest.by_id(submit.contest_id)
            if not contest.can_see_judge_result(session.get("uid"), permission_manager):
                obj["status"] = "invisible"
                obj["score"] = obj["memory_cost"] = obj["time_cost"] = 0
            if submit.virtual_contest_id:
                virtual_contest = db.session.query(
                    VirtualContest).filter_by(id=submit.virtual_contest_id).one_or_none()
                if (not contest.ranklist_visible) and virtual_contest.running():
                    obj["status"] = "invisible"
                    obj["score"] = obj["memory_cost"] = obj["time_cost"] = 0
        problem: Problem = db.session.query(Problem).filter(
            Problem.id == submit.problem_id).one()
        obj["problem_id"] = problem.id
        obj["problem_title"] = problem.title
        obj["total_score"] = problem.get_total_score()
        ret.append(obj)
    return make_response(0, data=ret, page_count=pages, current_page=page)
