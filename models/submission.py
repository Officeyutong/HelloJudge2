from main import db
from typing import Tuple
from ormtypes.json_pickle import JsonPickle


class Submission(db.Model):
    __tablename__ = "submissions"
    # 提交ID
    id = db.Column(db.Integer, primary_key=True)
    # 用户ID
    uid = db.Column(db.Integer, index=True)
    # 语言ID
    language = db.Column(db.String(10))
    # 题目ID
    problem_id = db.Column(db.Integer)
    # 提交时间
    submit_time = db.Column(db.DateTime)
    # 是否公开
    public = db.Column(db.Boolean, default=True)
    # 所属的比赛ID,-1表示非比赛
    contest_id = db.Column(db.Integer, nullable=False, default=-1, index=True)
    # 代码
    code = db.Column(db.Text)
    # 评测结果
    # 形如{"subtask1":{"score":100,"status":"WA",testcases:[{"input":"1.in","output":"1.out","score":0,status:"WA","message":"","full_score":"测试点满分，对于取min，只有0或1"}]}}
    judge_result = db.Column(JsonPickle, default={})
    # 总分
    score = db.Column(db.Integer, default=0, nullable=False, index=True)
    # 内存开销
    memory_cost = db.Column(db.Integer, default=0, nullable=False)
    # 时间开销
    time_cost = db.Column(db.Integer, default=0, nullable=False)
    # 附加编译参数
    extra_compile_parameter = db.Column(
        db.String(128), default="", nullable=False)
    # 选择的语言参数
    selected_compile_parameters = db.Column(
        JsonPickle, default=[], nullable=False)

    def get_total_memory_time_cost(self) -> Tuple[int, int]:
        memory, time = 0, 0
        for subtask in self.judge_result.values():
            for testcase in subtask["testcases"]:
                time += testcase["time_cost"]
                memory = max(memory, testcase["memory_cost"])
        return memory, time

    def get_total_score(self):
        return sum(map(lambda x: x["score"], self.judge_result.values()))
    # 评测状态
    # waiting:等待评测
    # judging:评测中
    # accepted:正确
    # unaccepted:错误
    status = db.Column(db.String(20))
    # 传递给用户的附加信息
    message = db.Column(db.Text, default="")
    # 评测机名
    judger = db.Column(db.String(20), default="")
    # 此提交对应的习题集ID
    problemset_id = db.Column(
        db.Integer, nullable=True, default=-1, index=True)

    def to_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret

    @staticmethod
    def by_id(id):
        return db.session.query(Submission).filter(Submission.id == id).one_or_none()
