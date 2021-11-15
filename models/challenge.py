from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import Boolean
from main import db

from ormtypes.json_pickle import JsonPickle

from sqlalchemy import Column, Integer, Text, String, ForeignKey


class Challenge(db.Model):
    __tablename__ = "challenge"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, default="新建挑战")
    # 挑战的等级，每个挑战的等级必须为一个互不相同正整数
    # 要获得使用一个挑战(非level=1)的权限，则必须通过比该挑战level低的所有挑战
    # level=1的挑战不需要前置条件
    # 通过一个挑战需要获取challenge.finish.挑战ID.习题集ID1 challenge.finish.挑战ID.习题集ID2...等该挑战下的所有习题集
    # 通过一个挑战后申请获取challenge.finish.挑战ID.all权限
    # 需要具有challenge.access.挑战ID(level=1的挑战除外)才可访问一个挑战
    level = Column(Integer, nullable=False,
                   default=1, unique=True, index=True)
    # 挑战的说明
    description = Column(Text, nullable=True)
    # 挑战包括的习题集列表
    problemset_list = Column(JsonPickle, nullable=False, default=[])


class ChallengeRecord(db.Model):
    __tablename__ = "challenge_record"
    # 用户ID
    uid = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    # 挑战ID
    challenge_id = Column(Integer, ForeignKey(
        "challenge.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    # 习题集
    problemset_id = Column(Integer, ForeignKey(
        "problem_set.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    
    # False表示已解锁未完成，True表示已完成
    finished = Column(Boolean, default=False, index=True)
