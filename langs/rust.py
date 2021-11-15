# 源程序文件名
SOURCE_FILE = "{filename}.rs"
# 输出程序文件名
OUTPUT_FILE = "{filename}.out"
# 编译命令行
COMPILE = "rustc -O -o {output} {source} {extra}"
# 运行命令行
RUN = 'sh -c "./{program} {redirect}"'
# 显示名
DISPLAY = "Rust 1.47.0"
# 版本
VERSION = "rustc 1.47.0"
# Ace.js模式
ACE_MODE = "c_cpp"
# HighlightJS高亮模式
HLJS_MODE = "rust"