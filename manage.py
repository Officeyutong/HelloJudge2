from flask_script import Manager
from main import web_app, db, redis_connection_pool
from flask_migrate import Migrate, MigrateCommand
import models
from models import User
manager = Manager(web_app)
migrate = Migrate(web_app, db)
manager.add_command('db', MigrateCommand)
@manager.command
def setadmin(username):
    """设置管理员"""
    user: User = db.session.query(User).filter(User.username == username).one()
    from redis import Redis
    Redis(connection_pool=redis_connection_pool).delete(f"hj2-perm-{user.id}")
    user.permission_group = "admin"
    user.permissions = [*user.permissions, "permission.manage"]
    db.session.commit()
    print("Done.")


@manager.command
def addperm(username, permstr):
    """用户增加权限"""
    user: User = db.session.query(User).filter(User.username == username).one()
    from redis import Redis
    Redis(connection_pool=redis_connection_pool).delete(f"hj2-perm-{user.id}")
    user.permissions = [*user.permissions, permstr]
    db.session.commit()
    print("Done.")


@manager.command
def removeperm(username, permstr):
    """用户删除权限"""
    user: User = db.session.query(User).filter(User.username == username).one()
    from redis import Redis
    Redis(connection_pool=redis_connection_pool).delete(f"hj2-perm-{user.id}")
    user.permissions = [x for x in user.permissions if x != permstr]
    db.session.commit()
    print("Done.")


if __name__ == '__main__':
    manager.run()
