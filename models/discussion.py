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
    topic = db.Column(db.String(128))
    # 标题
    title = db.Column(db.String(100))
    # 内容
    content = db.Column(db.Text)
    # 用户ID
    user_id = db.Column(db.Integer)
    # 是否置顶
    top = db.Column(db.Boolean, default=False)
