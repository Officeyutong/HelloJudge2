from main import db
from ormtypes import json_pickle


class PermissionGroup(db.Model):
    __tablename__ = "permission_groups"
    id = db.Column(db.String(20), primary_key=True)
    # 权限组名
    name = db.Column(db.String(50), nullable=False, default="新建权限组")
    # 权限列表
    permissions = db.Column(json_pickle.JsonPickle, nullable=False, default=[])
