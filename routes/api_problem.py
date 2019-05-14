from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import *
from models.problem import *
from models.submission import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename


@app.route("/api/get_problem_info", methods=["POST"])
def get_problem_info():
    """
    获取题目信息
    参数:
        id:int 题目ID
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//code非0的时候表示错误信息
            "data":{
                "id":-1//题目ID,
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
                "last_code":"qwq"//上一次提交的代码,
                "submit_count":0,//提交数
                "accepted_count":0,//通过数
                "my_submission":-1//-1表示没有提交过，否则有AC提交就表示最新一次AC提交，没有AC提交就是最新一次提交,
                "score":题目总分
            }
        }
    """
    problem = db.session.query(Problem).filter(
        Problem.id == request.form["id"])
    if problem.count() == 0:
        return make_response(-1, message="题目ID不存在")
    problem = problem.one()
    if not problem.public and not session.get("userid"):
        return make_response(-1, message="你没有权限查看此题目")
    if not problem.public and not db.session.query(User).filter(User.id == session.get("userid")).one().is_admin:
        return make_response(-1, message="你没有权限查看此题目")
    result = problem.as_dict()
    last_submission = db.session.query(Submission).filter(and_(
        Submission.problem_id == problem.id, Submission.user_id == session.get("userid"))).order_by(Submission.submit_time.desc())
    if last_submission.count():
        result["last_code"] = last_submission.first().code
    else:
        result["last_code"] = ""
    result["submission_count"] = db.session.query(Submission).count()
    result["accepted_count"] = db.session.query(
        Submission).filter(Submission.status == "accepted").count()
    result["my_submission"] = -1
    if session.get("userid"):
        ac_submit = db.session.query(Submission).filter(
            Submission.status == "accepted").filter(Submission.user_id == session.get("userid")).order_by(Submission.submit_time.desc())
        if ac_submit.count():
            result["my_submission"] = ac_submit.first().id
        else:
            any_submit = db.session.query(Submission).filter(
                Submission.user_id == session.get("userid")).order_by(Submission.submit_time.desc())
            if any_submit.count():
                result["my_submission"] = any_submit.first().id
    result["score"] = problem.get_total_score()
    return make_response(0, data=result)


@app.route("/api/upload_file/<int:id>", methods=["POST"])
def upload_file(id):
    """
    上传题目文件
    参数:
        files:
            上传列表
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//code非0的时候表示错误信息,
            "file_list":[{"name":"a.in","size":123456}]//现有的文件列表
        }
    """
    problem = db.session.query(Problem).filter(
        Problem.id == id)
    if problem.count() == 0:
        return make_response(-1, message="题目ID不存在")
    problem = problem.one()
    if not problem.public and not session.get("userid"):
        return make_response(-1, message="你没有权限执行此操作")
    user: User = db.session.query(User).filter(
        User.id == session.get("userid")).one()
    if not problem.public and not user.is_admin and user.id != problem.writer_id:
        return make_response(-1, message="你没有权限执行此操作")
    import os
    upload_path = os.path.join(basedir, "uploads/%d" % id)
    os.makedirs(upload_path, exist_ok=True)
    for file in request.files:
        request.files[file].save(os.path.join(
            upload_path, file))
        with open(os.path.join(upload_path, file)+".lock", "w") as file:
            import time
            file.write(f"{time.time()}")
    problem.files = generate_file_list(id)
    db.session.commit()

    return make_response(0, file_list=generate_file_list(id))


@app.route("/api/download_file/<int:id>/<string:filename>", methods=["POST", "GET"])
def download_file(id: int, filename: str):
    """
    下载题目文件
    参数:
        无
    返回:
        无
    """
    problem = db.session.query(Problem).filter(
        Problem.id == id)
    import flask
    if problem.count() == 0:
        flask.abort(404)
    problem = problem.one()
    if not problem.public and not session.get("userid"):
        flask.abort(403)
    if session.get("userid"):
        user: User = db.session.query(User).filter(
            User.id == session.get("userid")).one()
        if not problem.public and not user.is_admin and user.id != problem.writer_id:
            flask.abort(403)
        if problem.public and not user.is_admin and user.id != problem.writer_id and filename not in problem.downloads:
            flask.abort(403)
    import os
    file = os.path.join(
        basedir, f"uploads/{id}/{filename}")
    if not os.path.exists(file):
        flask.abort(404)
    return send_file(file, as_attachment=True)


@app.route("/api/remove_file", methods=["POST"])
def remove_file():
    """
    删除题目文件
    参数:
        id:int 题目ID
        file:str 文件名
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//code非0的时候表示错误信息,
            "file_list":[{"name":"a.in","size":123456}]//现有的文件列表
        }
    """
    problem = db.session.query(Problem).filter(
        Problem.id == request.form["id"])
    if problem.count() == 0:
        return make_response(-1, message="题目ID不存在")
    problem = problem.one()
    if not problem.public and not session.get("userid"):
        return make_response(-1, message="你没有权限执行此操作")
    user: User = db.session.query(User).filter(
        User.id == session.get("userid")).one()
    if not problem.public and not user.is_admin and user.id != problem.writer_id:
        return make_response(-1, message="你没有权限执行此操作")
    import os
    upload_path = os.path.join(basedir, f"uploads/{request.form['id']}")
    os.makedirs(upload_path, exist_ok=True)
    try:
        os.remove(os.path.join(upload_path, request.form["file"]))
        os.remove(os.path.join(upload_path, request.form["file"]+".lock"))

    except Exception as ex:
        pass
    problem.files = generate_file_list(request.form["id"])
    db.session.commit()
    return make_response(0, file_list=generate_file_list(request.form["id"]))


@app.route("/api/update_problem", methods=["POST"])
def update_problem():
    """
    更新题目
    参数:
        id:int 题目ID
        data:dict 题目数据
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//code非0的时候表示错误信息
        }
    """
    problem = db.session.query(Problem).filter(
        Problem.id == request.form["id"])
    if problem.count() == 0:
        return make_response(-1, message="题目ID不存在")
    problem = problem.one()
    if not session.get("userid"):
        return make_response(-1, message="你没有权限执行此操作")
    user: User = db.session.query(User).filter(
        User.id == session.get("userid")).one()
    if not user.is_admin and user.id != problem.writer_id:
        return make_response(-1, message="你没有权限执行此操作")
    data = decode_json(request.form["data"])
    for subtask in data["subtasks"]:
        if len(subtask["testcases"]) == 0:
            return make_response(-1, message=f"子任务{subtask['name']}的测试点个数为0！")
        if subtask["method"] == "sum" and (int(subtask["score"]) % len(subtask["testcases"]) != 0):
            return make_response(-1, message="如果计分方式为取和，那么子任务分数必须为测试点个数的倍数")
    for k, v in data.items():
        setattr(problem, k, v)
    for subtask in problem.subtasks:
        subtask["score"] = int(subtask["score"])
    db.session.commit()
    return make_response(0)


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
    return make_response(0, list=config.SUPPORTED_LANGUAGES)


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
    if not session.get("userid"):
        return make_response(-1, message="请先登录")
    user: User = db.session.query(User).filter(
        User.id == session.get("userid")).one()
    if not problem.public:
        if not user.is_admin and user.id != problem.writer_id:
            return make_response(-1, message="你没有权限执行此操作")
    if request.form["language"] not in map(lambda x: x["id"], config.SUPPORTED_LANGUAGES):
        return make_response(-1, message="不支持的语言ID")
    import datetime
    submit = Submission(user_id=user.id, language=request.form["language"], problem_id=problem.id, submit_time=datetime.datetime.now(), public=True, contest_id=request.form["contest_id"],
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
            "user_id":-1,//用户ID
            "language":"qwq",//语言ID
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
            "score":"总分"
        }
    }
    """
    if db.session.query(Submission).filter(Submission.id == request.form["submission_id"]).count() == 0:
        return "提交ID不存在", 404
    submit: Submission = db.session.query(Submission).filter(
        Submission.id == request.form["submission_id"]).one()
    if not submit.public and not session.get("userid"):
        return "你没有权限查看此提交", 403
    if session.get("userid"):
        user: User = db.session.query(User).filter(
            User.id == session.get("userid")).one()
        if not submit.public and not user.is_admin and not user.id == submit.user_id:
            return make_response(-1, "你没有权限查看此提交")
    ret = submit.to_dict()
    ret["score"] = submit.get_total_score()
    ret["submit_time"] = str(ret["submit_time"])
    print(ret)
    return make_response(0, data=ret)


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
        "unaccepted": {"icon": "times icon", "text": "未通过", "color": "red"}
    }
    return make_response(0, data=ret)


@app.route("/api/problem_list", methods=["POST"])
def problem_list():
    """
    获取题目列表
    参数:
    page:int 页数
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//调用失败时的信息
            "data":[
                {"id":-1,"title":"qwqqwq","submission":233,"status":"accepted","public":false,"total_submit":123,"accepted_submit":123}
            ],
            "total_pages":总页数,
            "current_page":当前页(根据URL分析)
        }
    """
    page = int(request.form.get("page", 1))
    result = None
    if not session.get("userid"):
        result = db.session.query(Problem).filter(Problem.public == True)
    else:
        user: User = db.session.query(User).filter(
            User.id == session.get("userid")).one()
        if user.is_admin:
            result = db.session.query(Problem)
        else:
            result = db.session.query(Problem).filter(
                or_(Problem.public == True, Problem.uploader_id == user.id))
    count = result.count()
    import math
    pages = int(math.ceil(count/config.PROBLEMS_PER_PAGE))
    result = result.slice(
        (page-1)*config.PROBLEMS_PER_PAGE, (page)*config.PROBLEMS_PER_PAGE).all()
    ret = []
    for item in result:
        obj = {
            "id": item.id,
            "title": item.title,
            "submission": -1,
            "status": None,
            "public": True,
            "total_submit": db.session.query(Submission).filter(Submission.problem_id == item.id).count(),
            "accepted_submit": db.session.query(Submission).filter(Submission.problem_id == item.id).filter(Submission.status == "accepted").count()
        }
        # accepted的字典序比其他三个状态都少，所以按照status升序排能优先排到ac
        submit = db.session.query(Submission).filter(Submission.user_id == session.get(
            "userid")).filter(Submission.problem_id == item.id).order_by(Submission.status.asc()).order_by(Submission.submit_time.desc())
        if submit.count():
            submit = submit.first()
            obj["submission"] = submit.id
            obj["status"] = submit.status
        obj["public"] = item.public
        ret.append(obj)
    return make_response(0, data=ret, page_count=pages, current_page=page)


@app.route("/api/submission_list", methods=["POST"])
def submission_list():
    """
    获取提交列表
    参数:
    page:int 页数
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
    if not session.get("userid"):
        result = db.session.query(Submission).filter(Submission.public == True)
    else:
        user: User = db.session.query(User).filter(
            User.id == session.get("userid")).one()
        if user.is_admin:
            result = db.session.query(Submission)
        else:
            result = db.session.query(Submission).filter(
                or_(Submission.public == True, Submission.user_id == user.id))
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
            "contest": submit.contest_id
        }
        problem: Problem = db.session.query(Problem).filter(
            Problem.id == submit.problem_id).one()
        obj["problem_id"] = problem.id
        obj["problem_title"] = problem.title
        obj["total_score"] = problem.get_total_score()
        ret.append(obj)
    return make_response(0, data=ret, page_count=pages, current_page=page)
