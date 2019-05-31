from main import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    # 用户名
    username = db.Column(db.String(20), unique=True)
    # 密码
    password = db.Column(db.String(64))
    # 个人简介
    description = db.Column(db.Text(), default="无")
    # 电子邮件
    email = db.Column(db.String(30))
    # 是否为管理员
    is_admin = db.Column(db.Boolean, default=False)
    # 重置密码所需token
    reset_token = db.Column(db.String(128), default="")

    @staticmethod
    def by_id(id):
        return db.session.query(User).filter(User.id == id).one()
    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret