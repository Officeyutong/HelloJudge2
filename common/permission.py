import redis
from flask_sqlalchemy import SQLAlchemy
from functools import wraps


class PermissionManager:
    def __init__(self, redis_conn_pool: redis.ConnectionPool, db_client: SQLAlchemy, permission_getter):
        self.pool = redis_conn_pool
        self.db = db_client
        self.permission_getter = permission_getter

    def _load_into_cache(self, uid: int):
        conn = redis.Redis(connection_pool=self.pool)
        set_name = f"hj2-perm-{uid}"
        permissions = self.permission_getter(uid)
        if not permissions:
            return
        conn.delete(set_name)
        # print(self.permission_getter(uid))
        conn.sadd(set_name, *permissions)

    def has_permission(self, uid: int, permission: str) -> bool:
        if not uid:
            return False
        conn = redis.Redis(connection_pool=self.pool)
        set_name = f"hj2-perm-{uid}"
        if not conn.exists(set_name):
            self._load_into_cache(uid)
        # 取消的优先级高于一切
        if conn.sismember(set_name, "-"+permission):
            return False
        # 有这个权限或者有任意权限
        if conn.sismember(set_name, permission) or conn.sismember(set_name, "*"):
            return True
        # 有某个子权限下的任意权限
        for idx, elem in enumerate(permission):
            if elem == ".":
                if conn.sismember(set_name, permission[:idx+1]+"*"):
                    return True
        return False


def require_permission(manager: PermissionManager, permission: str, details=False):
    from flask import session
    from utils import make_response

    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            if not manager.has_permission(session.get("uid", None), permission):
                return make_response(-1, message=f"你需要{permission}权限才能这样做" if details else "你没有权限这样做")
            return func(*args, **kwargs)
        return _wrapper
    return wrapper
