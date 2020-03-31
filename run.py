from main import *
# import eventlet
# eventlet.wsgi.server(
#     eventlet.wrap_ssl(eventlet.listen(("localhost", 443)),
#                       certfile='hj2-debug.crt',
#                       keyfile='hj2-debug.key',
#                       server_side=True), web_app)
socket.run(web_app, port=config.PORT, host=config.HOST,
           use_reloader=config.DEBUG, debug=config.DEBUG, log_output=True)

#  qwq
