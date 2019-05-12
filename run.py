from main import *

socket.run(web_app, port=config.PORT, host=config.HOST, debug=config.DEBUG)
