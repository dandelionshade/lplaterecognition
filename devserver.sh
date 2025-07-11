#!/bin/bash
###
# @Author: 张震 116089016+dandelionshade@users.noreply.github.com
# @Date: 2025-07-10 15:59:29
# @LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
# @LastEditTime: 2025-07-11 16:34:59
# @FilePath: /lplaterecognition/devserver.sh
# @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
###

# 开发服务器启动脚本
# 用于开发和测试环境

echo "🔧 智能车牌识别平台 - 开发服务器"
echo "================================="

# 设置开发环境变量
export FLASK_ENV=development
export FLASK_DEBUG=1

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，创建默认配置..."
    cat >.env <<EOL
API_KEY=your_gemini_api_key_here
PORT=8080
EOL
    echo "请编辑.env文件添加您的Gemini API密钥"
fi

# 检查端口是否被占用
PORT=${PORT:-8080} # 从环境变量读取端口，默认8080
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用，尝试终止..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 2
fi

# 创建必要目录
mkdir -p uploads

echo "🚀 启动开发服务器..."
echo ""
echo "📱 访问地址:"
echo "  - 🏠 主页: http://127.0.0.1:$PORT/home"
echo "  - 🔍 OCR平台: http://127.0.0.1:$PORT/ocr"
echo "  - 🎯 原始演示: http://127.0.0.1:$PORT/"
echo "  - 📊 引擎状态: http://127.0.0.1:$PORT/api/ocr-engines"
echo ""
echo "💡 功能说明:"
echo "  - Gemini AI 智能图像分析"
echo "  - 多种OCR引擎文字识别"
echo "  - HyperLPR3专业车牌识别"
echo "  - OpenCV图像处理"
echo ""
echo "⏹️  按 Ctrl+C 停止服务器"
echo ""

# 检查Python依赖
echo "🔍 检查Python环境和依赖..."
python -c "import cv2, flask, numpy, paddleocr, pytesseract, hyperlpr3; print('✅ 所有依赖已安装')" || {
    echo "❌ 依赖检查失败，请运行安装脚本："
    echo "   bash install.sh"
    exit 1
}

# 启动Flask应用 - 使用flask命令启动
# -m flask: 使用 flask 模块来运行应用。
# --app main: 指定 Flask 应用的入口文件是 main.py。
# run: Flask 的子命令，表示要启动开发服务器。
# -p $PORT: 设置服务器监听的端口
# --debug: 启用调试模式。这会让服务器在代码变动后自动重启，
#          并且在出错时提供详细的调试信息。
echo "🚀 启动 Flask 开发服务器..."
flask --app main run -p $PORT --debug
