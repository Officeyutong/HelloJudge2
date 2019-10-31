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
from common.utils import unpack_argument
from common.permission import require_permission
from main import permission_manager
legal_paths = re.compile(
    r"^(broadcast)|(discussion((.global)|(.problem((.global)|.(?P<id>[0-9]+)))))$")
path_query = re.compile(
    r"^(broadcast)|(discussion((.global)?|(.problem((.global)|.(?P<id>[0-9]+))?)))$")


def can_post_at(user: User, path: str):
    if not permission_manager.has_permission(user.id, "discussion.manage") and path.startswith("broadcast"):
        return False
    match_result = legal_paths.match(path)
    if not match_result:
        return False
    if match_result.groupdict().get("id", None):
        problem_id = int(match_result.groupdict()["id"])
        if not Problem.has(problem_id):
            return False
    return True


@app.route("/api/discussion/remove", methods=["POST"])
@unpack_argument
def discussion_remove(discussionID: int):
    """
    删除讨论
    discussionID:讨论ID
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    discussion: Discussion = Discussion.by_id(discussionID)
    if not discussion:
        return make_response(-1, message="讨论ID不存在")
    user: User = User.by_id(session.get("uid"))
    if not permission_manager.has_permission(user.id, "discussion.manage") and user.id != discussion.uid:
        return make_response(-1, message="你没有权限这样做")
    db.session.delete(discussion)
    db.session.commit()
    return make_response(0, message="操作成功")


@app.route("/api/discussion/update", methods=["POST"])
@unpack_argument
def discussion_update(id: int, content: str, title: str, top: bool):
    """
    更新讨论
    id:讨论ID
    content:内容
    title:标题:
    top:置顶
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    discussion: Discussion = Discussion.by_id(id)
    if not discussion:
        return make_response(-1, message="讨论ID不存在")
    user: User = User.by_id(session.get("uid"))
    if not permission_manager.has_permission(user.id, "discussion.manage") and user.id != discussion.uid:
        return make_response(-1, message="你没有权限这样做")
    import datetime
    discussion.content = content + \
        "\n\n最后编辑于"+str(datetime.datetime.now())
    discussion.title = title
    if top and not permission_manager.has_permission(user.id, "discussion.manage"):
        return make_response(-1, message="你没有权限发送置顶讨论")
    discussion.top = top
    db.session.commit()
    return make_response(0, message="操作成功")


@app.route("/api/post_discussion", methods=["POST"])
@unpack_argument
def post_discussion(title: str, content: str, path: str, top: bool):
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
    if not session.get("uid"):
        return make_response(-1, message="请登录")
    user: User = User.by_id(int(session.get("uid")))
    if not permission_manager.has_permission(user.id, "discussion.manage") and top:
        return make_response(-1, message="只有管理员才能发置顶讨论")
    if not can_post_at(user, path):
        return make_response(-1, message="你无权在这里发帖")
    if not title:
        return make_response(-1, message="标题不得为空")
    discussion = Discussion()
    discussion.content = content
    discussion.title = title
    discussion.path = path
    import datetime
    discussion.time = datetime.datetime.now()
    discussion.top = top
    discussion.uid = user.id
    db.session.add(discussion)
    db.session.commit()
    return make_response(0, discussion_id=discussion.id)


@app.route("/api/post_comment", methods=["POST"])
@unpack_argument
def post_comment(content: str, discussionID: int):
    """
    发送评论
    参数:
    content:str 内容
    discussionID:int 讨论id
    返回
    {
        "code":-1,//是否成功执行
        "message":"错误信息",
        "last_page":"最后一页的页码"
    }
    """
    if not Discussion.has(discussionID):
        return make_response(-1, message="讨论ID不合法")
    # content = request.form.get("content", "")
    if not content:
        return make_response(-1, message="内容不能为空")
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    comment: Comment = Comment()
    comment.discussion_id = discussionID
    comment.content = content
    comment.time = datetime.datetime.now()
    comment.uid = session.get("uid")
    db.session.add(comment)
    db.session.commit()
    return make_response(0, last_page=int(math.ceil(db.session.query(Comment.id).filter(Comment.discussion_id == int(discussionID)).count()/config.COMMENTS_PER_PAGE)))


@app.route("/api/get_discussion_list", methods=["POST"])
@unpack_argument
def get_discussion_list(path: str, page: id, countLimit: int = 10**8):
    """
    获取讨论列表
    参数:
    path:str 讨论路径
    page:id 页面ID
    countLimit:int 数量限制
    返回
    {
        "code":0,//调用失败返回-1 
        "message":-1,
        "page_count":10,//总页数
        "current_page":10,//当前页 
        "managable":"可否删除\编辑",
        "data":[
                {
                "uid":"用户ID",
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
    page = int(page)
    result = db.session.query(Discussion).filter(or_(
        Discussion.path == path, Discussion.path.like(f"{path}.%")))
    ret = {
        "page_count": int(math.ceil(result.count()/config.DISCUSSIONS_PER_PAGE)),
        "current_page": page,
        "data": [],
        "managable": permission_manager.has_permission(session.get("uid", None), "discussion.manage")
    }

    result = result.order_by(Discussion.id.desc()).order_by(Discussion.top.desc()).slice((page-1)*config.DISCUSSIONS_PER_PAGE,
                                                                                         min(page*config.DISCUSSIONS_PER_PAGE, (page-1)*config.DISCUSSIONS_PER_PAGE+int(countLimit)))
    for item in result:
        user: User = User.by_id(item.uid)
        comments = db.session.query(Comment).filter(
            Comment.discussion_id == item.id).order_by(Comment.id.desc())
        # import pdb
        # pdb.set_trace()
        ret["data"].append({
            "uid": user.id,
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
            {"id":"评论ID","user_name":"用户名","uid":"用户ID","content":"内容","time":"发布时间","email":"邮箱"}
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
        user: User = User.by_id(item.uid)
        ret["data"].append({
            "id": item.id,
            "username": user.username,
            "uid": user.id,
            "content": item.content,
            "time": str(item.time),
            "email": user.email
        })
    return make_response(0, **ret)


@app.route("/api/get_path_name", methods=["POST"])
@unpack_argument
def get_path_name(path: str):
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
    if not path_query.match(path):
        return make_response(-1, message="非法路径名")
    return make_response(0, name=({
        "discussion": "所有讨论",
        "discussion.global": "全局讨论",
        "discussion.problem": "所有题目讨论",
        "discussion.problem.global": "题目全局讨论",
        "broadcast": "公告"
    }.get(path, f"题目 {path.split('.')[-1]} 的讨论")))


@app.route("/api/get_discussion", methods=["POST"])
@unpack_argument
def get_discussion(id: int):
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
    import flask
    if not Discussion.has(id):
        flask.abort(404)
    ret = {
        "data": db.session.query(Discussion).filter(Discussion.id == id).one().as_dict()
    }
    user = User.by_id(ret["data"]["uid"])
    ret["data"]["email"] = user.email
    ret["data"]["username"] = user.username

    ret["data"]["time"] = str(ret["data"]["time"])
    return make_response(0, **ret)
