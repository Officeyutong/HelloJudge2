# 源程序文件名
SOURCE_FILE = "{filename}.cpp"
# 输出程序文件名
OUTPUT_FILE = "{filename}.out"
# 编译命令行
COMPILE = "g++ -Wall -Wextra -std=c++11 -fdiagnostics-color=never -O2 {source} -o {output}"
# 运行命令行
RUN = 'sh -c "./{program} {redirect}"'