from main import db, permission_manager, config
from main import web_app as app
from common.permission import require_permission
from common.utils import unpack_argument
from models import User, ProblemSet, Problem
from flask_sqlalchemy import BaseQuery
from flask import session
from utils import make_response
from datetime import datetime
import math


@app.route("/api/problemset/list", methods=["POST"])
@require_permission(permission_manager, "problemset.use.public")
def api_problemset_list(page: int = 1):
    """
    {
        "data":{
            "items":[
                {
                    "id":"问题集ID",
                    "name":"名称",
                    "owner":{
                        "uid":"用户ID",
                        "username":"用户名"
                    },
                    "problemCount":"题目数量",
                    "private":"是否私有",
                    "accessible":"是否可访问(仅对私有习题集有效)",
                    "createTime":"创建时间"
                }
            ],
            "pageCount":"总页数"
        }
    }
    """
    query_object: BaseQuery = db.session.query(ProblemSet.id,
                                               ProblemSet.name,
                                               ProblemSet.owner_uid,
                                               ProblemSet.problems,
                                               ProblemSet.private,
                                               ProblemSet.create_time)
    pages = int(math.ceil(query_object.count()/config.PROBLEMSETS_PER_PAGE))
    query_object = query_object.slice(
        (page-1)*config.PROBLEMSETS_PER_PAGE, (page)*config.PROBLEMSETS_PER_PAGE)
    result = []
    for item in query_object.all():
        item: ProblemSet = item
        owner: User = db.session.query(User.username, User.id).filter(
            User.id == item.owner_uid).one()
        accessible = (not item.private) or permission_manager.has_permission(
            session.get("uid"), "problemset.use."+str(item.id))
        result.append({
            "id": item.id,
            "name": item.name,
            "owner": {
                "uid": owner.id,
                "username": owner.username
            },
            "problemCount": len(item.problems) if accessible else -1,
            "private": item.private,
            "accessible": accessible,
            "createTime": str(item.create_time)
        })
    return make_response(0, data={
        "items": result, "pageCount": pages
    })


@app.route("/api/problemset/create", methods=["POST"])
@require_permission(permission_manager, "problemset.create")
def api_problemset_create():
    problemset: ProblemSet = ProblemSet(owner_id=int(
        session.get("uid")), create_time=datetime.now())
    db.session.add(problemset)
    db.session.commit()
    return make_response(0, data={
        "id": problemset.id
    })


@app.route("/api/problemset/remove", methods=["POST"])
def api_problemset_remove(id):
    problemset: ProblemSet = db.session.query(
        ProblemSet).filter(ProblemSet.id == id).one_or_none()
    if not problemset:
        return make_response(-1, message="非法ID")
    if not permission_manager.has_permission(session.get("uid"), "problemset.manage") and problemset.owner_uid != int(session.get("uid")):
        return make_response(-1, message="你没有权限进行此操作")
    db.session.delete(problemset)
    db.session.commit()
    return make_response(0, message="删除成功")


@app.route("/api/problemset/update", methods=["POST"])
def api_problemset_update(id: int, name: str, private: bool, invitationCode: str, showRanklist: bool, problems: list):
    problemset: ProblemSet = db.session.query(
        ProblemSet).filter(ProblemSet.id == id).one_or_none()
    if not problemset:
        return make_response(-1, message="非法ID")
    if not permission_manager.has_permission(session.get("uid"), "problemset.manage") and problemset.owner_uid != int(session.get("uid")):
        return make_response(-1, message="你没有权限进行此操作")
    problemset.name = name
    problemset.private = private
    problemset.invitation_code = invitationCode
    problemset.show_ranklist = showRanklist
    problemset.problems = problems
    db.session.commit()
    return make_response(0, message="更新成功")


@app.route("/api/problemset/get", methods=["POST"])
def api_problemset_get(id: int):
    problemset: ProblemSet = db.session.query(
        ProblemSet).filter(ProblemSet.id == id).one_or_none()
    if not problemset:
        return make_response(-1, message="非法ID")
    if problemset.private:
        if not permission_manager.has_permission(session.get("uid"), f"problemset.use.{problemset.id}"):
            return make_response(-1, message="你没有权限进行此操作", data={"requireInvitationCode": True})
    else:
        if not permission_manager.has_permission(session.get("uid"), "problemset.use.public"):
            return make_response(-1, message="你没有权限进行此操作")
    
    return make_response(0, message="更新成功")
