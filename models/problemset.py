from main import db
from ormtypes.json_pickle import JsonPickle


class ProblemSet(db.Model):
    __tablename__ = "problem_set"
    # id
    id = db.Column(db.Integer, primary_key=True)
    # 所有者用户ID
    owner_uid = db.Column(db.Integer, nullable=False)
    # 名称
    name = db.Column(db.String(100), nullable=False, default="新建习题集")
    # 是否私有
    # 如果私有,那么则必须输入正确的邀请码才能使用
    private = db.Column(db.Boolean, nullable=False, default=False)
    # 邀请码
    invitation_code = db.Column(db.String(100), nullable=True, default="")
    # 是否显示排行榜
    show_ranklist = db.Column(db.Boolean, nullable=False, default=False)
    # 题目列表 ["题目ID"]
    problems = db.Column(JsonPickle, nullable=False, default=[])
    # 创建时间
    create_time = db.Column(db.DateTime, nullable=False)
    # 说明
    description = db.Column(db.Text, default="")
