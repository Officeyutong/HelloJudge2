from routes.api_problem import refresh_cached_count
from flask_script import Manager
from main import web_app, db, redis_connection_pool
import models
from models import User, Problem
manager = Manager(web_app)


@manager.command
def db():
    print("Use `flask db` instead!")
# manager.add_command('db', MigrateCommand)


@manager.command
def setadmin(userid):
    """设置管理员"""
    user: User = db.session.query(User).filter(User.id == userid).one()
    from redis import Redis
    Redis(connection_pool=redis_connection_pool).delete(f"hj2-perm-{user.id}")
    user.permission_group = "admin"
    user.permissions = [*user.permissions, "permission.manage"]
    db.session.commit()
    print("Done.")


@manager.command
def addperm(userid, permstr):
    """用户增加权限"""
    user: User = db.session.query(User).filter(User.id == userid).one()
    from redis import Redis
    Redis(connection_pool=redis_connection_pool).delete(f"hj2-perm-{user.id}")
    user.permissions = [*user.permissions, permstr]
    db.session.commit()
    print("Done.")


@manager.command
def removeperm(userid, permstr):
    """用户删除权限"""
    user: User = db.session.query(User).filter(User.id == userid).one()
    from redis import Redis
    Redis(connection_pool=redis_connection_pool).delete(f"hj2-perm-{user.id}")
    user.permissions = [x for x in user.permissions if x != permstr]
    db.session.commit()
    print("Done.")


@manager.command
def recache_allproblems():
    """
    刷新所有题目的AC数和提交数缓存
    """
    problem_ids = db.session.query(Problem.id).all()
    for i, item in enumerate(problem_ids):
        refresh_cached_count(item.id)
        print(f"{i+1} / {len(problem_ids)} ok")


if __name__ == '__main__':
    manager.run()
