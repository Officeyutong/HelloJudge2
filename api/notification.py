from models import *
from main import db
from datetime import datetime
from flask_socketio import emit, rooms


def send_notification(user_id: str, text: str, send_message: bool):
    """
    向指定用户发送提醒。
    @param user_id: 目标用户ID
    @param text: 推送内容
    @param send_message: 是否显示在超级用户提供的私信中（为False时，忽略text参数）
    @return: None
    """

    if send_message:
        mail: Mail = Mail()
        mail.from_id = 0
        mail.to_id = user_id
        mail.text = text
        mail.time = datetime.now()
        emit("mail", {
            "from_id": 0, "to_id": user_id, "text": text, "time": str(mail.time)
        }, namespace="/ws/mail", room=f"mail:{user_id}")
        db.session.add(mail)
        db.session.commit()
    if f"mail:{user_id}" not in rooms():
        emit("notification", namespace="/ws/notification",
             room=f"notification:{user_id}")
