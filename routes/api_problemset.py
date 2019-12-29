from main import db, permission_manager, config
from main import web_app as app
from common.permission import require_permission
from common.utils import unpack_argument
from models import User, ProblemSet, Problem, Submission
from flask_sqlalchemy import BaseQuery
from flask import session
from utils import make_response
from datetime import datetime
import math


@app.route("/api/problemset/list", methods=["POST"])
@require_permission(permission_manager, "problemset.use.public")
@unpack_argument
def api_problemset_list(page: int):
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
                                               ProblemSet.create_time).order_by(ProblemSet.id.desc())
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
    problemset: ProblemSet = ProblemSet(owner_uid=int(
        session.get("uid")), create_time=datetime.now())
    db.session.add(problemset)
    db.session.commit()
    return make_response(0, data={
        "id": problemset.id
    })


@app.route("/api/problemset/remove", methods=["POST"])
@unpack_argument
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


@app.route("/api/problemset/get", methods=["POST"])
@unpack_argument
def api_problemset_get(id: int):
    """
    {
        "data":{
            "owner":{
                "uid":"创建者用户ID",
                "username":"创建者用户名"
            },
            "name":"qwq",
            "id":-1,
            "private":true,
            "invitationCode":"邀请码",
            "showRanklist":"是否显示排行榜",
            "problems":["题目ID"  ],
            "createTime":"qwq",
            "dscription":"说明"
        }
    }
    """
    problemset: ProblemSet = db.session.query(
        ProblemSet).filter(ProblemSet.id == id).one_or_none()
    if not problemset:
        return make_response(-1, message="ID不存在")
    if not permission_manager.has_permission(session.get("uid"), "problemset.manage") and problemset.owner_uid != int(session.get("uid", 0)):
        return make_response(-1, message="你没有权限进行此操作")
    owner: User = db.session.query(User.id, User.username).filter(
        User.id == problemset.owner_uid).one()
    return make_response(0, data={
        "owner": {
            "uid": owner.id,
            "username": owner.username,
        },
        "private": problemset.private,
        "invitationCode": problemset.invitation_code,
        "showRanklist": problemset.show_ranklist,
        "problems": problemset.problems,
        "createTime": str(problemset.create_time),
        "description": problemset.description,
        "name": problemset.name,
        "id": problemset.id
    })


@app.route("/api/problemset/update", methods=["POST"])
@unpack_argument
def api_problemset_update(data: dict):
    """
    { 
        "data":{
            "name":"qwq",
            "id":-1,
            "private":true,
            "invitationCode":"邀请码",
            "showRanklist":"是否显示排行榜",
            "problems":["题目ID"  ],
            "description":"说明",

        }
    }
    """
    problemset: ProblemSet = db.session.query(
        ProblemSet).filter(ProblemSet.id == data["id"]).one_or_none()
    if not problemset:
        return make_response(-1, message="ID不存在")
    if not permission_manager.has_permission(session.get("uid"), "problemset.manage") and problemset.owner_uid != int(session.get("uid", 0)):
        return make_response(-1, message="你没有权限进行此操作")
    problemset.name = data["name"]
    problemset.private = data["private"]
    problemset.show_ranklist = data["showRanklist"]
    problemset.invitation_code = data["invitationCode"]
    problemset.problems = data["problems"]
    problemset.description = data["description"]
    for item in data["problems"]:
        query: BaseQuery = db.session.query(
            Problem.id).filter(Problem.id == item)
        print("querying", item)
        print(query.limit(1).count())
        if query.limit(1).count() == 0:
            return make_response(-1, message=f"题目 {item} 非法")
    db.session.commit()
    return make_response(0, message="更新成功")


@app.route("/api/problemset/join_private_problemset", methods=["POST"])
@unpack_argument
def api_problemset_join_private_problemset(id: int, code: str):
    problemset: ProblemSet = db.session.query(
        ProblemSet.invitation_code).filter(ProblemSet.id == id).one_or_none()
    if not problemset:
        return make_response(-1, message="ID不存在")
    if code != problemset.invitation_code:
        return make_response(-1, message="邀请码错误")
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    permission_manager.add_permission(
        session.get("uid"), f"problemset.use.{id}")
    return make_response(0, message="ok")


@app.route("/api/problemset/get_public", methods=["POST"])
@unpack_argument
def api_problemset_get_public(id: int):
    """
    {
        "data":{
            "owner":{
                "uid":"创建者用户ID",
                "username":"创建者用户名"
            },
            "name":"qwq",
            "id":-1,
            "private":true,
            "showRanklist":"是否显示排行榜",
            "problems":[
                {
                    "title":"题目名",
                    "id":"题目ID"
                }
            ],
            "ranklist":[
                {
                    "uid":"qwq",
                    "username":"qwq",
                    "problems":[
                        {
                            "score":1,
                            "status":"qwq",
                            "submissionID":"相关提交ID"
                        }
                    ]
                }
            ],
            "createTime":"qwq",
            "description":"说明",
            "managable":"是否可管理"
        }
    }
    """
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
    owner = db.session.query(User.id, User.username).filter(
        User.id == problemset.owner_uid).one()
    result = {
        "owner": {
            "uid": owner.id,
            "username": owner.username
        },
        "name": problemset.name,
        "id": problemset.id,
        "private": problemset.private,
        "showRanklist": problemset.show_ranklist,
        "createTime": str(problemset.create_time),
        "ranklist": [],
        "problems": [],
        "description": problemset.description,
        "managable": permission_manager.has_permission(session.get("uid"), "problemset.manage") or int(session.get("uid")) == problemset.owner_uid
    }
    problems = result["problems"]
    for item in problemset.problems:
        problem: Problem = db.session.query(
            Problem.id, Problem.title).filter(Problem.id == item).one()
        submitted_users = db.session.query(Submission.uid).filter(
            Submission.problemset_id == problemset.id).distinct().all()
        current = {
            "title": problem.title,
            "id": problem.id,
            "userResults": {

            }
        }
        for user in submitted_users:
            current_submission: Submission = db.session.query(Submission.id, Submission.score, Submission.status).filter(Submission.uid == user).filter(
                Submission.problemset_id == problemset.id).order_by(Submission.score.desc()).first()
            current["userResults"][int(user)] = {
                "submissionID": current_submission.id,
                "score": current_submission.score,
                "status": current_submission.status
            }
        problems.append(current)
    # TODO:整理成排行榜
    return make_response(0, data=result)
