from .auth import *
from .remote_judge import *
from .judge import *
from .display import *
from .common import *
from .phoneauth import *
from .wiki import *
from .log import *
from collections import OrderedDict
# 在后台管理页面显示的配置
VISIBLE_SETTINGS = OrderedDict({
    "DEBUG": "调试模式",
    "UPLOAD_DIR": "上传文件目录",
    "PORT": "监听端口",
    "HOST": "监听地址",
    "APP_NAME": "应用程序名",
    "USERNAME_REGEX": "用户名正则",
    "PROBLEMS_PER_PAGE": "每页题目数量",
    "SUBMISSIONS_PER_PAGE": "每页提交数量",
    "DISCUSSIONS_PER_PAGE": "每页讨论数量",
    "COMMENTS_PER_PAGE": "每页评论数量",
    "CONTESTS_PER_PAGE": "每页比赛数量",
    "HOMEPAGE_BROADCAST": "主页公告数量",
    "HOMEPAGE_RANKLIST": "主页排行榜数量",
    "HOMEPAGE_PROBLEMS": "主页近期题目数量",
    "HOMEPAGE_DISCUSSIONS": "主页近期讨论数量",
    "USERS_ON_RANKLIST_PER_PAGE": "排行榜每页用户数量",
    "MAX_CODE_LENGTH": "代码最大长度(字节)",
    "COMPILE_TIME_LIMIT": "编译程序时间显示(ms)",
    "COMPILE_RESULT_LENGTH_LIMIT": "编译程序结果长度限制",
    "SPJ_EXECUTE_TIME_LIMIT": "SPJ执行时间限制(ms)",
    "IDE_RUN_TIME_LIMIT": "在线IDE运行程序时间限制(ms)",
    "IDE_RUN_MEMORY_LIMIT": "在线IDE运行程序内存限制(MB)",
    "IDE_RUN_RESULT_LENGTH_LIMIT": "在线IDE运行程序结果长度限制(char)",
    "AUTO_SYNC_FILES": "评测时自动同步题目文件",
    "OUTPUT_FILE_SIZE_LIMIT": "用户程序输出文件大小限制",
    "REQUIRE_REGISTER_AUTH": "注册时需要验证邮箱",
    "FAIL_SUBMIT_PENALTY": "比赛失败提交罚时(分钟)",
    "IDE_RUN_COMPILE_PARAMETER_LENGTH_LIMIT": "在线IDE自定义参数长度限制",
    "DISPLAY_DATA_LENGTH_LIMIT": "评测结束后显示的输入\\输出\\用户输出的长度限制,字符",
    "RANKLIST_UPDATE_INTEVAL": "比赛排行榜更新间隔"
})
