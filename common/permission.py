import redis
from flask_sqlalchemy import SQLAlchemy
from models import User


class PermissionManager:
    def __init__(self, redis_conn_pool: redis.ConnectionPool, db_client: SQLAlchemy):
        self.pool=redis_conn_pool
        self.db=db_client
    # def 