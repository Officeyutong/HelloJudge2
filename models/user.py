from main import db

from ormtypes.json_pickle import JsonPickle


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    # 是否封禁
    bannad = db.Column(db.Boolean, default=False, nullable=False)
    # 用户名
    username = db.Column(db.String(20), unique=True)
    # 密码
    password = db.Column(db.String(64))
    # 个人简介
    description = db.Column(db.Text(), default="")
    # 电子邮件
    email = db.Column(db.String(30))
    # 是否为管理员
    is_admin = db.Column(db.Boolean, default=False)
    # 重置密码所需token
    reset_token = db.Column(db.String(128), default="")
    # 验证账号所需token,留空表示已验证
    auth_token = db.Column(db.String(128), default="")
    # 注册时间
    register_time = db.Column(db.DateTime, nullable=False)
    # rating历史
    # [{"result":rating变化,"contest_id":"比赛ID"}]
    rating_history = db.Column(JsonPickle, nullable=False, default=[])
    # 所在团队列表
    joined_teams = db.Column(JsonPickle, nullable=False, default=[])
    rating = db.Column(db.Integer, nullable=False, default=1500, index=True)
    @staticmethod
    def by_id(id):
        return db.session.query(User).filter(User.id == id).one_or_none()

    def get_rating(self) -> int:
        result = 1500
        for x in self.rating_history:
            result += x["result"]
        return result

    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret
