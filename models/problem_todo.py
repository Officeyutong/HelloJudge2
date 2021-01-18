from main import db

from sqlalchemy import ForeignKey, Column, Integer, DateTime

import datetime


class ProblemTodo(db.Model):
    __tablename__ = "problem_todo"
    uid = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True
    )
    problem_id = Column(
        Integer,
        ForeignKey("problem.id", ondelete="CASCADE"),
        primary_key=True
    )
    join_time = Column(DateTime, default=datetime.datetime.now, index=True)
