from models.user import User
from main import db, web_app, permission_manager, config
from models.permission_pack import PermissionPack, PermissionPackUser
from utils import make_response
from flask import Blueprint, request, session
from common.utils import unpack_argument
from common.permission import require_permission
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
import math
import typing
import pathlib
import os
import time
router = Blueprint("permissionpack", __name__)


@router.route("/create", methods=["POST"])
@require_permission(permission_manager, "permission.manage")
def permissionpack_create():
    """
    创建权限包
    """
    pack = PermissionPack(
        name="新建权限包"
    )
    db.session.add(pack)
    db.session.commit()
    return make_response(0, message="操作完成", id=pack.id, name=pack.name)


@router.route("/remove", methods=["POST"])
@require_permission(permission_manager, "permission.manage")
@unpack_argument
def permissionpack_remove(id: int):
    """
    删除权限包
    """
    pack = db.session.query(PermissionPack).filter_by(id=id).one_or_none()
    if not pack:
        return make_response(-1, message="权限包不存在")
    db.session.delete(pack)
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/all", methods=["POST"])
@require_permission(permission_manager, "permission.manage")
def permissionpack_all():
    """
    列出所有权限包
    [
        {
            "id":"权限包ID",
            "name":"权限包名称",
            "permissionCount":"包含的权限数量",
            "userCount":"可以领取这个权限包的用户数量"
        }
    ]
    """
    packs = db.session.query(
        PermissionPack.id,
        PermissionPack.name,
        PermissionPack.permissions,
    ).all()
    result = [{
        "id": item.id,
        "name": item.name,
        "permissionCount": len(item.permissions),
        "userCount": db.session.query(PermissionPackUser).filter_by(pack_id=item.id).count()
    } for item in packs]
    return make_response(0, data=result)


@router.route("/detail", methods=["POST"])
@require_permission(permission_manager, "permission.manage")
@unpack_argument
def permissionpack_detail(packID: int):
    """
    查询某个权限包的详细信息
    {
        name:"名称",
        "id":"ID",
        "permissions":"权限",
        "description":"描述"
    }
    """
    pack: PermissionPack = db.session.query(
        PermissionPack).filter_by(id=packID).one_or_none()
    if not pack:
        return make_response(-1, message="权限包不存在")
    return make_response(0, data={
        "name": pack.name,
        "id": pack.id,
        "permissions": pack.permissions,
        "description": pack.description
    })


@router.route("/users", methods=["POST"])
@require_permission(permission_manager, "permission.manage")
@unpack_argument
def permissionpack_users(packID: int, page: int):
    """
    查询某个权限包的可使用用户列表的某一页
    {
        data:[
            {
                "phone":"手机号码",
                "用户名":"OJ用户名",
                "claimed":"是否已使用"
            }
        ],
        pageCount:"总页数"
    }
    """
    query = db.session.query(PermissionPackUser, User.username).outerjoin(
        User, User.phone_number == PermissionPackUser.phone).filter(PermissionPackUser.pack_id == packID).order_by(PermissionPackUser.phone.asc())
    page_count = int(
        math.ceil(query.count()/config.PERMISSIONPACK_USER_PER_PAGE))
    result = query.slice((page-1)*config.PERMISSIONPACK_USER_PER_PAGE,
                         page*config.PERMISSIONPACK_USER_PER_PAGE).all()
    result_with_username = []
    for item in result:
        permpack, username = item
        # qry = db.session.query(User.username).filter_by(
        #     phone_number=item.phone).one_or_none()
        result_with_username.append({
            "phone": permpack.phone,
            "claimed": permpack.claimed,
            "username": username or "[用户未注册]"
        })
    return make_response(0, data=result_with_username, pageCount=page_count)


@router.route("/users/remove", methods=["POST"])
@require_permission(permission_manager, "permission.manage")
@unpack_argument
def permissionpack_users_remove(packID: int, toRemove: typing.List[str] = [], removeAll: bool = False):
    """
    删除某个权限包的可领取用户
    """
    perm_str = f"[provider:permissionpack.{packID}]"

    query = db.session.query(
        PermissionPackUser).filter_by(pack_id=packID)
    qry_with_user = db.session.query(
        PermissionPackUser, User).filter_by(pack_id=packID)

    if not removeAll:
        cond = expr.or_(*(
            PermissionPackUser.phone == item for item in toRemove
        ))
        print(cond)
        query = query.filter(
            cond
        )
        qry_with_user = qry_with_user.filter(cond)
    for item in qry_with_user.join(User, User.phone_number ==
                                   PermissionPackUser.phone):
        item[1].permissions = [x for x in item[1].permissions if x.strip()
                               != perm_str]
    query.delete()
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/update", methods=["POST"])
@require_permission(permission_manager, "permission.manage")
@unpack_argument
def permissionpack_update(packID: int, name: str, description: str, permissions: typing.List[str]):
    """
    更新权限包
    """
    pack: PermissionPack = db.session.query(
        PermissionPack).filter_by(id=packID).one_or_none()
    if not pack:
        return make_response(-1, message="该包不存在")
    pack.name = name
    pack.description = description
    pack.permissions = permissions
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/users/upload", methods=["POST"])
@require_permission(permission_manager, "permission.manage")
def permissionpack_upload():
    """
    上传文件更新权限包用户列表
    """
    column = int(request.form.get("column", "1"))
    file = request.files["file"]
    pack_id = int(request.form["pack_id"])
    file_data = file.stream.read()
    pack_dir = pathlib.Path(os.getcwd())/"permissionpack-store"
    if os.path.exists(pack_dir) and not os.path.isdir(pack_dir):
        os.remove(pack_dir)
    if not os.path.exists(pack_dir):
        os.mkdir(pack_dir)
    with open(pack_dir/f"{int(time.time())}-{file.filename}", "wb") as f:
        f.write(file_data)
    from io import BytesIO
    buf = BytesIO()
    buf.write(file_data)
    import openpyxl
    book = openpyxl.load_workbook(buf)
    sheet = book.active
    added = 0
    total = 0
    for item in sheet.iter_rows(min_col=column, max_col=column, min_row=1):
        if not db.session.query(PermissionPackUser).filter_by(pack_id=pack_id, phone=item[0].value).limit(1).count():
            db.session.add(PermissionPackUser(
                pack_id=pack_id,
                phone=item[0].value
            ))
            added += 1
        total += 1
    db.session.commit()
    return make_response(0, message="操作完成")


@router.route("/user_packs", methods=["POST"])
def permissionpack_list_packs():
    """
    列出某个用户可使用的权限包
    [
        {
            "id":"权限包ID",
            "name":"权限包名",
            "description":"权限包描述",
            "permissions":["权限列表"],
            "claimed":"是否已领取"
        }
    ]
    """
    user: User = db.session.query(User.id, User.phone_verified, User.phone_number).filter_by(
        id=session.get("uid", -1)).one_or_none()
    if not user:
        return make_response(-1, message="请先登录")
    if not user.phone_verified:
        return make_response(-1, message="请先进行手机认证")
    result = db.session.query(
        PermissionPackUser.claimed,
        PermissionPackUser.pack_id,
        PermissionPack.description,
        PermissionPack.id,
        PermissionPack.name,
        PermissionPack.permissions).join(
            PermissionPack, PermissionPack.id == PermissionPackUser.pack_id
    ).filter(
        PermissionPackUser.phone == user.phone_number
    ).all()
    return make_response(0, data=[
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "permissions": item.permissions,
            "claimed": bool(item.claimed)
        }
        for item in result
    ])


@router.route("/claim", methods=["POST"])
@unpack_argument
def permissionpack_claim(packID: int):
    """
    领取权限包
    """
    user: User = db.session.query(User.id, User.phone_verified, User.phone_number).filter_by(
        id=session.get("uid", -1)).one_or_none()
    if not user:
        return make_response(-1, message="请先登录")
    if not user.phone_verified:
        return make_response(-1, message="请先进行手机认证")
    pack = db.session.query(
        PermissionPack.permissions,
        PermissionPackUser.claimed,
        PermissionPackUser.phone
    ).join(
        PermissionPack,
        PermissionPack.id == PermissionPackUser.pack_id
    ).filter(PermissionPackUser.pack_id == packID, PermissionPackUser.phone == user.phone_number).one_or_none()
    if not pack:
        return make_response(-1, message="您没有权限使用此权限包")
    permission_manager.add_permission(
        user.id, f"[provider:permissionpack.{packID}]")
    db.session.query(PermissionPackUser).filter_by(phone=user.phone_number, pack_id=packID).update({
        PermissionPackUser.claimed: True
    })
    db.session.commit()
    return make_response(0, message="操作完成")
