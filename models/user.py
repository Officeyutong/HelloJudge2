from main import db

from ormtypes.json_pickle import JsonPickle


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    # 是否封禁
    banned = db.Column(db.Boolean, default=False, nullable=False)
    # 用户名
    username = db.Column(db.String(20), unique=True)
    # 密码
    password = db.Column(db.String(64))
    # 个人简介
    description = db.Column(db.Text(), default="")
    # 电子邮件
    email = db.Column(db.String(30))
    # # 是否为管理员
    # is_admin = db.Column(db.Boolean, default=False)
    # # 是否是原始管理员(用于切换管理员模式)
    # raw_admin = db.Column(db.Boolean, nullable=False, default=False)
    # 重置密码所需token
    reset_token = db.Column(db.String(128), default="")
    # 验证账号所需token,留空表示已验证
    auth_token = db.Column(db.String(128), default="", nullable=False)
    # 注册时间
    register_time = db.Column(db.DateTime, nullable=False)
    # rating历史
    # [{"result":rating变化,"contest_id":"比赛ID"}]
    rating_history = db.Column(JsonPickle, nullable=False, default=[])
    # 所在团队列表
    joined_teams = db.Column(JsonPickle, nullable=False, default=[])
    # rating
    rating = db.Column(db.Integer, nullable=False, default=1500, index=True)
    # 所属权限组ID
    permission_group = db.Column(
        db.Text(20), nullable=False, default="default")
    # 用户特有权限列表
    permissions = db.Column(JsonPickle, nullable=False, default=[])
    # 强制退出登陆时间在此之前的客户端
    # 通常用于用户 退出\修改密码 后强行下线所有客户端
    force_logout_before = db.Column(db.BigInteger, nullable=False, default=0)
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
