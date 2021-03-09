from os import name
from main import web_app as app
from main import db, config, basedir, permission_manager
from flask import session, request, send_file, send_from_directory
from utils import *

from models import *
from models.user import User
from models import Follower
from sqlalchemy.sql.expression import *
# from werkzeug.utils import secure_filename
from typing import Tuple, Set
from common.utils import unpack_argument
from common.permission import require_permission
import sqlalchemy.sql.expression as expr
import math


@app.route("/api/this_should_be_the_first_request", methods=["POST"])
@app.route("/api/query_login_state", methods=["POST"])
def query_login_state():
    """
    查询登录状态。
    参数:
        无
    返回:
        {
            "code":0,//0表示调用成功
            "result": true,//表示是否已登录
            "uid":-1//如果已登录则表示用户ID,
            "group":"用户组ID",
            "group_name":"用户组名",
            "backend_managable":"是否可以进行后台管理"
            "username":"用户名",
            "email":"电子邮件",
            "salt":"密码盐",
            "judgeStatus":{ 
                "评测状态列表"
            },
            "appName":"应用程序名",
            "usePolling":"是否使用轮询",
            "registerURL":"注册页面的URL",
            "gravatarURL":"gravatarURL前缀"

        }

    """
    use_phone_auth = config.USE_PHONE_WHEN_REGISTER_AND_RESETPASSWD
    result = {
        "result": session.get("uid") is not None,
        "judgeStatus": config.JUDGE_STATUS,
        "salt": config.PASSWORD_SALT,
        "appName": config.APP_NAME,
        "usePolling": config.USE_POLLING,
        "usePhoneAuth": use_phone_auth,
        "registerURL": "/phone/register" if use_phone_auth else "/register",
        "gravatarURL": config.GRAVATAR_URL_PREFIX
    }
    if session.get("uid"):
        user: User = db.session.query(User.id, User.permission_group, User.email, User.username).filter(
            User.id == session.get("uid")).one()
        result["uid"] = user.id
        group: PermissionGroup = db.session.query(PermissionGroup.name).filter(
            PermissionGroup.id == user.permission_group).one()
        result.update(group=user.permission_group, group_name=group.name,
                      backend_managable=permission_manager.has_permission(user.id, "backend.manage"))
        result.update(username=user.username, email=user.email)
    return make_response(0, **result)


@app.route("/api/login", methods=["POST"])
def login():
    """
    登录
    参数:
        identifier:str 用户名或者邮箱或手机号
        password:str 密码的加盐md5
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    if session.get("uid") is not None:
        return make_response(-1, message="你已经登录了！")
    if db.session.query(User).filter_by(email=request.form["identifier"]).count() > 1:
        return make_response(-1, message="此邮箱对应多个账号，请使用用户名登录!")
    query = db.session.query(User).filter(or_(
        User.email == request.form["identifier"], User.username == request.form["identifier"])).filter(User.password == request.form["password"])
    if query.count() == 0:
        return make_response(-1, message="用户名或密码错误")
    user: User = query.one()
    if user.banned:
        return make_response(-1, message="此账户已被封禁.")
    # if user.auth_token != "":
    #     return make_response(-1, message="请点击您邮箱内的激活邮件验证您的账号。如果没有收到或者想要更改邮箱请使用您的用户名重新注册")
    session["uid"] = query.one().id
    import time
    session["login_time"] = str(int(time.time()))
    session.permanment = True
    return make_response(0)


@app.route("/api/auth_email", methods=["POST"])
def auth_email():
    """
    验证用户邮箱 + 创建用户
    username: 用户名
    token: 验证密钥
    """
    if config.USE_PHONE_WHEN_REGISTER_AND_RESETPASSWD:
        return make_response(-1, message="当前不使用邮箱注册")

    from config import AUTH_PASSWORD, AUTH_TOKEN, REGISTER_EMAIL_AUTH_EXPIRE_SECONDS
    from common.aes import encrypt, decrypt
    from common.datatypes import load_from_json, RegisterToken
    data: RegisterToken = load_from_json(
        RegisterToken, decrypt(AUTH_PASSWORD, request.form["token"]))
    import time
    import datetime
    if time.time() > data.expire_after:
        return make_response(-1, message="此请求已过期")
    if data.token != AUTH_TOKEN:
        return make_response(-1, message="token错误")
    if request.form["username"] != data.username:
        return make_response(-1, message="用户名错误")
    # 一切完成,创建用户
    user = User(
        username=data.username,
        password=data.password,
        email=data.email,
        register_time=datetime.datetime.now()
    )
    db.session.add(user)

    db.session.commit()
    session.permanment = True
    session["uid"] = user.id
    session["login_time"] = str(int(time.time()))
    return make_response(0, message="ok", data={
        "uid": user.id
    })


@app.route("/api/register", methods=["POST"])
def register():
    """
    注册账号
    参数:
        username:str 用户名
        email:str 邮箱
        password:str 密码
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    if config.USE_PHONE_WHEN_REGISTER_AND_RESETPASSWD:
        return make_response(-1, message="当前不使用邮箱注册")
    if session.get("uid") is not None:
        return make_response(-1, message="你已经登录了！")
    import re
    import utils
    if re.match(config.USERNAME_REGEX, request.form["username"]) is None:
        return make_response(-1, message="用户名必须满足以下正则表达式:"+config.USERNAME_REGEX)
    # if config.REQUIRE_REGISTER_AUTH:
    #     user = db.session.query(User).filter(
    #         User.username == request.form["username"])
    #     if user.count():
    #         user: User = user.one()
    #         next_query = db.session.query(User).filter(
    #             User.email == request.form["email"])
    #         if next_query.count() != 0 and next_query.one().username != request.form["username"]:
    #             return make_response(-1, message="此邮箱已被使用")
    #         if user.auth_token != "":
    #             import uuid
    #             user.auth_token = str(uuid.uuid1())
    #             send_mail(config.REGISTER_AUTH_EMAIL.format(
    #                 auth_token=user.auth_token), "验证邮件", request.form["email"])
    #             user.email = request.form["email"]
    #             db.session.commit()
    #             return make_response(-1, message=f"验证邮件已经发送到您的新邮箱{request.form['email']}")

    query = db.session.query(User).filter(
        User.username == request.form["username"])
    if query.count():
        return make_response(-1, message="此用户名或邮箱已被用于注册账号")
    from datetime import datetime
    # import uuid
    if config.REQUIRE_REGISTER_AUTH:
        # 需要邮箱验证
        from config import AUTH_PASSWORD, AUTH_TOKEN, REGISTER_EMAIL_AUTH_EXPIRE_SECONDS
        from common.aes import encrypt, decrypt
        from common.datatypes import load_from_json, RegisterToken
        from urllib.parse import quote_plus
        import time
        data = RegisterToken(
            username=request.form["username"],
            email=request.form["email"],
            password=request.form["password"],
            expire_after=int(time.time())+REGISTER_EMAIL_AUTH_EXPIRE_SECONDS,
            token=AUTH_TOKEN
        )
        encoded_token = encrypt(
            AUTH_PASSWORD, data.as_json())
        # user.auth_token = str(uuid.uuid1())
        print("token", encoded_token)
        quoted = quote_plus(quote_plus(encoded_token))
        print("quoted",quoted)
        send_mail(config.REGISTER_AUTH_EMAIL.format(
            auth_token=quoted), "验证邮件", request.form["email"])
        # db.session.add(user)
        # db.session.commit()
        return make_response(-1, message="验证邮件已经发送到您邮箱的垃圾箱，请注意查收")
    else:
        # 不需要验证
        user = User(
            username=request.form["username"],
            email=request.form["email"],
            password=request.form["password"],
            register_time=datetime.now())

        db.session.add(user)
        db.session.commit()
        session.permanment = True
        session["uid"] = user.id
        import time
        session["login_time"] = str(int(time.time()))
        return make_response(0)


@app.route("/api/logout", methods=["POST"])
def logout():
    """
    登出账号
    参数:
        无
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    if session.get("uid") is None:
        return make_response(-1, message="你尚未登录!")
    user: User = db.session.query(User).filter(
        User.id == session.get("uid")).one()
    # 之后强制所有客户端下线重新登录
    import time

    user.force_logout_before = int(time.time())
    db.session.commit()

    return make_response(0)


@app.route("/api/require_reset_password", methods=["POST"])
def require_reset_password():
    """
    请求重设密码
    参数:
        {
            "identifier":"用户识别符"
        }
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    if config.USE_PHONE_WHEN_REGISTER_AND_RESETPASSWD:
        return make_response(-1, message="当前不使用邮箱验证密码")

    import uuid
    if db.session.query(User).filter(User.email == request.form["identifier"]).count() > 1:
        return make_response(-1, message="此邮箱对应多个用户，请使用用户名进行操作")
    query = db.session.query(User).filter(or_(
        User.email == request.form["identifier"], User.username == request.form["identifier"]))
    if query.count() == 0:
        return make_response(-1, message="用户名或邮箱错误")
    user: User = query.one()
    from common.aes import encrypt
    from common.datatypes import PasswordResetToken, load_from_json
    from config import AUTH_PASSWORD, AUTH_TOKEN, RESET_PASSWORD_EXPIRE_SECONDS
    from time import time
    from urllib.parse import quote_plus
    raw_json = PasswordResetToken(
        user.id, int(time())+RESET_PASSWORD_EXPIRE_SECONDS, AUTH_TOKEN).as_json()
    # print(raw_json)
    to_send_token = encrypt(config.AUTH_PASSWORD, raw_json)
    # print("raw token", to_send_token)
    to_send_token = quote_plus(quote_plus(to_send_token))
    # print(to_send_token)
    # user.reset_token = str(uuid.uuid1())
    from utils import send_mail
    try:
        send_mail(config.RESET_PASSWORD_EMAIL.format(
            reset_token=to_send_token), "重置密码", user.email)
    except Exception as ex:
        import traceback
        return make_response(-1, message=traceback.format_exc())
    return make_response(0, message="重置密码的邮件已经发送到您邮箱的垃圾箱，请注意查收")


@app.route("/api/reset_password", methods=["POST"])
def reset_password():
    """
    重设密码
    参数:
        {
            "identifier":"用户识别符",
            "reset_token":"重置密钥", //更新为新版的重置密钥
            "password":"新密码"
        }
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
        }
    """
    if config.USE_PHONE_WHEN_REGISTER_AND_RESETPASSWD:
        return make_response(-1, message="当前不使用邮箱重置密码")
    if db.session.query(User).filter(User.email == request.form["identifier"]).count() > 1:
        return make_response(-1, message="此邮箱对应多个用户，请使用用户名进行操作")
    query = db.session.query(User).filter(or_(
        User.email == request.form["identifier"], User.username == request.form["identifier"]))
    if query.count() == 0:
        return make_response(-1, message="用户名或邮箱错误")
    user: User = query.one()
    from common.aes import decrypt
    from common.datatypes import PasswordResetToken, load_from_json
    from config import AUTH_PASSWORD, AUTH_TOKEN
    import time
    token: PasswordResetToken = load_from_json(PasswordResetToken,
                                               decrypt(AUTH_PASSWORD, request.form["reset_token"]))
    if token.token != AUTH_TOKEN:
        return make_response(-1, message="非法重置密钥")
    if token.uid != user.id:
        return make_response(-1, message="用户ID错误")
    if time.time() >= token.expire_after:
        return make_response(-1, message="请求已过期，请重新申请")
    user.password = request.form["password"]
    # 之后强制所有客户端下线重新登录
    import time
    user.force_logout_before = int(time.time())
    db.session.commit()
    return make_response(0, message="密码重置完成，请使用新密码登录。")


# @app.route("/api/user/pass_email_auth", methods=["POST"])
# def user_pass_email_auth():
#     """
#     强行让某用户通过邮箱验证
#     uid:用户ID
#     """
#     if not session.get("uid"):
#         return make_response(-1, message="请先登录")
#     operator: User = User.by_id(session.get("uid"))
#     if not permission_manager.has_permission(operator.id, "user.manage"):
#         return make_response(-1, message="你没有权限进行此操作")
#     user: User = User.by_id(request.get_json()["uid"])
#     user.auth_token = ""
#     db.session.commit()
#     return make_response(0, message="操作完成")

@app.route("/api/user/toggle_follow_state", methods=["POST"])
@unpack_argument
def api_user_toggle_follow_state(target: int):
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    source = int(session.get("uid"))
    if source == target:
        return make_response(-1, message="禁止关注你自己")

    if (query := db.session.query(Follower).filter_by(
        source=int(session.get("uid")),
        target=target
    )).count():
        query.delete()
        followed = False
    else:
        if db.session.query(Follower).filter_by(source=source).count() >= config.FOLLOWING_COUNT_LIMIT:
            return make_response(-1, message=f"你最多只能关注 {config.FOLLOWING_COUNT_LIMIT} 个人")

        db.session.add(Follower(
            source=session.get('uid'),
            target=target
        ))
        followed = True
    db.session.commit()
    return make_response(0, message="操作完成", data={"followed": followed})


@app.route("/api/user/get_follower_list", methods=["POST"])
@unpack_argument
def api_user_get_follower_list(target: int, page: int = 1):
    """
    {
        "code":
        "data":[
            {
                "uid":"",
                "username":"",
                "email":"",
                "followedByMe":"当前登录的用户是否关注了该用户",
                "time":
            }
        ],
        "pageCount":""
    }
    """
    total_count = db.session.query(Follower).filter_by(target=target).count()
    page_count = int(math.ceil(total_count/config.FOLLOWERS_PER_PAGE))
    followers_resp = db.session.query(User.id, User.username, User.email, Follower.time).join(User, User.id == Follower.source).filter(Follower.target == target).slice(
        (page-1)*config.FOLLOWERS_PER_PAGE,
        page*config.FOLLOWERS_PER_PAGE
    ).all()
    data = [{
        "uid": item.id,
        "username": item.username,
        "email": item.email,
        "time": str(item.time),
        "followedByMe": db.session.query(Follower).filter_by(source=session.get("uid", -1), target=item.id).count() != 0
    } for item in followers_resp]
    return make_response(0, data=data, pageCount=page_count)


@app.route("/api/user/get_followee_list", methods=["POST"])
@unpack_argument
def api_user_get_followee_list(source: int, page: int = 1):
    """
    {
        "code":
        "data":[
            {
                "uid":"",
                "username":"",
                "email":"",
                "followedByMe":"当前登录的用户是否关注了该用户",
                "time":
            }
        ],
        "pageCount":""
    }
    """
    total_count = db.session.query(Follower).filter_by(source=source).count()
    page_count = int(math.ceil(total_count/config.FOLLOWERS_PER_PAGE))
    followees_resp = db.session.query(User.id, User.username, User.email, Follower.time).join(User, User.id == Follower.target).filter(Follower.source == source).slice(
        (page-1)*config.FOLLOWERS_PER_PAGE,
        page*config.FOLLOWERS_PER_PAGE
    ).all()
    data = [{
        "uid": item.id,
        "username": item.username,
        "email": item.email,
        "time": str(item.time),
        "followedByMe": db.session.query(Follower).filter_by(source=session.get("uid", -1), target=item.id).count() != 0
    } for item in followees_resp]
    return make_response(0, data=data, pageCount=page_count)


@app.route("/api/get_user_profile", methods=["POST"])
def get_user_profile():
    """
    获取用户个人信息
    参数:
        uid:int 用户ID
    返回:
        {
            "code":0,//非0表示调用成功
            "message":"qwq"//code非0的时候表示错误信息
            "data":{
                "id":"用户ID"
                "username":"用户名",
                "email":"邮箱",
                "description":"描述",
                "ac_problems":"通过题目",
                "rating_history":[],
                "joined_teams":[
                    {"name":"团队名","id":"团队ID"}
                ],
                "banned":"是否已封禁",
                "hasEmailAuth":"是否已进行邮箱验证",
                "permissions":[权限列表],
                "permission_group":"权限组",
                "group_name":"权限组名",
                "managable":"是否有权限管理",
                "canSetAdmin":"是否有权限切换管理员模式",
                "group_permissions":"权限组权限列表",
                "following": "是否follow过该用户"
            }
        }
    """
    user = db.session.query(User).filter(User.id == request.form["uid"])
    if user.count() == 0:
        return make_response(-1, message="未知用户ID")
    user: User = user.one()
    ret = {
        "id": user.id,
        "banned": user.banned,
        "username": user.username,
        "description": user.description,
        "email": user.email,
        "register_time": str(user.register_time),
        "rating": user.rating,
        "rating_history": user.rating_history,
        "permission_group": user.permission_group,
        "permissions": user.permissions,
        "phone_verified": user.phone_verified,
        "following": False
    }
    if session.get("uid", None):
        ret["following"] = db.session.query(Follower).filter_by(
            source=int(session.get("uid")),
            target=user.id
        ).count() != 0
    if user.phone_verified:
        ret["phone_number"] = "*" * \
            (len(user.phone_number)-4)+user.phone_number[-4:]
    # del ret["password"]
    # del ret["reset_token"]
    # del ret["auth_token"]
    problems = db.session.query(Submission.problem_id).filter(and_(Submission.uid == user.id, Submission.status == "accepted")
                                                              ).distinct().all()
    ret["ac_problems"] = [x[0] for x in problems]
    # for item in user.joined_teams:
    #     team = Team.by_id(item)
    #     joined_teams.append({"id": team.id, "name": team.name})
    ret["joined_teams"] = [
        {
            "id": x.team_id,
            "name": x.name
        }
        for x in db.session.query(
            TeamMember.team_id,
            Team.name
        ).join(Team).filter(TeamMember.uid == user.id)
    ]
    for item in ret["rating_history"]:
        contest_name: Tuple[str] = db.session.query(Contest.name).filter(
            Contest.id == item["contest_id"]).one_or_none()
        if not contest_name:
            item["contest_name"] = "比赛不存在"
            # contest_name = "比赛不存在"
        else:
            # print(contest_name)
            item["contest_name"] = contest_name.name
    # ret["hasEmailAuth"] = user.auth_token == ""
    group: PermissionGroup = db.session.query(PermissionGroup).filter(
        PermissionGroup.id == user.permission_group).one()
    ret["group_name"] = group.name
    group_perms: Set[str] = set()
    loaded_groups: Set[str] = set()
    while group:
        if group.id in loaded_groups:
            break
        group_perms.update(group.permissions)
        loaded_groups.add(group.id)
        if group.inherit:
            group = db.session.query(PermissionGroup).filter_by(
                id=group.inherit).one_or_none()
        else:
            break

    ret["group_permissions"] = list(group_perms)
    # ret["permissions"] = list(set(db.session.query(PermissionGroup.name).filter(
    #     PermissionGroup.id == user.permission_group).one().permissions).union(ret["permissions"]))
    ret["managable"] = permission_manager.has_permission(
        session.get("uid"), "user.manage")
    ret["canSetAdmin"] = permission_manager.has_permission(
        session.get("uid"), "permission.manage")

    return make_response(0, data=ret)


@app.route("/api/user/toggle_admin_mode", methods=["POST"])
def user_toggle_admin_mode():
    """
    切换当前用户的管理员模式
    """
    if not session.get("uid"):
        return make_response(-1, message="请先登录！")
    user: User = User.by_id(session.get("uid"))
    if not permission_manager.has_permission(user.id, "permission.manage"):
        return make_response(-1, message="你没有权限进行此操作")
    # 在default组的，移动到admin
    if user.permission_group == "default":
        user.permission_group = "admin"
    else:
        user.permission_group = "default"

    from main import redis_connection_pool
    from redis import Redis
    Redis(connection_pool=redis_connection_pool).delete(
        f"hj2-perm-{session.get('uid')}")
    db.session.commit()
    return make_response(0, message="操作成功")


@app.route("/api/update_profile", methods=["POST"])
def update_profile():
    """
    更新个人信息
    {
        "uid":"用户ID",
        "data":{
            "username":"用户名",
            "email":"电子邮件",
            "description":"个人简介",
            "changePassword":"是否更改密码",
            "newPassword":"新密码",
            "banned":"是否已封禁",
            "rawAdmin":"是否是原始管理员",
            "permissions":[新的权限列表],
            "permission_group":"新的权限组"
        }
    }
    {
        "code":0,"message":"qwq"
    }
    """
    import re
    if not session.get("uid"):
        return make_response(-1, message="请先登录")
    operator: User = User.by_id(session.get("uid"))
    user: User = User.by_id(request.form["uid"])
    if user.id != operator.id and not permission_manager.has_permission(operator.id, "user.manage"):
        return make_response(-1, message="你无权进行此操作")
    data: dict = decode_json(request.form["data"])
    regex = re.compile(config.USERNAME_REGEX)
    if not regex.search(data["username"]):
        return make_response(-1, message="用户名必须符合以下正则表达式: {}".format(config.USERNAME_REGEX))
    if not re.compile(r"(.+)@(.+)").search(data["email"]):
        return make_response(-1, message="请输入合法的邮箱")
    if not permission_manager.has_permission(operator.id, "permission.manage"):
        if data["permission_group"] != user.permission_group:
            return make_response(-1, message="你没有权限更改用户所属权限组")
        if set(data["permissions"]) != set(user.permissions):
            return make_response(-1, message="你没有权限更改用户权限")
    user.permission_group = data["permission_group"]
    if db.session.query(PermissionGroup.id).filter(PermissionGroup.id == user.permission_group).one_or_none() is None:
        return make_response(-1, message="非法权限组ID")
    user.permissions = data["permissions"]
    # 移除缓存
    from main import redis_connection_pool
    from redis import Redis
    client = Redis(connection_pool=redis_connection_pool)
    client.delete(f"hj2-perm-{user.id}")
    # user.username = data["username"]

    user.description = data["description"]
    if data["changePassword"]:
        user.password = data["newPassword"]
        import time
        user.force_logout_before = int(time.time())
    if data["banned"] != user.banned and not permission_manager.has_permission(operator.id, "user.manage"):
        return make_response(-1, message="你没有权限封禁/解封此用户")
    user.banned = data["banned"]
    # if user.email != data["email"]:
    #     # 注册不需要邮箱验证的话，改邮箱也不需要
    #     if config.REQUIRE_REGISTER_AUTH and not permission_manager.has_permission(session.get("uid"), "user.manage"):
    #         db.session.commit()
    #         from common.aes import encrypt
    #         from config import AUTH_PASSWORD, AUTH_TOKEN, CHANGE_EMAIL_EXPIRE_SECONDS
    #         from urllib.parse import quote_plus
    #         from common.datatypes import EmailChangeToken
    #         import time
    #         data = EmailChangeToken(uid=user.id,
    #                                 new_email=data["email"],
    #                                 token=AUTH_TOKEN,
    #                                 expire_after=int(
    #                                     time.time())+CHANGE_EMAIL_EXPIRE_SECONDS
    #                                 )
    #         print("raw", encrypt(AUTH_PASSWORD, data.as_json()))
    #         encoded_data = quote_plus(quote_plus(
    #             encrypt(AUTH_PASSWORD, data.as_json())))
    #         send_mail(config.CHANGE_EMAIL_AUTH_EMAIL.format(
    #             change_token=encoded_data), "更改邮箱", data.new_email)
    #         print("encoded", encoded_data)
    #         return make_response(0, message="数据已经更改成功。请前往新邮箱中点击确认。")
    #     else:
    #         user.email = data["email"]

    db.session.commit()
    # 检查邮箱相关
    return make_response(0, message="操作完成")


@app.route("/api/change_email/<string:token>", methods=["POST", "GET"])
def api_user_change_email(token: str):
    import time
    from common.aes import decrypt
    from common.datatypes import EmailChangeToken, load_from_json
    from urllib.parse import quote_plus, unquote_plus, unquote
    token = unquote(unquote(token))
    print("decoded", token)
    import flask
    data: EmailChangeToken = load_from_json(EmailChangeToken, decrypt(
        config.AUTH_PASSWORD, token))
    if time.time() > data.expire_after:
        return flask.redirect("/error?message="+quote_plus("此请求已过期"))
    if data.token != config.AUTH_TOKEN:
        return flask.redirect("/error?message="+quote_plus("非法请求"))
    user: User = db.session.query(User).filter(User.id == data.uid).one()
    user.email = data.new_email
    db.session.commit()
    return flask.redirect("/success?message="+quote_plus("更改成功"))
