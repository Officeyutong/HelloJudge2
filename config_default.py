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
# 支持的语言
# 语言ID将会被直接发送给评测机
SUPPORTED_LANGUAGES = [
    {
        "id": "c++11",
        "display": "C++ 11",
        "version": "G++ 8.3",
        "ace_mode": "c_cpp"
    },
    {
        "id": "c++98",
        "display": "C++ 98",
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
