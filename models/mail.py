from main import db

from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey


class Mail(db.Model):
    __tablename__ = "mail"
    id = Column(Integer, primary_key=True)
    # 发送者用户ID
    from_id = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=False)
    # 接收者用户ID
    to_id = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=False)
    # 发送时间
    time = Column(DateTime, nullable=False, index=True)
    # 内容
    text = Column(Text)
