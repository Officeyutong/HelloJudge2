import redis
from typing import Optional


class LogManager:
    def __init__(
            self,
            redis_conn_pool: redis.ConnectionPool,
            timeout: int):
        self.__pool = redis_conn_pool
        self.__timeout = timeout

    def set_log(self, log_key: str, log: str) -> None:
        client = redis.Redis(connection_pool=self.__pool)
        key = f"hj2-log-{log_key}"
        client.set(key, log.encode(), ex=self.__timeout)

    def get_log(self, log_key: str) -> Optional[str]:
        client = redis.Redis(connection_pool=self.__pool)
        key = f"hj2-log-{log_key}"
        if not client.exists(key):
            return None
        val = client.get(key)
        client.set(key, val, ex=self.__timeout)
        return val.decode()
