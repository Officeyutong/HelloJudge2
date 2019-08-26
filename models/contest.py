from main import db
from typing import List, Mapping, Any
from ormtypes.json_pickle import JsonPickle
from models import User


class Contest(db.Model):
    # 比赛ID
    id = db.Column(db.Integer, primary_key=True)
    # 所有者ID
    owner_id = db.Column(db.Integer, nullable=False)
    # 比赛名称
    name = db.Column(db.String(128), nullable=False, default="新建比赛")
    # 比赛描述
    description = db.Column(db.Text, nullable=False, default="")
    # 开始时间
    start_time = db.Column(db.DateTime, nullable=False)
    # 结束时间
    end_time = db.Column(db.DateTime, nullable=False)
    # 题目列表,[{"id":1,"weight":1}]
    problems = db.Column(JsonPickle, nullable=False, default=[])
    # 比赛时可否看到排行总榜
    ranklist_visible = db.Column(db.Boolean, nullable=False, default=False)
    # 比赛时可否得知评测结果
    judge_result_visible = db.Column(db.Boolean, nullable=False, default=False)
    # 排行依据
    # 如果排行依据为max_score，则按照题目最高分
    # 如果排行依据为last_submit，则按照最后一次提交的分数排序
    # 如果排行依据为penalty，则每道题AC即通过，非AC即未通过，首先按照通过题目数排名，题目数相同按照罚时排名
    rank_criterion = db.Column(
        db.String(20), nullable=False, default="max_score")
    # 比赛邀请码
    # 如果非空字符串，则必须正确输入邀请码才可进入比赛
    invite_code = db.Column(db.String(10), nullable=False, default="")
    @staticmethod
    def by_id(id):
        return db.session.query(Contest).filter(Contest.id == id).one_or_none()

    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret

    def running(self):
        import datetime
        now = datetime.datetime.now()
        return now >= self.start_time and now <= self.end_time

    def can_see_judge_result(self, uid) -> bool:
        if not uid:
            return self.judge_result_visible
        user: User = User.by_id(uid)
        return user.is_admin or user.id == self.owner_id or self.judge_result_visible

    def can_see_ranklist(self, uid) -> bool:
        if not uid:
            return self.ranklist_visible
        user: User = User.by_id(uid)
        return user.is_admin or user.id == self.owner_id or self.ranklist_visible
