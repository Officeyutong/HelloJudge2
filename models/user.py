from main import db

from ormtypes.json_pickle import JsonPickle

from sqlalchemy.dialects import mysql

from sqlalchemy import Column, Integer,  String, Text, DateTime

from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    # 是否封禁
    banned = Column(mysql.TINYINT(display_width=1),
                    default=False, nullable=False)
    # 用户名
    username = Column(String(20), unique=True)
    # 密码
    password = Column(String(256))
    # 个人简介
    description = Column(mysql.LONGTEXT, default="")
    # 电子邮件
    email = Column(String(128), index=True)
    # # 是否为管理员
    # is_admin = Column(mysql.TINYINT(display_width=1), default=text("0"))
    # # 是否是原始管理员(用于切换管理员模式)
    # raw_admin = Column(mysql.TINYINT(display_width=1), nullable=False, default=text("0"))
    # # 重置密码所需token
    # reset_token = Column(String(128), default="")
    # # 验证账号所需token,留空表示已验证
    # auth_token = Column(String(128), default="", nullable=False)
    # 注册时间
    register_time = Column(DateTime, nullable=False)
    # rating历史
    # [{"result":rating变化,"contest_id":"比赛ID"}]
    rating_history = Column(JsonPickle, nullable=False, default=[])
    # 所在团队列表
    # joined_teams = Column(JsonPickle, nullable=False, default=[])
    # rating
    rating = Column(Integer, nullable=False, default=1500, index=True)
    # 所属权限组ID
    permission_group = Column(
        String(20), nullable=False, default="default")
    # 用户特有权限列表
    permissions = Column(JsonPickle, nullable=False, default=[])
    # 强制退出登陆时间在此之前的客户端
    # 通常用于用户 退出\修改密码 后强行下线所有客户端
    force_logout_before = Column(db.BigInteger, nullable=False, default=0)
    # 用户手机号码
    phone_number = Column(
        String(20), nullable=True, default="", index=True)
    # 用户手机号码是否经过验证
    phone_verified = Column(mysql.TINYINT(
        display_width=1), nullable=False, default=False)
    # 最后一次有效的短信验证码
    last_auth_code = Column(String(10), nullable=True)
    # 最后一次发送验证码的时间
    last_send_time = Column(DateTime, nullable=True)

    @staticmethod
    def by_id(id):
        return db.session.query(User).filter(User.id == id).one_or_none()

    def get_rating(self) -> int:
        result = 1500
        for x in self.rating_history:
            result += x["result"]
        return result

    def as_dict(self):
        ret = dict(filter(lambda x: not x[0].startswith(
            "_"), self.__dict__.items()))
        return ret
