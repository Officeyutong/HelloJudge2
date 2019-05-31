from models import *
from main import db
from datetime import datetime
from flask_socketio import emit, rooms
import api.notification


def send(from_id: int, to_id: int, text: str):
    mail: Mail = Mail()
    mail.from_id = from_id
    mail.to_id = to_id
    mail.text = text
    mail.time = datetime.now()
    ids = [from_id, to_id]
    if ids[0] > ids[1]:
        ids[0], ids[1] = ids[1], ids[0]
    if "mail:"+str(tuple(ids)) in rooms():
        emit("mail", {
            "from_id": from_id, "to_id": to_id, "text": text, "time": str(mail.time)
        }, namespace="/ws/mail", room="mail:"+str(tuple(ids)))
    else:
        api.notification.send_notification(
            to_id, f"收到来自@{User.by_id(from_id).username} 的消息.")
    db.session.commit()
