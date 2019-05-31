# 实现评测时实时广播进度

from main import socket, web_app, config, db
from flask_socketio import emit, send, join_room


@socket.on("init", namespace="/ws/submission")
def handle_submission(data):
    """
    用于广播评测状态的socket
    data:{"submission_id":"提交ID"}
    room为"judge:提交ID"
    """
    join_room("judge:"+str(data["submission_id"]))

# 用来进行实时聊天的WebSocket


@socket.on("init", namespace="/ws/mail")
def handle_mail(data):
    """
    用于实时聊天
    每个用户和别人进入聊天时建立连接，然后扔到"mail:(用户1，用户2)"的房间里，其中前者数字较小
    data:[userid1,userid2]
    """
    if data[0] > data[1]:
        data[0], data[1] = data[1], data[0]
    ids = tuple(data[:2])
    join_room("mail:"+str(ids))


@socket.on("init", namespace="/ws/notification")
def handle_notification(data):
    """
    用于接收实时通知
    每个用户扔到"notification:用户id"的房间里
    data:{"user_id":用户ID}
    """
    join_room("notification:"+str(data["user_id"]))
