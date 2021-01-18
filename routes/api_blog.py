"""
    博客基于讨论，大多数使用与讨论相同的API与后端
    用户自己的博客的讨论路径为blog.user.用户ID

"""
from utils import make_response
from main import config, permission_manager, db
from flask import Blueprint, session, request

from common.utils import unpack_argument
from common.permission import require_permission
from models.comment import Comment
from models.discussion import Discussion
from models.user import User
import sqlalchemy.sql.expression as expr
import sqlalchemy.sql.functions as func

from flask_sqlalchemy import BaseQuery

import typing
import math
router = Blueprint("blog", __name__)


@router.route("/list", methods=["POST"])
@unpack_argument
def blog_list(uid: int = 1, page: int = 1):
    """
    获取用户博客列表
    {
        "pageCount":"总页数",
        "data":[
            {
                "title":"标题",
                "time":"发送时间",
                "commentCount":"评论条数",
                "lastCommentAt":"最后评论",
                "summary":"摘要",
                "id":"讨论ID",
                "private":"是否私有"
            }
        ],
        "userData":{
            "uid":"用户ID",
            "username":"用户名",
            "email":"电子邮箱",
            "publicBlogCount":"公开博客数"
        },
        "managable":"是否有管理权限"
    }
    """
    user: User = db.session.query(
        User.id,
        User.username,
        User.email
    ).filter_by(id=uid).one_or_none()
    if not user:
        return make_response(-1, message="用户不存在")
    query: BaseQuery = db.session.query(
        Discussion.id,
        Discussion.content,
        Discussion.private,
        Discussion.title,
        Discussion.time,
        # func.count(Comment.id).label("comment_count"),
        # func.max(Comment.time).label("last_comment_time")
    ).filter(
        Discussion.path == (f"blog.user.{uid}")
    ).order_by(Discussion.id.desc())
    public_blog_count = query.filter(Discussion.private == False).count()
    if session.get("uid", -1) == uid or permission_manager.has_permission(session.get("uid", None), "discussion.manage"):
        pass
    else:
        query = query.filter(Discussion.private == False)

    page_count = int(math.ceil(
        query.count()/config.BLOGS_PER_PAGE
    ))
    data = query.slice(
        (page-1)*config.BLOGS_PER_PAGE,
        page*config.BLOGS_PER_PAGE
    ).all()
    result = []
    for item in data:
        last_comment = db.session.query(Comment.time).filter_by(
            discussion_id=item.id).order_by(Comment.time.desc()).one_or_none()
        current = {
            "id": item.id,
            "title": item.title,
            "time": str(item.time),
            "commentCount": db.session.query(Comment).filter_by(discussion_id=item.id).count(),
            "lastCommentAt": last_comment.time if last_comment else None,
            "summary": item.content[:config.BLOG_SUMMARY_LENGTH],
            "private": item.private

        }
        result.append(current)
    return make_response(0, pageCount=page_count, data=result, userData={
        "uid": user.id,
        "username": user.username,
        "email": user.email,
        "publicBlogCount": public_blog_count
    }, managable=(session.get("uid", -1) == uid or permission_manager.has_permission(session.get("uid", None), "discussion.manage")))
