from main import web_app as app
from main import db, config, basedir
from flask import session, request, send_file, send_from_directory
from utils import *
from models import *
from sqlalchemy.sql.expression import *

@app.route("/api/admin/show")
def admin_show():
    """
    获取后台信息
    """