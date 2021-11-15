from main import db

from ormtypes.json_pickle import JsonPickle
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from sqlalchemy.dialects import mysql

import uuid


class Team(db.Model):
    __tablename__ = "team"
    # ID
    id = Column(Integer, primary_key=True)
    # 团队名
    name = Column(String(30), nullable=False, default="新建团队")
    # 团队描述
    description = Column(mysql.LONGTEXT, nullable=True, default="")
    # 所有者ID
    owner_id = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # 成员列表，list[int]
    # members = Column(JsonPickle, default=[], nullable=False)
    # 除了创建者之外的管理员列表
    # admins = Column(JsonPickle, default=[], nullable=False)
    # 团队任务列表
    # [{"name":"xxxx","problems":[1,2,3,4]}]
    tasks = Column(JsonPickle, default=[], nullable=False)
    # 创建时间
    create_time = Column(DateTime, nullable=False)
    # 是否私有，如果私有则需要用户具有team.use.题目ID权限
    private = Column(mysql.TINYINT(display_width=1), default=False)
    # 邀请码，输入此邀请码可以加入私有团队
    invite_code = Column(mysql.TEXT,  default=lambda: str(uuid.uuid1()))
    # 团队题目 [题目ID]
    team_problems = Column(JsonPickle, default=[])
    # 团队比赛 [比赛ID]
    team_contests = Column(JsonPickle, default=[])
    # 团队习题集
    team_problemsets = Column(JsonPickle, default=[])
    # 团队成员可以获得使用上述私有题目和私有比赛和私有习题集的权限

    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret

    def by_id(id):
        return db.session.query(Team).filter(Team.id == id).one_or_none()


class TeamMember(db.Model):
    # 表示一条用户的团队关系
    __tablename__ = "team_member"
    uid = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    # 团队
    team_id = Column(Integer, ForeignKey(
        "team.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    # 是否是管理
    is_admin = Column(mysql.TINYINT(display_width=1),
                      default=False, index=True)


class TeamFile(db.Model):
    __tablename__ = "team_file"
    team_id = Column(Integer, ForeignKey(
        "team.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    file_id = Column(String(128), ForeignKey(
        "file_storage.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    uid = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
