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
        "acceptedSubmissionCount": db.session.query(Submission).filter(Submission.status == "accepted").count()
    }
    return make_response(0, data=result)
