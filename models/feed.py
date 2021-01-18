from main import db
from sqlalchemy.dialects import mysql
from sqlalchemy import Column, Integer, DateTime, ForeignKey
import datetime


class Feed(db.Model):
    __tablename__ = "feed"
    id = Column(Integer, primary_key=True)
    # 发送者用户ID
    uid = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE"), nullable=False, index=True)
    # 发送时间
    time = Column(DateTime, nullable=False,
                  default=datetime.datetime.now, index=True)
    # 内容
    content = Column(mysql.LONGTEXT, nullable=True)
    # 是否置顶
    top = Column(mysql.TINYINT(display_width=1), default=False, index=True)
