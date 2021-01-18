from models.follower import Follower
from time import sleep
from models.submission import Submission
import typing

from main import background_task_queue, db, config, permission_manager, redis_connection_pool
from main import web_app as app
from common.permission import require_permission
from common.utils import unpack_argument
from flask_sqlalchemy import BaseQuery
from flask import session
import flask
from utils import make_response
from models.user import User
from models.feed import Feed
import sqlalchemy.sql.expression as expr
from sqlalchemy.sql import func
from api.feed import rebuild_feed_cache, rebuild_global_feed_cache
import math
import redis
import json


@app.route("/api/feed/get_feeds", methods=["POST"])
@unpack_argument
def api_feed_get_feeds(uid: int, page: int = 1):
    """
    获取某个用户的动态
    {
        "uid":"用户ID",
        "username":"用户名",
        "email":"邮箱",
        "time":"发送时间",
        "content":"内容'
    }
    """
    total_count = db.session.query(Feed).filter_by(uid=uid).count()
    page_count = int(math.ceil(total_count/config.USERFEEDS_PER_PAGE))
    resp = db.session.query(Feed.content, Feed.time, User.id, User.email, User.username).join(User, User.id == Feed.uid).filter(Feed.uid == uid).slice(
        (page-1)*config.USERFEEDS_PER_PAGE,
        page*config.USERFEEDS_PER_PAGE
    ).all()

    return make_response(0, data=[{
        "uid": item.id,
        "username": item.username,
        "email": item.email,
        "time": str(item.time),
        "content": item.content
    } for item in resp], pageCount=page_count)


@app.route("/api/feed/toggle_top_state", methods=["POST"])
@unpack_argument
@require_permission(manager=permission_manager, permission="feed.manage")
def api_feed_toggle_top_state(feedID: int):
    feed: Feed = db.session.query(Feed).filter_by(id=feedID).one_or_none()
    if not feed:
        return make_response(-1, message="该feed不存在")
    feed.top = not feed.top
    db.session.commit()
    return make_response(0, message="操作完成", topped=feed.top)


@app.route("/api/feed/get_feed_stream", methods=["POST"])
def api_feed_get_feed_stream():
    """
    [
        {
            "id":"feedID",
            "uid":"发送者的用户ID",
            "email":"发送者的邮箱",
            "time":"发送时间",
            "content":"内容",
            "top":"是否置顶",
            "username":"发送者用户名"
        }
    ]
    """
    client = redis.Redis(connection_pool=redis_connection_pool)
    if not session.get("uid", None):
        key = f"hj2-feed-cache-global"
        if not client.exists(key):
            rebuild_global_feed_cache()
    else:
        uid = int(session.get("uid"))

        key = f"hj2-feed-cache-{uid}"
        if not client.exists(key):
            rebuild_feed_cache(uid)
    result = []
    length = client.llen(key)
    for item in client.lrange(key, 0, length):
        result.append(json.loads(item.decode()))
    return make_response(0, data=result)
