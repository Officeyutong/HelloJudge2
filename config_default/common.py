# session密钥，应该是一个随机生成的字符串。
SESSION_KEY = "qwkqpoksqi0xoqwkqpoksqi0xoqwkqpoksqi0xoqwkqpoksqi0xo"
# 数据库
DATABASE_URI = "sqlite:///data.db"
# 调试模式
DEBUG = False
# 文件上传目录
UPLOAD_DIR = "uploads"
# 端口
PORT = 8080
# 监听地址
HOST = "0.0.0.0"
# 应用程序名称
APP_NAME = "HelloJudgeV2"
# 用于密码的盐
PASSWORD_SALT = "qeiduew9odpjh8q9uohr8"
# 用户名正则
USERNAME_REGEX = r"^[a-zA-Z0-9_-]+$"
# Redis地址
REDIS_URI = "redis://localhost:6379"
# 用于缓存的Redis数据库
CACHE_URL = "redis://localhost:6379/hj2-cache"
# 评测机列表
JUDGERS = {
    "UUID": "评测机名"
}

# 比赛失败提交罚时(分钟)
FAIL_SUBMIT_PENALTY = 20

