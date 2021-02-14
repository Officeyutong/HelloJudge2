from eventlet import monkey_patch
monkey_patch()
from main import socket, web_app, config
socket.run(web_app, port=config.PORT, host=config.HOST,
           use_reloader=config.DEBUG, debug=config.DEBUG, log_output=True)
