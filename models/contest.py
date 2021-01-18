from main import db
from typing import List, Mapping, Any
from ormtypes.json_pickle import JsonPickle
from models import User
from common.permission import PermissionManager
from sqlalchemy.dialects import mysql

from sqlalchemy import Column, Integer, String, Text, DateTime,  ForeignKey
from sqlalchemy.sql.expression import text

import datetime
import uuid


class Contest(db.Model):
    # 比赛ID
    id = Column(Integer, primary_key=True)
    # 所有者ID
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False)
    # 比赛名称
    name = Column(String(128), nullable=False, default="新建比赛")
    # 比赛描述
    description = Column(mysql.LONGTEXT, nullable=False, default="")
    # 开始时间
    start_time = Column(DateTime, nullable=False)
    # 结束时间
    end_time = Column(DateTime, nullable=False)
    # 题目列表,[{"id":1,"weight":1}]
    problems = Column(JsonPickle, nullable=False, default=[])
    # 比赛时可否看到排行总榜
    ranklist_visible = Column(mysql.TINYINT(display_width=1), nullable=False,
                              default=False)
    # 比赛时可否得知评测结果
    judge_result_visible = Column(
        mysql.TINYINT(display_width=1), nullable=False, default=0)
    # 排行依据
    # 如果排行依据为max_score，则按照题目最高分
    # 如果排行依据为last_submit，则按照最后一次提交的分数排序
    # 如果排行依据为penalty，则每道题AC即通过，非AC即未通过，首先按照通过题目数排名，题目数相同按照罚时排名
    rank_criterion = Column(
        String(20), nullable=False, default="max_score")
    # 比赛邀请码
    # 如果非空字符串，则必须正确输入邀请码才可进入比赛
    invite_code = Column(mysql.LONGTEXT, nullable=False,
                         default=lambda: str(uuid.uuid1()))
    # 是否已应用rating
    rated = Column(mysql.TINYINT(display_width=1), nullable=False, default=0)
    # 应用rating的时间
    rated_time = Column(DateTime, nullable=True)
    # 是否为私有比赛
    # 私有比赛需要用户拥有contest.use.比赛ID权限才可使用
    private_contest = Column(mysql.TINYINT(
        display_width=1), nullable=False, default=True)
    # 比赛是否关闭
    closed = Column(mysql.TINYINT(display_width=1),
                    default=False, nullable=True)

    @staticmethod
    def by_id(id):
        return db.session.query(Contest).filter(Contest.id == id).one_or_none()

    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret

    def running(self):
        import datetime
        now = datetime.datetime.now()
        return now >= self.start_time and now <= self.end_time

    def can_see_judge_result(self, uid, perm_manager: PermissionManager = None) -> bool:
        if not uid:
            return self.judge_result_visible
        user: User = User.by_id(uid)
        return (perm_manager.has_permission(user.id, "contest.manage")) or (user.id == self.owner_id) or (self.judge_result_visible) or (not self.running())

    def can_see_ranklist(self, uid, perm_manager: PermissionManager = None) -> bool:
        if not uid:
            return self.ranklist_visible
        user: User = User.by_id(uid)
        return (perm_manager.has_permission(user.id, "contest.manage")) or (user.id == self.owner_id) or (self.ranklist_visible) or (not self.running())


class Clarification(db.Model):
    __tablename__ = "contest_clarification"
    id = Column(Integer, primary_key=True)
    # 这个Clarification对应的比赛
    contest = Column(Integer, ForeignKey(
        "contest.id", ondelete="CASCADE"), index=True)
    # 发送者
    sender = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), index=True)
    # 发送时间
    send_time = Column(DateTime, default=datetime.datetime.now,
                       index=True, nullable=False)
    # 内容
    content = Column(mysql.LONGTEXT, default="")
    # 是否已回复
    replied = Column(mysql.TINYINT(display_width=1), index=True, default=False)
    # 回复者
    replier = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), index=True, nullable=True)
    # 回复内容
    reply_content = Column(mysql.LONGTEXT, default="")
    # 回复时间
    reply_time = Column(DateTime, index=True, nullable=True)
