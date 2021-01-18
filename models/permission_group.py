from main import db
from ormtypes import json_pickle

from sqlalchemy import Column, String


class PermissionGroup(db.Model):
    __tablename__ = "permission_group"
    id = Column(String(20), primary_key=True)
    # 权限组名
    name = Column(String(50), nullable=False, default="新建权限组")
    # 权限列表
    permissions = Column(json_pickle.JsonPickle, nullable=False, default=[])
    # 继承自
    inherit = Column(String(20), nullable=False, default="")
