import typing
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
import sqlalchemy.sql.expression as expr


@app.route("/api/problemset/unlock_permissions", methods=["POST"])
@unpack_argument
@require_permission(permission_manager, "problemset.use.public")
def api_problemset_unlock_permissions(problemset: int):
    """
    用户解锁权限包
    """
    problemset_inst: ProblemSet = db.session.query(
        ProblemSet.problems,
        ProblemSet.private,
        ProblemSet.owner_uid
    ).filter_by(id=problemset).one_or_none()
    if not problemset_inst:
        return make_response(-1, message="权限包不存在")
    if problemset_inst.private and int(session.get("uid", -1)) != problemset_inst.owner_uid and not permission_manager.has_permission(int(session.get("uid")), f"problemset.use.{problemset}"):
        return make_response(-1, message="你没有权限使用该权限包")
    user: User = db.session.query(User).filter_by(id=session.get("uid")).one()
    to_add = {f"problem.use.{x}" for x in problemset_inst.problems}
    user.permissions = [
        x for x in user.permissions if x not in to_add] + list(to_add)
    db.session.commit()
    permission_manager.refresh_user(session.get("uid"))
    return make_response(0, message="操作完成")


@app.route("/api/problemset/list", methods=["POST"])
# @require_permission(permission_manager, "problemset.use.public")
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
    # 用户所创建的习题集中的题目，则用户要么是该题目的创建者，要么有problem.manage权限，要么该题目是公开题目
    for prob in data["problems"]:
        curr: Problem = db.session.query(Problem.public, Problem.uploader_id).filter_by(
            id=prob).one_or_none()
        if not curr:
            return make_response(-1, message=f"题号{prob}不存在")
        if not curr.public:
            if int(session.get("uid", -1)) != curr.uploader_id and not permission_manager.has_permission(session.get("uid", -1), "problem.manage"):
                return make_response(-1, message=f"要使用非公开题目{prob}，那么要么您是该题目的创建者，要么您具有problem.manage权限")
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
                    "id":"题目ID",
                    "userResult":{
                        "score":"分数",
                        "status":"状态",
                        "submissionID":"评测ID" -1表示没有提交过
                    }
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
        # "ranklist": [],
        "problems": [],
        "description": problemset.description,
        "managable": permission_manager.has_permission(session.get("uid"), "problemset.manage") or int(session.get("uid")) == problemset.owner_uid
    }
    # problems: typing.List[typing.Dict[str, typing.Any]] = result["problems"]
    # new_problems:  = []
    for problem_id in problemset.problems:
        problem_data: Problem = db.session.query(Problem.title).filter(
            Problem.id == problem_id).one_or_none()
        if not problem_data:
            continue
        problem = {
            "title": problem_data.title,
            "id": problem_id,
            # "user"
        }
        if not session.get("uid", None):
            problem["userResult"] = {
                "score": 0,
                "status": "unsubmitted",
                "submissionID": -1
            }
        else:
            current_submit = db.session.query(Submission.id, Submission.score, Submission.status).filter(
                expr.and_(
                    Submission.uid == session.get("uid"),
                    Submission.problem_id == problem_id
                )).order_by(Submission.score.desc()).limit(1).one_or_none()
            if not current_submit:
                problem["userResult"] = {
                    "score": 0,
                    "status": "unsubmitted",
                    "submissionID": -1
                }
            else:
                problem["userResult"] = {
                    "score": current_submit.score,
                    "status": current_submit.status,
                    "submissionID": current_submit.id
                }
        result["problems"].append(problem)
    return make_response(0, data=result)
