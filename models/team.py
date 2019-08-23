from main import db

from ormtypes.json_pickle import JsonPickle

class Team(db.Model):
    # ID
    id = db.Column(db.Integer, primary_key=True)
    # 团队名
    name = db.Column(db.String(30), nullable=False, default="新建团队")
    # 团队描述
    description = db.Column(db.Text, nullable=True, default="")
    # 所有者ID
    owner_id = db.Column(db.Integer, nullable=False)
    # 成员列表，list[int]
    members = db.Column(JsonPickle, default=[], nullable=False)
    # 除了创建者之外的管理员列表
    admins = db.Column(JsonPickle, default=[], nullable=False)
    # 团队任务列表
    # [{"name":"xxxx","problems":[1,2,3,4]}]
    tasks = db.Column(JsonPickle, default=[], nullable=False)
    # 创建时间
    create_time = db.Column(db.DateTime, nullable=False)

    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret
    def by_id(id):
        return db.session.query(Team).filter(Team.id == id).one_or_none()
