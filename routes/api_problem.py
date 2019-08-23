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
                "last_code":"qwq",//上一次提交的代码,
                "last_lang":"qwq",//上一次选择的语言ID
                "submit_count":0,//提交数
                "accepted_count":0,//通过数
                "my_submission":-1//-1表示没有提交过，否则有AC提交就表示最新一次AC提交，没有AC提交就是最新一次提交,
                //我的提交状态
                "my_submission_status":-1,
                "score":题目总分
            }
        }
    """
    problem = db.session.query(Problem).filter(
        Problem.id == int(request.form["id"]))
    if problem.count() == 0:
        return make_response(-1, message="题目ID不存在")
    problem = problem.one()
    if not problem.public and not session.get("uid"):
        return make_response(-1, message="你没有权限查看此题目")
    if not problem.public and not db.session.query(User).filter(User.id == session.get("uid")).one().is_admin:
        return make_response(-1, message="你没有权限查看此题目")
    result = problem.as_dict()
    last_submission = db.session.query(Submission).filter(and_(
        Submission.problem_id == problem.id, Submission.uid == session.get("uid"))).order_by(Submission.submit_time.desc())
    if last_submission.count():
        submit = last_submission.first()
        result["last_code"] = submit.code
        result["last_lang"] = submit.language
    else:
        result["last_lang"] = result["last_code"] = ""
    result["submission_count"] = db.session.query(Submission).filter(
        Submission.problem_id == problem.id).count()
    result["accepted_count"] = db.session.query(
        Submission).filter(Submission.status == "accepted").filter(Submission.problem_id == problem.id).count()
    result["my_submission"] = -1
    if session.get("uid"):
        ac_submit = db.session.query(Submission.id, Submission.status).filter(
            Submission.status == "accepted").filter(Submission.uid == session.get("uid")).filter(Submission.problem_id == problem.id).order_by(Submission.submit_time.desc())
        if ac_submit.count():
            result["my_submission"], result["my_submission_status"] = ac_submit.first()
        else:
            any_submit = db.session.query(Submission.id, Submission.status).filter(
                Submission.uid == session.get("uid")).filter(Submission.problem_id == problem.id).order_by(Submission.submit_time.desc())
            if any_submit.count():
                result["my_submission"], result["my_submission_status"] = any_submit.first()
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
    if not problem.public and not session.get("uid"):
        return make_response(-1, message="你没有权限执行此操作")
    if not session.get("uid"):
        return make_response(-1, message="你没有权限执行此操作")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
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
    if not problem.public and not session.get("uid"):
        flask.abort(403)
    if session.get("uid"):
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        if not problem.public and not user.is_admin and user.id != problem.writer_id:
            flask.abort(403)
        if problem.public and not user.is_admin and user.id != problem.writer_id and filename not in problem.downloads:
            flask.abort(403)
    else:
        if not problem.public or filename not in problem.downloads:
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
    if not problem.public and not session.get("uid"):
        return make_response(-1, message="你没有权限执行此操作")
    if not session.get("uid"):
        return make_response(-1, message="你没有权限执行此操作")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
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
    if not session.get("uid"):
        return make_response(-1, message="你没有权限执行此操作")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    if not user.is_admin and user.id != problem.writer_id:
        return make_response(-1, message="你没有权限执行此操作")
    data = decode_json(request.form["data"])
    for subtask in data["subtasks"]:
        subtask["score"] = int(subtask["score"])
    for subtask in data["subtasks"]:
        if len(subtask["testcases"]) == 0:
            return make_response(-1, message=f"子任务{subtask['name']}的测试点个数为0！")
        if subtask["method"] == "sum" and (int(subtask["score"]) % len(subtask["testcases"]) != 0):
            return make_response(-1, message="如果计分方式为取和，那么子任务分数必须为测试点个数的倍数")
        if subtask["score"] < len(subtask["testcases"]):
            return make_response(-1, message="测试点个数不得多于分数")
        if subtask["method"] == "min":
            list(map(lambda x: x.__setitem__(
                "full_score", 1), subtask["testcases"]))
        else:
            score = subtask["score"]//len(subtask["testcases"])
            for i in range(0, len(subtask["testcases"])-1):
                subtask["testcases"][i]["full_score"] = score
            subtask["testcases"][-1]["full_score"] = subtask["score"] - \
                score*(len(subtask["testcases"])-1)
    for k, v in data.items():
        setattr(problem, k, v)

    db.session.commit()
    return make_response(0)


@app.route("/api/problem_list", methods=["POST"])
def problem_list():
    """
    获取题目列表
    参数:
    page:int 页数
    search_keyword:str 题目名关键字
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
    if not session.get("uid"):
        result = db.session.query(Problem).filter(Problem.public == True)
    else:
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        if user.is_admin:
            result = db.session.query(Problem)
        else:
            result = db.session.query(Problem).filter(
                or_(Problem.public == True, Problem.uploader_id == user.id))
    keyword = request.form.get("search_keyword", "")
    result = result.filter(Problem.title.like(f"%{keyword}%"))
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
        submit = db.session.query(Submission).filter(Submission.uid == session.get(
            "uid")).filter(Submission.problem_id == item.id).order_by(Submission.status.asc()).order_by(Submission.submit_time.desc())
        if submit.count():
            submit = submit.first()
            obj["submission"] = submit.id
            obj["status"] = submit.status
        obj["public"] = item.public
        ret.append(obj)
    return make_response(0, data=ret, page_count=pages, current_page=page)


@app.route("/api/ui_search_problem/", methods=["POST", "GET"])
@app.route("/api/ui_search_problem/<string:search_keyword>", methods=["POST", "GET"])
def search_problem(search_keyword=""):
    """
    搜索题目
    参数:
    search_keyword:str 题目名关键字
    以Semantic UI的格式通讯
    返回:
        {
            "success":true,
            "results":[
                {"name":"qwq","value":"1234","text":"1234.题目名"}
            ]
        }
    """
    result = None
    if not session.get("uid"):
        result = db.session.query(Problem).filter(Problem.public == True)
    else:
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        if user.is_admin:
            result = db.session.query(Problem)
        else:
            result = db.session.query(Problem).filter(
                or_(Problem.public == True, Problem.uploader_id == user.id))
    result = result.filter(Problem.title.like(
        f"%{search_keyword}%")).slice(0, 10)
    ret = {
        "success": True,
        "results": [{"value": search_keyword, "name": f"搜索 {search_keyword}", "text": f"{search_keyword}"}]
    }
    for x in result:
        ret["results"].append(
            {"value": x.id, "name": f"{x.id}. {x.title}", "text": f"{x.id}"})
    # print(f"search {search_keyword} = {ret}")
    return encode_json(ret)

@app.route("/api/create_problem", methods=["POST"])
def create_problem():
    """
    创建空题目
    参数:
        无
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
            "problem_id":-1//成功时表示题目ID
        }
    """
    if session.get("uid") is None:
        return make_response(-1, message="你尚未登录!")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    if not user.is_admin:
        return make_response(-1, message="你没有权限进行此操作")
    problem = Problem(uploader_id=user.id)
    db.session.add(problem)
    db.session.commit()
    return make_response(0, problem_id=problem.id)

