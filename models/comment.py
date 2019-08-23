from main import db


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    # 内容
    content = db.Column(db.Text, nullable=False)
    # 用户ID
    uid = db.Column(db.Integer, nullable=False, index=True)
    # 发送时间
    time = db.Column(db.DateTime, nullable=False)
    # 讨论ID
    discussion_id = db.Column(db.Integer, nullable=False, index=True)
