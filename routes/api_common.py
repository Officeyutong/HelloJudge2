from main import web_app as app
from main import db
from models import User
from flask import session
import time


@app.before_request
def check_logout():
    if session.get("uid") and not session.get("login_time"):
        session.pop("uid")
        return
    user: User = db.session.query(User.force_logout_before).filter(
        User.id == session.get("uid", -1)).one_or_none()
    if user:
        login_time = int(session.get("login_time", 1))
        # print("Checking user :", session.get("uid"))
        # print(login_time)
        # print("Force logout before: ", user.force_logout_before)
        if login_time < user.force_logout_before:
            session.pop("uid")
            session.pop("login_time")


@app.before_request
def banned_check():
    if session.get("uid"):
        user: User = db.session.query(User.banned).filter(
            User.id == session.get("uid")).one()
        if user.banned:
            session.pop("uid")
