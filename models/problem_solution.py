import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from main import db
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT, TINYINT


class ProblemSolution(db.Model):
    __tablename__ = "problem_solution"
    id = Column(Integer, primary_key=True)
    # 提交者ID
    uid = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), index=True)
    user = relationship("User", backref="problem_solutions", foreign_keys=[uid])
    # 题目ID
    problem_id = Column(Integer, ForeignKey(
        "problem.id", ondelete="CASCADE", onupdate="CASCADE"), index=True)
    problem = relationship("Problem", backref="solutions",
                           foreign_keys=[problem_id])
    # 题解内容
    content = Column(LONGTEXT, nullable=False)
    upload_time = Column(
        DateTime, default=datetime.datetime.now, nullable=False, index=True)
    # 是否置顶
    top = Column(TINYINT(1), nullable=False, default=False, index=True)
    # 是否经过审核
    verified = Column(TINYINT(1), nullable=False, default=False, index=True)
    # 审核者
    verifier = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True, default=None)
    # 审核时间
    verify_time = Column(DateTime, default=None, nullable=True)
    # 审核评语
    verify_comment  = Column(LONGTEXT, nullable=True)
