# 源程序文件名
SOURCE_FILE = "{filename}.hs"
# 输出程序文件名
OUTPUT_FILE = "{filename}.out"
# 编译命令行
COMPILE = "ghc {source} -o {output} {extra}"
# 运行命令行
RUN = 'sh -c "./{program} {redirect}"'
# 显示名
DISPLAY = "Haskell"
# 版本
VERSION = "GHC 8.6.5"
# Ace.js模式
ACE_MODE = "haskell"
# HighlightJS高亮模式
HLJS_MODE = "haskell"