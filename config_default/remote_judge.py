# 远程评测可用OJ
REMOTE_JUDGE_OJS = {
    "luogu": {
        "display": "洛谷",
        "availableLanguages": {
            "1": {"display": "Pascal", "aceMode": "pascal"},
            "2": {"display": "C", "aceMode": "c_cpp"},
            "3": {"display": "C++", "aceMode": "c_cpp"},
            "4": {"display": "Python 2", "aceMode": "python"},
            "5": {"display": "Python 3", "aceMode": "python"},
        }
    },
    # "codeforces": {"display": "Codeforces"}
}
# 每次爬取后的延迟时间，单位为秒
TRACK_DELAY_INTERVAL = [3]*10+[10]*3+[30]*8+[60]*5
