from main import web_app as app
from main import db, config, basedir, permission_manager
from flask import session, request, send_file, send_from_directory
from utils import *
from models.user import *
from models.problem import *
from models.submission import *
from models.contest import *
from models.team import *
from sqlalchemy.sql.expression import *
from werkzeug.utils import secure_filename
from typing import Tuple
from datetime import datetime
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
                "member_count":"人数"
            }
        ]
    }
    """
    teams = db.session.query(
        Team.id, Team.name, Team.owner_id, Team.members).all()
    result = []
    for item in teams:
        owner = User.by_id(item.owner_id)
        result.append({
            "name": item.name, "id": item.id, "owner_id": owner.id, "owner_username": owner.username,
            "member_count": len(item.members)
        })
    return make_response(0, data=result)


@app.route("/api/team/create", methods=["POST"])
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
    if not permission_manager.has_permission(owner.id, "team.create"):
        return make_response(-1, message="现在只允许管理员创建团队.")
    team = Team(owner_id=owner.id, create_time=datetime.now())
    team.members = [owner.id]
    db.session.add(team)
    db.session.commit()
    owner.joined_teams = [*owner.joined_teams, team.id]
    db.session.commit()
    return make_response(0, team_id=team.id)


@app.route("/api/team/join", methods=["POST"])
def join_team():
    """
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
    owner: User = User.by_id(session.get("uid"))
    if int(owner.id) != int(request.form["uid"]):
        return make_response(-1, message="此操作只能由用户本人进行")

    team: Team = Team.by_id(request.form["team_id"])
    if team.id in owner.joined_teams or owner.id in team.members:
        return make_response(-1, message="您已经在本团队内")
    team.members = [*team.members, owner.id]
    owner.joined_teams = [*owner.joined_teams, team.id]
    #TODO: 写完JSON序列化
    db.session.commit()
    return make_response(0, message="加入成功")


@app.route("/api/team/quit", methods=["POST"])
def quit_team():
    """
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

    if team.id not in user.joined_teams and user.id in team.members:
        return make_response(-1, message="您不在此团队内")
    if user.id == team.owner_id:
        return make_response(-1, message="此用户不可被移出团队")

    def remove_and_return(a, val):
        a = a.copy()
        a.remove(val)
        return a
    # print(team.members)
    team.members = remove_and_return(team.members, user.id)
    user.joined_teams = remove_and_return(user.joined_teams, team.id)
    if user.id in team.admins:
        team.admins = remove_and_return(team.admins, user.id)
    # print(team.members)
    db.session.commit()
    return make_response(0, message="操作完成")


@app.route("/api/team/set_admin", methods=["POST"])
def set_admin():
    """
    此操作只可由团队主进行
    参数
    {
        "team_id":"团队ID",
        "uid":"用户ID",
        "value":True/False,表示设定\取消管理员
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
    if user.id not in team.members:
        return make_response(-1, message="此用户不在团队中")
    if user.id == team.owner_id:
        return make_response(-1, message="无法对此用户进行此操作")
    if team.owner_id != operator.id and operator.id not in team.admins:
        return make_response(-1, message="你没有权限执行此操作")

    def remove_and_return(a, val):
        a = a.copy()
        a.remove(val)
        return a
    if value:
        if user.id not in team.admins:
            team.admins = [*team.admins, user.id]
    else:
        if user.id in team.admins:
            team.admins = remove_and_return(team.admins, user.id)
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
            "id":"团队ID",
            "name":"团队名",
            "description":"团队描述",
            "owner_id":"所有者ID",
            "owner_username":"所有者用户名",
            "admins":[],//管理员列表[1,2,3]
            "members":[],//用户列表{"username":"xxx","uid":xxx}
            "create_time":"创建时间",
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
    result = team.as_dict()
    result["owner_username"] = User.by_id(result["owner_id"]).username

    for item in result["tasks"]:
        problems = []
        for problem in item["problems"]:
            current: Problem = Problem.by_id(problem)
            last = {
                "id": current.id, "name": current.title,
                "scores": []
            }
            for user in result["members"]:
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
    result["members"] = list(map(lambda x: {"username": User.by_id(
        x).username, "uid": x}, result["members"]))
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
            ]
        }
    }
    """
    team: Team = Team.by_id(request.form["team_id"])
    if not team:
        return make_response(-1, message="团队ID不存在")
    return make_response(0, data={
        "id": team.id, "name": team.name, "description": team.description, "tasks": team.tasks
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
            ]
        }
    }

    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    team: Team = Team.by_id(request.form["team_id"])
    user: User = User.by_id(session.get("uid"))
    if user.id != team.owner_id and user.id not in team.admins:
        return make_response(-1, message="你没有权限进行此操作")
    data: dict = decode_json(request.form["data"])
    team.name = data["name"]
    team.description = data["description"]
    team.tasks = data["tasks"]
    for task in team.tasks:
        for problem in task["problems"]:
            if not Problem.has(problem):
                return make_response(-1, message=f"任务 {task['name']} 中的题目 {problem}不存在！")
    db.session.commit()
    return make_response(0, message="保存成功")
