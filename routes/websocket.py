# 实现评测时实时广播进度

from main import socket, web_app, config, db
from flask_socketio import emit, send, join_room


@socket.on("init", namespace="/ws/submission")
def handle_submission(data):
    join_room(str(data["submission_id"]))