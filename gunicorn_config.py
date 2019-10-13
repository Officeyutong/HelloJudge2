from main import config as cfg
from main import web_app
import logging
import multiprocessing
import os
if not os.path.exists("./log"):
    os.makedirs("./log")
bind = f"{cfg.HOST}:{cfg.PORT}"
workers = multiprocessing.cpu_count()*2+1
daemon = False
pidfile = './log/gunicorn.pid'
errorlog = './log/gunicorn_error.log'
accesslog="./log/gunicorn_access.log"
worker_class = "eventlet"
proc_name = 'hjv2'

