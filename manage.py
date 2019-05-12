from flask_script import Manager
from main import web_app, db
from flask_migrate import Migrate, MigrateCommand
import models
manager = Manager(web_app)
migrate = Migrate(web_app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
