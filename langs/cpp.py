# 源程序文件名
SOURCE_FILE = "{filename}.cpp"
# 输出程序文件名
OUTPUT_FILE = "{filename}.out"
# 编译命令行
COMPILE = "g++ -Wall -Wextra  -fdiagnostics-color=never -DONLINE_JUDGE -O2 {source} -o {output} {extra}"
# 运行命令行
RUN = 'sh -c "./{program} {redirect}"'
# 显示名
DISPLAY = "C++"
# 版本
VERSION = "G++ 8.3"
# Ace.js模式
ACE_MODE = "c_cpp"
