from main import db
from ormtypes.json_pickle import JsonPickle
from sqlalchemy.dialects import mysql
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql.expression import text
import uuid


class ProblemSet(db.Model):
    __tablename__ = "problem_set"
    # id
    id = Column(Integer, primary_key=True)
    # 所有者用户ID
    owner_uid = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=False)
    # 名称
    name = Column(String(100), nullable=False, default="新建习题集")
    # 是否私有
    # 如果私有,那么则必须输入正确的邀请码才能使用
    private = Column(mysql.TINYINT(display_width=1),
                     nullable=False, default=True)
    # 邀请码
    invitation_code = Column(mysql.LONGTEXT, nullable=True,
                             default=lambda: str(uuid.uuid1()))
    # 是否显示排行榜
    show_ranklist = Column(mysql.TINYINT(display_width=1),
                           nullable=False, default=False)
    # 题目列表 ["题目ID"]
    problems = Column(JsonPickle, nullable=False, default=[])
    # 创建时间
    create_time = Column(DateTime, nullable=False)
    # 说明
    description = Column(mysql.LONGTEXT, default="")
    # 外部题目
    # [{"name":"名称","url":"链接"}]
    foreign_problems = Column(JsonPickle, nullable=False, default=[])
