from main import db


class Mail(db.Model):
    __tablename__ = "mails"
    id = db.Column(db.Integer, primary_key=True)
    # 发送者用户ID
    from_id = db.Column(db.Integer)
    # 接收者用户ID
    to_id = db.Column(db.Integer)
    # 发送时间
    time = db.Column(db.DateTime)
    # 内容
    text = db.Column(db.Text)
