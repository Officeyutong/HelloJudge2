from utils import make_response
from common.utils import unpack_argument
from main import config, web_app, permission_manager, background_task_queue, db
from pathlib import Path
from flask import send_from_directory, redirect, request, Blueprint, session
from flask.helpers import safe_join
from werkzeug.exceptions import NotFound
from common.permission import require_permission
from models.wiki import WikiConfig, WikiNavigationItem, WikiPage, WikiPageVersion
from models.user import User
import typing
import json
import math
from const_var import SYSTEM_NOTIFICATION_USERID
router = Blueprint("wiki", __name__)

CONFIG_ITEMS = {
    "indexPage": "-1"
}


def get_config() -> typing.Dict[str, str]:
    result = {

    }
    for key, value in CONFIG_ITEMS.items():
        if db.session.query(WikiConfig).filter_by(key=key).limit(1).count() == 0:
            result[key] = value
        else:
            result[key] = db.session.query(WikiConfig).filter_by(
                key=key).limit(1).one().value

    return result


def save_config(config: typing.Dict[str, str]):
    for key, value in config.items():
        if key not in CONFIG_ITEMS:
            raise NotFound(f"Config key not found: {key}")
        if db.session.query(WikiConfig).filter_by(key=key).limit(1).count() == 0:
            db.session.add(WikiConfig(
                key=key,
                value=value
            ))
        else:
            db.session.query(WikiConfig).filter_by(
                key=key).update({
                    WikiConfig.value: value
                })
    db.session.commit()


@router.route("/config/navigation/create", methods=["POST"])
@require_permission(permission_manager, "wiki.manage")
def wiki_config_navigation_create():
    """
    创建导航栏物品，返回title,priority,menu
    """
    item = WikiNavigationItem()
    db.session.add(item)
    db.session.commit()
    return make_response(0, data={
        "id": item.id,
        "title": item.title,
        "menu": json.dumps(item.menu, sort_keys=True, indent=2, ensure_ascii=False),
        "priority": item.priority
    })


@router.route("/config/navigation/remove", methods=["POST"])
@require_permission(permission_manager, "wiki.manage")
def wiki_config_navigation_remove(id: int):
    """
    移除导航栏物品
    """
    db.session.query(WikiNavigationItem).filter_by(id=id).delete()
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/config/update", methods=["POST"])
@require_permission(permission_manager, "wiki.manage")
@unpack_argument
def wiki_config_update(config: typing.Dict[str, str], navigations: typing.List[typing.Dict[str, typing.Any]]):
    save_config(config)

    def check_page_exist(page_id: int) -> bool:
        return page_id == -1 or db.session.query(WikiPage).filter_by(id=page_id).limit(1).count() != 0
    for navigation in navigations:
        navigation["menu"] = json.loads(navigation["menu"], encoding="utf-8")
        try:
            for first_menu in navigation["menu"]:
                if not check_page_exist(first_menu["target"]):
                    return make_response(-1, message=f"一级菜单{first_menu['title']}中的指向页面不存在")
                for second_menu in first_menu["children"]:
                    if not check_page_exist(second_menu["target"]):
                        return make_response(-1, message=f"一级菜单{first_menu['title']}下的二级菜单{second_menu['title']}的指向页面不存在")
        except Exception:
            import traceback
            return make_response(-1, message=f"处理导航菜单{navigation['title']}时出错:\n{str(traceback.format_exc())}")
        db.session.query(WikiNavigationItem).filter_by(id=navigation["id"]).update({
            WikiNavigationItem.priority: navigation["priority"],
            WikiNavigationItem.title: navigation["title"],
            WikiNavigationItem.menu: navigation["menu"]
        })
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/config/get", methods=["POST", "GET"])
@unpack_argument
def wiki_config_get(menu_as_text: bool = True):
    """ 
    获取wiki的配置
    {
        "config":{
            "indexPage":"首页ID"
        },  
        "navigations":[
            {
                "id":"导航菜单ID"
                "priority":"优先级",
                "title":"导航页标题",
                "menu":[ //menu以文本形式提供JSON！
                    {
                        "title":"导航菜单一级标题",
                        "target":"导航菜单指向页面",
                        "children":[ //导航二级菜单
                            {
                                "title":"二级菜单标题",
                                "target":"二级菜单目标"
                            }
                        ]
                    }
                ]
            }s
        ]
    }
    """

    return make_response(0, data={
        "config": get_config(),
        "navigations": [
            {
                "id": item.id,
                "title": item.title,
                "menu": json.dumps(item.menu, sort_keys=True, indent=2, ensure_ascii=False) if menu_as_text else item.menu,
                "priority": item.priority
            } for item in db.session.query(WikiNavigationItem).all()
        ]
    })


@router.route("/page", methods=["POST"])
@unpack_argument
def wiki_page(page: int = -1, version: int = -1, editing=False):
    """
    显示wiki页
    page为-1则显示主页
    {
        "comment":"版本注释",
        "pageID":"页面ID",
        "content":"内容",
        "title":"标题",
        "version":"版本ID",
        "user":{
            "uid":"发送者用户ID",
            "username":"发送者用户名",
            "email":"发送者邮箱"
        },
        "time":"发送时间",
        "verified":"是否审核过",
        "menu":[
            {
                "title":"标题",
                "target":"指向页面ID",
                "children":[
                    {
                        "title":"标题",
                        "target":"指向页面ID"
                    }
                ]
            }
        ],
        "navigationID":"导航ID"
        # "basedOn":{ # editing为True时
        #     "version":"版本",
        #     "user":{
        #         "uid":"用户ID",
        #         "username":"用户名"
        #     },
        #     "time":"发布时间",
        #     "verified":"是否审核过"
        # }
    }
    """
    if editing:
        if not permission_manager.has_permission(session.get("uid", None), "wiki.edit"):
            return make_response(-1, message="你没有权限进行此操作")
    else:
        if int(page) == -1:
            page = int(db.session.query(WikiConfig).filter_by(
                key="indexPage").one().value)
        if int(page) == -1:
            user = db.session.query(User.id, User.username, User.email).filter_by(
                id=SYSTEM_NOTIFICATION_USERID).one()
            return make_response(0, data={
                "content": "# 主页尚未设置",
                "title": "默认主页",
                "time": "",
                "verified": True,
                "menu": [],
                "version": -1,
                "navigationID": -1,
                "user": {
                    "uid": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "pageID": -1,
                "comment": ""
            })
    wikipage: WikiPage = db.session.query(
        WikiPage,
        # WikiNavigationItem.menu
    ).filter_by(id=page).one_or_none()
    if not wikipage:
        return make_response(-1, message="页面不存在")
    if version == -1:
        version = wikipage.cached_newest_version
        if version is None:
            newest_id = db.session.query(
                WikiPageVersion.id).order_by(WikiPageVersion.id.desc()).first().id
            db.session.query(WikiPage).filter_by(id=page).update({
                WikiPage.cached_newest_version: newest_id
            })
            db.session.commit()
            version = newest_id
    print(f"Loading version {version}")
    page_version: WikiPageVersion = db.session.query(
        WikiPageVersion.id,
        WikiPageVersion.uid,
        WikiPageVersion.navigation_id,
        WikiPageVersion.content,
        WikiPageVersion.title,
        WikiPageVersion.time,
        WikiPageVersion.verified,
        WikiPageVersion.comment,
        User.username,
        User.email,
        # WikiNavigationItem.menu
    ).join(
        User, User.id == WikiPageVersion.uid
        # ).join(
        # WikiNavigationItem, WikiNavigationItem.id == WikiPageVersion.navigation_id
    ).filter(WikiPageVersion.id == version).one_or_none()
    if not page_version:
        return make_response(-1, message="未知版本ID")
    # print(dir(page_version))
    if page_version.navigation_id:
        menu = db.session.query(WikiNavigationItem.menu).filter(
            WikiNavigationItem.id == page_version.navigation_id).one().menu
    else:
        menu = []
    if not page_version:
        return make_response(-1, message="版本不存在")
    return make_response(0, data={
        "content": page_version.content,
        "title": page_version.title,
        "time": str(page_version.time),
        "verified": bool(page_version.verified),
        "menu": menu,
        "user": {
            "uid": page_version.uid,
            "username": page_version.username,
            "email": page_version.email
        },
        "version": page_version.id,
        "navigationID": page_version.navigation_id,
        "pageID": wikipage.id,
        "comment": page_version.comment
    })


@router.route("/newversion", methods=["POST"])
@require_permission(permission_manager, "wiki.edit")
@unpack_argument
def wiki_new_version(page: int, version: int, content: str, navigation_id: int, comment: str = ""):
    """
    发布某个页面的新版本
    page: 页面ID
    version: 前序版本ID
    content: 新的内容
    """
    page_version: WikiPageVersion = db.session.query(
        WikiPageVersion,
    ).filter_by(id=version).one_or_none()
    if not page_version:
        return make_response(-1, message="版本不存在")
    if page_version.wikipage_id != page:
        return make_response(-1, message="此版本不对应于指定的页面")
    new_version = WikiPageVersion(
        wikipage_id=page,
        uid=session.get("uid"),
        title=page_version.title,
        content=content,
        verified=False,
        base=page_version.id,
        navigation_id=navigation_id,
        comment=comment
    )
    db.session.add(new_version)
    db.session.commit()
    return make_response(0, message=f"您的版本已经提交成功，请前往该页面的版本列表查看并等待管理员审核。")


@router.route("/createpage", methods=["POST"])
@require_permission(permission_manager, "wiki.manage")
@unpack_argument
def wiki_create_page(title: str, content: str, navigation_id: int):
    """
    创建wiki页面
    """
    if navigation_id and not db.session.query(WikiNavigationItem).filter_by(id=navigation_id).one_or_none():
        return make_response(-1, message="非法导航ID")
    page: WikiPage = WikiPage()
    db.session.add(page)
    db.session.commit()
    version: WikiPageVersion = WikiPageVersion(
        wikipage_id=page.id,
        uid=session.get("uid"),
        title=title,
        content=content,
        verified=True,
        base=-1,
        navigation_id=navigation_id
    )
    db.session.add(version)
    db.session.commit()
    return make_response(0, message="操作完成", pageID=page.id)


@router.route("/verify", methods=["POST"])
@require_permission(permission_manager, "wiki.manage")
@unpack_argument
def wiki_verify(version: int):
    """
    审核一个版本
    即从某个版本复制一份，同时设置verified为True
    """
    old_one: WikiPageVersion = db.session.query(WikiPageVersion).filter_by(
        id=version).one_or_none()
    if not old_one:
        return make_response(-1, message="版本不存在")
    old_one.verified = True
    new_one = WikiPageVersion(
        wikipage_id=old_one.wikipage_id,
        uid=session.get("uid"),
        title=old_one.title,
        content=old_one.content,
        verified=True,
        base=old_one.id,
        navigation_id=old_one.navigation_id,
        comment=f"审核自 {old_one.time} 的版本 {old_one.id}"
    )
    db.session.add(new_one)
    db.session.commit()
    page: WikiPage = db.session.query(
        WikiPage).filter_by(id=new_one.wikipage_id).one()
    page.cached_newest_version = new_one.id
    db.session.commit()
    return make_response(0, message="操作完成", id=new_one.id)


@router.route("/versions", methods=["POST"])
@unpack_argument
def wiki_versions(pageID: int, page: int = 1):
    """
    返回一个页面的版本列表
    [
        {
            "id":"版本ID",
            "title":"标题",
            "time":"创建时间",
            "user":{
                "uid":"",
                "username"
            },
            "verified":"是否认证过",
            "navigationID":"导航菜单ID",
            "base":"前序版本",
            "comment":"注释"
        }
    ]
    """
    query = db.session.query(
        WikiPageVersion.id,
        WikiPageVersion.time,
        WikiPageVersion.uid,
        WikiPageVersion.verified,
        WikiPageVersion.navigation_id,
        WikiPageVersion.base,
        WikiPageVersion.title,
        WikiPageVersion.comment,
        User.username
    ).join(User, User.id == WikiPageVersion.uid).filter(
        WikiPageVersion.wikipage_id == pageID
    ).order_by(WikiPageVersion.id.desc())
    page_count = int(math.ceil(query.count()/config.WIKI_VERSIONS_PER_PAGE))
    result = query.slice((page-1)*config.WIKI_VERSIONS_PER_PAGE,
                         page*config.WIKI_VERSIONS_PER_PAGE).all()
    return make_response(0, data=[
        {
            "id": item.id,
            "title": item.title,
            "time": str(item.time),
            "user": {
                "uid": item.uid,
                "username": item.username,
            },
            "verified": bool(item.verified),
            "navigationID": item.navigation_id,
            "base": item.base,
            "comment": item.comment
        }
        for item in result
    ], pageCount=page_count)
