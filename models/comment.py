from main import db

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey


class Comment(db.Model):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    # 内容
    content = Column(Text, nullable=False)
    # 用户ID
    uid = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    # 发送时间
    time = Column(DateTime, nullable=False)
    # 讨论ID
    discussion_id = Column(Integer, ForeignKey(
        "discussion.id", ondelete="CASCADE"), nullable=False, index=True)
