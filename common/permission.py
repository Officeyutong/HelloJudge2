import redis
import re
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

from typing import Callable, Optional, Union, List, Set,  Dict


PROVIDER_REF_EXPR = re.compile(
    r"\[provider:(?P<name>[a-zA-Z0-9\-]+)(\.(?P<arg>.+))?\]")


class PermissionManager:
    def __init__(self,
                 redis_conn_pool: redis.ConnectionPool,
                 db_client: SQLAlchemy,
                 permission_getter: Callable[[Union[int, str]], Set[str]],
                 permission_adder: Callable[[Union[int, str], str], None],
                 default_permissions: Set[str]
                 ):
        self.pool = redis_conn_pool
        self.db = db_client
        self.permission_getter = permission_getter
        self.permission_adder = permission_adder
        self.providers: Dict[str, Callable[[
            int, Optional[str]], Set[str]]] = dict()
        self.default_permissions = default_permissions

    def add_provider(self, name: str, handler: Callable[[
            int, Optional[str]], Set[str]]) -> None:
        self.providers[name] = handler

    def _parse_permission(self, text: str, uid: int) -> Set[str]:
        match = PROVIDER_REF_EXPR.match(text)
        # print(text,match)
        if match is None:
            return {text}
        result = match.groupdict()
        name = result["name"]
        arg = result["arg"]
        if name not in self.providers:
            print(
                f"Invalid provider when parsing the permissions of uid {uid}: '{name}'")
            return set()
        return self.providers[name](uid, arg)

    def _rec_parse_permission(self, perms: Set[str], uid: int, log: Set[str] = None) -> Set[str]:
        result: Set[str] = set()
        providers: Set[str] = set()
        for x in perms:
            if PROVIDER_REF_EXPR.match(x):
                providers.add(x)
            else:
                result.add(x)
        if log is None:
            log = set()
        for x in providers:
            if x in log:
                print(
                    f"Recursive provider reference when parsing uid `{uid}``, provider: `{x}`, log: `{log}`")
                return result
            result |= self._rec_parse_permission(
                self._parse_permission(x, uid), uid, log | {x})
        return result

    def _load_into_cache(self, uid: int):
        conn = redis.Redis(connection_pool=self.pool)
        set_name = f"hj2-perm-{uid}"
        permissions = self._rec_parse_permission(
            self.permission_getter(uid), uid)
        # print("result=",permissions)
        if not permissions:
            return
        conn.delete(set_name)
        # print(self.permission_getter(uid))
        conn.sadd(set_name, *permissions)
        conn.expire(set_name, 60)

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
            return permission in self.default_permissions
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

    def get_all_permissions(self, uid: int) -> List[str]:
        set_name = f"hj2-perm-{uid}"
        conn = redis.Redis(connection_pool=self.pool)
        if not conn.exists(set_name):
            self._load_into_cache(uid)
        return [x.decode() for x in conn.smembers(set_name)]


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
