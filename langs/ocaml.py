# 源程序文件名
SOURCE_FILE = "{filename}.ml"
# 输出程序文件名
OUTPUT_FILE = "{filename}.out"
# 编译命令行
COMPILE = "ocamlc -custom str.cma -o {output} {source} {extra}"
# 运行命令行
RUN = 'sh -c "./{program} {redirect}"'
# 显示名
DISPLAY = "OCaml"
# 版本
VERSION = "OCamlc 4.05.0"
# Ace.js模式
ACE_MODE = "ocaml"
