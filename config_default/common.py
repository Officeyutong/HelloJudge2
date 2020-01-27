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
# 比赛排行榜更新间隔
RANKLIST_UPDATE_INTEVAL = 60

ENABLE_CSRF_TOKEN = True

# 评测状态
JUDGE_STATUS = {
    "waiting": {"icon": "circle notched loading icon", "text": "等待评测中", "color": "blue"},
    "judging": {"icon": "circle notched loading icon", "text": "评测中", "color": "blue"},
    "accepted": {"icon": "check icon", "text": "通过", "color": "green"},
    "unaccepted": {"icon": "times icon", "text": "未通过", "color": "red"},
    "wrong_answer": {"icon": "x icon", "text": "答案错误", "color": "red"},
    "time_limit_exceed": {"icon": "clock outline icon", "text": "超出时限", "color": "red"},
    "memory_limit_exceed": {"icon": "microchip icon", "text": "内存超限", "color": "purple"},
    "runtime_error": {"icon": "exclamation circle icon", "text": "运行时错误", "color": "red"},
    "skipped": {"icon": "cog icon", "text": "跳过", "color": "blue"},
    "unknown": {"icon": "question circle icon", "text": "未知", "color": "black"},
    "invisible": {"icon": "times icon", "text": "不可见", "color": "black"},
    "unsubmitted": {"icon": "code icon", "text": "未提交", "color": "yellow"},
    "judge_failed": {"icon": "times icon", "text": "评测失败", "color": "red"},
    "compile_error": {"icon": "cog icon", "text": "编译错误", "color": "blue"}
}
