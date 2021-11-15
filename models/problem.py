from main import db
from ormtypes.json_pickle import JsonPickle

from sqlalchemy.dialects import mysql

from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey

import json
from sqlalchemy.sql.expression import text

import uuid


class Problem(db.Model):
    """
    对于提交答案题,problem_type为submit_answer,code段为其提交的答案的zip压缩包的base64,答案的文件名遵从子任务设定的的各个子任务的输入文件
    """
    __tablename__ = "problem"
    # 题目ID
    id = Column(Integer, primary_key=True)
    uploader_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    # 题目名
    title = Column(String(100), default="新建题目")
    # 背景
    background = Column(mysql.LONGTEXT, default="")
    # 题目内容
    content = Column(mysql.LONGTEXT, default="")
    # 输入
    input_format = Column(mysql.LONGTEXT, default="")
    # 输出
    output_format = Column(mysql.LONGTEXT, default="")
    # 数据范围与提示
    hint = Column(mysql.LONGTEXT, default="")
    # 样例
    # 使用list存储，每组形如[("输入","输出"),("输入","输出")]
    example = Column(JsonPickle, default=[
        {'input': "输入1", "output": "输出1"}, {'input': "输入2", "output": "输出2"}])
    # 文件列表
    # 形如[{"name":"a.in","size":123456},{"name":"a.out","size":233333}]
    files = Column(JsonPickle, default=[])
    # 可下载文件列表
    downloads = Column(JsonPickle, default=[])
    # 编译时提供的文件列表,这些文件将会在编译的时候和程序放在一起
    provides = Column(JsonPickle, default=[])
    # 子任务安排
    # subtasks:{"name": "Subtask1", "score": 40, "method": "min", "testcases": [], "time_limit":1000, "memory_limit":512, "comment":"这里是注释"}
    # testcases:[{"input":"a.in","output":"b.out","full_score":"该测试点满分"}]
    # method: min->取最小值(一个为0整个subtask没分) sum->普通求和
    subtasks = Column(JsonPickle, default=[])
    # 题目是否公开
    # 不公开的题目，则用户必须具有problem.use.题目ID权限，或者是题目创建者才能使用
    public = Column(mysql.TINYINT(display_width=1), default=0, index=True)
    # （如果这是个私有题）是否允许用户查看其他人得提交
    submission_visible = Column(mysql.TINYINT(
        display_width=1), default=True, index=True, nullable=False)
    # 题目邀请码
    invite_code = Column(mysql.LONGTEXT,  nullable=True,
                         default=lambda: str(uuid.uuid1()))
    # spj文件名,留空以不使用
    spj_filename = Column(String(20), default="")
    # 使用文件输入输出
    using_file_io = Column(mysql.TINYINT(display_width=1), default=0)
    # 输入文件名
    input_file_name = Column(String(30), default="")
    # 输出文件名
    output_file_name = Column(String(30), default="")
    # 题目类型
    # traditional - 传统题
    # remote_judge 远程评测
    # submit_answer - 提交答案
    problem_type = Column(String(20), default="traditional")
    # 附加编译参数
    extra_parameter = Column(JsonPickle, default=[
        {"lang": "cpp", "parameter": "-std=c++98", "name": "C++98", "force": False},
        {"lang": "cpp", "parameter": "-std=c++11", "name": "C++11", "force": False},
        {"lang": "cpp", "parameter": "-std=c++14", "name": "C++14", "force": False},
        {"lang": "cpp", "parameter": "-std=c++17", "name": "C++17", "force": False},
        {"lang": ".*", "parameter": "-O2", "name": "O2优化", "force": False},
    ], nullable=False)
    # 是否可见用户输出\输入\标准输出
    can_see_results = Column(mysql.TINYINT(
        display_width=1), default=True, nullable=False)
    # 创建日期
    create_time = Column(DateTime, nullable=False)
    # 远程评测OJ
    remote_judge_oj = Column(String(10), nullable=True)
    # 远程题目ID
    remote_problem_id = Column(String(20), nullable=True)
    # 是否为权限题
    # 如果为True，则该题目需要problem.use.题目ID权限才可使用
    # require_permission = Column(
    #     mysql.TINYINT(display_width=1), nullable=False, default=False)
    # 一个提交评测完成之后，缓存的提交数量
    cached_submit_count = Column(Integer, nullable=False, default=0)
    # 一个提交评测完成之后，缓存的ACCEPTED数量
    cached_accepted_count = Column(Integer, nullable=False, default=0)
    # 此题目所属的团队ID
    # null表示不属于团队
    team_id = Column(Integer, ForeignKey(
        "team.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)

    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret

    def get_total_score(self):
        if self.problem_type == "remote_judge":
            return 100
        return sum(map(lambda x: int(x["score"]), self.subtasks))

    @staticmethod
    def by_id(id):
        return db.session.query(Problem).filter(Problem.id == id).one_or_none()

    @staticmethod
    def has(id):
        return db.session.query(Problem.id).filter(Problem.id == id).count() != 0
