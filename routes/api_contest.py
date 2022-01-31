import typing

from config_default.display import CLARIFICATION_PER_PAGE
from main import web_app as app, permission_manager
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory, Blueprint
from utils import *
from models import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename
import datetime
import math
import re
from typing import Iterable
from main import permission_manager
from common.utils import make_json_response, unpack_argument, get_uid
from common.permission import require_permission
import sqlalchemy.sql.expression as expr
from sqlalchemy import distinct, alias
import datetime
import json
import redis_lock
router = Blueprint("contest", __name__)


# TODO: 虚拟比赛的提交信息，虚拟比赛时的提交返回遵从于比赛的实际设定。
@router.route("/clarification/detail", methods=["POST"])
@unpack_argument
def contest_clarification_detail(clarification_id: int):
    """
    查询Clarification详情
    {
            "sender":{
                "uid":"发送者ID",
                "username":"发送者用户名",
                "email":"xxx"
            },
            "send_time":"发送时间",
            "content":"内容",
            "replied":"是否已回复",
            "replier":{
                "uid":"回复者ID",
                "username":"回复者用户名",
                "email":"xxx"
            },
            reply_time:"回复时间",
            "reply_content":"回复内容"
    }
    """
    clar: Clarification = db.session.query(
        Clarification.sender,
        Clarification.send_time,
        Clarification.content,
        Clarification.contest,
        Clarification.replied,
        Clarification.replier,
        Clarification.reply_content,
        Clarification.reply_time,
        User.username,
        User.email).join(User, User.id == Clarification.sender).filter(Clarification.id == clarification_id).one_or_none()
    if not clar:
        return make_response(-1, message="提问不存在")
    contest_inst: Contest = db.session.query(
        Contest.id, Contest.owner_id
    ).filter_by(id=clar.contest).one_or_none()
    has_permission = (
        session.get("uid", -1) == contest_inst.owner_id or permission_manager.has_permission(session.get("uid"), "contest.manage"))
    if not has_permission:
        return make_response(-1, message="你没有权限进行此操作")
    current = {
        "sender": {
            "uid": clar.sender,
            "username": clar.username,
            "email": clar.email
        },
        "send_time": str(clar.send_time),
        "content": clar.content,
        "replied": bool(clar.replied),
        "replier": {
            "uid": clar.replier,
            "username": None,
            "email": None
        },
        "reply_time": str(clar.reply_time),
        "reply_content": clar.reply_content
    }
    if clar.replied:
        replier = db.session.query(
            User.username, User.email).filter_by(id=clar.replier).one()
        current["replier"] = {
            "uid": clar.replier,
            "username": replier.username,
            "email": replier.email
        }
    return make_response(0, data=current)


@router.route("/clarification/reply", methods=["POST"])
@unpack_argument
def contest_clarification_reply(clarification_id: int, content: str):
    """
    回复Clarification
    """
    clar: Clarification = db.session.query(
        Clarification).filter_by(id=clarification_id).one_or_none()
    if not clar:
        return make_response(-1, message="提问不存在")
    contest_inst: Contest = db.session.query(
        Contest
    ).filter_by(id=clar.contest).one_or_none()
    has_permission = (
        session.get("uid", -1) == contest_inst.owner_id or permission_manager.has_permission(session.get("uid"), "contest.manage"))
    if not has_permission:
        return make_response(-1, message="你没有权限进行此操作")

    clar.replied = True
    clar.replier = session.get("uid")
    clar.reply_content = content
    clar.reply_time = datetime.datetime.now()
    db.session.commit()
    return make_response(0, message="操作完成")

@router.route("/clarification/remove", methods=["POST"])
@unpack_argument
def contest_clarification_remove(clarification_id: int):
    """
    删除Clarification
    """
    clar: Clarification = db.session.query(
        Clarification).filter_by(id=clarification_id).one_or_none()
    if not clar:
        return make_response(-1, message="提问不存在")
    contest_inst: Contest = db.session.query(
        Contest
    ).filter_by(id=clar.contest).one_or_none()
    has_permission = (
        session.get("uid", -1) == contest_inst.owner_id or permission_manager.has_permission(session.get("uid"), "contest.manage"))
    if not has_permission:
        return make_response(-1, message="你没有权限进行此操作")
    db.session.delete(clar)
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/clarification/send", methods=["POST"])
@unpack_argument
def contest_clarification_send(contest: int, content: str):
    """
    发送Clarification
    {

    }
    """
    contest_inst: Contest = db.session.query(
        Contest
    ).filter_by(id=contest).one_or_none()
    has_permission = (
        permission_manager.has_permission(session.get(
            "uid", None), f"contest.use.{contest_inst.id}")
        or session.get("uid", -1) == contest_inst.owner_id
        or (not contest_inst.private_contest))
    if not has_permission:
        return make_response(-1, message="你没有权限执行此操作")
    if not contest_inst.running():
        return make_response(-1, message="比赛未在运行")
    if not session.get("uid", None):
        return make_response(-1, message="请登录")
    db.session.add(Clarification(
        contest=contest_inst.id,
        sender=session.get("uid"),
        content=content
    ))
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/clarification/all", methods=["POST"])
@unpack_argument
def contest_clarification_all(contest: int, page: int = 1):
    """
    获取clarification列表
    {
        "pageCount":页数,
        "data":[
            {
                "id":"ID",
                "sender":{
                    "uid":"发送者ID",
                    "username":"发送者用户名"
                },
                "send_time":"发送时间",
                "content":"内容",
                "replied":"是否已回复",
                "replier":{
                    "uid":"回复者ID",
                    "username":"回复者用户名"
                },
                reply_time:"回复时间",
                "reply_content":"回复内容"
            }
        ]
    }
    """
    contest_inst: Contest = db.session.query(
        Contest.id,
        Contest.owner_id,
        Contest.private_contest
    ).filter_by(id=contest).one_or_none()
    has_permission = (
        permission_manager.has_permission(session.get(
            "uid", None), f"contest.use.{contest_inst.id}")
        or session.get("uid", -1) == contest_inst.owner_id
        or (not contest_inst.private_contest))
    if not has_permission:
        return make_response(-1, message="你没有权限执行此操作")
    query = db.session.query(
        Clarification.sender,
        Clarification.send_time,
        Clarification.content,
        Clarification.replied,
        Clarification.replier,
        Clarification.reply_content,
        Clarification.reply_time,
        Clarification.id,
        User.username,
        User.email
    ).filter(Clarification.contest == contest).join(User, User.id == Clarification.sender).order_by(Clarification.send_time.desc())
    total_count = int(math.ceil(query.count()/config.CLARIFICATION_PER_PAGE))
    items = query.slice((page-1)*config.CLARIFICATION_PER_PAGE,
                        page*config.CLARIFICATION_PER_PAGE).all()
    result = []
    for item in items:
        item: Clarification
        current = {
            "id": item.id,
            "sender": {
                "uid": item.sender,
                "username": item.username,
                "email": item.email
            },
            "send_time": str(item.send_time),
            "content": item.content,
            "replied": bool(item.replied),
            "replier": {
                "uid": item.replier,
                "username": None,
                "email": None
            },
            "reply_time": str(item.reply_time),
            "reply_content": item.reply_content
        }
        result.append(current)
        if item.replied:
            replier = db.session.query(
                User.username, User.email).filter_by(id=item.replier).one()
            current["replier"] = {
                "uid": item.replier,
                "username": replier.username,
                "email": replier.email
            }
    return make_response(0, data=result, pageCount=total_count)


@ app.route("/api/contest/close", methods=["POST"])
@ unpack_argument
def api_contest_close(contestID: int):
    """
    关闭比赛
    比赛关闭后即不可再更改设置或者提交等
    比赛关闭后可以被其他用户用以VirtualParticipate
    """
    contest: Contest = db.session.query(
        Contest).filter_by(id=contestID).one_or_none()
    if not contest:
        return make_response(-1, message="比赛不存在")
    if not session.get("uid", -1) == contest.owner_id and not permission_manager.has_permission(session.get("uid", None), "contest.manage"):
        return make_response(-1, message="你没有权限执行此操作")
    if contest.running():
        return make_response(-1, message="此比赛正在进行")
    contest.closed = True
    db.session.commit()
    return make_response(0, message="操作完成")


@ app.route("/api/contest/unlock", methods=["POST"])
@ unpack_argument
def api_contest_unlock(contestID: int, inviteCode: str):
    """
    使用邀请码申请某比赛的权限
    """
    contest: Contest = db.session.query(Contest.private_contest, Contest.invite_code, Contest.id).filter_by(
        id=contestID).one_or_none()
    if not contest:
        return make_response(-1, message="此比赛不存在")
    if inviteCode != contest.invite_code:
        return make_response(-1, message="邀请码错误")
    if not session.get("uid", None):
        return make_response(-1, message="请登录")
    permission_manager.add_permission(
        session.get("uid"), f"contest.use.{contest.id}")
    return make_response(0, message="操作完成")


@ app.route("/api/contest/remove", methods=["POST"])
@ unpack_argument
def remove_contest(contestID: int):
    """
    参数:
    {
        "contestID":"比赛ID"
    }
    {
        "code":0,
        "message":"",
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    contest: Contest = Contest.by_id(contestID)
    if not permission_manager.has_permission(user.id, "admin") and user.id != contest.owner_id:
        return make_response(-1, message="只有管理员或比赛创建者才可进行此操作")
    db.session.query(Submission).filter(
        Submission.contest_id == contest.id).delete()
    db.session.query(Contest).filter(Contest.id == contest.id).delete()
    db.session.commit()
    return make_response(0, message="成功")


@ app.route("/api/contest/create", methods=["POST"])
@ require_permission(manager=permission_manager, permission="contest.create")
def create_contest():
    """
    参数:
    {
        ""
    }
    {
        "code":0,
        "message":"",
        "contest_id":1
    """

    import datetime
    contest = Contest(owner_id=session.get("uid"),
                      start_time=datetime.datetime.now(),
                      end_time=datetime.datetime.now()+datetime.timedelta(hours=3)
                      )
    db.session.add(contest)
    db.session.commit()
    permission_manager.add_permission(
        session.get("uid"), f"contest.use.{contest.id}")
    return make_response(0, contest_id=contest.id)


@ app.route("/api/contest/list", methods=["POST"])
@ unpack_argument
def contest_list(page: int = 1, order_by: typing.Union[typing.Literal["id"], typing.Literal["start_time"]] = "start_time"):
    """
    {
        "page":"切换到的页面",
        "order_by":"id"|"start_time"
    }
    {
        "code":0,
        "data":{
            "page_count":"页面总数",
            "list":[
                {
                    "id":"比赛ID",
                    "name":"比赛名",
                    "owner_id":"所有者用户ID",
                    "owner_username":"所有者用户名",
                    "start_time":"开始秒数",
                    "end_time":"结束秒数",
                    "privateContest":"该比赛是否私有",
                    "hasPermission":"是否有权限访问该比赛"
                }
            ]
        }
    }
    """
    subquery = db.session.query(
        Submission.contest_id).filter(expr.and_(
            Submission.contest_id != -1,
            Submission.uid == session.get("uid", -1)
        )).distinct()
    result = db.session.query(Contest)
    if order_by == "id":
        result = result.order_by(Contest.id.desc())
    elif order_by == "start_time":
        result = result.order_by(Contest.start_time.desc())
    else:
        return make_json_response(-1, message="非法排序方式")
    last_team: Team = db.session.query(Team.team_contests, TeamMember.team_id, Team.id, TeamMember.uid).join(Team, Team.id == TeamMember.team_id).filter(
        TeamMember.uid == get_uid()).order_by(TeamMember.team_id.desc()).limit(1).one_or_none()
    # print(last_team)
    team_contests = []
    if last_team:
        team_contests = last_team.team_contests
    if not permission_manager.has_permission(session.get("uid", None), "contest.manage"):
        result = result.filter(expr.or_(
            Contest.owner_id == session.get("uid", -1),
            Contest.private_contest == False,
            Contest.id.in_(subquery),
            Contest.id.in_(team_contests)
        ))
    count = result.count()
    import math
    result: Iterable[Contest] = result.slice(
        (page-1)*config.CONTESTS_PER_PAGE, (page)*config.CONTESTS_PER_PAGE).all()
    ret = {"page_count": int(math.ceil(count/config.CONTESTS_PER_PAGE)), "list": [

    ]}
    import time
    for contest in result:
        user: User = User.by_id(contest.owner_id)
        ret["list"].append({
            "id": contest.id,
            "name": contest.name,
            "owner_id": user.id,
            "owner_username": user.username,
            "start_time": int(time.mktime(contest.start_time.timetuple())),
            "end_time": int(time.mktime(contest.end_time.timetuple())),
            "privateContest": bool(contest.private_contest),
            "hasPermission": permission_manager.has_permission(session.get("uid", None), f"contest.use.{contest.id}")

        })
    return make_response(0, data=ret)


@ app.route("/api/contest/show", methods=["POST"])
@ unpack_argument
def show_contest(contestID: int, virtualID: int = -1):
    """
    参数:
    {
        "contestID",
        virtualID:虚拟比赛ID，如果不存在则为-1
    }
    {
        "code":0,
        "message":"",
        "data":{
            "managable":"是否具有管理权限",
            "name":"比赛名",
            "description":"说明",
            "id":"比赛ID",
            "owner_id":"所有者ID",
            "owner_username":"所有者用户名",
            "start_time":"开始时间(timestampm,s)",
            "end_time":"结束时间",
            "ranklist_visible":false,
            "judge_result_visible":false,
            "rank_criterion":"",
            "private_contest":"是否为私有比赛",
            "problems":[
                {
                    "weight":"题目权值,
                    "title":"题目标题",
                    "id":"题目ID(比赛中的)"
                    "total_submit":"总提交数",//-1表示不可见
                    "accepted_submit":"通过提交数",//-1表示不可见
                    "my_submit":"我的提交最高分提交",
                    "status":"我的状态",
                    "rawID":"原始ID"
                }
            ],
            "accessible":"是否有权访问",
            "closed":"是否关闭",
            "virtual":"是否虚拟"
        }
    }
    """
    import time
    contest: Contest = Contest.by_id(contestID)
    if not contest:
        return make_response(-1, message="比赛ID不存在！")
    virtual_contest: VirtualContest = db.session.query(
        VirtualContest
    ).filter_by(id=virtualID).one_or_none()
    virtualID = int(virtualID)
    using_virtual = (virtualID != -1)

    can_see_ranklist = contest.can_see_ranklist(
        session.get("uid"), permission_manager)
    if using_virtual:
        can_see_judge_result = (contest.judge_result_visible) or (
            not virtual_contest.running())
        if not contest.ranklist_visible and virtual_contest.running() and not permission_manager.has_permission(session.get("uid"), "contest.manage"):
            can_see_ranklist = False
    else:
        can_see_judge_result = contest.can_see_judge_result(
            session.get("uid"), permission_manager)
    has_login = bool(session.get("uid"))
    if has_login:
        user: User = User.by_id(session.get("uid"))
    if not contest:
        return make_response(-1, message="未知比赛ID")
    has_permission = permission_manager.has_permission(
        session.get("uid", None), f"contest.use.{contest.id}") or session.get("uid", -1) == contest.owner_id or (not contest.private_contest)
    owner: User = User.by_id(contest.owner_id)
    if using_virtual:
        if not virtual_contest:
            return make_response(-1, message="虚拟比赛不存在")
        if virtual_contest.contest_id != contest.id:
            return make_response(-1, message="该虚拟比赛不对应于此比赛")
        if virtual_contest.owner_id != session.get('uid', -1):
            return make_response(-1, message="这场虚拟比赛不是由你主办的")
    if has_permission:
        result = {
            "id": contest.id,
            "name": contest.name,
            "description": contest.description,
            "owner_id": owner.id,
            "owner_username": owner.username,
            "start_time": virtual_contest.start_time.timestamp() if using_virtual else int(time.mktime(contest.start_time.timetuple())),
            "end_time": virtual_contest.end_time.timestamp() if using_virtual else int(time.mktime(contest.end_time.timetuple())),
            "problems": [],
            "ranklist_visible": bool(contest.ranklist_visible),
            "judge_result_visible": bool(contest.judge_result_visible),
            "rank_criterion": contest.rank_criterion,
            "private_contest": bool(contest.private_contest),
            # "invite_code": contest.invite_code,
            "managable": permission_manager.has_permission(session.get("uid", None), "contest.manage") or contest.owner_id == session.get("uid", -1),
            "hasPermission": has_permission,
            "closed": bool(contest.closed),
            "virtual": using_virtual
        }
        problem_raw_ids = [item["id"] for item in contest.problems] + [-1]
        problems = result["problems"]
        for (i, problem), problem_data in zip(
            enumerate(
                db.session.query(Problem).filter(
                    Problem.id.in_(problem_raw_ids)
                ).order_by(func.field(Problem.id, *problem_raw_ids))
            ),
                contest.problems):
            # print(problem)
            # problem: Problem = Problem.by_id(problem_data["id"])
            current = {
                "title": problem.title,
                "id": i,
                "total_submit": -1,
                "accepted_submit": -1,
                "my_submit": -1,
                "status": "unsubmitted",
                "weight": problem_data["weight"],
                "rawID": problem_data["id"]
            }
            if can_see_ranklist:
                submit_query = db.session.query(Submission).filter(
                    Submission.contest_id == contest.id).filter(Submission.problem_id == problem.id)
                if using_virtual:
                    submit_query = submit_query.filter(
                        Submission.virtual_contest_id == virtual_contest.id)
                current["total_submit"] = submit_query.count()
                current["accepted_submit"] = submit_query.filter(
                    Submission.status == "accepted").count()
            if has_login:
                my_best_submit: Submission = db.session.query(Submission.id, Submission.status).filter(
                    Submission.contest_id == contest.id).filter(and_(Submission.uid == user.id, Submission.problem_id == problem.id))
                if using_virtual:
                    my_best_submit = my_best_submit.filter(
                        Submission.virtual_contest_id == virtual_contest.id)
                if contest.rank_criterion != "last_submit":
                    my_best_submit = my_best_submit.order_by(
                        Submission.status.asc()).first()
                else:
                    my_best_submit = my_best_submit.order_by(
                        Submission.id.desc()).first()
                if my_best_submit:
                    current["my_submit"] = my_best_submit.id
                    current["status"] = my_best_submit.status
                    if not can_see_judge_result:
                        current["status"] = "invisible"
            problems.append(current)
    else:
        result = {
            "id": contest.id,
            "name": contest.name,
            "hasPermission": has_permission
        }

    return make_response(0, data=result)


@app.route("/api/contest/raw_data", methods=["POST"])
@unpack_argument
def contest_raw_data(contestID):
    """
    contestID
    {
        "id": contest.id,
        "name": contest.name,
        "description": contest.description,
        "start_time": int(time.mktime(contest.start_time.timetuple())),
        "end_time": int(time.mktime(contest.end_time.timetuple())),
        "problems": contest.problems,
        "ranklist_visible": contest.ranklist_visible,
        "judge_result_visible": contest.judge_result_visible,
        "rank_criterion": contest.rank_criterion,
        "private_contest": contest.private,
        "invite_code":"邀请码",
        "closed":true
    }
    """
    if not session.get("uid"):
        return "你没有权限这样做", 403

    user: User = User.by_id(session.get("uid"))
    contest: Contest = Contest.by_id(contestID)
    # if contest.closed:
    #     return "此比赛已关闭", 403
    if contest.private_contest and not permission_manager.has_permission(session.get("uid", -1), f"contest.use.{contest.id}"):
        return "你没有权限查看该比赛", 403
    if not permission_manager.has_permission(user.id, "contest.manage") and user.id != contest.owner_id:
        return "你没有权限这样做", 403
    import time
    result = {
        "id": contest.id,
        "name": contest.name,
        "description": contest.description,
        "start_time": int(time.mktime(contest.start_time.timetuple())),
        "end_time": int(time.mktime(contest.end_time.timetuple())),
        "problems": contest.problems,
        "ranklist_visible": bool(contest.ranklist_visible),
        "judge_result_visible": bool(contest.judge_result_visible),
        "rank_criterion": contest.rank_criterion,
        "private_contest": bool(contest.private_contest),
        "invite_code": contest.invite_code,
        "closed": bool(contest.closed)
    }
    return make_response(0, data=result)


@app.route("/api/contest/update", methods=["POST"])
@unpack_argument
def contest_update(contestID: int, data: dict):
    """
    更新比赛信息
    {
        contestID:比赛ID,
        data:数据字典
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    contest: Contest = Contest.by_id(contestID)
    if contest.closed:
        import datetime

        if (
            contest.name != data["name"] or
            contest.start_time != datetime.datetime.fromtimestamp(data["start_time"]) or
            contest.end_time != datetime.datetime.fromtimestamp(data["end_time"]) or
            contest.problems != data["problems"] or
            contest.ranklist_visible != data["ranklist_visible"] or
            contest.judge_result_visible != data["judge_result_visible"] or
            contest.rank_criterion != data["rank_criterion"]
        ):
            return make_response(-1, message="关闭后的比赛只能修改描述、是否公开和邀请码")
    if not permission_manager.has_permission(user.id, "contest.manage") and user.id != contest.owner_id:
        return make_response(-1, message="你没有权限这么做")
    # 修改比赛的人必须能够访问其所设定的题目
    for problem_obj in data["problems"]:
        problem_id = problem_obj["id"]
        problem = db.session.query(
            Problem.id, Problem.public, Problem.uploader_id).filter_by(id=problem_id).one_or_none()
        if not problem:
            return make_response(-1, message=f"比赛题目{problem_id}不存在")
        if user.id != problem.uploader_id:
            if not problem.public and not permission_manager.has_permission(user.id, f"problem.use.{problem.id}"):
                return make_response(-1, message=f"你没有权限访问题目{problem_id}")

    contest.name = data["name"]
    contest.description = data["description"]
    contest.start_time = data["start_time"]
    contest.end_time = data["end_time"]
    contest.problems = data["problems"]
    contest.ranklist_visible = data["ranklist_visible"]
    if (data["ranklist_visible"] or data["judge_result_visible"]) and config.DISABLE_IOI_CONTEST:
        return make_json_response(-1, message="当前暂时禁止比赛设置为赛时公开排行榜或提交结果")
    contest.judge_result_visible = data["judge_result_visible"]
    contest.rank_criterion = data["rank_criterion"]
    if contest.private_contest and not data["private_contest"]:
        # 没有权限的人只能搞私有比萨
        if not permission_manager.has_permission(session.get("uid"), "contest.manage"):
            return make_response(-1, message="你没有权限公开比赛")
    contest.private_contest = data["private_contest"]
    contest.invite_code = data["invite_code"]

    def from_second_to_datetime(seconds):
        import time
        import datetime
        time_struct = time.localtime(seconds)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        # print(time_str)
        return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    contest.start_time = from_second_to_datetime(data["start_time"])
    contest.end_time = from_second_to_datetime(data["end_time"])
    if contest.end_time < contest.start_time:
        return make_response(-1, message="开始时间必须早于结束时间")
    # print(contest.start_time, contest.end_time)
    db.session.commit()
    import redis
    import main
    redis.Redis(connection_pool=main.redis_connection_pool).delete(
        f"hj2-contest-ranklist-{contest.id}")
    return make_response(0, message="完成")


@app.route("/api/contest/<int:contest_id>/<int:problem_id>/download_file/<string:file>")
def contest_download_file(contest_id, problem_id, file):
    """
    下载比赛中的题目文件
    """
    import flask
    if not session.get("uid"):
        return flask.abort(403)
    contest: Contest = Contest.by_id(contest_id)
    if contest.private_contest and not permission_manager.has_permission(session.get("uid", -1), f"contest.use.{contest.id}"):
        return "你没有权限查看该比赛", 403
    problem: Problem = Problem.by_id(contest.problems[int(problem_id)]["id"])
    if file not in problem.downloads:
        return flask.abort(404)
    import os
    to_send = os.path.join(
        basedir, f"{config.UPLOAD_DIR}/{problem.id}/{file}")
    if not os.path.exists(to_send) or not os.path.isfile(to_send):
        return flask.abort(404)
    return flask.send_file(to_send, as_attachment=True)


@app.route("/api/contest/problem/show", methods=["POST"])
@unpack_argument
def contest_show_problem(problemID: int, contestID: int, virtualID: int = -1):
    """
    获取比赛题目信息
    参数:
        problemID:int 题目ID(比赛中的)
        contestID:int 比赛ID
        virtualID:int 虚拟比赛ID
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq",//code非0的时候表示错误信息
            "data":{
                "title":"qwq",//题目名
                "backcground":"qwq",//题目背景
                "content":"题目内容",
                "input_format":"输入格式",
                "output_format":"输出格式",
                "hint":"数据范围与提示",
                "example":"样例,形如[{'input':'xxx','output':'xxx'}]",
                "files":["a.in","a.out"],//不包括具体的二进制数据！
                "subtasks":[
                         {"name": "Subtask1", "score": 40, "method": "min", "files": [], "time_limit":1000, "memory_limit":512}].
                "last_code":"qwq",//上一次提交的代码,
                "last_lang":"qwq",//上一次选择的语言ID
                "score":题目总分,
                "extra_parameter":[],
                "id":"ID",
                "virtual":"是否为虚拟比赛",
                "downloads":"可供下载文件",
                "using_file_io":"是否使用文件IO",
                "input_file_name":"输入文件名",
                "output_file_name":"输出文件名"
            }
        }
    """
    virtualID = int(virtualID)
    using_virtual = (virtualID != -1)
    contest: Contest = Contest.by_id(contestID)
    virtual_contest: VirtualContest = db.session.query(
        VirtualContest).filter_by(id=virtualID).one_or_none()
    if using_virtual:
        if not virtual_contest:
            return make_response(-1, message="虚拟比赛不存在")
        if virtual_contest.contest_id != contest.id:
            return make_response(-1, message="此虚拟比赛不对应于此实际比赛")
        if not virtual_contest.running():
            return make_response(-1, message="虚拟比赛未在进行")
        if virtual_contest.owner_id != session.get("uid", -1):
            return make_response(-1, message="这场虚拟比赛不是由你创建的")
    else:

        if not contest.running():
            if not session.get("uid"):
                return make_response(-1, message="你没有权限查看此题目")
            user: User = User.by_id(session.get("uid"))
            if not permission_manager.has_permission(user.id, "contest.manage") and user.id != contest.owner_id:
                return make_response(-1, message="你没有权限查看此题目")
    if contest.private_contest and not permission_manager.has_permission(session.get("uid", -1), f"contest.use.{contest.id}"):
        return make_response(-1, message="你没有权限查看该比赛")
    problem: Problem = Problem.by_id(
        contest.problems[int(problemID)]["id"])
    print("loaded contest problem", contest.problems, problem.title)
    if problem.problem_type == "remote_judge":
        return make_response(-1, message="远程评测题目", is_remote=True)
    result = {
        "id": problemID,
        "title": problem.title,
        "background": problem.background,
        "content": problem.content,
        "input_format": problem.input_format,
        "output_format": problem.output_format,
        "hint": problem.hint,
        "example": problem.example,
        "files": problem.files,
        "subtasks": problem.subtasks,
        "score": Problem.get_total_score(problem),
        "extra_parameter": problem.extra_parameter,
        "virtual": using_virtual,
        "downloads": problem.downloads,
        "using_file_io": bool(problem.using_file_io),
        "input_file_name": problem.input_file_name,
        "output_file_name": problem.output_file_name,
        "problem_type": problem.problem_type,
        "last_code": "",
        "last_lang": "",
        "usedParameters": []
    }
    last_submission = db.session.query(Submission).filter(and_(
        Submission.problem_id == problem.id, Submission.uid == session.get("uid"))).filter(Submission.contest_id == contest.id).order_by(Submission.submit_time.desc())
    if last_submission.count():
        submit = last_submission.first()
        if problem.problem_type != "submit_answer":
            result["last_code"] = submit.code
        else:
            result["last_code"] = "提交答案题不提供源代码"
        result["last_lang"] = submit.language
        result["usedParameters"] = submit.selected_compile_parameters
    else:
        result["last_lang"] = result["last_code"] = ""
    return make_response(0, data=result)


def get_contest_rank_list(contest: Contest, virtual_id: int = -1) -> dict:
    import datetime
    # extra_contitions = []
    print(f"{virtual_id=}")
    if virtual_id != -1:
        virtual_contest: VirtualContest = db.session.query(
            VirtualContest.start_time
        ).filter(VirtualContest.id == virtual_id).one()
        time_delta = datetime.datetime.now() - virtual_contest.start_time
    else:
        time_delta = datetime.datetime.now()-contest.start_time  # 默认为非虚拟比赛情况
    print(f"{time_delta=}")
    # time_delta: 逻辑意义上的，当前比赛进程时间(如果当前正在使用虚拟比赛，则为当前时间距离虚拟比赛开始时间所经过的时间)
    users = db.session.query(
        Submission.uid,
        Submission.virtual_contest_id
    ).filter(
        Submission.contest_id == contest.id).distinct().all()  # 同时选出来虚拟比赛和非虚拟比赛
    ranklist = []
    for item in users:
        user: User = db.session.query(
            User.id,
            User.username
        ).filter_by(id=item.uid).one()
        using_virtual = (item.virtual_contest_id != -
                         1) and (item.virtual_contest_id is not None)
        virtual_contest_id = item.virtual_contest_id
        extra_conditions = []
        # print(item)
        if using_virtual:
            virtual_contest: VirtualContest = db.session.query(
                VirtualContest.start_time,
                VirtualContest.end_time
            ).filter_by(id=virtual_contest_id).one()
            extra_conditions = [
                Submission.submit_time <= virtual_contest.start_time+time_delta
            ]
            # 对于进行中的虚拟比赛，只在相应的虚拟比赛排行榜里显示排名(防止选手通过其他方法知道评测结果)
            if virtual_contest_id != virtual_id and Contest.running(virtual_contest):
                continue
        else:
            extra_conditions = [
                Submission.submit_time <= contest.start_time+time_delta
            ]
        if db.session.query(Submission).filter(expr.and_(
            Submission.uid == user.id,
            Submission.contest_id == contest.id,
            (Submission.virtual_contest_id ==
             virtual_contest_id) if using_virtual else Submission.virtual_contest_id.is_(None),
            *extra_conditions
        )).count() == 0:
            # 因为虚拟比赛的提交时间限制而啥都没搞到的
            continue

        # if using_virtual and virtual_contest_id != virtual_id and :
        #     continue
        current = {
            "uid": user.id,
            "username": user.username,
            "scores": [],
            "total": {},
            "virtualContestID": virtual_contest_id,
            "virtual": using_virtual,
            "rank": -1  # 用户排名
        }
        ranklist.append(current)
        scores = current["scores"]
        # 处理用户user在problem下的结果
        for problem_obj in contest.problems:
            id, weight = problem_obj["id"], problem_obj["weight"]
            # 获取分数最高中，最早的提交
            if contest.rank_criterion != "last_submit":
                # ACM赛制和IOI赛制，获取分数最高且最靠前的提交
                best_submit = db.session.query(Submission.status,
                                               Submission.score,
                                               Submission.submit_time,
                                               Submission.id)\
                    .order_by(
                    Submission.score.desc()
                )\
                    .order_by(
                    Submission.id.asc()
                )\
                    .filter(
                    expr.and_(
                        Submission.uid == user.id,
                        Submission.contest_id == contest.id,
                        Submission.problem_id == id,
                        (Submission.virtual_contest_id ==
                         virtual_contest_id) if using_virtual else Submission.virtual_contest_id.is_(None),
                        *extra_conditions
                    )
                )

            else:
                # NOI赛制，获取最后一次提交
                best_submit = db.session.query(Submission.status,
                                               Submission.score,
                                               Submission.submit_time,
                                               Submission.id)\
                    .order_by(Submission.id.desc())\
                    .filter(
                    expr.and_(
                        Submission.uid == user.id,
                        Submission.contest_id == contest.id,
                        Submission.problem_id == id,
                        Submission.status != "compile_error",
                        (Submission.virtual_contest_id ==
                         virtual_contest_id) if using_virtual else Submission.virtual_contest_id.is_(None),
                        *extra_conditions
                    )
                )

            if best_submit.count() == 0:
                scores.append({
                    "score": 0,
                    "submit_count": -1,
                    "ac_time": -1,
                    "penalty": 0,
                    "submit_id": -1,
                    "status": "unsubmitted",
                    "submit_time": -1
                })
                continue
            best_submit = best_submit.first()

            import time
            if best_submit.status == "accepted":
                # print(f"ac time cal,{using_virtual=}, {int((best_submit.submit_time-(contest.start_time if not using_virtual else virtual_contest.start_time)).total_seconds()/60)}")
                last = {
                    "score": best_submit.score*weight,
                    "submit_count": db.session.query(Submission.id).filter(expr.and_(
                        Submission.contest_id == contest.id,
                        Submission.uid == user.id,
                        Submission.status != "accepted",
                        Submission.id < best_submit.id,
                        *extra_conditions
                    )).count(),
                    "ac_time": int((best_submit.submit_time-(contest.start_time if not using_virtual else virtual_contest.start_time)).total_seconds()/60),
                    "submit_id": best_submit.id,
                    "status": best_submit.status,
                    "submit_time": int((best_submit.submit_time-(contest.start_time if not using_virtual else virtual_contest.start_time)).total_seconds()/60)
                }
                last["penalty"] = last["ac_time"] + \
                    last["submit_count"]*config.FAIL_SUBMIT_PENALTY
                if db.session.query(Submission.id).filter(expr.and_(
                    Submission.contest_id == contest.id,
                    Submission.id < best_submit.id,
                    Submission.problem_id == id,
                    Submission.status == "accepted",
                    *extra_conditions
                )).count() == 0:
                    last["first_blood"] = True
            else:
                last = {
                    "score": best_submit.score*weight,
                    "submit_count": db.session.query(Submission.id).filter(expr.and_(
                        Submission.contest_id == contest.id,
                        Submission.uid == user.id,
                        Submission.status != "accepted",
                        Submission.id <= best_submit.id,
                        *extra_conditions
                    )).count(),
                    "ac_time": -1,
                    "submit_id": best_submit.id,
                    "status": best_submit.status,
                    "submit_time": int((best_submit.submit_time-(contest.start_time if not using_virtual else virtual_contest.start_time)).total_seconds()/60)
                }
                last["penalty"] = last["submit_count"] * \
                    config.FAIL_SUBMIT_PENALTY
                last["first_blood"] = False
            scores.append(last)
        # 处理用户的total
        total = {
            "score": sum((item["score"] for item in scores)),
            "penalty": sum((item["penalty"] for item in scores if (item["status"] == "accepted"))),
            "ac_count": sum((1 for item in scores if (item["status"] == "accepted"))),
            "submit_time_sum": sum((item["submit_time"] for item in scores if (item["submit_time"] != -1) and item["score"] > 0))
        }
        current["total"] = total
    if contest.rank_criterion == "penalty":
        ranklist.sort(
            key=lambda x: (-x["total"]["ac_count"], x["total"]["penalty"]))
    else:
        ranklist.sort(key=lambda x: (
            -x["total"]["score"], x["total"]["submit_time_sum"]))
    for i, item in enumerate(ranklist):
        item["rank"] = i+1
    problems = []
    result = {"ranklist": ranklist, "problems": problems,
              "name": contest.name, "contest_id": contest.id, "using_penalty": contest.rank_criterion == "penalty"}
    for i, x in enumerate(contest.problems):
        problem: Problem = Problem.by_id(x["id"])
        problems.append({  # 计数只统计非虚拟提交
            "name": problem.title,
            "id": i,
            "accepted_submit": db.session.query(Submission.id).filter(
                expr.and_(
                    Submission.contest_id == contest.id,
                    Submission.status == "accepted",
                    Submission.problem_id == problem.id,
                    Submission.virtual_contest_id.is_(None)
                )
            ).count(),
            "total_submit": db.session.query(Submission.id).filter(
                expr.and_(
                    Submission.contest_id == contest.id,
                    Submission.problem_id == problem.id,
                    Submission.virtual_contest_id.is_(None)
                )
            ).count()
        })
    return result


@app.route("/api/contest/ranklist", methods=["POST"])
@unpack_argument
def contest_ranklist(contestID: int, virtualID: int = -1):
    """
    获取比赛的排行榜
    {
        contestID:比赛ID
        virtualID:虚拟比赛ID
    }
    返回值:
    {
        "code":0,
        "data":{
            "refresh_interval":"刷新间隔",
            "closed":"比赛是否已关闭",
            "name":'比赛名',
            "contest_id":"比赛ID",
            "using_penalty":"使用罚时(True或False)",
            "ranklist":[
                {
                    "rank":"排名",
                    "uid":"用户ID",
                    "username":"用户名",
                    "virtual":"是否为虚拟参赛",
                    "virtualContestID":"虚拟比赛ID"
                    "scores":[
                        {
                            "score":"题目得分",
                            "submit_count":1,//AC前的提交次数,
                            "ac_time":"AC时间(分钟)",//
                            "penalty":"罚时"//AC时间+config.FAIL_SUBMIT_PENALTY*提交次数
                            "submit_id":"提交ID",
                            "status":"题目状态",
                            "first_blood":True//一血
                        }
                    ],
                    "total":{
                        "score":"分数",
                        "penalty":"总罚时",
                        "ac_count":"总通过数"
                    }
                }        
            ],
            "problems":[
                {
                    "name":"题目名",
                    "id":"题目ID",//比赛中的
                    "accepted_submit":"通过数量",
                    "total_submit":"总提交数量"
                }
            ]
        }
    }
    """
    contest: Contest = Contest.by_id(contestID)

    virtualID = int(virtualID)
    using_virtual = (virtualID != -1)
    virtual_contest: VirtualContest = db.session.query(
        VirtualContest
    ).filter_by(id=virtualID).one_or_none()
    # show_all_submissions_when_using_virtual_contest = False
    if using_virtual:
        if not virtual_contest:
            return make_response(-1, message="虚拟比赛不存在")
        if virtual_contest.contest_id != contest.id:
            return make_response(-1, message="此虚拟比赛不对应于此实际比赛")
        # if virtual_contest.owner_id!=session.get("uid",-1):
            # return make_response(-)
        can_see_ranklist = (not virtual_contest.running()
                            ) or (contest.ranklist_visible)
        # 虚拟比赛跑完了，同时显示上其他虚拟比赛的提交
        # show_all_submissions_when_using_virtual_contest = not virtual_contest.running()
    else:
        can_see_ranklist = contest.can_see_ranklist(
            session.get("uid"), permission_manager)
        if contest.owner_id != session.get("uid", -1) and contest.private_contest and not permission_manager.has_permission(session.get("uid", -1), f"contest.use.{contest.id}"):
            return make_response(-1, message="你没有权限查看该比赛")
    if not can_see_ranklist:
        return make_response(-1, message="你无权进行此操作")
    import redis
    from main import redis_connection_pool
    from json import JSONEncoder, JSONDecoder
    key = f"hj2-contest-ranklist-{contest.id}-virtual-{virtualID}"
    client = redis.Redis(connection_pool=redis_connection_pool)
    with redis_lock.Lock(client, name=f"hj2-refresh-lock-contest-ranklist-{contest.id}|{virtualID}", expire=3, auto_renewal=True):
        if not client.exists(key):
            print(f"Ranklist for {key} not found, generating..")
            refresh_interval = config.RANKLIST_UPDATE_INTERVAL if not contest.closed else config.RANKLIST_UPDATE_INTERVAL_CLOSED_CONTESTS
            if VirtualContest.running(virtual_contest or contest):
                refresh_interval = config.RANKLIST_UPDATE_INTERVAL
            else:
                refresh_interval = config.RANKLIST_UPDATE_INTERVAL_CLOSED_CONTESTS
            ranklist_data = {
                **get_contest_rank_list(contest, virtualID),
                "refresh_interval": refresh_interval,
                "closed": bool(contest.closed),
                "running": VirtualContest.running(virtual_contest) if virtual_contest else Contest.running(contest)
            }
            client.set(key, JSONEncoder().encode(ranklist_data),
                       ex=refresh_interval)
        else:
            ranklist_data = json.loads(client.get(key).decode())
    return make_response(0, data={**ranklist_data, "managable": permission_manager.has_permission(session.get("uid", -1), "contest.manage")})


@app.route("/api/contest/refresh_ranklist", methods=["POST"])
@unpack_argument
@require_permission(permission_manager, "contest.manage")
def contest_refresh_ranklist(contestID: int, virtualID: int = -1):
    key = f"hj2-contest-ranklist-{contestID}-virtual-{virtualID}"
    import redis
    from main import redis_connection_pool
    client = redis.Redis(connection_pool=redis_connection_pool)
    with redis_lock.Lock(client, name=f"hj2-refresh-lock-contest-ranklist-{contestID}|{virtualID}", expire=3, auto_renewal=True):
        client.delete(key)
    return make_json_response(0)
