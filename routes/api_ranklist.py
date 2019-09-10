from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models import *
from sqlalchemy.sql.expression import *


@app.route("/api/ranklist", methods=["POST", "GET"])
def global_ranklist():
    """
    全站排行榜
    page: 页码
    search: 过滤用户名

    {
        "code",
        "data":{
            "pageCount":"总页数",
            "ranklist":[
                "username":"用户名",
                "uid":"用户ID",
                "rating":"rating"
            ]
        }
    }
    """
    import math
    data: dict = request.get_json()
    query = db.session.query(User.id, User.username,
                             User.rating, User.description)
    if data["search"]:
        query = query.filter(User.username.like(f"%{data['search']}%"))
    pages = int(math.ceil(query.count()/config.USERS_ON_RANKLIST_PER_PAGE))
    page = data["page"]
    query = query.order_by(User.rating.desc())
    query = query.slice(
        (page-1)*config.USERS_ON_RANKLIST_PER_PAGE, (page)*config.USERS_ON_RANKLIST_PER_PAGE).all()
    result = {
        "pageCount": pages,
        "ranklist": []
    }
    ranklist = result["ranklist"]
    for x in query:
        ranklist.append({
            "username": x.username, "uid": x.id, "rating": x.rating, "description": x.description
        })
    return make_response(0, data=result)
