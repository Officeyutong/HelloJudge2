from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename
import re

legal_paths = re.compile(
    r"^discussion((.global)|(.problem((.global)|.(?P<id>[0-9]+))))$")


def can_post_at(user: User, path: str):
    if not user.is_admin and path.startswith("broadcast."):
        return False
    match_result = legal_paths.match(path)
    if not match_result:
        return False
    if "id" in match_result.groupdict():
        problem_id = int(match_result.groupdict()["id"])
        if not Problem.has(problem_id):
            return False
    return True


@app.route("/api/disscussion_post", method=["POST"])
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
