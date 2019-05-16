from main import db


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    time = db.Column(db.DateTime, nullable=False)
    discussion_id = db.Column(db.Integer, nullable=False, index=True)
