from main import db
from typing import List, Mapping, Any


class Contest(db.Model):
    # 比赛ID
    id = db.Column(db.Integer, primary_key=True)
    # 比赛名称
    name = db.Column(db.String(128), nullable=False, default="新建比赛")
    # 开始时间
    start_time = db.Column(db.DateTime, nullable=False)
    # 结束时间
    end_time = db.Column(db.DateTime, nullable=False)
    # 题目列表
    problems = db.Column(db.PickleType, nullable=False, default=[])

    # 比赛时可否看到排行总榜
    ranklist_visible = db.Column(db.Boolean, nullable=False, default=False)
    # 比赛时可否得知评测结果
    judge_result_visible = db.Column(db.Boolean, nullable=False, default=False)
    # 排行依据
    # 如果排行依据为score，则按照题目总分高低排序
    # 如果排行依据为penalty，则每道题AC即通过，非AC即未通过，首先按照通过题目数排名，题目数相同按照罚时排名
    rank_criterion = db.Column(db.String(20), nullable=False, default="score")
    # 题目加权值，仅适用于rank_criterion为score
    # 格式为{"题目编号":"分数权值"}
    score_weight = db.Column(db.PickleType, nullable=False, default=None)
    # 生成排行榜
    def generate_rank_list(self) -> List[Mapping[str, Any]]:
        pass
