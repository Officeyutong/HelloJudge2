from main import db


class RemoteAccount(db.Model):
    __tablename__ = "remote_accounts"
    # 唯一ID
    account_id = db.Column(db.String(128), primary_key=True, unique=True)
    # 用户名
    username = db.Column(db.String(100), nullable=False)
    # 密码
    password = db.Column(db.String(100), nullable=False)
    # oj
    oj = db.Column(db.String(20), nullable=False)
    # 用户id
    uid = db.Column(db.Integer, nullable=False)
    # session对象
    session = db.Column(db.String(1024), nullable=False, default="{}")
