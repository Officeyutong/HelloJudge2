from main import db
from sqlalchemy.dialects import mysql

from sqlalchemy import Column, Integer, Text, String,  DateTime, ForeignKey

from sqlalchemy.sql.expression import text


class Discussion(db.Model):
    __tablename__ = "discussion"
    # 讨论ID
    id = Column(Integer, primary_key=True)
    # 板块
    # 每一个板块使用一个字符串表示，比如discussion.problem.233 表示编号为233的题目的所有讨论
    # discussion.problem 表示所有题目的讨论
    # discussion.problem.global 表示题目全局讨论
    # discussion.global 表示全局讨论
    path = Column(String(128), index=True, nullable=False)
    # 标题
    title = Column(String(100), index=True, nullable=False)
    # 内容
    content = Column(Text, nullable=False)
    # 用户ID
    uid = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # 是否置顶
    top = Column(mysql.TINYINT(display_width=1),
                 default=0, nullable=False, index=True)
    # 发送时间
    time = Column(DateTime, nullable=False)
    # 是否为私有讨论
    # 私有讨论即只有发布者和有discussion.manage的用户可见
    private = Column(mysql.TINYINT(display_width=1),
                          nullable=True, default=None)

    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret

    @staticmethod
    def by_id(id):
        return db.session.query(Discussion).filter(Discussion.id == id).one_or_none()

    @staticmethod
    def has(id):
        return db.session.query(Discussion.id).filter(Discussion.id == id).count() != 0
