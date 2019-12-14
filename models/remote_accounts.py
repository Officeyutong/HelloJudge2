from main import db


class RemoteAccount(db.Model):
    __tablename__ = "remote_accounts"
    # 唯一ID
    remote_user_id = db.Column(db.String(128), primary_key=True)
    # 用户名
    username = db.Column(db.String(100), nullable=False)
    # 密码
    password = db.Column(db.String(100), nullable=False)
    # oj
    oj = db.Column(db.String(20), nullable=False)
