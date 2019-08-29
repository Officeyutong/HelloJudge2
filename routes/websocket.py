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
    每个用户和别人进入聊天时建立连接，然后扔到"mail:接收者ID"的room中
    data:[uid1,uid2]
    """
    join_room("mail:"+str(data["uid"]))


@socket.on("init", namespace="/ws/notification")
def handle_notification(data):
    """
    用于接收实时通知
    每个用户扔到"notification:用户id"的房间里
    data:{"uid":用户ID}
    """
    join_room("notification:"+str(data["uid"]))


@socket.on("init", namespace="/ws/import")
def handle_import(data):
    """
    用于实时显示从SYZOJ的导入进度
    data:{"uuid":'uuid'}
    """
    join_room("import:"+str(data["uuid"]))
