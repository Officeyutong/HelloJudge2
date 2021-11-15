from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Float
from sqlalchemy.dialects import mysql
from main import db
from ormtypes.json_pickle import JsonPickle
import datetime
import enum


class PreliminaryProblemType(enum.Enum):
    # 选择
    selection = "selection"
    # 填空
    fill_blank = "fill_blank"


class PreliminaryContest(db.Model):
    __tablename__ = "preliminary_contest"
    id = Column(Integer, primary_key=True)
    # 比赛标题
    title = Column(mysql.TEXT, default="", nullable=False)
    # 比赛描述
    description = Column(mysql.LONGTEXT, default="", nullable=True)
    # 比赛提供者
    uploader = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    # 比赛时长，秒
    duration = Column(Integer, nullable=False)
    # 上传时间
    upload_time = Column(
        DateTime, default=datetime.datetime.now, nullable=False, index=True)


class PreliminaryProblem(db.Model):
    __tablename__ = "preliminary_problem"
    id = Column(Integer, primary_key=True)
    # 比赛
    contest = Column(Integer, ForeignKey(
        "preliminary_contest.id", ondelete="CASCADE", onupdate="CASCADE"))
    # 题目种类
    problem_type = Column(Enum(PreliminaryProblemType), index=True)
    # 题号
    problem_id = Column(Integer, index=True, default=-1)
    # 题目内容，markdown
    content = Column(mysql.TEXT, default="")
    # 题目定义
    """
    [   选择:
        {
            "choices":[
                "选项1",
                "选项2"
            ],
            "answer":[
                "A","B"..
            ],
            "score":"该小题分值"
        },
        填空:{
            "score":"分值",
            "answers":[
                "答案1","答案2"...
            ],
            "multiline":"是否允许多行"
        }
    ]
    """
    questions = Column(JsonPickle, default=[], nullable=True)
    # 分值
    score = Column(Float, default=0, nullable=False)
