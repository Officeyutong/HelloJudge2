from main import db

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects import mysql

import datetime


class VirtualContest(db.Model):
    __tablename__ = "virtual_contest"
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

    def running(self) -> bool:
        return self.start_time <= datetime.datetime.now() <= self.end_time
