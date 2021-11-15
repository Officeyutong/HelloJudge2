from main import db

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects import mysql


class Tag(db.Model):
    __tablename__ = "tag"
    # 标签id
    id = Column(String(20), primary_key=True)
    # 显示名
    display = Column(mysql.LONGTEXT, default="新建标签", nullable=False)
    # SemanticUI颜色
    color = Column(String(30), nullable=False, default="")


class ProblemTag(db.Model):
    __tablename__ = "problemtag"
    problem_id = Column(Integer, ForeignKey(
        "problem.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    tag_id = Column(String(20), ForeignKey(
        "tag.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
