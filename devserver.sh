#!/bin/sh
# 这是一个 shebang，它告诉系统这个脚本应该使用 /bin/sh 来执行。

# 下面的命令用于启动一个 Python Flask web 服务器。
# -u: 禁用标准输出的缓冲，使得日志和打印信息可以立刻显示出来。
# -m flask: 使用 flask 模块来运行应用。
# --app main: 指定 Flask 应用的入口文件是 main.py。
# run: Flask 的子命令，表示要启动开发服务器。
# -p ${PORT:-8000}: 设置服务器监听的端口。它会首先检查环境变量 PORT 是否被设置，
#                  如果没有，就使用默认端口 8000。
# --debug: 启用调试模式。这会让服务器在代码变动后自动重启，
#          并且在出错时提供详细的调试信息。
python -u -m flask --app main run -p ${PORT:-8000} --debug
