import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))



from main import db, web_app,config,csrf
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
web_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

csrf.csrf_valid=False
web_app.config['WTF_CSRF_ENABLED'] = False

manager = Manager(web_app)
migrate = Migrate(web_app, db)


def init_db():
    from flask_migrate import init, migrate, upgrade
    init("./test/migrations")
    with open("./test/migrations/script.py.mako", "r") as f:
        lines = f.readlines()
    
    for i,x in enumerate(lines):
        if "from alembic import op" in x:
            lines.insert(i,"import ormtypes\n")
            break
    with open("./test/migrations/script.py.mako", "w") as f:
        f.writelines(lines)
            
    
    migrate("./test/migrations")
    upgrade("./test/migrations")
