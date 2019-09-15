from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models import *
from sqlalchemy.sql.expression import *


@app.route("/api/admin/show", methods=["POST"])
def admin_show():
    """
    获取后台信息
    """
    if not session.get("uid"):
        return make_response(-1, message="你没有权限这么做")
    user: User = User.by_id(session.get("uid"))
    if not user.is_admin:
        return make_response(-1, message="你没有权限这么做")
    result = {
        "problemCount": db.session.query(Problem).count(),
        "publicProblemCount": db.session.query(Problem).filter(Problem.public == True).count(),
        "submissionCount": db.session.query(Submission).count(),
        "userCount": db.session.query(User).count(),
        "discussionCount": db.session.query(Discussion).count(),
        "acceptedSubmissionCount": db.session.query(Submission).filter(Submission.status == "accepted").count(),
        "settings": []
    }
    settings = result["settings"]
    for k, v in config.VISIBLE_SETTINGS.items():
        settings.append({
            "key": k,
            "value": getattr(config, k),
            "description": v
        })

    return make_response(0, data=result)


@app.route("/api/admin/rating/remove", methods=["POST"])
def admin_rated_contest_remove():
    """
    删除一场比赛及其之后比赛的rating造成的影响
    {
        "contestID":比赛ID
    }
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    if not user.is_admin:
        return make_response(-1, message="你没有权限进行此操作")
    data = request.get_json()
    from typing import List, Tuple
    contest = Contest.by_id(data["contestID"])

    def drop_contest(contest_id):
        print(f"Droping {contest_id}")
        users: List[Tuple[int]] = db.session.query(Submission.uid).filter(
            Submission.contest_id == contest_id).distinct().all()
        for x in users:
            user: User = User.by_id(x.uid)
            user.rating_history = [
                x for x in user.rating_history.copy() if x["contest_id"] != contest_id]
            user.rating = user.get_rating()
        current_contest: Contest = Contest.by_id(contest_id)
        current_contest.rated = False
        current_contest.rated_time = None
    contests = db.session.query(Contest.id).filter(Contest.rated == True).filter(
        Contest.rated_time >= contest.rated_time).all()
    for x in contests:
        drop_contest(x.id)
    db.session.commit()
    return make_response(0, message="完成")


@app.route("/api/admin/rating/rated_contests", methods=["POST"])
def admin_rated_contests():
    """ 
    获取rated比赛列表

    [
        {
            "ratedTime":"rated应用时间",
            "contestID":"比赛ID",
            "contestName":"比赛名",
            "contestantCount":"参赛人数"
        }
    ]
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    if not user.is_admin:
        return make_response(-1, message="你没有权限进行此操作")
    query = db.session.query(Contest.id, Contest.name, Contest.rated_time).filter(
        Contest.rated == True).order_by(Contest.rated_time.desc()).all()
    result = [

    ]
    for x in query:
        result.append({
            "ratedTime": x.rated_time,
            "contestID": x.id,
            "contestName": x.name,
            "contestantCount": db.session.query(Submission.uid).filter(Submission.contest_id == x.id).distinct().count()
        })
    return make_response(0, data=result)


@app.route("/api/admin/rating/append", methods=["POST"])
def admin_rating_append():
    """
    应用某场比赛的rating
    {
        "contestID":"比赛ID"
    }
    {
        "code","message"
    }
    """
    data: dict = request.get_json()
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    user: User = User.by_id(session.get("uid"))
    if not user.is_admin:
        return make_response(-1, message="你没有权限进行此操作")
    contest: Contest = Contest.by_id(data["contestID"])
    if not contest:
        return make_response(-1, message="比赛ID不存在")
    if contest.rated:
        return make_response(-1, message="此比赛已rated！")
    if contest.running():
        return make_response(-1, message="比赛还在进行!")
    from routes import get_contest_rank_list
    from cf_rating import Contestant, calculate_rating
    from typing import List
    ranklist = get_contest_rank_list(contest)
    if len(ranklist["ranklist"]) <= 1:
        return make_response(-1, message="至少有2人参加的比赛才可以应用rating")
    contestants = []
    for i, item in enumerate(ranklist["ranklist"]):
        contestants.append(Contestant(
            identifier=item["uid"],
            before_rating=db.session.query(User.rating).filter(
                User.id == item["uid"]).one().rating,
            rank=i+1
        ))
    print(contestants)
    rating_result: List[Contestant] = calculate_rating(contestants)
    print(rating_result)
    for x in rating_result:
        current_user: User = User.by_id(x.identifier)
        old = current_user.rating_history.copy()
        old.append({
            "result": x.after_rating-x.before_rating,
            "contest_id": contest.id
        })
        current_user.rating_history = old
        current_user.rating = current_user.get_rating()
    contest.rated = True
    from datetime import datetime
    contest.rated_time = datetime.now()
    db.session.commit()

    return make_response(0, message="完成")
