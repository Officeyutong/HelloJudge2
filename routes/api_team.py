
import os
from common.exceptions import APIException
from models.problemset import ProblemSet
from models.permission_group import PermissionGroup
from models.file_storage import FileStorage
from common.permission import require_permission
from common.utils import make_json_response, unpack_argument
from main import web_app as app
from main import db, config, basedir, permission_manager, user_operation, file_storage
from flask import session, request, send_file, send_from_directory, Blueprint
from utils import *
from models.user import User
from models.problem import Problem
from models.submission import Submission
from models.contest import Contest
from models.team import Team, TeamFile, TeamMember
from sqlalchemy.sql.expression import *
from typing import List, Tuple
from datetime import datetime
import typing
from sqlalchemy.sql import expression as expr
from sqlalchemy.sql import functions as func
import flask
router = Blueprint("team", __name__)


@router.route("/unlock_problems_and_contests_and_problemsets", methods=["POST"])
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
    db.session.commit()
    permission_manager.refresh_user(user.id)

    return make_response(0, message="操作完成")


@router.route("/add_problem_or_contest_or_problemset", methods=["POST"])
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


@router.route("/list", methods=["POST"])
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
        Team.id,
        Team.name,
        Team.owner_id,
        Team.private,
        User.username,
        expr.select(func.count(TeamMember.uid)).where(
            TeamMember.team_id == Team.id).scalar_subquery().label("member_count")
        # functions.count().label("member_count")
    ).join(User).order_by(Team.id.desc()).all()
    result = []
    for item in teams:
        # print(item)
        # owner = User.by_id(item.owner_id)
        result.append({
            "name": item.name,
            "id": item.id,
            "owner_id": item.owner_id,
            "owner_username": item.username,
            "member_count": item.member_count,
            "private": bool(item.private),
            "accessible": (not bool(item.private)) or permission_manager.has_permission(session.get("uid", None), f"team.use.{item.id}")
        })
    return make_response(0, data=result)


@router.route("/create", methods=["POST"])
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


@router.route("/join", methods=["POST"])
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
    permission_manager.refresh_user(session.get("uid", -1))
    return make_response(0, message="加入成功")


@router.route("/quit", methods=["POST"])
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
    db.session.delete(relation)
    db.session.commit()
    permission_manager.refresh_user(user.id)
    return make_response(0, message="操作完成")


@router.route("/set_admin", methods=["POST"])
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
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/show", methods=["POST"])
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
            "members":[],//用户列表{"username":"xxx","uid":xxx,"email":xxx,"group_name":"权限组名"}
            "create_time":"创建时间",
            "hasPermission":"是否有权限查看详情",
            "team_problems":[ // 团队题目列表
                {"id":"题目ID","title":"题目名"}
            ],
            "team_contests":[ // 团队题目列表
                {"id":"比赛ID","name":"比赛名"}
            ],
            "team_problemsets":[ // 团队题目列表
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
        user.id, f"team.use.{team.id}") or (not team.private) or user.id == team.owner_id or (user_relationship is not None)
    # result = team.as_dict()
    members = db.session.query(
        TeamMember.uid,
        TeamMember.is_admin,
        User.username,
        User.email,
        User.permission_group,
        PermissionGroup.name.label("group_name")
    ).join(User).join(PermissionGroup, PermissionGroup.id == User.permission_group).filter(TeamMember.team_id == team.id).order_by(TeamMember.is_admin.desc()).order_by(User.username.asc()).all()
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
        "id": item.id,
        "title": item.title
    } for item in db.session.query(Problem.title, Problem.id).filter(Problem.id.in_(result["team_problems"])).all()]
    result["team_contests"] = [{
        "id": item.id,
        "name": item.name,
        "start_time": int(item.start_time.timestamp())
    } for item in db.session.query(Contest.name, Contest.id, Contest.start_time).filter(Contest.id.in_(result["team_contests"])).all()]
    result["team_problemsets"] = [{
        "id": item.id,
        "name": item.name
    } for item in db.session.query(ProblemSet.name, ProblemSet.id).filter(ProblemSet.id.in_(result["team_problemsets"])).all()]

    if has_permission:

        result["create_time"] = str(result["create_time"])

        result["admins"] = []
        result["members"] = [
        ]
        for x in members:
            result["members"].append({
                "username": x.username,
                "uid": x.uid,
                "email": x.email,
                "group_name": x.group_name
            })
            if x.is_admin:
                result["admins"].append(x.uid)
    else:
        result["description"] = ""
        result["admins"] = []
        result["members"] = []
        result["create_time"] = ""
        result["tasks"] = []

    return make_response(0, message="操作完成", data=result)


@router.route("/raw_data", methods=["POST"])
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
            "invite_code":"邀请码",
            "team_problems":number[],
            "team_contests":number[],
            "team_problemsets":number[],
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
        Team.owner_id,
        Team.team_problemsets,
        Team.team_contests,
        Team.team_problems
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
        "private": bool(team.private),
        "invite_code": team.invite_code,
        "team_problems": team.team_problems,
        "team_contests": team.team_contests,
        "team_problemsets": team.team_problemsets
    })


@router.route("/update", methods=["POST"])
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
            "invite_code":"邀请码",
            "team_problems":number[],
            "team_contests":number[],
            "team_problemsets":number[]
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

    def check_stuff(keyname: str, model):
        team_stuff = data[keyname]
        if db.session.query(model).filter(model.id.in_(team_stuff)).count() != len(team_stuff):
            raise APIException(f"{keyname}中存在非法ID", -1)
        setattr(team, keyname, team_stuff)
    check_stuff("team_problems", Problem)
    check_stuff("team_contests", Contest)
    check_stuff("team_problemsets", ProblemSet)

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


@router.route("/send_team_notification", methods=["POST"])
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


@router.route("/invite", methods=["POST"])
@unpack_argument
@require_permission(manager=permission_manager, permission="team.manage")
def api_team_invitemembers(team: int, uid: List[int], setAdmin: bool):
    teamobj = db.session.query(Team).filter(Team.id == team).count()
    if not teamobj:
        return make_json_response(-1, message="题目ID错误")
    db.session.add_all([
        TeamMember(uid=user, team_id=team, is_admin=setAdmin) for user in uid
    ])
    db.session.commit()
    return make_json_response(0, message="操作完成")


@router.route("/get_files", methods=["POST"])
@unpack_argument
def api_get_team_files(teamID: int):
    uid = user_operation.ensure_login()
    if not user_operation.ensure_in_team(uid, teamID):
        return make_json_response("请先加入该团队!")
    files = db.session.query(
        TeamFile.file_id,
        FileStorage.filename,
        FileStorage.filesize,
        FileStorage.upload_time,
        User.username,
        User.email,
        TeamFile.uid
    ).join(FileStorage).join(User).filter(TeamFile.team_id == teamID)
    return make_json_response(0, data=[
        {
            "file_id": item.file_id,
            "filename": item.filename,
            "filesize": item.filesize,
            "upload_time": int(item.upload_time.timestamp()),
            "uploader": {
                "uid": item.uid,
                "username": item.username,
                "email": item.email
            }
        } for item in files
    ])


@router.route("/remove_file", methods=["POST"])
@unpack_argument
def remove_teamfile(teamID: int, fileID: str):
    uid = user_operation.ensure_login()
    if not user_operation.ensure_in_team(uid, teamID):
        return make_json_response("请先加入该团队!")
    has_file = bool(db.session.query(TeamFile).filter_by(
        team_id=teamID, file_id=fileID).one_or_none())
    if not has_file:
        return make_json_response(-1, message="文件不存在!")
    file_storage.remove_file(fileID)
    return make_json_response(0, message="操作完成!")


@router.route("/upload_file", methods=["POST"])
def upload_file():
    """
    上传题目文件
    URL query:
        teamID: int 团队ID
    FormData:
        文件
    """
    import uuid
    import os
    uid = user_operation.ensure_login()
    team_id = flask.request.args.get("teamID", type=int, default=-1)
    if not user_operation.ensure_in_team(uid, team_id):
        return make_json_response(-1, message="你没有权限进行此操作")
    if not user_operation.ensure_team_admin(uid, team_id, True, False):
        return make_json_response(-1, message="你不是团队管理!")
    file_storage.ensure_datadir()
    files_store = []
    for filename, file in request.files.items():
        curr_id = str(uuid.uuid4())
        save_path = file_storage.get_filepath(curr_id)
        file.save(save_path)
        files_store.append({
            "filename": filename,
            "uuid": curr_id,
            "filesize": os.path.getsize(save_path),
            "upload_time": datetime.now()
        })
    new_names = [item["filename"] for item in files_store]
    uuid_query = db.session.query(TeamFile.file_id).join(FileStorage).filter(
        expr.and_(
            FileStorage.filename.in_(new_names),
            TeamFile.team_id == team_id
        )
    )
    correspond_uuids = [item.file_id for item in uuid_query.all()]
    for item in correspond_uuids:
        os.remove(file_storage.get_filepath(item))
    db.session.query(FileStorage).filter(
        FileStorage.uuid.in_(correspond_uuids)).delete()
    db.session.commit()
    db.session.add_all(
        FileStorage(**entry) for entry in files_store
    )
    db.session.commit()
    db.session.add_all(TeamFile(
        team_id=team_id,
        file_id=entry["uuid"],
        uid=uid
    ) for entry in files_store)
    db.session.commit()
    return make_json_response(0)


@router.route("/download_file", methods=["GET", "POST"])
def download_file():
    uid = user_operation.ensure_login()
    team_id = flask.request.args.get("teamID", type=int, default=-1)
    file_id = flask.request.args.get("fileID", type=str, default="")
    if not user_operation.ensure_in_team(uid, team_id):
        flask.abort(403)
    file_storage.ensure_datadir()
    if db.session.query(TeamFile).filter_by(team_id=team_id, file_id=file_id).count() == 0:
        return make_json_response(-1, message="文件不存在!")
    return file_storage.get_flask_sendfile(file_id, True)
