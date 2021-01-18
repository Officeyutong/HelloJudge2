from models.user import User
from main import db, web_app, permission_manager, config
from models.problem_todo import ProblemTodo
from models.problem import Problem
from models.submission import Submission
from models.contest import Contest
from models.virtual_contest import VirtualContest
from utils import encode_json, make_response
from flask import Blueprint, request, session
from common.utils import unpack_argument
from common.permission import require_permission
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
import math
import typing
import time
import datetime
router = Blueprint("virtualcontest", __name__)


@router.route("/create", methods=["POST"])
@unpack_argument
@require_permission(manager=permission_manager, permission="virtualcontest.use")
def virtualcotest_create(contestID: int, startAt: int):
    """
    创建虚拟比赛,返回比赛ID
    {
        "id":虚拟比赛ID
    }

    """
    contest: Contest = db.session.query(
        Contest.id,
        Contest.private_contest,
        Contest.start_time,
        Contest.end_time,
        Contest.closed,
        Contest.owner_id
    ).filter_by(id=contestID).one_or_none()
    user: User = db.session.query(User.id).filter_by(
        id=session.get("uid", -1)).one_or_none()
    if not contest:
        return make_response(-1, message="比赛ID不存在")
    if not user:
        return make_response(-1, message="请先登录")
    if not contest.closed:
        return make_response(-1, message="此比赛尚未关闭")
    if user.id != contest.owner_id and contest.private_contest and not permission_manager.has_permission(user.id, f"contest.use.{contest.id}"):
        return make_response(-1, message="你没有权限使用该比赛")
    if time.time() >= startAt:
        return make_response(-1, message="开始时间不得早于当前时间")
    start_time = datetime.datetime.fromtimestamp(startAt)
    virtual = VirtualContest(
        owner_id=user.id,
        contest_id=contest.id,
        start_time=start_time,
        end_time=contest.end_time-contest.start_time+start_time
    )
    db.session.add(virtual)
    db.session.commit()
    return make_response(0, data={
        "id": virtual.id
    })


@router.route("/list", methods=["POST"])
@unpack_argument
@require_permission(manager=permission_manager, permission="virtualcontest.use")
def virtualcotest_all(page: int = 1):
    """
    列出该用户的所有虚拟比赛
    {
        "contest":{
            "id":"对应的比赛ID",
            "name":"对应的比赛名"
        },
        "startTime":"开始时间(时间戳)",
        "endTime":"结束时间(时间戳)",
        "id":"虚拟比赛ID"
    },
    pageCount:"页数"
    """
    user: User = db.session.query(User.id).filter_by(
        id=session.get("uid", -1)).one_or_none()
    if not user:
        return make_response(-1, message="请先登录")
    query = db.session.query(
        VirtualContest.id,
        VirtualContest.contest_id,
        VirtualContest.end_time,
        VirtualContest.start_time,
        Contest.name
    ).join(Contest, Contest.id == VirtualContest.contest_id).filter(VirtualContest.owner_id == user.id)
    page_count = int(math.ceil(query.count()/config.VIRTUAL_CONTESTS_PER_PAGE))
    data = query.slice((page-1)*config.VIRTUAL_CONTESTS_PER_PAGE,
                       page*config.VIRTUAL_CONTESTS_PER_PAGE).all()
    return make_response(0, pageCount=page_count, data=[
        {
            "contest": {
                "id": item.contest_id,
                "name": item.name
            },
            "startTime": item.start_time.timestamp(),
            "endTime": item.end_time.timestamp(),
            "id": item.id
        } for item in data
    ])
