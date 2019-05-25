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

legal_paths = re.compile(
    r"^discussion((.global)|(.problem((.global)|.(?P<id>[0-9]+))))$")
path_query = re.compile(
    r"^discussion((.global)?|(.problem((.global)|.(?P<id>[0-9]+))?))$")


def can_post_at(user: User, path: str):
    if not user.is_admin and path.startswith("broadcast."):
        return False
    match_result = legal_paths.match(path)
    if not match_result:
        return False
    if match_result.groupdict().get("id", None):
        problem_id = int(match_result.groupdict()["id"])
        if not Problem.has(problem_id):
            return False
    return True


@app.route("/api/post_discussion", methods=["POST"])
def discussion_post():
    """
    发送讨论
    参数:
    title:str 讨论题目
    content:str 内容
    path:str 路径
    top:bool 是否置顶
    返回
    {
        "code":-1,//是否成功执行
        "discussion_id":"成功执行时的讨论ID",
        "message":"错误信息"
    }
    """
    if not session.get("userid"):
        return make_response(-1, message="请登录")
    user: User = User.by_id(int(session.get("userid")))
    if not user.is_admin and bool(request.form["top"]):
        return make_response(-1, message="只有管理员才能发置顶讨论")
    if not can_post_at(user, request.form["path"]):
        return make_response(-1, message="你无权在这里发帖")
    if not request.form.get("title", ""):
        return make_response(-1, message="标题不得为空")
    discussion = Discussion()
    discussion.content = request.form["content"]
    discussion.title = request.form["title"]
    discussion.path = request.form["path"]
    import datetime
    discussion.time = datetime.datetime.now()
    discussion.top = bool(request.form["top"])
    discussion.user_id = user.id
    db.session.add(discussion)
    db.session.commit()
    return make_response(0, discussion_id=discussion.id)


@app.route("/api/post_comment", methods=["POST"])
def post_comment():
    """
    发送评论
    参数:
    content:str 内容
    discussion_id:int 讨论id
    返回
    {
        "code":-1,//是否成功执行
        "message":"错误信息",
        "last_page":"最后一页的页码"
    }
    """
    if not Discussion.has(request.form.get("discussion_id", -1)):
        return make_response(-1, message="讨论ID不合法")
    content = request.form.get("content", "")
    if not content:
        return make_response(-1, message="内容不能为空")
    if not session.get("userid"):
        return make_response(-1, message="请先登录")
    comment: Comment = Comment()
    comment.discussion_id = int(request.form.get("discussion_id"))
    comment.content = request.form["content"]
    comment.time = datetime.datetime.now()
    comment.user_id = session.get("userid")
    db.session.add(comment)
    db.session.commit()
    return make_response(0, last_page=int(math.ceil(db.session.query(Comment.id).filter(Comment.discussion_id == int(request.form["discussion_id"])).count()/config.COMMENTS_PER_PAGE)))


@app.route("/api/get_discussion_list", methods=["POST"])
def get_discussion_list():
    """
    获取讨论列表
    参数:
    path:str 讨论路径
    page:id 页面ID
    返回
    {
        "code":0,//调用失败返回-1 
        "message":-1,
        "pafe_count":10,//总页数
        "current_page":10,//当前页 
        "data":[
                {
                "user_id":"用户ID",
                "username":"用户名",
                "email":"电子邮件"
                "time":"发布时间",
                "title":"讨论题目",
                "comment_count":0,//评论数量
                "last_comment_time":"最后评论时间",
                "id":-1//讨论ID
                }
        ]
    }
    """
    # print(request.form)
    # import pdb
    # pdb.set_trace()
    result = db.session.query(Discussion).filter(or_(
        Discussion.path == request.form["path"], Discussion.path.like(f"{request.form['path']}.%")))
    page = int(request.form.get("page", 1))
    ret = {
        "page_count": int(math.ceil(result.count()/config.DISCUSSION_PER_PAGE)),
        "current_page": page,
        "data": []
    }

    result = result.order_by(Discussion.id.desc()).order_by(Discussion.top.desc()).slice((page-1)*config.DISCUSSION_PER_PAGE,
                                                                                         page*config.DISCUSSION_PER_PAGE)
    for item in result:
        user: User = User.by_id(item.user_id)
        comments = db.session.query(Comment).filter(
            Comment.discussion_id == item.id).order_by(Comment.id.desc())
        # import pdb
        # pdb.set_trace()
        ret["data"].append({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "time": str(item.time),
            "title": item.title,
            "comment_count": comments.count(),
            "last_comment_time": str(comments.first().time) if (comments.count() != 0) else None,
            "id": item.id
        })
    return make_response(0, **ret)


@app.route("/api/get_comments", methods=["POST"])
def get_comments():
    """ 
    获取某个讨论的所有评论
    参数:
    discussion_id:int 讨论id
    page:int 页
    返回:
    {
        "code":0,//返回是否成功
        "data":[
            {"id":"评论ID","user_name":"用户名","userid":"用户ID","content":"内容","time":"发布时间","email":"邮箱"}
        ],
        "page_count":"总页面数",
        "current_page":"当前页"
    }
    """
    if not Discussion.has(int(request.form["discussion_id"])):
        return make_response(-1, message="讨论ID不存在")
    result = db.session.query(Comment).filter(
        Comment.discussion_id == int(request.form["discussion_id"]))
    page = int(request.form.get("page", 1))
    ret = {
        "page_count": int(math.ceil(result.count()/config.COMMENTS_PER_PAGE)),
        "current_page": page,
        "data": []
    }
    result = result.order_by(Comment.id.asc()).slice((page-1)*config.COMMENTS_PER_PAGE,
                                                     page*config.COMMENTS_PER_PAGE)
    for item in result:
        user: User = User.by_id(item.user_id)
        ret["data"].append({
            "id": item.id,
            "username": user.username,
            "user_id": user.id,
            "content": item.content,
            "time": str(item.time),
            "email": user.email
        })
    return make_response(0, **ret)


@app.route("/api/get_path_name", methods=["POST"])
def get_path_name():
    """
    查询路径名
    参数:
    path:str 路径
    返回:
    {
        "code":-1,
        "name":"qwq"
    }
    """
    if not path_query.match(request.form["path"]):
        return make_response(-1, message="非法路径名")
    return make_response(0, name=({
        "discussion": "所有讨论",
        "discussion.global": "全局讨论",
        "discussion.problem": "所有题目讨论",
        "discussion.problem.global": "题目全局讨论"
    }.get(request.form["path"], f"题目 {request.form['path'].split('.')[-1]} 的讨论")))


@app.route("/api/get_discussion", methods=["POST"])
def get_discussion():
    """
    获取讨论信息
    参数:
    id:int 讨论ID
    返回
    {
        "code":1,
        "message":"",
        "data":{
            同数据模型,
            "email":邮箱,
            "username":"用户名"
        }
    }
    """
    id = int(request.form["id"])
    import flask
    if not Discussion.has(id):
        flask.abort(404)
    ret = {
        "data": db.session.query(Discussion).filter(Discussion.id == id).one().as_dict()
    }
    user = User.by_id(ret["data"]["user_id"])
    ret["data"]["email"] = user.email
    ret["data"]["username"] = user.username

    ret["data"]["time"] = str(ret["data"]["time"])
    return make_response(0, **ret)
