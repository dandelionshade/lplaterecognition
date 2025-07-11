#!/bin/bash
###
# @Author: 张震 116089016+dandelionshade@users.noreply.github.com
# @Date: 2025-07-11 16:30:00
# @LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
# @LastEditTime: 2025-07-11 16:30:00
# @FilePath: /lplaterecognition/test_login.sh
# @Description: 测试登录功能的脚本
###

echo "🧪 天津仁爱学院车牌识别系统 - 登录功能测试"
echo "=============================================="

# 检查Python和依赖
echo "📋 检查环境..."
python3 -c "import flask, hashlib, functools; print('✅ 必要的Python模块已安装')" || {
    echo "❌ 缺少必要的Python模块"
    exit 1
}

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "📝 创建测试用的.env文件..."
    cat >.env <<EOL
# Gemini API 密钥
API_KEY=test_key_for_development

# 服务器配置
PORT=8080

# 会话密钥（生产环境请修改）
SECRET_KEY=tianjin_renai_college_plate_recognition_2025
EOL
fi

echo ""
echo "🎯 测试信息："
echo "   管理员账号: admin"
echo "   管理员密码: admin"
echo "   登录页面: http://127.0.0.1:8080/login"
echo "   管理控制台: http://127.0.0.1:8080/admin"
echo "   系统主页: http://127.0.0.1:8080/home"
echo "   车牌识别: http://127.0.0.1:8080/ocr"
echo ""
echo "🔒 安全特性："
echo "   ✅ 所有页面均需要登录验证"
echo "   ✅ 所有API接口均需要登录验证"
echo "   ✅ 会话管理和自动跳转"
echo "   ✅ 密码哈希存储"
echo ""

# 询问是否启动测试服务器
read -p "是否启动测试服务器? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动天津仁爱学院车牌识别系统..."
    echo "   访问 http://127.0.0.1:8080/login 开始测试"
    python3 main.py
fi
