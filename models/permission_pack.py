from main import db

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects import mysql

from ormtypes.json_pickle import JsonPickle


class PermissionPack(db.Model):
    __tablename__ = "permission_pack"
    id = Column(Integer, primary_key=True)
    name = Column(mysql.TEXT, nullable=False, default="")
    description = Column(mysql.LONGTEXT, nullable=True)
    permissions = Column(JsonPickle, nullable=False, default=[])


class PermissionPackUser(db.Model):
    __tablename__ = "permission_pack_user"
    pack_id = Column(Integer, ForeignKey(
        "permission_pack.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    phone = Column(String(20), primary_key=True)
    claimed = Column(mysql.TINYINT(display_width=1),
                     nullable=False, default=False)
