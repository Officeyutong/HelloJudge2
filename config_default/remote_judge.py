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
    "poj": {
        "display": "POJ",
        "availableLanguages": {
            "0": {"display": "G++", "aceMode": "c_cpp"},
            "1": {"display": "GCC", "aceMode": "c_cpp"},
            "2": {"display": "Java", "aceMode": "java"},
            "3": {"display": "Pascal", "aceMode": "pascal"},
            "4": {"display": "C++", "aceMode": "c_cpp"},
            "5": {"display": "C", "aceMode": "c_cpp"},
            "6": {"display": "Fortran", "aceMode": "fortran"},
        }
    },
    "uoj": {
        "display": "Universal OJ",
        "availableLanguages": {
            "C++": {"display": "C++", "aceMode": "c_cpp"},
            "Python2.7": {"display": "Python2.7", "aceMode": "python"},
            "Java7": {"display": "Java7", "aceMode": "java"},
            "C++11": {"display": "C++11", "aceMode": "c_cpp"},
            "Python3": {"display": "Python 3", "aceMode": "python"},
            "Java8": {"display": "Java8", "aceMode": "java"},
            "C": {"display": "C", "aceMode": "c_cpp"},
            "Pascal": {"display": "Pascal", "aceMode": "pascal"},
        }
    },
    "darkbzoj": {
        "display": "Dark BZOJ",
        "availableLanguages": {
            "C++": {"display": "C++", "aceMode": "c_cpp"},
            "Python2.7": {"display": "Python2.7", "aceMode": "python"},
            "Java7": {"display": "Java7", "aceMode": "java"},
            "C++11": {"display": "C++11", "aceMode": "c_cpp"},
            "Python3": {"display": "Python 3", "aceMode": "python"},
            "Java8": {"display": "Java8", "aceMode": "java"},
            "C": {"display": "C", "aceMode": "c_cpp"},
            "Pascal": {"display": "Pascal", "aceMode": "pascal"},
        }
    }
    # "codeforces": {"display": "Codeforces"}
}
# 每次爬取后的延迟时间，单位为秒
TRACK_DELAY_INTERVAL = [3]*10+[10]*3+[30]*8+[60]*5
