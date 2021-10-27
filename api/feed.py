from models import feed
from models.follower import Follower
from models.user import User
from main import db, redis_connection_pool, config, lock_conn_pool
from models.feed import Feed
from sqlalchemy.sql import expression as expr
from const_var import SYSTEM_NOTIFICATION_USERID
import json
import redis
import redis_lock


def send_feed(uid: int, top: bool, content: str) -> int:
    """
    发送feed，返回feed_id
    """
    feed = Feed(
        uid=uid,
        content=content,
        top=top
    )
    db.session.add(feed)
    db.session.commit()
    return feed.id


def rebuild_global_feed_cache():
    """
    重建未登录用户的feed缓存
    """
    with redis_lock.Lock(redis.Redis(connection_pool=lock_conn_pool), name=f"feed-refresh-lock-common", expire=3, auto_renewal=True):
        client = redis.Redis(connection_pool=redis_connection_pool)
        key = f"hj2-feed-cache-global"
        if client.exists(key):
            client.delete(key)
        feeds = db.session.query(Feed.id, Feed.uid, Feed.time, Feed.top, Feed.content, User.username, User.email).join(User, User.id == Feed.uid).filter(expr.or_(
            Feed.uid == SYSTEM_NOTIFICATION_USERID,
        )).distinct().order_by(Feed.time.desc()).order_by(Feed.top.desc()).limit(config.FEED_STREAM_COUNT_LIMIT).all()
        for item in feeds:
            # print(item)
            client.rpush(key, json.dumps(
                {
                    "id": item.id,
                    "uid": item.uid,
                    "username": item.username,
                    "email": item.email,
                    "time": str(item.time),
                    "top": bool(item.top),
                    "content": item.content
                }
            ))
        client.expire(key, config.FEED_STREAM_REFRESH_INTERVAL)


def rebuild_feed_cache(uid: int):
    """
    """
    with redis_lock.Lock(redis.Redis(connection_pool=lock_conn_pool), name=f"feed-refresh-lock-{uid}", expire=3, auto_renewal=True):
        print(f"Refreshing feed for {uid=}")
        client = redis.Redis(connection_pool=redis_connection_pool)
        key = f"hj2-feed-cache-{uid}"
        subquery = db.session.query(
            Follower.target).filter_by(source=uid)
        feeds_query = db.session.query(Feed.id, Feed.uid, Feed.time, Feed.top, Feed.content, User.username, User.email).join(User, User.id == Feed.uid).filter(expr.or_(
            Feed.uid == SYSTEM_NOTIFICATION_USERID,  # 所有用户强制关注系统通知
            Feed.uid.in_(subquery)
        )).order_by(Feed.top.desc()).order_by(Feed.time.desc()).limit(config.FEED_STREAM_COUNT_LIMIT)
        feeds = feeds_query.all()
        print(feeds)
        if client.exists(key):
            client.delete(key)
        for item in feeds:
            # print(item)
            client.rpush(key, json.dumps(
                {
                    "id": item.id,
                    "uid": item.uid,
                    "username": item.username,
                    "email": item.email,
                    "time": str(item.time),
                    "top": bool(item.top),
                    "content": item.content
                }
            ))
        client.expire(key, config.FEED_STREAM_REFRESH_INTERVAL)
