from sqlalchemy.sql.functions import user
from models.challenge import ChallengeRecord
from models.submission import Submission
import typing

from main import db, config, permission_manager
from main import web_app as app
from common.permission import require_permission
from common.utils import unpack_argument
from flask_sqlalchemy import BaseQuery
from flask import session
from utils import make_response
from models import User, Problem, ProblemSet, Challenge
import sqlalchemy.sql.expression as expr
from sqlalchemy.sql import func


@app.route("/api/challenge/list", methods=["POST"])
def api_get_challenge_list():
    """
    获取挑战列表
    "managable":"是否可管理"
    [
        {
            "id":挑战ID,
            "name":挑战名,
            "description":描述,
            "problemsetList":"习题集列表",
            "accessible":"是否有权访问",
            "level":"挑战等级",
            "hasFinished":"是否完成"
        }
    ]
    """
    challenges: typing.Iterable[Challenge] = db.session.query(
        Challenge).order_by(Challenge.level.asc()).all()
    result = []
    for item in challenges:
        result.append({
            "id": item.id,
            "name": item.name,
            "description": item.description or "",
            "problemsetList": item.problemset_list,
            "accessible": permission_manager.has_permission(session.get("uid", None), f"challenge.access.{item.id}"),
            "hasFinished": permission_manager.has_permission(session.get("uid", None), f"challenge.finish.{item.id}.all"),
            "level": item.level,
        })
    return make_response(0, data=result, managable=permission_manager.has_permission(session.get("uid"), "challenge.manage"))


@app.route("/api/challenge/unlock", methods=["POST"])
@require_permission(manager=permission_manager, permission="challenge.use")
@unpack_argument
def api_unlock_challenge(id: int):
    """
    尝试解锁一个挑战
    id:挑战ID
    """
    current_challenge: Challenge = db.session.query(
        Challenge).filter(Challenge.id == id).one_or_none()
    if not current_challenge:
        return make_response(-1, message="挑战不存在")
    lower_challenges: typing.Iterable[Challenge] = db.session.query(
        Challenge.id).filter(Challenge.level < current_challenge.level).all()
    for item in lower_challenges:
        if not permission_manager.has_permission(session.get("uid"), f"challenge.finish.{item.id}.all"):
            print(f"{item.id=} not finished yet")
            return make_response(-1, message=f"你还有至少一个等级低于当前挑战的挑战尚未完成")
    from main import user_operation
    uid = user_operation.ensure_login()
    if db.session.query(db.session.query(ChallengeRecord).filter_by(uid=uid, challenge_id=id).exists()).one()[0]:
        return make_response(-1, message="你已解锁此挑战!")
    db.session.add_all([
        ChallengeRecord(uid=uid, challenge_id=id, problemset_id=item, finished=False) for item in current_challenge.problemset_list
    ])
    db.session.commit()
    permission_manager.refresh_user(uid)
    # permission_manager.add_permission(session.get(
    #     "uid"), f"[provider:challenge-access.{current_challenge.id}]")
    # for problemset in current_challenge.problemset_list:
    #     permission_manager.add_permission(
    #         session.get("uid"), f"problemset.use.{problemset}")
    return make_response(0, message="操作完成")


@app.route("/api/challenge/finish_problemset", methods=["POST"])
@require_permission(manager=permission_manager, permission="challenge.use")
@unpack_argument
def api_finish_problemset(challengeID: int, problemsetID: int):
    """
    申请完成一个挑战下的某个习题集
    challengeID 挑战ID
    problemsetID 习题集ID
    """

    if not permission_manager.has_permission(session.get("uid"), f"challenge.access.{challengeID}"):
        return make_response(-1, message="你没有权限访问该挑战")
    challenge: Challenge = db.session.query(Challenge.problemset_list).filter(
        Challenge.id == challengeID).one_or_none()
    if not challenge:
        return make_response(-1, message="该挑战不存在")
    if problemsetID not in challenge.problemset_list:
        return make_response(-1, message="该习题集ID不在该挑战之下")
    problemset: ProblemSet = db.session.query(
        ProblemSet.problems).filter(ProblemSet.id == problemsetID).one()
    for problem in problemset.problems:
        submission = db.session.query(Submission.id).filter(expr.and_(
            Submission.uid == session.get("uid"),
            Submission.problem_id == problem,
            Submission.status == "accepted"
        )).one_or_none()
        if not submission:
            return make_response(-1, message="在该习题集之下，你尚存题目未完成.")
    # permission_manager.add_permission(session.get(
    #     "uid"), f"challenge.finish.{challengeID}.{problemsetID}")
    from main import user_operation
    uid = user_operation.ensure_login()
    record: ChallengeRecord = db.session.query(ChallengeRecord).filter_by(
        uid=uid, challenge_id=challengeID, problemset_id=problemsetID).one()
    record.finished = True
    db.session.commit()
    permission_manager.refresh_user(uid)
    return make_response(0, message="操作完成")


# @app.route("/api/challenge/finish_challenge", methods=["POST"])
# @require_permission(manager=permission_manager, permission="challenge.use")
# @unpack_argument
# def api_finish_challenge(challengeID: int):
#     """
#     申请完成一个挑战
#     challengeID 挑战ID
#     """

#     if not permission_manager.has_permission(session.get("uid"), f"challenge.access.{challengeID}"):
#         return make_response(-1, message="你没有权限访问该挑战")
#     challenge: Challenge = db.session.query(Challenge.problemset_list).filter(
#         Challenge.id == challengeID).one_or_none()
#     if not challenge:
#         return make_response(-1, message="该挑战不存在")
#     for problemset in challenge.problemset_list:
#         if not permission_manager.has_permission(session.get("uid"), f"challenge.finish.{challengeID}.{problemset}"):
#             return make_response(-1, message="该挑战之下存在未完成的习题集")
#     permission_manager.add_permission(session.get(
#         "uid"), f"challenge.finish.{challengeID}.all")
#     return make_response(0, message="操作完成")


@app.route("/api/challenge/detail_raw", methods=["POST"])
@require_permission(manager=permission_manager, permission="challenge.manage")
@unpack_argument
def api_get_challenge_detail_raw(id: int):
    """
    获取挑战原始数据
    {
        "id":"ID",
        "name":"名称",
        "level":"等级",
        "description":"描述",
        "problemsetList":"习题集列表"
    }
    """
    challenge = db.session.query(Challenge).filter(
        Challenge.id == id).one_or_none()
    if not challenge:
        return make_response(-1, message="挑战不存在")
    return make_response(0, data={
        "id": challenge.id,
        "name": challenge.name,
        "level": challenge.level,
        "description": challenge.description or "",
        "problemsetList": challenge.problemset_list
    })


@app.route("/api/challenge/update", methods=["POST"])
@require_permission(manager=permission_manager, permission="challenge.manage")
@unpack_argument
def api_get_challenge_update(id: int, name: str, level: int, description: str, problemsetList: typing.List[int]):
    """
    更新挑战数据
    {
        "id":"ID",
        "name":"名称",
        "level":"等级",
        "description":"描述",
        "problemsetList":"习题集列表"
    }
    """
    challenge: Challenge = db.session.query(Challenge).filter(
        Challenge.id == id).one_or_none()
    if not challenge:
        return make_response(-1, message="挑战不存在")
    challenge.name = name
    challenge.level = level
    challenge.description = description
    challenge.problemset_list = problemsetList
    db.session.commit()
    return make_response(0, message="操作完成")


@app.route("/api/challenge/remove", methods=["POST"])
@require_permission(manager=permission_manager, permission="challenge.manage")
@unpack_argument
def api_get_challenge_remove(id: int):
    """
    删除挑战

    """
    challenge: Challenge = db.session.query(Challenge).filter(
        Challenge.id == id).one_or_none()
    if not challenge:
        return make_response(-1, message="挑战不存在")
    db.session.delete(challenge)
    db.session.commit()
    return make_response(0, message="操作完成")


@app.route("/api/challenge/create", methods=["POST"])
@require_permission(manager=permission_manager, permission="challenge.manage")
@unpack_argument
def api_get_challenge_create():
    """
    创建新挑战，返回挑战id

    """
    max_level = db.session.query(func.max(Challenge.level)).one_or_none()[0]
    challenge = Challenge(
        level=(1 if not max_level else max_level+1)
    )
    db.session.add(challenge)
    db.session.commit()
    return make_response(0, id=challenge.id)


@app.route("/api/challenge/detail", methods=["POST"])
@require_permission(manager=permission_manager, permission="challenge.use")
@unpack_argument
def api_get_challenge_detail(challengeID: int):
    """
    查询挑战详情
    {
        "name":"名称",
        "id":ID,
        "description":描述,
        "level":等级,
        "hasFinished":是否完成,
        "accessible":"是否可访问",
        "problemsetList":[
            {
                "name":"名称",
                "hasFinished":"是否完成",
                "id":"ID"
            }
        ]
    }

    """

    if not permission_manager.has_permission(session.get("uid"), f"challenge.access.{challengeID}"):
        return make_response(-1, message="你没有权限访问该挑战")
    challenge: Challenge = db.session.query(Challenge).filter(
        Challenge.id == challengeID).one_or_none()
    if not challenge:
        return make_response(-1, message="该挑战不存在")
    result = {
        "name": challenge.name,
        "id": challenge.id,
        "description": challenge.description or "",
        "hasFinished": permission_manager.has_permission(session.get("uid"), f"challenge.finish.{challengeID}.all"),
        "level": challenge.level,
        "problemsetList": [],
        "accessible": permission_manager.has_permission(session.get("uid", None), f"challenge.access.{challengeID}"),
    }
    for problemset in challenge.problemset_list:
        current = db.session.query(ProblemSet.id, ProblemSet.name).filter(
            ProblemSet.id == problemset).one()
        result["problemsetList"].append({
            "name": current.name,
            "id": current.id,
            "hasFinished": permission_manager.has_permission(session.get("uid"), f"challenge.finish.{challengeID}.{problemset}")
        })
    return make_response(0, data=result)
