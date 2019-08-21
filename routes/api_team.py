from main import web_app as app
from main import db, config, basedir
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
    if not session.get("userid"):
        return make_response(-1, message="请先登录")
    owner: User = User.by_id(session.get("userid"))
    if not owner.is_admin:
        return make_response(-1, message="现在只允许管理员创建团队.")
    team = Team(owner_id=owner.id, create_time=datetime.now())
    team.members = [owner.id]
    db.session.add(team)
    db.session.commit()
    return make_response(0, team_id=team.id)


@app.route("/api/team/join", methods=["POST"])
def join_team():
    """
    参数
    {
        "user_id":"用户ID",
        "team_id":"团队ID"
    }
    返回:
    {
        "code":0,
        "message":""
    }
    """
    if not session.get("userid"):
        return make_response(-1, message="请先登录")
    owner: User = User.by_id(session.get("userid"))
    if int(owner.id) != int(request.form["user_id"]):
        return make_response(-1, message="此操作只能由用户本人进行")

    team: Team = Team.by_id(request.form["team_id"])
    if team.id in owner.joined_teams or owner.id in team.members:
        return make_response(-1, message="您已经在本团队内")
    team.members.append(owner.id)
    owner.joined_teams.append(team.id)
    db.session.commit()
    return make_response(0, message="加入成功")


@app.route("/api/team/quit", methods=["POST"])
def quit_team():
    """
    参数
    {
        "user_id":"用户ID",
        "team_id":"团队ID"
    }
    返回:
    {
        "code":0,
        "message":""
    }
    """
    if not session.get("userid"):
        return make_response(-1, message="请先登录")
    operator: User = User.by_id(session.get("userid"))
    user: User = User.by_id(request.form["user_id"])
    team: Team = Team.by_id(request.form["team_id"])
    if user.id != operator.id and not operator.is_admin and operator.id not in team.admins and operator.id != team.owner_id:
        return make_response(-1, message="你没有权限这样做")

    if team.id not in user.joined_teams and user.id in team.members:
        return make_response(-1, message="您不在此团队内")
    team.members.remove(user.id)
    user.joined_teams.remove(team.id)
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
            "admins":[],//管理员列表
            "members":[],//用户列表
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
                                    "id":"用户ID",
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
    if not session.get("userid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("userid"))
    team: Team = Team.by_id(request.form["team_id"])
    result = team.as_dict()
    for item in result["tasks"]:
        problems = []
        for problem in item["problems"]:
            current: Problem = Problem.by_id(problem)
            last = {
                "id": current.id, "name": current.title,
                "scores": []
            }
            for user in result["members"]:
                submit: Submission = db.session.query(Submission).filter(Submission.user_id == user).filter(
                    Submission.problem_id == current.id).order_by(Submission.status.asc()).order_by(Submission.submit_time.desc())
                if submit.count() == 0:
                    submit = None
                else:
                    submit = submit.first()
                if submit:
                    last["scores"].append({
                        "id": user,
                        "username": User.by_id(user).username,
                        "score": submit.get_total_score(),
                        "status": submit.status,
                        "submit_id": submit.id
                    })
                else:
                    last["scores"].append({
                        "id": user, "username": User.by_id(user).username,
                        "score": 0, "status": "unsubmitted"
                    })

            problems.append(last)
        item["problems"] = problems
    result["create_time"] = str(result["create_time"])
    return make_response(0, message="操作完成", data=result)
