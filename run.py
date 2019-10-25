from main import *

socket.run(web_app, port=config.PORT, host=config.HOST,
           use_reloader=config.DEBUG, debug=config.DEBUG, log_output=True)

# 