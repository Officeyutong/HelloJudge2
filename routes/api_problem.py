from models.problem_todo import ProblemTodo
from main import web_app as app, permission_manager
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import *
from models.problem import *
from models.submission import *
from models import Discussion
from models.tag import Tag, ProblemTag
from sqlalchemy.sql.expression import *
import sqlalchemy.sql.expression as expr
import sqlalchemy.sql.functions as func
from sqlalchemy.orm.query import Query
from werkzeug.utils import secure_filename
from common.utils import make_json_response, unpack_argument
from common.permission import require_permission
import os
import importlib
import typing


@app.route("/api/problem/unlock", methods=["POST"])
@unpack_argument
def api_problem_unlock(problemID: int, inviteCode: str):
    """
    使用邀请码申请某题目的权限
    """
    problem: Problem = db.session.query(Problem.public, Problem.invite_code, Problem.id).filter_by(
        id=problemID).one_or_none()
    if not problem:
        return make_response(-1, message="此题目不存在")
    if inviteCode != problem.invite_code:
        return make_response(-1, message="邀请码错误")
    if not session.get("uid", None):
        return make_response(-1, message="请登录")
    permission_manager.add_permission(
        session.get("uid"), f"problem.use.{problem.id}")
    return make_response(0, message="操作完成")


@app.route("/api/problem/remove", methods=["POST"])
def problem_remove():
    """
    删除题目
    problem_id:int 题目
    {
        "code":0,
        "message":"qwq"
    }
    """
    problem: Problem = Problem.by_id(request.form["problem_id"])
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    if not permission_manager.has_permission(user.id, "problem.manage") and user.id != problem.uploader_id:
        return make_response(-1, message="你没有权限执行此操作")
    db.session.query(Submission).filter(
        Submission.problem_id == problem.id).delete()
    db.session.delete(problem)
    db.session.commit()
    import shutil
    shutil.rmtree(
        f"{config.UPLOAD_DIR}/{request.form['problem_id']}", ignore_errors=True)
    return make_response(0, message="操作完成")


@app.route("/api/refresh_cached_count", methods=["POST"])
@unpack_argument
def api_refresh_cached_count(problem_id: int):
    """
    刷新题目AC数和提交数缓存
    problem_id: 题目ID

    """
    user: User = User.by_id(session.get("uid"))
    problem: Problem = Problem.by_id(problem_id)
    if not permission_manager.has_permission(user.id, "problem.manage") and user.id != problem.uploader_id:
        return make_response(-1, message="你没有权限执行此操作")
    refresh_cached_count(problem_id)
    return make_response(0, message="操作完成")


@app.route("/api/regenerate_filelist", methods=["POST"])
def regenerate_filelist():
    """
    重新生成文件列表
    problem_id:int 题目ID
    {
        "code":""
        "data":[
            "新生成的文件列表"
        ]
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    problem: Problem = Problem.by_id(request.form["problem_id"])
    if not permission_manager.has_permission(user.id, "problem.manage") and user.id != problem.uploader_id:
        return make_response(-1, message="你没有权限执行此操作")
    import pathlib
    import os
    import shutil
    path = pathlib.PurePath(config.UPLOAD_DIR)/str(problem.id)
    os.makedirs(path, exist_ok=True)
    for file in filter(lambda x: x.endswith(".lock"), os.listdir(path)):
        os.remove(path/file)
    for file in filter(lambda x: not x.endswith(".lock"), os.listdir(path)):
        with open(path/(file+".lock"), "w") as f:
            import time
            f.write(str(time.time()))
    from utils import generate_file_list
    file_list = generate_file_list(problem.id)
    file_list.sort(key=lambda x: x["name"])
    problem.files = file_list
    problem.downloads = []
    problem.provides = []
    db.session.commit()
    return make_response(0, data=file_list)


@app.route("/api/get_problem_info", methods=["POST"])
def get_problem_info():
    """
    获取题目信息
    参数:
        id:int 题目ID
        edit:int 是否为编辑模式
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//code非0的时候表示错误信息
            "data":{
                "managable":"是否有管理权限",
                "id":-1//题目ID,
                "title":"qwq",//题目名
                "backcground":"qwq",//题目背景
                "content":"题目内容",
                "input_format":"输入格式",
                "output_format":"输出格式",
                "hint":"数据范围与提示",
                "example":"样例,形如[{'input':'xxx','output':'xxx'}]",
                "files":[{"last_modified_time":"time.time()","name":"1.in","size":"bytes"}],//不包括具体的二进制数据！
                "subtasks":[
                         {"name": "Subtask1", "score": 40, "method": "min", "files": [], "time_limit":1000, "memory_limit":512}].
                "last_code":"qwq",//上一次提交的代码,
                "last_lang":"qwq",//上一次选择的语言ID
                "submission_count":0,//提交数
                "accepted_count":0,//通过数
                "my_submission":-1//-1表示没有提交过，否则有AC提交就表示最新一次AC提交，没有AC提交就是最新一次提交,
                //我的提交状态
                "my_submission_status":-1,
                "score":题目总分,
                "extra_parameter":[
                    {"lang":"语言ID正则","parameter":"参数","name":"名称"}
                ],
                "lastUsedParameters":[1,2,4],
                "uploader":{
                    "uid":"上传者用户ID",
                    "username":"上传者用户名"
                },
                "recentDiscussions":[
                    {
                        "title":"讨论题目",
                        "id":"讨论ID"
                    }
                ],
                "languages":[
                    {id:"cpp","display":"显示名","version":"G++8.3"}
                ],
                "tags":[
                    {
                        "id":"标签ID",
                        "display":"标签显示名",
                        "color":"标签颜色"
                    }
                ],
                "hasPermission":"是否有权限访问",
                "inTodoList":"是否在待做题目列表中",
                "submissionVisible":"是否可以看到提交"
            }
        }
    """
    problem: Problem = db.session.query(Problem).filter(
        Problem.id == int(request.form["id"]))
    if problem.count() == 0:
        return make_response(-1, message="题目ID不存在")
    edit = int(request.form.get("edit", 0))
    problem = problem.one()
    if edit:
        if session.get("uid", -1) != problem.uploader_id and not permission_manager.has_permission(session.get("uid"), "problem.manage"):
            return make_response(-1, message="你没有权限编辑此题目")

    has_permission = problem.public or permission_manager.has_permission(session.get(
        "uid", None), f"problem.use.{problem.id}") or int(session.get("uid", -1)) == problem.uploader_id
    # result = problem.as_dict()
    # print(result.keys())
    result = {}
    if has_permission:
        USING_KEYS = [
            'background',
            'problem_type',
            'subtasks',
            'content',
            'extra_parameter',
            'public',
            'id',
            'input_format',
            'can_see_results',
            'output_format',
            'create_time',
            'spj_filename',
            'hint',
            'remote_judge_oj',
            'using_file_io',
            'example',
            'remote_problem_id',
            'uploader_id',
            'input_file_name',
            'files',
            'cached_submit_count',
            'title',
            'output_file_name',
            'downloads',
            'cached_accepted_count',
            'team_id',
            'provides']
    else:
        USING_KEYS = [
            "title", "id"
        ]
    if edit:
        USING_KEYS.append("invite_code")
    for item in USING_KEYS:
        result[item] = getattr(problem, item)
    if "public" in result:
        result["public"] = bool(result["public"])
    if "using_file_io" in result:
        result["using_file_io"] = bool(result["using_file_io"])
    result["hasPermission"] = has_permission
    if has_permission:
        last_submission: Submission = db.session.query(Submission).filter(and_(
            Submission.problem_id == problem.id, Submission.uid == session.get("uid"))).filter(Submission.contest_id == -1).order_by(Submission.submit_time.desc())
        result["lastUsedParameters"] = []
        if last_submission.count():
            submit = last_submission.first()
            if problem.problem_type == "submit_answer":
                result["last_code"] = "提交答案题不提供源代码"
            else:
                result["last_code"] = submit.code
            result["last_lang"] = submit.language
            result["lastUsedParameters"] = submit.selected_compile_parameters
        else:
            result["last_lang"] = result["last_code"] = ""
        result["submission_count"] = problem.cached_submit_count
        result["accepted_count"] = problem.cached_accepted_count
        result["my_submission"] = -1

        if session.get("uid"):
            ac_submit = db.session.query(Submission.id, Submission.status).filter(
                Submission.status == "accepted").filter(Submission.uid == session.get("uid")).filter(Submission.problem_id == problem.id).filter(Submission.contest_id == -1).order_by(Submission.submit_time.desc())
            if ac_submit.count():
                result["my_submission"], result["my_submission_status"] = ac_submit.first()
            else:
                any_submit = db.session.query(Submission.id, Submission.status).filter(
                    Submission.uid == session.get("uid")).filter(Submission.problem_id == problem.id).filter(Submission.contest_id == -1).order_by(Submission.submit_time.desc())
                if any_submit.count():
                    result["my_submission"], result["my_submission_status"] = any_submit.first(
                    )
        result["score"] = Problem.get_total_score(problem)
        result["create_time"] = str(result["create_time"])
        result["managable"] = permission_manager.has_permission(
            session.get("uid", None), "problem.manage")
        uploader: User = db.session.query(User.id, User.username).filter(
            User.id == problem.uploader_id).one()
        result["uploader"] = {
            "uid": uploader.id,
            "username": uploader.username
        }
        recent_discussions: Discussion = db.session.query(
            Discussion.id, Discussion.title).filter(Discussion.path == f"discussion.problem.{problem.id}").order_by(Discussion.id.desc()).limit(5)
        result["recentDiscussions"] = [
            {"id": item.id, "title": item.title} for item in recent_discussions
        ]
        result["languages"] = [

        ]
        for file in (x for x in os.listdir("langs") if x.endswith(".py")):
            module = importlib.import_module("langs."+file.replace(".py", ""))
            result["languages"].append({
                "id": file.replace(".py", ""),
                "display": module.DISPLAY,
                "version": module.VERSION,
                "ace_mode": module.ACE_MODE
            })
        result["tags"] = []
        for item in db.session.query(Tag.color, Tag.display, Tag.id, ProblemTag.tag_id).join(Tag, Tag.id == ProblemTag.tag_id).filter(ProblemTag.problem_id == problem.id).all():
            result["tags"].append({
                "id": item.id,
                "display": item.display,
                "color": item.color
            })
        result["inTodoList"] = bool(db.session.query(ProblemTodo).filter_by(
            uid=session.get("uid", -1), problem_id=problem.id).limit(1).count())
        result["submissionVisible"] = bool(problem.submission_visible)
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
    decompress_zip = bool(request.form.get("decompress_zip", "0") == "1")
    print(f"{decompress_zip=}")
    problem = db.session.query(Problem).filter(
        Problem.id == id)
    if problem.count() == 0:
        return make_response(-1, message="题目ID不存在")
    problem = problem.one()
    if not session.get("uid"):
        return make_response(-1, message="你没有权限执行此操作")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    if not permission_manager.has_permission(user.id, "problem.manage") and user.id != problem.uploader_id:
        return make_response(-1, message="你没有权限执行此操作")
    import os
    import shutil
    import zipfile
    from io import BytesIO
    import pathlib
    upload_path = pathlib.Path(os.path.join(
        basedir, f"{config.UPLOAD_DIR}/%d" % id))
    os.makedirs(upload_path, exist_ok=True)

    def handle_zipfile(fileobj):
        buf = BytesIO(fileobj.stream.read())
        zipf = zipfile.ZipFile(buf)
        for f in zipf.filelist:
            if not f.is_dir() and "/" not in f.filename:
                zipf.extract(f, upload_path)
                new_file_name = secure_filename(f.filename)
                shutil.move(upload_path/f.filename, upload_path/new_file_name)
                with open(os.path.join(upload_path, new_file_name)+".lock", "w") as file:
                    import time
                    file.write(f"{time.time()}")
    for file in request.files:
        if decompress_zip and request.files[file].filename.endswith(".zip"):
            handle_zipfile(request.files[file])
            continue
        request.files[file].save(os.path.join(
            upload_path, secure_filename(file)))
        with open(os.path.join(upload_path, secure_filename(file))+".lock", "w") as file:
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
    problem: Problem = problem.one()
    # filename = secure_filename(filename)
    if not problem.public and not session.get("uid", None):
        # print("cond387")
        flask.abort(403)
    if not any((x["name"] == filename for x in problem.files)):
        flask.abort(404)
    public_file = filename in problem.downloads
    # if not problem.public and not permission_manager.has_any_permission(session.get("uid", None), f"problem.use.{problem.id}"):
    # 用户未登录
    ok = False
    if not session.get("uid", None):
        # 只能下载公开题目的公开文件
        if not problem.public or not public_file:
            # print("cond1")
            flask.abort(403)
        else:
            ok = True
    else:
        # 用户已登录
        # 区分是否有题目管理权限
        # 题目创建者或者有管理权限，那么任何时候都行
        if session.get("uid", -1) == problem.uploader_id or permission_manager.has_any_permission(session.get("uid", None), f"problem.manage"):
            ok = True
        # 其他情况，如果是公开题或者有权限的私有题，则任何时候都允许下公开文件
        else:
            if problem.public or permission_manager.has_any_permission(session.get("uid", -1), f"problem.use.{problem.id}"):
                if public_file:
                    ok = True
    # if not problem.public and not permission_manager.has_any_permission(session.get("uid", None), f"problem.manage") and not public_file:
    #     flask.abort(403)
    # if session.get("uid"):
    #     user: User = db.session.query(User).filter(
    #         User.id == session.get("uid")).one()
    #     if not permission_manager.has_permission(user.id, f"problem.manage") and user.id != problem.uploader_id and not public_file:
    #         flask.abort(403)
    # else:
    #     if not problem.public or not public_file:
    #         flask.abort(403)
    if not ok:
        flask.abort(403)
    import os
    file = os.path.join(
        basedir, f"{config.UPLOAD_DIR}/{id}/{filename}")
    if not os.path.exists(file):
        flask.abort(404)
    return send_file(file, as_attachment=True, conditional=True)


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
    # if not problem.public and not session.get("uid"):
    #     return make_response(-1, message="你没有权限执行此操作")
    if not session.get("uid"):
        return make_response(-1, message="你没有权限执行此操作")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    if not permission_manager.has_permission(user.id, "problem.manage") and user.id != problem.uploader_id:
        return make_response(-1, message="你没有权限执行此操作")
    if not any((x["name"] == request.form["file"] for x in problem.files)):
        return make_response(-1, message="此文件不存在!")
    import os
    upload_path = os.path.join(
        basedir, f"{config.UPLOAD_DIR}/{request.form['id']}")
    os.makedirs(upload_path, exist_ok=True)
    try:
        os.remove(os.path.join(upload_path, request.form["file"]))
        os.remove(os.path.join(upload_path, request.form["file"]+".lock"))

    except Exception as ex:
        pass
    problem.files = generate_file_list(request.form["id"])

    # def remove_and_return(seq, val):
    #     seq = seq.copy()
    #     if val in seq:
    #         seq.remove(val)
    #     return seq
    filename = request.form["file"]

    # problem.downloads = remove_and_return(
    #     problem.downloads, request.form["file"])
    # problem.provides = remove_and_return(
    #     problem.provides, request.form["file"])
    problem.downloads = [x for x in problem.downloads if x != filename]
    problem.provides = [x for x in problem.provides if x != filename]

    db.session.commit()
    return make_response(0, file_list=generate_file_list(request.form["id"]))


@app.route("/api/update_problem", methods=["POST"])
def update_problem():
    """
    更新题目
    参数:
        id:int 题目ID
        data:dict 题目数据
        submitAnswer: "true"|"false" 是否提交答案
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//code非0的时候表示错误信息
        }
    """
    problem: Problem = db.session.query(Problem).filter(
        Problem.id == request.form["id"])
    if problem.count() == 0:
        return make_response(-1, message="题目ID不存在")
    problem = problem.one()
    if not session.get("uid"):
        return make_response(-1, message="你没有权限执行此操作")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    if not permission_manager.has_permission(user.id, "problem.manage") and user.id != problem.uploader_id:
        return make_response(-1, message="你没有权限执行此操作")
    data = decode_json(request.form["data"])
    for subtask in data["subtasks"]:
        try:
            subtask["score"] = int(subtask["score"])
        except Exception as ex:
            return make_response(-1, message=f"子任务{subtask['name']}的分数非整数")
    for subtask in data["subtasks"]:
        if len(subtask["testcases"]) == 0:
            return make_response(-1, message=f"子任务{subtask['name']}的测试点个数为0！")
        if subtask["score"] < len(subtask["testcases"]) and subtask["method"] != "min":
            return make_response(-1, message="非捆绑测试时，测试点个数不得多于分数")
        if subtask["method"] == "min":
            list(map(lambda x: x.__setitem__(
                "full_score", 1), subtask["testcases"]))
        else:
            score = subtask["score"]//len(subtask["testcases"])
            for i in range(0, len(subtask["testcases"])-1):
                subtask["testcases"][i]["full_score"] = score
            subtask["testcases"][-1]["full_score"] = subtask["score"] - \
                score*(len(subtask["testcases"])-1)
    if len(set(item["name"] for item in data["subtasks"])) != len(data["subtasks"]):
        return make_json_response(-1, message="不允许存在重名的子任务")
    if not permission_manager.has_any_permission(user.id, "problem.manage", "problem.publicize") and problem.public == False and data["public"] == True:
        return make_response(-1, message="你没有权限公开题目")
    # 更改题目ID
    if data["newProblemID"] != problem.id:
        old_id: int = int(problem.id)
        new_id: int = int(data["newProblemID"])
        if db.session.query(Problem.id).filter(Problem.id == new_id).one_or_none():
            return make_response(-1, message="题目ID已存在!")

        # 移动题目数据文件夹
        import shutil
        import pathlib
        path = pathlib.Path(config.UPLOAD_DIR)
        try:
            shutil.move(path/str(old_id), path/str(new_id))
        except Exception as ex:
            pass
        # 修改提交中涉及的题目ID
        db.session.query(Submission).filter(
            Submission.problem_id == old_id).update({Submission.problem_id: new_id})
        # 至于比赛...不管了
        problem.id = new_id
    AVAILABLE_KEYS = [
        "background",
        "extra_parameter",
        "subtasks",
        "content",
        "can_see_results",
        "public",
        "input_format",
        "spj_filename",
        "output_format",
        "using_file_io",
        "hint",
        "input_file_name",
        "example",
        "output_file_name",
        "title",
        "downloads",
        "provides",
        "invite_code"
    ]
    submit_answer = (request.form["submitAnswer"] == "true")
    if problem.problem_type == "remote_judge":
        return make_response(-1, message="远程评测题目不得更改题目类型")
    problem.problem_type = "submit_answer" if submit_answer else "traditional"
    for key in AVAILABLE_KEYS:
        setattr(problem, key, data[key])
    problem.submission_visible = data["submissionVisible"]
    db.session.commit()
    return make_response(0)


@app.route("/api/problem_list", methods=["POST"])
@unpack_argument
def problem_list(page: int = 1, filter: typing.Dict[str, typing.Any] = {}):
    """
    获取题目列表
    参数:
    page 页码
    filter 使用的过滤器
    {
        "过滤器ID1":{
            "过滤器定义"
        }
    }
    支持的过滤器
    searchKeyword: 搜索题目名关键字
        searchKeyword:"要搜索的内容"
    tag: 按标签搜索题目
        "tag":["tag1","tag2"...]
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//调用失败时的信息
            "data":[
                {
                    "id":-1,//题目ID
                    "title":"题目名",
                    mySubmission:{
                        "id":"我的提交ID,-1表示不存在",
                        "status":"提交状态",
                    },
                    "public":"是否公开",
                    "totalSubmit":"总提交数",
                    "acceptedSubmit":"通过提交数",
                    "tags":["id1","id2"..]
                }
            ],
            "pageCount":"总页数"
        }
    """
    result: Query = db.session.query(
        Problem.id,
        Problem.title,
        Problem.public,
        Problem.cached_accepted_count,
        Problem.cached_submit_count,
    )
    if not session.get("uid"):
        result = result.filter_by(public=True)
    else:
        user: User = db.session.query(User).filter(
            User.id == session.get("uid")).one()
        # 有查看私有题的权限
        if permission_manager.has_permission(user.id, "problem.manage"):
            pass
        else:
            result = result.filter(
                expr.or_(Problem.public == True, Problem.uploader_id == user.id))

    def apply_filter_search_keyword(keyword: str):
        nonlocal result
        result = result.filter(Problem.title.like(f"%{keyword}%"))

    def apply_filter_tag(tags: typing.List[str]):
        nonlocal result
        if not tags:
            return
        available_problems: Query = db.session.query(ProblemTag.problem_id).filter(expr.or_(
            *(ProblemTag.tag_id == item for item in tags)
        )).group_by(ProblemTag.problem_id).having(func.count() == len(tags)).subquery()
        result = result.filter(Problem.id == available_problems.c.problem_id)
    FILTER_REGISTRY = {
        "searchKeyword": apply_filter_search_keyword,
        "tag": apply_filter_tag
    }
    for key, value in filter.items():
        if key not in FILTER_REGISTRY:
            return make_response(-1, message=f"未知过滤器: {key}")
        FILTER_REGISTRY[key](value)
    count = result.count()
    import math
    pageCount = int(math.ceil(count/config.PROBLEMS_PER_PAGE))

    result = result.slice(
        (page-1)*config.PROBLEMS_PER_PAGE, (page)*config.PROBLEMS_PER_PAGE)
    data = []
    # print("mapping results.")
    for item in result:
        obj = {
            "id": item.id,
            "title": item.title,
            "mySubmission": {
                "id": -1,
                "status": "unsubmitted"
            },
            "public": item.public,
            "totalSubmit": item.cached_submit_count,
            "acceptedSubmit": item.cached_accepted_count,
            "tags": []
        }
        # 翻出来这个题目的标签...
        obj["tags"] = [tag.tag_id for tag in db.session.query(
            ProblemTag.tag_id).filter_by(problem_id=item.id).all()]
        # accepted的字典序比其他三个状态都少，所以按照status升序排能优先排到ac
        submit = db.session.query(Submission.id, Submission.status).filter_by(
            uid=session.get("uid", -1),
            problem_id=item.id,
            contest_id=-1
        ).order_by(
            Submission.status.asc()
        ).order_by(Submission.submit_time.desc()).limit(1)
        my_submission = obj["mySubmission"]
        if submit.count():
            submit = submit.first()
            my_submission["id"] = submit.id
            my_submission["status"] = submit.status
        data.append(obj)
    return make_response(0, data=data, pageCount=pageCount)


# @app.route("/api/ui_search_problem/", methods=["POST", "GET"])
# @app.route("/api/ui_search_problem/<string:search_keyword>", methods=["POST", "GET"])
# def search_problem(search_keyword=""):
#     """
#     搜索题目
#     参数:
#     search_keyword:str 题目名关键字
#     以Semantic UI的格式通讯
#     返回:
#         {
#             "success":true,
#             "results":[
#                 {"name":"qwq","value":"1234","text":"1234.题目名"}
#             ]
#         }
#     """
#     result = None
#     if not session.get("uid"):
#         result = db.session.query(Problem).filter(Problem.public == True)
#     else:
#         user: User = db.session.query(User).filter(
#             User.id == session.get("uid")).one()
#         if permission_manager.has_permission(user.id, "problem.manage"):
#             result = db.session.query(Problem)
#         else:
#             result = db.session.query(Problem).filter(
#                 or_(Problem.public == True, Problem.uploader_id == user.id))
#     result = result.filter(Problem.title.like(
#         f"%{search_keyword}%")).slice(0, 10)
#     ret = {
#         "success": True,
#         "results": [{"value": search_keyword, "name": f"搜索 {search_keyword}", "text": f"{search_keyword}"}]
#     }
#     for x in result:
#         ret["results"].append(
#             {"value": x.id, "name": f"{x.id}. {x.title}", "text": f"{x.id}"})
#     # print(f"search {search_keyword} = {ret}")
#     return encode_json(ret)


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
    if not permission_manager.has_any_permission(user.id, "problem.manage", "problem.create"):
        return make_response(-1, message="你没有权限进行此操作")
    from datetime import datetime
    problem = Problem(uploader_id=user.id,
                      create_time=datetime.now(), public=False)
    db.session.add(problem)
    db.session.commit()
    return make_response(0, problem_id=problem.id)


def refresh_cached_count(problem_id: int):
    """
    刷新题目AC和提交数缓存
    """
    print(f"Refreshing cached count: {problem_id=}")
    accepted_count: int = db.session.query(Submission).filter(and_(
        Submission.problem_id == problem_id, Submission.status == "accepted")).count()
    submit_count: int = db.session.query(Submission).filter(
        Submission.problem_id == problem_id).count()
    problem: Problem = db.session.query(
        Problem).filter(Problem.id == problem_id).one()
    problem.cached_accepted_count = accepted_count
    problem.cached_submit_count = submit_count
    print(f"Refreshed: {accepted_count=} {submit_count=}")
    db.session.commit()


@app.route("/api/problem/rejudge_all", methods=["POST"])
@unpack_argument
@require_permission(permission_manager, "problem.manage")
def api_rejudge_all_submission(problem_id: int):
    """
    重测某道题的所有提交
    """
    from api.judge import push_to_queue
    ids = []
    for item in db.session.query(Submission).filter(Submission.problem_id == problem_id).all():
        item: Submission
        item.status = "waiting"
        ids.append(item.id)
    db.session.commit()
    for x in ids:
        push_to_queue(x)
    return make_response(0, message="操作完成")
