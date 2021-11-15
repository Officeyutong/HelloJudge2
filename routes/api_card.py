from models.problem import Problem
from models.submission import Submission
import typing

from main import background_task_queue, db, config, permission_manager
from main import web_app as app
from common.permission import require_permission
from common.utils import unpack_argument
from flask_sqlalchemy import BaseQuery
from flask import session
from utils import make_response
from models.user import User
import sqlalchemy.sql.expression as expr
from sqlalchemy.sql import func
import flask

@app.route("/api/card/problem", methods=["POST"])
@unpack_argument
def api_card_problem(problemID: int):
    """
    获取题目卡片数据
    {
        "id":"题目ID",
        "title":"题目名",
        "acceptedCount":"AC数",
        "submitCount":"总提交数",
        "myStatus":{ //如果不存在则为空
            "score":"我的分数",
            "fullScore":"题目满分",
            "status":"提交状态",
            "submissionID":"提交ID"
        }
    }
    """
    problem: Problem = db.session.query(
        Problem.id,
        Problem.title,
        Problem.cached_accepted_count,
        Problem.cached_submit_count,
        Problem.subtasks).filter(Problem.id == problemID).one_or_none()
    if not problem:
        flask.abort(404)
    result = {
        "id": problem.id,
        "title": problem.title,
        "acceptedCount": problem.cached_accepted_count,
        "submitCount": problem.cached_submit_count,
        "myStatus": None
    }
    my_submission: Submission = db.session.query(
        Submission.id,
        Submission.score,
        Submission.status
    ).filter(expr.and_(
        Submission.uid == session.get("uid", -1),
        Submission.problem_id == problemID
    )).order_by(Submission.score.desc()).limit(1).one_or_none()
    if my_submission:
        result["myStatus"] = {
            "score": my_submission.score,
            "fullScore": sum(item["score"] for item in problem.subtasks),
            "status": my_submission.status,
            "submissionID": my_submission.id
        }
    return make_response(0, data=result)
