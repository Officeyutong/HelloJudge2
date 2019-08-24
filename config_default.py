# session密钥，应该是一个随机生成的字符串。
SESSION_KEY = "qwkqpoksqi0xoqwkqpoksqi0xoqwkqpoksqi0xoqwkqpoksqi0xo"
# 数据库
DATABASE_URI = "sqlite:///data.db"
# 调试模式
DEBUG = False
# 端口
PORT = 8080
# 监听地址
HOST = "0.0.0.0"
# 应用程序名称
APP_NAME = "HelloJudgeV2"
# 用于密码的盐
PASSWORD_SALT = "qeiduew9odpjh8q9uohr8"
# 用户名正则
USRENAME_REGEX = r"^[a-zA-Z0-9_-]+$"
# Redis地址
REDIS_URI = "redis://localhost:6379"
# 评测机列表
JUDGERS = {
    "UUID": "评测机名"
}
# 每页题目数量
PROBLEMS_PER_PAGE = 50
# 每页的提交数量
SUBMISSIONS_PER_PAGE = 20
# 每页显示的讨论数量
DISCUSSION_PER_PAGE = 30
# 每页显示的评论数量
COMMENTS_PER_PAGE = 30
# 每页显示的比赛数量
CONTESTS_PER_PAGE = 50
# 编译时间限制,ms
COMPILE_TIME_LIMIT = 10*1000
# 编译结果长度限制,单位字符
COMPILE_RESULT_LENGTH_LIMIT = 500
# SPJ运行时间限制
SPJ_EXECUTE_TIME_LIMIT = 3000
# 支持的语言
# 语言ID将会被直接发送给评测机
SUPPORTED_LANGUAGES = [
    {
        "id": "cpp11",
        "display": "C++ 11",
        "version": "G++ 8.3",
        "ace_mode": "c_cpp"
    },
    {
        "id": "cpp98",
        "display": "C++ 98",
        "version": "G++ 8.3",
        "ace_mode": "c_cpp"
    },
    {
        "id": "cpp17",
        "display": "C++ 17",
        "version": "G++ 8.3",
        "ace_mode": "c_cpp"
    },
    {
        "id": "java8",
        "display": "Java 8",
        "version": "OpenJDK8",
        "ace_mode": "java"
    },
    {
        "id": "python2",
        "display": "Python 2.7",
        "version": "CPython 2.7",
        "ace_mode": "python"
    },
    {
        "id": "python3",
        "display": "Python 3.7",
        "version": "CPython 3.7",
        "ace_mode": "python"
    }
]
SUPPORTED_LANGUAGES_DICT = dict(
    map(lambda x: (x["id"], x), SUPPORTED_LANGUAGES))

# 发信SMTP服务器
SMTP_SERVER = "smtp.qwq.com"
# 发信SMTP服务器端口
SMTP_PORT = 25
# SMTP账号
SMTP_USER = "qwqqwq"
# SMTP密码
SMTP_PASSWORD = "password"
# 发信账号
EMAIL_SENDER = "qwq@qwq.com"
# 重置密码邮件格式
RESET_PASSWORD_EMAIL = "请前往 http://[此处替换为网站地址]/reset_password/{reset_token} 重置密码。此链接仅有效一次。"
