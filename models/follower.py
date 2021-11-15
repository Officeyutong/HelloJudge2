from main import db
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime


class Follower(db.Model):
    # 用户source对用户target的关注
    source = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        index=True)
    target = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        index=True)
    time = Column(DateTime, index=True, default=datetime.datetime.now)
