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
APP_NAME = "QBXTOJ"
# 用于密码的盐
PASSWORD_SALT = "qeiduew9odpjh8q9uohr8"
# 用户名正则
USERNAME_REGEX = r"^[a-zA-Z0-9_-]+$"
# Redis地址 (评测队列)
REDIS_URI = "redis://localhost:6379/1"
# 用于缓存的Redis数据库
CACHE_URL = "redis://localhost:6379/2"
# 用于执行后台任务的队列
BACKGROUNDTASK_URI = "redis://localhost:6379/3"
# 用于存储短信验证码的数据库
REDIS_PHONEAUTH_URI = "redis://localhost:6379/4"
# 用于分布式锁的REDIS_URL
REDIS_LOCK_URI = "redis://localhost:6379/5"
# 评测机列表
JUDGERS = {
    "UUID": "评测机名"
}

# 比赛失败提交罚时(分钟)
FAIL_SUBMIT_PENALTY = 20
# 比赛排行榜更新间隔
RANKLIST_UPDATE_INTERVAL = 60
# 已关闭的比赛排行榜的更新间隔(s)
RANKLIST_UPDATE_INTERVAL_CLOSED_CONTESTS = 60*30
# 通过题目列表刷新间隔(秒)
ACCEPTED_PROBLEMS_REFRESH_INTERVAL = 5*60
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

# 在在线IDE和评测信息页面使用轮询而不是SocketIO
USE_POLLING = False

# 每个用户关注的用户数上限
FOLLOWING_COUNT_LIMIT = 30

# 多长时间刷新一下用户的feed流
# 单位为秒
FEED_STREAM_REFRESH_INTERVAL = 30

# 用户待做题目最大数量
MAX_PROBLEMTODO_COUNT = 50

# 图床展示页每页数量
IMAGES_PER_PAGE = 20

# Gravatar URL前缀
GRAVATAR_URL_PREFIX = "https://www.gravatar.com/avatar/"

DISABLE_IOI_CONTEST = False