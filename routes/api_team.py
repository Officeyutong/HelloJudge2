from models.problemset import ProblemSet
from common.permission import require_permission
from common.utils import unpack_argument
from main import web_app as app
from main import db, config, basedir, permission_manager
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import User
from models.problem import Problem
from models.submission import Submission
from models.contest import Contest
from models.team import Team, TeamMember
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename
from typing import Tuple
from datetime import datetime
import typing


@app.route("/api/team/unlock_problems_and_contests_and_problemsets", methods=["POST"])
@unpack_argument
def api_team_unlock_problems_and_contests(teamID: int):
    """
    团队用户解锁团队题目和团队比赛和团队习题集
    """
    user: User = db.session.query(User).filter_by(
        id=session.get("uid", -1)).one_or_none()
    if not user:
        return make_response(-1, message="请登录")
    team: Team = db.session.query(
        Team.team_problems,
        Team.team_contests,
        Team.team_problemsets
    ).filter_by(id=teamID).one_or_none()
    if not team:
        return make_response(-1, message="团队不存在")
    if not db.session.query(TeamMember).filter_by(uid=session.get("uid"), team_id=teamID).count():
        return make_response(-1, message="你不是团队成员")
    permissions = set((f"problem.use.{id}" for id in team.team_problems)) | set(
        (f"contest.use.{id}" for id in team.team_contests)) | set(f"problemset.use.{id}" for id in team.team_problemsets)

    # user.permissions = [
    #     item for item in user.permissions if item not in permissions] + list(permissions)
    db.session.commit()
    permission_manager.refresh_user(user.id)

    return make_response(0, message="操作完成")


@app.route("/api/team/add_problem_or_contest_or_problemset", methods=["POST"])
@unpack_argument
def api_team_add_problem_or_contest(teamID: int, problems: typing.List[int], contests: typing.List[int], problemsets: typing.List[int]):
    """
    向一个团队中添加团队题目和团队比赛

    """
    team: Team = db.session.query(Team).filter_by(id=teamID).one_or_none()
    if not team:
        return make_response(-1, message="团队不存在")
    relationship = db.session.query(TeamMember).filter_by(
        team_id=teamID, uid=session.get('uid', -1), is_admin=True).one_or_none()
    if session.get("uid", -1) != team.owner_id and not relationship:
        return make_response(-1, message="只有团队主或管理员才能进行此操作")
    for problem in problems:
        current = db.session.query(Problem.uploader_id).filter_by(
            id=problem).one_or_none()
        if not current:
            return make_response(-1, message=f"题目{problem}不存在")
        if current.uploader_id != session.get("uid", -1) and not permission_manager.has_permission(session.get("uid", -1), "problem.manage"):
            return make_response(-1, message=f"题目{problem}的上传者必须是你自己，或者你需要有problem.manage权限")
    for contest in contests:
        current: Contest = db.session.query(Contest.owner_id).filter_by(
            id=contest).one_or_none()
        if not current:
            return make_response(-1, message=f"比赛{contest}不存在")
        if current.owner_id != session.get("uid", -1) and not permission_manager.has_permission(session.get("uid", -1), "contest.manage"):
            return make_response(-1, message=f"比赛{contest}的创建者必须是你自己，或者你需要具有contest.manage权限")
    for problemset in problemsets:
        current: ProblemSet = db.session.query(ProblemSet.owner_uid).filter_by(
            id=problemset).one_or_none()
        if not current:
            return make_response(-1, message=f"习题集{problemset}不存在")
        if current.owner_uid != session.get("uid", -1) and not permission_manager.has_permission(session.get("uid", -1), "problemset.manage"):
            return make_response(-1, message=f"习题集{problemset}的创建者必须是你自己，或者你需要具有problemset.manage权限")

    team.team_contests = [
        *(item for item in team.team_contests if item not in contests), *contests]
    team.team_problems = [
        *(item for item in team.team_problems if item not in problems), *problems]
    team.team_problemsets = [
        *(item for item in team.team_problemsets if item not in problemsets), *problemsets]

    db.session.commit()
    return make_response(0, message="操作完成")


@app.route("/api/team/list", methods=["POST"])
def team_list():
    """
    参数
    {
        ""
    }
    返回:
    {
        "code":0,
        "data":[
            {
                "name":"团队名",
                "id":"团队ID",
                "owner_id":"创建者ID",
                "owner_username":"创建者用户名",
                "member_count":"人数",
                "private":"是否私有",
                "accessible":"是否有权限访问"
            }
        ]
    }
    """
    teams = db.session.query(
        Team.id, Team.name, Team.owner_id,  Team.private).all()
    result = []
    for item in teams:
        owner = User.by_id(item.owner_id)
        result.append({
            "name": item.name,
            "id": item.id,
            "owner_id": owner.id,
            "owner_username": owner.username,
            "member_count": db.session.query(TeamMember).filter_by(team_id=item.id).count(),
            "private": item.private,
            "accessible": permission_manager.has_permission(session.get("uid", None), f"team.use.{item.id}")
        })
    return make_response(0, data=result)


@app.route("/api/team/create", methods=["POST"])
@require_permission(permission="team.create", manager=permission_manager)
def create_team():
    """
    参数
    {
        ""
    }
    返回:
    {
        "code":0,
        "team_id":"创建完成的队伍的ID"
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    owner: User = User.by_id(session.get("uid"))
    team = Team(owner_id=owner.id, create_time=datetime.now())
    # team.members = [owner.id]
    db.session.add(team)
    db.session.commit()
    db.session.add(TeamMember(
        uid=owner.id,
        team_id=team.id,
        is_admin=True
    ))
    db.session.commit()
    return make_response(0, team_id=team.id)


@app.route("/api/team/join", methods=["POST"])
def join_team():
    """
    参数
    {
        "uid":"用户ID",
        "team_id":"团队ID"
        "invite_code":"邀请码"
    }
    返回:
    {
        "code":0,
        "message":""
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    owner: User = User.by_id(session.get("uid"))
    if int(owner.id) != int(request.form["uid"]):
        return make_response(-1, message="此操作只能由用户本人进行")
    team: Team = Team.by_id(request.form["team_id"])
    if db.session.query(TeamMember).filter_by(uid=session.get("uid"), team_id=request.form["team_id"]).count():
        return make_response(-1, message="您已经在本团队内")
    if team.private and not permission_manager.has_permission(session.get("uid"), f"team.use.{team.id}"):
        if team.invite_code != request.form.get("invite_code", ""):
            return make_response(-1, message="邀请码错误")
        else:
            permission_manager.add_permission(
                session.get("uid"), f"team.use.{team.id}")
    # team.members = [*team.members, owner.id]
    # owner.joined_teams = [*owner.joined_teams, team.id]

    db.session.add(TeamMember(
        uid=session.get("uid"),
        team_id=team.id,
        is_admin=False
    ))
    db.session.commit()
    return make_response(0, message="加入成功")


@app.route("/api/team/quit", methods=["POST"])
def quit_team():
    """
    退出团队并清空相应权限
    参数
    {
        "uid":"用户ID",
        "team_id":"团队ID"
    }
    返回:
    {
        "code":0,
        "message":""
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    operator: User = User.by_id(session.get("uid"))
    user: User = User.by_id(request.form["uid"])
    team: Team = Team.by_id(request.form["team_id"])
    if user.id != operator.id and not permission_manager.has_permission(operator.id, "team.manage") and operator.id not in team.admins and operator.id != team.owner_id:
        return make_response(-1, message="你没有权限这样做")
    relation = db.session.query(TeamMember).filter_by(
        uid=user.id, team_id=team.id).one_or_none()
    if not relation:
        return make_response(-1, message="您不在此团队内")
    if user.id == team.owner_id:
        return make_response(-1, message="此用户不可被移出团队")

    # def remove_and_return(a, val):
    #     a = a.copy()
    #     a.remove(val)
    #     return a
    # # print(team.members)
    # team.members = remove_and_return(team.members, user.id)
    # user.joined_teams = remove_and_return(user.joined_teams, team.id)
    # if user.id in team.admins:
    #     team.admins = remove_and_return(team.admins, user.id)
    # print(team.members)
    db.session.delete(relation)
    db.session.commit()
    perms = set((f"contest.use.{item}" for item in team.team_contests)) | set(
        (f"problem.use.{item}" for item in team.team_problems)) | set(
        (f"problemset.use.{item}" for item in team.team_problemsets))
    user.permissions = [item for item in user.permissions if item not in perms]
    db.session.commit()
    permission_manager.refresh_user(user.id)
    return make_response(0, message="操作完成")


@app.route("/api/team/set_admin", methods=["POST"])
def set_admin():
    """
    此操作只可由团队主进行
    (更新：也可由具有team.manage权限的用户进行)
    参数
    {
        "team_id":"团队ID",
        "uid":"用户ID",
        "value":True/False,表示设定/取消管理员
    }
    {
        "code":-1,"message":""
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录!")
    user: User = User.by_id(request.form["uid"])
    team: Team = Team.by_id(request.form["team_id"])
    operator: User = User.by_id(session.get("uid"))
    value = request.form["value"].lower() == "true"
    to_modify_relationship: TeamMember = db.session.query(TeamMember).filter_by(
        team_id=team.id, uid=user.id).one_or_none()
    operator_relationship: TeamMember = db.session.query(TeamMember).filter_by(
        team_id=team.id, uid=operator.id).one_or_none()
    if not operator_relationship:
        return make_response(-1, message="你没有权限进行此操作")
    if not to_modify_relationship:
        return make_response(-1, message="此用户不在团队中")
    if user.id == team.owner_id:
        return make_response(-1, message="无法对此用户进行此操作")
    if team.owner_id != operator.id and not operator_relationship.is_admin and not permission_manager.has_permission(session.get("uid", -1), "team.manage"):
        return make_response(-1, message="你没有权限执行此操作")
    to_modify_relationship.is_admin = value

    # def remove_and_return(a, val):
    #     a = a.copy()
    #     a.remove(val)
    #     return a
    # if value:
    #     if user.id not in team.admins:
    #         team.admins = [*team.admins, user.id]
    # else:
    #     if user.id in team.admins:
    #         team.admins = remove_and_return(team.admins, user.id)
    db.session.commit()
    return make_response(0, message="操作完成")


@app.route("/api/team/show", methods=["POST"])
def show_team():
    """
    参数
    {
        "team_id":"团队ID"
    }
    返回:
    {
        "code":0,
        "data":{
            "canManage":"是否可以管理",
            "id":"团队ID",
            "name":"团队名",
            "description":"团队描述",
            "owner_id":"所有者ID",
            "owner_username":"所有者用户名",
            "admins":[],//管理员列表[1,2,3]
            "members":[],//用户列表{"username":"xxx","uid":xxx}
            "create_time":"创建时间",
            "hasPermission":"是否有权限查看详情",
            "problems":[ // 团队题目列表
                {"id":"题目ID","title":"题目名"}
            ],
            "contests":[ // 团队题目列表
                {"id":"比赛ID","name":"比赛名"}
            ],
            "problemsets":[ // 团队题目列表
                {"id":"习题集ID","name":"习题集名"}
            ],
            "tasks":[
                {
                    "name":"任务名",
                    "problems":[
                        {
                            "name":"题目名",
                            "id":"题目ID",
                            scores:[
                                {
                                    "uid":"用户ID",
                                    "username":"用户名"
                                    "score":"题目得分",
                                    "status":"题目状态",
                                    "submit_id":"提交ID"
                                },
                            ]
                        }
                    ]
                }
            ]
        }
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    team: Team = Team.by_id(request.form["team_id"])
    user_relationship: TeamMember = db.session.query(
        TeamMember).filter_by(uid=user.id, team_id=team.id).one_or_none()
    has_permission = permission_manager.has_permission(
        user.id, f"team.use.{team.id}") or (not team.private) or user.id == team.owner_id or (user_relationship)
    # result = team.as_dict()
    members = db.session.query(
        TeamMember.uid,
        TeamMember.is_admin,
        User.username
    ).join(User).filter(TeamMember.team_id == team.id).order_by(TeamMember.is_admin.desc()).order_by(User.username.asc()).all()
    result = {
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "owner_id": team.owner_id,
        "tasks": team.tasks,
        "create_time": str(team.create_time),
        "private": bool(team.private),
        "team_problems": team.team_problems,
        "team_contests": team.team_contests,
        "team_problemsets": team.team_problemsets,
        "canManage": permission_manager.has_permission(session.get("uid", -1), "team.manage")
    }
    result["owner_username"] = User.by_id(result["owner_id"]).username
    result["hasPermission"] = has_permission
    result["team_problems"] = [{
        "id": item,
        "title": db.session.query(Problem.title).filter_by(id=item).one().title
    } for item in result["team_problems"]]
    result["team_contests"] = [{
        "id": item,
        "name": db.session.query(Contest.name).filter_by(id=item).one().name
    } for item in result["team_contests"]]
    result["team_problemsets"] = [{
        "id": item,
        "name": db.session.query(ProblemSet.name).filter_by(id=item).one().name
    } for item in result["team_problemsets"]]

    if has_permission:
        for item in result["tasks"]:
            problems = []
            for problem in item["problems"]:
                current: Problem = Problem.by_id(problem)
                last = {
                    "id": current.id, "name": current.title,
                    "scores": []
                }
                for user_ in members:
                    user = user_.uid
                    submit: Submission = db.session.query(Submission).filter(Submission.uid == user).filter(
                        Submission.problem_id == current.id).order_by(Submission.status.asc()).order_by(Submission.submit_time.desc())
                    if submit.count() == 0:
                        submit = None
                    else:
                        submit = submit.first()
                    if submit:
                        last["scores"].append({
                            "uid": user,
                            "username": User.by_id(user).username,
                            "score": submit.get_total_score(),
                            "status": submit.status,
                            "submit_id": submit.id
                        })
                    else:
                        last["scores"].append({
                            "uid": user, "username": User.by_id(user).username,
                            "score": 0, "status": "unsubmitted"
                        })

                problems.append(last)
            item["problems"] = problems

        result["create_time"] = str(result["create_time"])

        result["admins"] = []
        result["members"] = [
        ]
        for x in members:
            result["members"].append({
                "username": x.username,
                "uid": x.uid
            })
            if x.is_admin:
                result["admins"].append(x.uid)
        # result["members"] = list(map(lambda x: {"username": User.by_id(
        #     x).username, "uid": x}, result["members"]))
    else:
        result["description"] = ""
        result["admins"] = []
        result["members"] = []
        result["create_time"] = ""
        result["tasks"] = []

    return make_response(0, message="操作完成", data=result)


@app.route("/api/team/raw_data", methods=["POST"])
def team_raw_data():
    """
    获取团队原始信息
    {
        "team_id":"团队ID"
    }
    {
        "code":-1,
        "data":{
            "id":团队ID,
            "name":"团队名",
            "description":"团队描述",
            "tasks":[
                {"name":"任务名","problems":[1,2,3]}
            ],
            "private":"是否为私有团队",
            "invite_code":"邀请码"
        }
    }
    """
    # team: Team = Team.by_id(request.form["team_id"])
    team: Team = db.session.query(
        Team.id,
        Team.name,
        Team.description,
        Team.tasks,
        Team.private,
        Team.invite_code,
        Team.owner_id
    ).filter_by(id=request.form["team_id"]).one_or_none()
    if not team:
        return make_response(-1, message="团队ID不存在")
    user = session.get("uid", -1)
    relationship = db.session.query(TeamMember).filter_by(
        uid=user, team_id=team.id, is_admin=True).one_or_none()
    if user != team.owner_id and not relationship and not permission_manager.has_permission(user, "team.manage"):
        return make_response(-1, message="你没有权限进行此操作")
    return make_response(0, data={
        "id": team.id,
        "name": team.name,
        "description": team.description,
        "tasks": team.tasks,
        "private": team.private,
        "invite_code": team.invite_code
    })


@app.route("/api/team/update", methods=["POST"])
def team_update():
    """
    更新团队信息
    {
        "team_id":"团队ID",
        "data":{
            "id":团队ID,
            "name":"团队名",
            "description":"团队描述",
            "tasks":[
                {"name":"任务名","problems":[1,2,3]}
            ],
            "private":"是否为私有团队",
            "invite_code":"邀请码"
        }
    }

    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    team: Team = Team.by_id(request.form["team_id"])
    user: User = User.by_id(session.get("uid"))
    relationship = db.session.query(TeamMember).filter_by(
        uid=user.id, team_id=team.id, is_admin=True).one_or_none()
    if user.id != team.owner_id and not relationship and not permission_manager.has_permission(user, "team.manage"):
        return make_response(-1, message="你没有权限进行此操作")
    data: dict = decode_json(request.form["data"])
    team.name = data["name"]
    team.description = data["description"]
    team.tasks = data["tasks"]
    team.private = data["private"]
    team.invite_code = data["invite_code"]
    for task in team.tasks:
        for problem in task["problems"]:
            if not Problem.has(problem):
                return make_response(-1, message=f"任务 {task['name']} 中的题目 {problem}不存在！")
    db.session.commit()
    return make_response(0, message="保存成功")


@app.route("/api/team/send_team_notification", methods=["POST"])
@unpack_argument
def api_team_send_team_notification(team_id: int, content: str):
    """
    向团队所有成员发送团队消息
    """
    team: Team = db.session.query(Team).filter_by(id=team_id).count()
    if team == 0:
        return make_response(-1, message="团队不存在")
    relationship: TeamMember = db.session.query(TeamMember).filter_by(
        uid=session.get("uid", -1),
        team_id=team_id,
        is_admin=True
    ).one_or_none()
    if not relationship:
        return make_response(-1, message="你没有权限这样做")
    members = db.session.query(TeamMember.uid).filter_by(team_id=team_id).all()
    from api.feed import send_feed
    for item in members:
        send_feed(item.uid, False, content)
    return make_response(0, message="操作完成")
