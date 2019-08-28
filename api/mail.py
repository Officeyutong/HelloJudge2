from models import *
from main import db
from datetime import datetime
from flask_socketio import emit, rooms
import api.notification


def make_room_name(id1, id2):
    return f"mail:({id1},{id2})"


def send(from_id: int, to_id: int, text: str):
    """
    向某用户发送私信
    @param from_id: 来源用户ID
    @param to_id: 目标用户ID
    @param text: 消息内容
    """
    mail: Mail = Mail()
    mail.from_id = from_id
    mail.to_id = to_id
    mail.text = text
    mail.time = datetime.now()
    if f"mail:{to_id}" in rooms():
        emit("mail", {
            "from_id": from_id, "to_id": to_id, "text": text, "time": str(mail.time)
        }, namespace="/ws/mail", room=make_room_name(from_id, to_id))
    else:
        api.notification.send_notification(
            to_id, f"收到来自@{User.by_id(from_id).username} 的消息.", False)
    db.session.add(mail)
    db.session.commit()
