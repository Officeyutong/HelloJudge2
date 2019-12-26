
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
from typing import Set, NoReturn
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
    web_app.name,  broker=config.REDIS_URI)
remote_judge_queue = celery.Celery(
    web_app.name,  broker=config.REMOTE_JUDGE_BROKER)
redis_connection_pool = ConnectionPool.from_url(config.CACHE_URL)


def get_permissions(uid: int) -> Set[str]:
    from models import User, PermissionGroup
    user: User = db.session.query(
        User.permissions, User.permission_group).filter(User.id == uid).one()
    permissions = set(user.permissions)
    group: PermissionGroup = db.session.query(PermissionGroup.permissions, PermissionGroup.inherit).filter(
        PermissionGroup.id == user.permission_group).one()
    permissions = permissions.union(group.permissions)
    while group.inherit:
        group = db.session.query(PermissionGroup.permissions, PermissionGroup.inherit).filter(
            PermissionGroup.id == group.inherit).one()
        permissions = permissions.union(group.permissions)
    return permissions.union(group.permissions)


def add_permission(uid: int, perm: str) -> NoReturn:
    from models import User
    user: User = db.session.query(User).filter(User.id == uid).one()
    user.permissions = [*user.permissions, perm]
    db.session.commit()


permission_manager: PermissionManager = PermissionManager(
    redis_connection_pool, db, get_permissions, add_permission)


def _import_routes():
    import routes


_import_routes()
