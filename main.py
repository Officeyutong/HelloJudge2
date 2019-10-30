
import flask
from flask_sqlalchemy import SQLAlchemy
try:
    import config as config
except:
    import config_default as config
import logging
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
# from concurrent.futures import ThreadPoolExecutor
from common.permission import PermissionManager
from redis import ConnectionPool
import os
import celery
web_app = flask.Flask("HelloJudge2")
web_app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
web_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
web_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

web_app.secret_key = config.SESSION_KEY
csrf = CSRFProtect(web_app)
db = SQLAlchemy(web_app)
basedir = os.path.dirname(__file__)
logger = web_app.logger
socket = SocketIO(web_app)
queue = celery.Celery(
    web_app.name,  broker=config.REDIS_URI, backend=config.REDIS_URI)
redis_connection_pool = ConnectionPool.from_url(config.CACHE_URL)


def get_permissions(uid: int):
    from models import User, PermissionGroup
    user: User = db.session.query(User.permissions, User.permission_group).filter(User.id==uid).one()
    permissions=set(user.permissions)
    group:PermissionGroup=db.session.query(PermissionGroup.permissions).filter(PermissionGroup.id==user.permission_group).one()
    return permissions.union(group.permissions)


permission_manager = PermissionManager(
    redis_connection_pool, db, get_permissions)
import routes