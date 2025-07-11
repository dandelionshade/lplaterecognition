#!/bin/bash

# 智能车牌识别系统安装脚本
echo "🚀 开始安装智能车牌识别系统依赖..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1)
echo "检测到 Python 版本: $python_version"

# 创建虚拟环境（如果不存在）
if [ ! -d ".venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 升级 pip
echo "📈 升级 pip..."
pip install --upgrade pip

# 安装基础依赖
echo "📚 安装基础依赖包..."
#!/bin/bash

# 智能车牌识别平台 - 自动安装脚本
# 作者: 张震
# 日期: 2025-07-11

echo "🚀 智能车牌识别平台 - 自动安装程序"
echo "===================================="

# 检查操作系统
OS="$(uname -s)"
case "${OS}" in
Linux*) MACHINE=Linux ;;
Darwin*) MACHINE=Mac ;;
CYGWIN*) MACHINE=Cygwin ;;
MINGW*) MACHINE=MinGw ;;
*) MACHINE="UNKNOWN:${OS}" ;;
esac
echo "🖥️  操作系统: $MACHINE"

# 检查Python版本
check_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
        PYTHON_CMD="python3"
        echo "✅ 发现Python3: $PYTHON_VERSION"
        return 0
    elif command -v python &>/dev/null; then
        PYTHON_VERSION=$(python --version | cut -d ' ' -f 2)
        PYTHON_CMD="python"
        echo "✅ 发现Python: $PYTHON_VERSION"
        return 0
    else
        echo "❌ 错误: 未找到Python解释器"
        echo "请安装Python 3.8或更高版本"
        echo "下载地址: https://www.python.org/downloads/"
        return 1
    fi
}

# 检查pip
check_pip() {
    if command -v pip3 &>/dev/null; then
        PIP_CMD="pip3"
        echo "✅ 发现pip3"
        return 0
    elif command -v pip &>/dev/null; then
        PIP_CMD="pip"
        echo "✅ 发现pip"
        return 0
    else
        echo "❌ 错误: 未找到pip包管理器"
        echo "请安装pip"
        return 1
    fi
}

# 安装核心依赖
install_core_dependencies() {
    echo "📦 安装核心依赖包..."

    # 核心包列表
    CORE_PACKAGES=(
        "flask>=3.0.0"
        "google-genai>=1.25.0"
        "python-dotenv>=1.0.0"
        "opencv-python>=4.8.0"
        "numpy>=1.24.0"
        "Pillow>=10.0.0"
        "requests>=2.31.0"
        "werkzeug>=3.0.0"
    )

    for package in "${CORE_PACKAGES[@]}"; do
        echo "  安装: $package"
        $PIP_CMD install "$package" --quiet
        if [ $? -eq 0 ]; then
            echo "  ✅ $package 安装成功"
        else
            echo "  ⚠️  $package 安装失败，继续..."
        fi
    done
}

# 安装OCR引擎
install_ocr_engines() {
    echo "🔍 安装OCR引擎..."

    # OCR包列表
    OCR_PACKAGES=(
        "paddlepaddle"
        "paddleocr"
        "pytesseract"
        "hyperlpr3"
    )

    for package in "${OCR_PACKAGES[@]}"; do
        echo "  尝试安装: $package"
        $PIP_CMD install "$package" --quiet
        if [ $? -eq 0 ]; then
            echo "  ✅ $package 安装成功"
        else
            echo "  ⚠️  $package 安装失败，可选功能将不可用"
        fi
    done
}

# 创建项目结构
setup_project_structure() {
    echo "📁 创建项目结构..."

    # 创建必要目录
    mkdir -p uploads
    mkdir -p web

    # 创建.env文件
    if [ ! -f ".env" ]; then
        echo "📝 创建环境配置文件..."
        cat >.env <<EOL
# Gemini API 密钥 - 请访问 https://aistudio.google.com/app/apikey 获取
API_KEY=your_gemini_api_key_here

# 服务器配置
PORT=8080
FLASK_ENV=development
FLASK_DEBUG=true
EOL
        echo "  ✅ .env 文件已创建"
    else
        echo "  ✅ .env 文件已存在"
    fi
}

# 验证安装
verify_installation() {
    echo "🔍 验证安装..."

    # 测试Python导入
    $PYTHON_CMD -c "
import flask
import cv2
import numpy as np
from PIL import Image
import google.genai as genai
print('✅ 核心模块导入成功')
" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "  ✅ 核心功能验证通过"
    else
        echo "  ⚠️  核心功能验证失败，可能需要手动安装某些依赖"
    fi

    # 测试可选模块
    echo "  检查可选模块..."

    $PYTHON_CMD -c "import paddleocr; print('  ✅ PaddleOCR 可用')" 2>/dev/null || echo "  ⚠️  PaddleOCR 不可用"
    $PYTHON_CMD -c "import pytesseract; print('  ✅ Tesseract 可用')" 2>/dev/null || echo "  ⚠️  Tesseract 不可用"
    $PYTHON_CMD -c "import hyperlpr3; print('  ✅ HyperLPR3 可用')" 2>/dev/null || echo "  ⚠️  HyperLPR3 不可用"
}

# 显示使用说明
show_usage() {
    echo ""
    echo "🎉 安装完成！"
    echo ""
    echo "📋 下一步操作:"
    echo "   1. 编辑 .env 文件，添加您的 Gemini API 密钥"
    echo "      获取地址: https://aistudio.google.com/app/apikey"
    echo ""
    echo "   2. 启动服务器:"
    echo "      ./devserver.sh"
    echo "      或者"
    echo "      $PYTHON_CMD main.py"
    echo ""
    echo "   3. 访问应用:"
    echo "      主页: http://127.0.0.1:8080/home"
    echo "      OCR平台: http://127.0.0.1:8080/ocr"
    echo ""
    echo "🔧 可选安装 (如果上述安装失败):"
    echo "   手动安装OCR引擎:"
    echo "   $PIP_CMD install paddleocr      # 百度OCR"
    echo "   $PIP_CMD install pytesseract    # Tesseract OCR"
    echo "   $PIP_CMD install hyperlpr3      # 车牌识别"
    echo ""
    echo "📚 文档地址:"
    echo "   README.md - 详细使用说明"
    echo "   GitHub: https://github.com/dandelionshade/lplaterecognition"
    echo ""
}

# 主安装流程
main() {
    echo "开始安装..."

    # 检查环境
    if ! check_python; then
        exit 1
    fi

    if ! check_pip; then
        exit 1
    fi

    # 升级pip
    echo "⬆️  升级pip..."
    $PIP_CMD install --upgrade pip --quiet

    # 安装依赖
    install_core_dependencies
    install_ocr_engines

    # 配置项目
    setup_project_structure

    # 验证安装
    verify_installation

    # 显示使用说明
    show_usage

    # 询问是否立即启动
    echo ""
    read -p "🚀 是否现在启动服务器? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "main.py" ]; then
            echo "启动服务器..."
            $PYTHON_CMD main.py
        else
            echo "❌ 未找到main.py文件"
        fi
    fi
}

# 运行主程序
main "$@"

# 检查 Tesseract 安装状态
echo "🔍 检查 Tesseract OCR 安装状态..."
if command -v tesseract &>/dev/null; then
    echo "✅ Tesseract 已安装"
    tesseract --version
else
    echo "❌ Tesseract 未安装"
    echo "请手动安装 Tesseract:"
    echo "  macOS: brew install tesseract tesseract-lang"
    echo "  Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim"
    echo "  Windows: 下载并安装 https://github.com/UB-Mannheim/tesseract/wiki"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "🚀 启动服务器:"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo ""
echo "🌐 访问地址:"
echo "  原始功能: http://localhost:8000"
echo "  车牌识别: http://localhost:8000/ocr"
echo ""
echo "📝 功能说明:"
echo "  ✨ Gemini AI 多模态分析"
echo "  🔤 PaddleOCR 中英文识别"
echo "  🏛️ Tesseract 传统 OCR"
echo "  🚗 HyperLPR3 专业车牌识别"
echo "  🖼️ OpenCV 图像处理"
