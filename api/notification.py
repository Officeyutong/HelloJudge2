from models import *
from main import db
from datetime import datetime
from flask_socketio import emit, rooms


def send_notification(uid: str, text: str, send_message: bool):
    """
    向指定用户发送提醒。
    @param uid: 目标用户ID
    @param text: 推送内容
    @param send_message: 是否显示在超级用户提供的私信中（为False时，忽略text参数）
    @return: None
    """
    def make_room_name(id1, id2):
        return f"mail:({id1},{id2})"

    if send_message:
        mail: Mail = Mail()
        mail.from_id = 0
        mail.to_id = uid
        mail.text = text
        mail.time = datetime.now()
        emit("mail", {
            "from_id": 0, "to_id": uid, "text": text, "time": str(mail.time)
        }, namespace="/ws/mail", room=make_room_name(0, mail.to_id))
        db.session.add(mail)
        db.session.commit()
    if f"mail:{uid}" not in rooms():
        emit("notification", namespace="/ws/notification",
             room=f"notification:{uid}")
