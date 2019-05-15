from main import db


class Discussion(db.Model):
    __tablename__ = "discussions"
    # 讨论ID
    id = db.Column(db.Integer, primary_key=True)
    # 板块
    # 每一个板块使用一个字符串表示，比如discussion.problem.233 表示编号为233的题目的所有讨论
    # discussion.problem 表示所有题目的讨论
    # discussion.problem.global 表示题目全局讨论
    # discussion.global 表示全局讨论
    path = db.Column(db.String(128), index=True, nullable=False)
    # 标题
    title = db.Column(db.String(100), index=True, nullable=False)
    # 内容
    content = db.Column(db.Text, nullable=False)
    # 用户ID
    user_id = db.Column(db.Integer, nullable=False)
    # 是否置顶
    top = db.Column(db.Boolean, default=False, nullable=False)
    # 发送时间
    time = db.Column(db.DateTime, nullable=False)
