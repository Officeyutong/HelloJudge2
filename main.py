


import flask
from flask_sqlalchemy import SQLAlchemy
try:
    import config as config
except:
    import config_default as config
import logging
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from concurrent.futures import ThreadPoolExecutor
import os
import celery
web_app = flask.Flask("HelloJudge2")
web_app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
web_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
# web_app.config["SQLALCHEMY_ECHO"] = config.DEBUG

web_app.secret_key = config.SESSION_KEY
csrf = CSRFProtect(web_app)
db = SQLAlchemy(web_app)
basedir = os.path.dirname(__file__)
logger = web_app.logger
socket = SocketIO(web_app)
queue = celery.Celery(
    web_app.name,  broker=config.REDIS_URI, backend=config.REDIS_URI)
# logger.info("Starting server...")
executor = ThreadPoolExecutor(3)
import routes