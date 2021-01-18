from models.user import User
from main import db, web_app, permission_manager, config
from models.problem_todo import ProblemTodo
from models.problem import Problem
from models.submission import Submission
from utils import make_response
from flask import Blueprint, request, session
from common.utils import unpack_argument
from common.permission import require_permission
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
import math
import typing
router = Blueprint("problemtodo", __name__)


@router.route("/add", methods=["POST"])
@unpack_argument
def problemtodo_add(problemID: int):
    if not session.get("uid", None):
        return make_response(-1, message="请先登录")
    if db.session.query(ProblemTodo).filter_by(problem_id=problemID, uid=session.get("uid")).limit(1).count():
        return make_response(-1, message="此题目已经在您的题单内")
    if db.session.query(ProblemTodo).filter_by(uid=session.get("uid")).count() >= config.MAX_PROBLEMTODO_COUNT:
        return make_response(-1, message="已经达到了您的待做题目数上限")
    db.session.add(ProblemTodo(
        uid=session.get("uid"),
        problem_id=problemID
    ))
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/remove", methods=["POST"])
@unpack_argument
def problemtodo_remove(problemID: int):
    if not session.get("uid", None):
        return make_response(-1, message="请先登录")
    if db.session.query(ProblemTodo).filter_by(problem_id=problemID, uid=session.get("uid")).limit(1).count() == 0:
        return make_response(-1, message="此题目不在您的题单内")
    db.session.query(ProblemTodo).filter_by(
        uid=session.get("uid"), problem_id=problemID).delete()
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/all", methods=["POST"])
def problemtodo_all():
    """
    列出用户所有的待做题目
    [{
        "id":"题目ID",
        "title":"题目名",
        "joinTime":"加入时间",
        "submission":{
            "id":"提交ID", //-1表示未提交
            "status":"状态"
        }
    }]
    """
    if not session.get("uid", None):
        return make_response(-1, message="请先登录")
    result = []
    items = db.session.query(ProblemTodo.join_time, ProblemTodo.problem_id, Problem.title).join(
        Problem, Problem.id == ProblemTodo.problem_id).filter(ProblemTodo.uid == session.get("uid")).all()
    for item in items:
        submission = db.session.query(Submission.id, Submission.status).filter_by(
            uid=session.get("uid"),
            problem_id=item.problem_id
        ).order_by(Submission.score.desc()).limit(1).one_or_none()
        result.append({
            "id": item.problem_id,
            "title": item.title,
            "joinTime": str(item.join_time),
            "submission": {
                "id": submission.id if submission else -1,
                "status": submission.status if submission else "unsubmitted"
            }
        })
    return make_response(0, data=result)
