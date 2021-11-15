from main import db

from sqlalchemy import Column, ForeignKey, Integer, DateTime, String
from sqlalchemy.dialects import mysql
from ormtypes.json_pickle import JsonPickle
import datetime


class WikiPageVersion(db.Model):
    # 表示一个Wiki页面的版本
    __tablename__ = "wikipage_version"
    id = Column(Integer, primary_key=True)
    # 对应的wikipage ID
    wikipage_id = Column(Integer, ForeignKey(
        "wikipage.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    # 发布用户
    uid = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    # 标题
    title = Column(mysql.TEXT, nullable=True)
    # 内容
    content = Column(mysql.LONGTEXT)
    # 发布时间
    time = Column(DateTime, default=datetime.datetime.now,
                  nullable=False, index=True)
    # 是否审核过
    verified = Column(mysql.TINYINT(display_width=1),
                      default=False, nullable=False, index=True)
    # 这个版本的前序版本号
    # -1表示不存在前序版本
    base = Column(mysql.INTEGER, default=-1, nullable=True, index=True)
    # 这个页面对应的导航页的ID
    navigation_id = Column(Integer, ForeignKey(
        "wiki_navigation_item.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True, index=True)
    comment = Column(mysql.LONGTEXT, nullable=True)


class WikiNavigationItem(db.Model):
    __tablename__ = "wiki_navigation_item"
    # 表示一个导航栏物品
    id = Column(Integer, primary_key=True)
    title = Column(mysql.TEXT, nullable=False, default="新建导航")
    # [
    #   {
    #       "title":"一级菜单标题",
    #       "target":"指向页面",
    #       "children":[
    #           {
    #               "title":"二级菜单标题",
    #               "target":"指向页面"
    #           }
    #          ]
    #   }
    # ]
    menu = Column(JsonPickle, default=[
        {
            "title": "一级菜单标题",
            "target": -1,
            "children": [
                {
                    "title": "二级菜单标题1",
                    "target": -1
                }, {
                    "title": "二级菜单标题2",
                    "target": -1
                }
            ]
        },
        {
            "title": "一级菜单标题2",
            "target": -1,
            "children": [
                {
                    "title": "二级菜单标题1",
                    "target": -1
                }, {
                    "title": "二级菜单标题2",
                    "target": -1
                }
            ]
        }
    ])
    # 优先级，越高的越靠前
    priority = Column(Integer, default=1, nullable=False, index=True)


class WikiPage(db.Model):
    # 表示一个wiki页面
    __tablename__ = "wikipage"
    id = Column(Integer, primary_key=True)
    # 缓存的最新的审核过的版本
    cached_newest_version = Column(Integer, index=True)
    # cached_last_modified_time = Column(DateTime, nullable=True)
    # cached_last_modified_user = Column(Integer, ForeignKey(
    #     "user.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)


class WikiConfig(db.Model):
    __tablename__ = "wikiconfig"
    key = Column(String(length=30), primary_key=True)
    value = Column(mysql.LONGTEXT)
