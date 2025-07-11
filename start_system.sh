#!/bin/bash
###
# @Author: 张震 116089016+dandelionshade@users.noreply.github.com
# @Date: 2025-07-11 16:35:00
# @FilePath: /lplaterecognition/start_system.sh
# @Description: 天津仁爱学院车牌识别系统启动脚本
###

echo "🚗 天津仁爱学院车牌识别系统"
echo "=============================="
echo ""

# 检查环境
if ! command -v python3 &>/dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

# 检查并创建.env文件
if [ ! -f ".env" ]; then
    echo "📝 首次运行，创建配置文件..."
    cat >.env <<EOL
# Gemini API 密钥 - 请访问 https://aistudio.google.com/app/apikey 获取
API_KEY=your_gemini_api_key_here

# 服务器配置
PORT=8080

# 系统安全密钥（生产环境请修改为随机字符串）
SECRET_KEY=tianjin_renai_college_plate_recognition_2025
EOL
    echo "⚠️  请编辑 .env 文件，添加您的 Gemini API 密钥"
fi

# 创建上传目录
mkdir -p uploads

echo ""
echo "🔐 管理员登录信息："
echo "   账号: admin"
echo "   密码: admin"
echo ""
echo "🌐 访问地址："
echo "   登录页面: http://127.0.0.1:8080/login"
echo "   管理控制台: http://127.0.0.1:8080/admin"
echo "   系统主页: http://127.0.0.1:8080/home"
echo "   车牌识别: http://127.0.0.1:8080/ocr"
echo ""

# 启动系统
echo "🚀 启动天津仁爱学院车牌识别系统..."
python3 main.py
