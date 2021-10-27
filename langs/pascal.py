# 源程序文件名
SOURCE_FILE = "{filename}.pas"
# 输出程序文件名
OUTPUT_FILE = "{filename}.out"
# 编译命令行
COMPILE = "fpc {source} -o{output} {extra}"
# 运行命令行
RUN = 'sh -c "./{program} {redirect}"'
# 显示名
DISPLAY = "Pascal"
# 版本
VERSION = "FreePascal"
# Ace.js模式
ACE_MODE = "pascal"
# HighlightJS高亮模式
HLJS_MODE = "pascal"