from main import db

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
import datetime

CURR_TABLE_NAME = "virtual_contest"


class VirtualContest(db.Model):
    __tablename__ = CURR_TABLE_NAME
    id = Column(Integer, primary_key=True)
    # 创建者ID
    owner_id = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=False, index=True)
    # 对应的实际比赛ID
    contest_id = Column(Integer, ForeignKey(
        "contest.id", ondelete="CASCADE"), nullable=False, index=True)
    # 开始时间
    start_time = Column(DateTime, nullable=False)
    # 结束时间
    end_time = Column(DateTime, nullable=False)
    related_contest = relationship(
        "Contest", backref=CURR_TABLE_NAME, foreign_keys=[contest_id])
    name = association_proxy("related_contest", "name")
    description = association_proxy("related_contest", "description")
    problems = association_proxy("related_contest", "problems")
    judge_result_visible = association_proxy(
        "related_contest", "judge_result_visible")
    rank_criterion = association_proxy("related_contest", "rank_criterion")
    uid = association_proxy("related_contest", "uid")

    def running(self) -> bool:
        return self.start_time <= datetime.datetime.now() <= self.end_time
