from models import *
from main import db
from datetime import datetime
from flask_socketio import emit, rooms


def send_notification(user_id, text):
    mail: Mail = Mail()
    mail.from_id = 0
    mail.to_id = user_id
    mail.text = text
    mail.time = datetime.now()
    if f"mail:(0,{user_id})" in rooms():
        emit("mail", {
            "from_id": 0, "to_id": user_id, "text": text, "time": str(mail.time)
        }, namespace="/ws/mail", room=f"mail:{(0,user_id)}")
    else:
        emit("notification", namespace="/ws/notification",
             room=f"notification:{user_id}")

    db.session.commit()
