from models.preliminary_contest import PreliminaryProblem
from flask import Blueprint
from main import db, config
from common.utils import unpack_argument
from utils import make_response
from models import PreliminaryContest, PreliminaryContest, PreliminaryProblemType
from models.user import User
import math
router = Blueprint("preliminary", __name__)


@router.route("/contest/list", methods=["POST"])
@unpack_argument
def preliminary_contest_list(page: int):
    query = db.session.query(
        PreliminaryContest.title,
        PreliminaryContest.id,
        PreliminaryContest.duration
    )
    page_count = int(
        math.ceil(query.count()/config.PRELIMINARY_CONTESTS_PER_PAGE))
    result = query.slice((page-1)*config.PRELIMINARY_CONTESTS_PER_PAGE,
                         page*config.PRELIMINARY_CONTESTS_PER_PAGE).all()
    return make_response(0, data=[
        {
            "title": item.title,
            "id": item.id,
            "duration": item.duration
        } for item in result
    ], pageCount=page_count)


@router.route("/contest/detail", methods=["POST"])
@unpack_argument
def preliminary_contest_detail(id: int):
    """
    {
        "title":"比赛标题",
        "description":"比赛描述",
        "uploader":{
            "uid":"",
            "username":""
        },
        "duration":"",
        "upload_time":"",
        "problems":[]
    }
    """

    contest: PreliminaryContest = db.session.query(
        PreliminaryContest.id,
        PreliminaryContest.title,
        PreliminaryContest.description,
        PreliminaryContest.uploader,
        PreliminaryContest.duration,
        PreliminaryContest.upload_time,
        User.username
    ).join(User, User.id == PreliminaryContest.uploader).filter(PreliminaryContest.id == id).one_or_none()
    if not contest:
        return make_response(-1, message="比赛不存在")
    result = {
        "title": contest.title,
        "description": contest.description,
        "uploader": {
            "uid": contest.uploader,
            "username": contest.username
        },
        "duration": contest.duration,
        "upload_time": contest.upload_time.timestamp(),
        "problems": []
    }
    problems = db.session.query(PreliminaryProblem).filter_by(
        contest=contest.id).order_by(PreliminaryProblem.problem_id.asc()).all()
    result["problems"] = [
        {
            "problemType": str(item.problem_type.value),
            "problemID": item.problem_id,
            "content": item.content,
            "questions": item.questions,
            "score": item.score
        } for item in problems
    ]
    return make_response(0, data=result)
