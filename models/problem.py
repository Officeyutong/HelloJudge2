from main import db
from ormtypes.json_pickle import JsonPickle


class Problem(db.Model):
    __tablename__ = "problems"
    # 题目ID
    id = db.Column(db.Integer, primary_key=True)
    uploader_id = db.Column(db.Integer, default=-1)
    # 题目名
    title = db.Column(db.String(50), default="新建题目")
    # 背景
    background = db.Column(db.Text, default="")
    # 题目内容
    content = db.Column(db.Text, default="")
    # 输入
    input_format = db.Column(db.Text, default="")
    # 输出
    output_format = db.Column(db.Text, default="")
    # 数据范围与提示
    hint = db.Column(db.Text, default="")
    # 样例
    # 使用list存储，每组形如[("输入","输出"),("输入","输出")]
    example = db.Column(JsonPickle, default=[
                        {'input': "输入1", "output": "输出1"}, {'input': "输入2", "output": "输出2"}])
    # 文件列表
    # 形如[{"name":"a.in","size":123456},{"name":"a.out","size":233333}]
    files = db.Column(JsonPickle, default=[])
    # 可下载文件列表
    downloads = db.Column(JsonPickle, default=[])
    # 编译时提供的文件列表,这些文件将会在编译的时候和程序放在一起
    provides = db.Column(JsonPickle, default=[])
    # 子任务安排
    # testcases:[{"input":"a.in","output":"b.out"}]
    subtasks = db.Column(JsonPickle, default=[
                         {"name": "Subtask1", "score": 40, "method": "min", "testcases": [], "time_limit":1000, "memory_limit":512, "comment":"这里是注释"}])
    # 题目是否公开
    public = db.Column(db.Boolean, default=False)
    # spj文件名,留空以不使用
    spj_filename = db.Column(db.String(20), default="")
    # 使用文件输入输出
    using_file_io = db.Column(db.Boolean, default=False)
    # 输入文件名
    input_file_name = db.Column(db.String(30), default="")
    # 输出文件名
    output_file_name = db.Column(db.String(30), default="")
    # 题目类型
    problem_type = db.Column(db.String(20), default="traditional")
    # 附加编译参数
    extra_parameter = db.Column(JsonPickle, default=[
        {"lang": "cpp", "parameter": "-std=c++98", "name": "C++98", "force": False},
        {"lang": "cpp", "parameter": "-std=c++11", "name": "C++11", "force": False},
        {"lang": "cpp", "parameter": "-std=c++14", "name": "C++14", "force": False},
        {"lang": "cpp", "parameter": "-std=c++17", "name": "C++17", "force": False},
        {"lang": ".*", "parameter": "-O2", "name": "O2优化", "force": False},
    ], nullable=False)
    # 是否可见用户输出\输入\标准输出
    can_see_results = db.Column(db.Boolean, default=True, nullable=False)
    # 创建日期
    create_time = db.Column(db.DateTime, nullable=False)

    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret

    def get_total_score(self):
        return sum(map(lambda x: int(x["score"]), self.subtasks))

    @staticmethod
    def by_id(id):
        return db.session.query(Problem).filter(Problem.id == id).one_or_none()

    @staticmethod
    def has(id):
        return db.session.query(Problem.id).filter(Problem.id == id).count() != 0
