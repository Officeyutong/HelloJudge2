import redis
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from typing import Callable, Union, List, Set, NoReturn


class PermissionManager:
    def __init__(self,
                 redis_conn_pool: redis.ConnectionPool,
                 db_client: SQLAlchemy,
                 permission_getter: Callable[[Union[int, str]], Set[str]],
                 permission_adder: Callable[[Union[int, str], str], None],
                 ):
        self.pool = redis_conn_pool
        self.db = db_client
        self.permission_getter = permission_getter
        self.permission_adder = permission_adder

    def _load_into_cache(self, uid: int):
        conn = redis.Redis(connection_pool=self.pool)
        set_name = f"hj2-perm-{uid}"
        permissions = self.permission_getter(uid)
        if not permissions:
            return
        conn.delete(set_name)
        # print(self.permission_getter(uid))
        conn.sadd(set_name, *permissions)

    def refresh_user(self, uid: int) -> None:
        """刷新某个用户的缓存"""
        conn = redis.Redis(connection_pool=self.pool)
        conn.delete(f"hj2-perm-{uid}")

    def add_permission(self, uid: int, perm: str) -> None:
        self.permission_adder(uid, perm)
        print(f"adding {perm=} to {uid=}")
        # 刷新缓存
        conn = redis.Redis(connection_pool=self.pool)
        conn.delete(f"hj2-perm-{uid}")

    def has_any_permission(self, uid, *perms) -> bool:
        return any((self.has_permission(uid, x) for x in perms))

    def has_permission(self, uid: int, permission: str) -> bool:
        if uid is None:
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


def require_permission(manager: PermissionManager, permission: str, details=True):
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
