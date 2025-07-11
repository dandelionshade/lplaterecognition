#!/bin/bash
###
# @Author: 张震 116089016+dandelionshade@users.noreply.github.com
# @Date: 2025-07-11 15:49:01
# @LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
# @LastEditTime: 2025-07-11 15:56:45
# @FilePath: /lplaterecognition/quickstart.sh
# @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
###

# 天津仁爱学院车牌识别系统 - 快速启动脚本
# 作者: 张震
# 日期: 2025-07-11

echo "🚀 天津仁爱学院车牌识别系统启动脚本"
echo "================================"

# 检查Python版本
python_version=$(python3 --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ 发现Python: $python_version"
    PYTHON_CMD="python3"
else
    python_version=$(python --version 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✅ 发现Python: $python_version"
        PYTHON_CMD="python"
    else
        echo "❌ 错误: 未找到Python解释器"
        echo "请安装Python 3.8或更高版本"
        exit 1
    fi
fi

# 检查pip
if ! command -v pip &>/dev/null; then
    echo "❌ 错误: 未找到pip"
    echo "请安装pip包管理器"
    exit 1
fi

echo "✅ pip已安装"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 虚拟环境创建失败"
        exit 1
    fi
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📚 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠️  部分依赖包安装失败，尝试安装核心包..."
    pip install flask google-genai python-dotenv opencv-python numpy Pillow requests werkzeug
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "📝 创建环境配置文件..."
    cat >.env <<EOL
# Gemini API 密钥
# 请访问 https://aistudio.google.com/app/apikey 获取
API_KEY=your_gemini_api_key_here

# 服务器配置
PORT=8080
EOL
    echo "⚠️  请编辑 .env 文件，添加您的 Gemini API 密钥"
    echo "   获取地址: https://aistudio.google.com/app/apikey"
fi

# 创建上传目录
mkdir -p uploads

echo ""
echo "🎉 环境准备完成！"
echo ""
echo "📋 使用说明:"
echo "   1. 编辑 .env 文件，添加 Gemini API 密钥"
echo "   2. 运行 $PYTHON_CMD main.py 启动服务"
echo "   3. 访问 http://127.0.0.1:8080/home 查看主页"
echo "   4. 访问 http://127.0.0.1:8080/ocr 使用OCR功能"
echo ""
echo "🔧 可选安装 (提升功能):"
echo "   pip install paddleocr      # 百度OCR引擎"
echo "   pip install pytesseract    # Tesseract OCR"
echo "   pip install hyperlpr3      # 车牌识别引擎"
echo ""

# 询问是否立即启动
read -p "是否现在启动服务? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动服务..."
    $PYTHON_CMD main.py
fi
