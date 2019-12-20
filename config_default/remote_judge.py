# 使用的消息队列
REMOTE_JUDGE_BROKER = "redis://127.0.0.1/2"
# 远程评测可用OJ
REMOTE_JUDGE_OJS = {
    "luogu": {
        "display": "洛谷",
        "availableLanguages": {
            "1": {"display": "Pascal", "aceMode": "pascal"},
            "2": {"display": "C", "aceMode": "c_cpp"},
            "3": {"display": "C++", "aceMode": "c_cpp"},
            "4": {"display": "C++ 11", "aceMode": "c_cpp"},
            "6": {"display": "Python 2", "aceMode": "python"},
            "7": {"display": "Python 3", "aceMode": "python"},
            "8": {"display": "Java 8", "aceMode": "java"},
            "9": {"display": "Node v8.9", "aceMode": "javascript"},
            "11": {"display": "C++ 14", "aceMode": "c_cpp"},
            "12": {"display": "C++ 17", "aceMode": "c_cpp"},
        }
    },
    # "codeforces": {"display": "Codeforces"}
}
# 每次爬取后的延迟时间，单位为秒
TRACK_DELAY_INTERVAL = [3]*10+[10]*3+[30]*8+[60]*5
