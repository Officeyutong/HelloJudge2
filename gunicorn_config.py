from main import config as cfg
import multiprocessing
import os
if not os.path.exists("./log"):
    os.makedirs("./log")
bind = f"{cfg.HOST}:{cfg.PORT}"
workers = multiprocessing.cpu_count()*2+1
daemon = False
pidfile = './log/gunicorn.pid'
# errorlog = './log/gunicorn.log'
# accesslog="./log/gunoco"
worker_class = "eventlet"
proc_name = 'hjv2'