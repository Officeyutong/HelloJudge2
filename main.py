
import flask
from flask_sqlalchemy import SQLAlchemy

from common.user_operation import UserOperation
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
from common.log import LogManager
from redis import ConnectionPool
from typing import Optional, Set, NoReturn, Union
import os
import celery
from flask_cors import CORS
from flask_migrate import Migrate
from api.model_api import ModelAPI
from common.file_storage import FileStorage
import redis_lock
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
web_app = flask.Flask("HelloJudge2")
web_app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
web_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
web_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# web_app.config["SQLALCHEMY_ECHO"] = True
web_app.config["WTF_CSRF_TIME_LIMIT"] = 24*60*60
web_app.secret_key = config.SESSION_KEY
csrf = CSRFProtect()
# csrf.
if config.ENABLE_CSRF_TOKEN:
    csrf.init_app(web_app)
limiter = Limiter(
    web_app,
    key_func=get_remote_address,
    default_limits=config.RATE_LIMIT,
)
if config.DEBUG:
    import logging
    logging.getLogger('flask_cors').level = logging.DEBUG
db = SQLAlchemy(web_app)
db.session.execute("SET NAMES utf8mb4")
model_api = ModelAPI(db)
migrate = Migrate(web_app, db)

CORS(web_app, supports_credentials=True, resources={
    ".*": {"origins": "*", "supports_credentials": True}
})
basedir = os.path.dirname(__file__)
logger = web_app.logger
socket = SocketIO(web_app, async_mode="eventlet", logger=True)
queue = celery.Celery(
    web_app.name,  broker=config.REDIS_URI)
remote_judge_queue = celery.Celery(
    web_app.name,  broker=config.REMOTE_JUDGE_BROKER)
background_task_queue = celery.Celery(
    web_app.name, broker=config.BACKGROUNDTASK_URI)
redis_connection_pool = ConnectionPool.from_url(config.CACHE_URL)

lock_conn_pool = ConnectionPool.from_url(config.REDIS_LOCK_URI)


def get_permissions(uid: Union[int, str]) -> Set[str]:
    from models import User, PermissionGroup
    user: User = db.session.query(
        User.permissions, User.permission_group).filter(User.id == uid).one_or_none()
    permissions = set(user.permissions)
    group: PermissionGroup = db.session.query(PermissionGroup.permissions, PermissionGroup.inherit).filter(
        PermissionGroup.id == user.permission_group).one()
    permissions = permissions.union(group.permissions)
    while group.inherit:
        group = db.session.query(PermissionGroup.permissions, PermissionGroup.inherit).filter(
            PermissionGroup.id == group.inherit).one()
        permissions = permissions.union(group.permissions)
    return permissions.union(group.permissions)


def add_permission(uid: Union[int, str], perm: str):
    from models import User
    user: User = db.session.query(User).filter(User.id == uid).one()
    user.permissions = [*user.permissions, perm]
    user.permissions = [
        item for item in user.permissions if item != perm] + [perm]
    db.session.commit()


permission_manager: PermissionManager = PermissionManager(
    redis_connection_pool, db, get_permissions, add_permission, set())

log_manager: LogManager = LogManager(
    redis_connection_pool, config.DEFAULT_LOG_EXPIRE)

file_storage = FileStorage(db)

user_operation = UserOperation(db, permission_manager)


def _import_routes():
    import routes
    from routes.api_contest import router as contest
    from routes.api_permissionpack import router as permissionpack
    from routes.api_problemtodo import router as problemtodo
    from routes.api_virtualcontest import router as virtualcontest
    from routes.api_blog import router as blog
    from routes.api_log import router as log
    from routes.api_wiki import router as wiki
    from routes.api_preliminary import router as preliminary
    from routes.api_phoneutil import router as phoneutil
    from routes.api_phoneuser import router as phoneuser
    from routes.api_misc import router as misc
    from routes.api_solution import router as solution
    from routes.api_permission import router as permission
    from routes.api_team import router as team
    from routes.api_imagestore import router as imagestore
    web_app.register_blueprint(
        contest, url_prefix="/api/contest")
    web_app.register_blueprint(
        problemtodo, url_prefix="/api/problemtodo")
    web_app.register_blueprint(
        permissionpack, url_prefix="/api/permissionpack")
    web_app.register_blueprint(
        virtualcontest, url_prefix="/api/virtualcontest")
    web_app.register_blueprint(
        blog, url_prefix="/api/blog")
    web_app.register_blueprint(
        log, url_prefix="/api/log")
    web_app.register_blueprint(
        wiki, url_prefix="/api/wiki")
    web_app.register_blueprint(
        preliminary, url_prefix="/api/preliminary")
    web_app.register_blueprint(
        phoneutil, url_prefix="/api/phoneutil")
    web_app.register_blueprint(
        phoneuser, url_prefix="/api/phoneuser")
    web_app.register_blueprint(
        misc, url_prefix="/api/misc")
    web_app.register_blueprint(
        solution, url_prefix="/api/solution")
    web_app.register_blueprint(
        permission, url_prefix="/api/permission")
    web_app.register_blueprint(
        team, url_prefix="/api/team")
    web_app.register_blueprint(
        imagestore, url_prefix="/api/imagestore")
    


def _init_web_app():
    _import_routes()
    from common.permission_provider import DefaultPermissionProvider
    provider = DefaultPermissionProvider(db)
    permission_manager.add_provider("team", provider.get_team_permissions)
    permission_manager.add_provider(
        "problemset", provider.get_problemset_permissions)
    permission_manager.add_provider(
        "permissionpack", provider.get_permissionpack_permissions)
    permission_manager.add_provider(
        "contest", provider.get_contest_permissions)
    permission_manager.add_provider(
        "allteams", provider.get_allteams_permissions
    )
    permission_manager.add_provider(
        "challenge-access", provider.get_challenge_access)
    permission_manager.add_provider(
        "all-challenge", provider.get_all_challenge_access)
    permission_manager.add_provider(
        "challenge-finish", provider.get_challenge_finish)    
    


_init_web_app()
