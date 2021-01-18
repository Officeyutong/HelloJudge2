import typing

from main import background_task_queue, db, config, permission_manager, redis_connection_pool
from main import web_app as app
from common.permission import require_permission
from common.utils import unpack_argument
from flask_sqlalchemy import BaseQuery
from flask import session
import flask
from utils import make_response
from models.user import User
from models.tag import Tag, ProblemTag
from models.problem import Problem
import sqlalchemy.sql.expression as expr
from sqlalchemy.sql import func
from api.feed import rebuild_feed_cache
import math
import redis
import json


@app.route("/api/problemtag/all", methods=["POST"])
def api_problemtag_get_all_tags():
    """
    获取所有的tag
    """
    tags = db.session.query(Tag).all()
    result = [{
        "id": item.id,
        "display": item.display,
        "color": item.color
    } for item in tags]
    return make_response(0, data=result)


@app.route("/api/problemtag/remove", methods=["POST"])
@unpack_argument
@require_permission(manager=permission_manager, permission="problemtag.manage")
def api_problemtag_remove(id: str):
    """
    删除某个tag
    """
    db.session.query(Tag).filter_by(id=id).delete()
    db.session.commit()
    return make_response(0, message="操作完成")


@app.route("/api/problemtag/update", methods=["POST"])
@unpack_argument
@require_permission(manager=permission_manager, permission="problemtag.manage")
def api_problemtag_update(id: str, display: str, color: str):
    """
    更新某个tag
    """
    # db.session.query(Tag).filter_by(id=id).delete()
    tag = db.session.query(Tag).filter_by(id=id).one_or_none()
    if not tag:
        return make_response(-1, message="Tag不存在")
    tag.display = display
    tag.color = color
    db.session.commit()
    return make_response(0, message="操作完成")


@app.route("/api/problemtag/create", methods=["POST"])
@unpack_argument
@require_permission(manager=permission_manager, permission="problemtag.manage")
def api_problemtag_create(id: str):
    """
    创建tag
    """
    # db.session.query(Tag).filter_by(id=id).delete()
    if db.session.query(Tag).filter_by(id=id).one_or_none():
        return make_response(-1, message="此Tag已经存在")
    tag = Tag(id=id, display="新建Tag", color="")
    db.session.add(tag)
    db.session.commit()
    return make_response(0, display=tag.display, color=tag.color, message="操作完成")


@app.route("/api/problemtag/update_problem", methods=["POST"])
@unpack_argument
def api_problemtag_update_problem(problemID: int, tags: typing.List[int]):
    uid = int(session.get("uid", -1))
    problem = db.session.query(
        Problem.uploader_id).filter_by(id=problemID).one()
    if not permission_manager.has_permission(uid, "problem.manage") and uid != problem.uploader_id:
        return make_response(-1, message="你没有权限执行此操作")
    db.session.query(ProblemTag).filter(
        ProblemTag.problem_id == problemID).delete()
    db.session.add_all(
        (ProblemTag(problem_id=problemID, tag_id=item) for item in tags))
    db.session.commit()
    return make_response(0, message="操作完成")
