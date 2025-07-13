'''
Author: 张震 116089016+dandelionshade@users.noreply.github.com
Date: 2025-07-10 15:44:41
LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
LastEditTime: 2025-07-12 18:43:13
FilePath: /lplaterecognition/main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# 导入 json 库，用于处理 JSON 数据格式。
import json
# 导入 os 库，用于与操作系统交互，如此处用于获取环境变量。
import os
# 导入 load_dotenv 函数，用于从 .env 文件加载环境变量。
from dotenv import load_dotenv
# 导入 base64 库，用于图像编码解码
import base64
# 导入 io 库，用于处理字节流
import io
# 导入时间库，用于生成唯一文件名
import time
# 导入 Flask 相关模块，增加会话管理功能
from flask import Flask, jsonify, request, send_file, send_from_directory, Response, session, redirect, url_for, render_template_string
from werkzeug.utils import secure_filename
# 导入 functools 用于装饰器
from functools import wraps
# 导入 hashlib 用于密码哈希
import hashlib
import io
import json
import os
import re
import time
import traceback
import base64

import cv2
import numpy as np
# 导入 OpenCV 用于图像处理
# 导入 numpy 用于数值计算
# 导入 PIL 用于图像操作
from PIL import Image

# 导入 OCR 相关库
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PaddleOCR = None  # Define PaddleOCR as None if import fails
    PADDLEOCR_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import hyperlpr3 as lpr3
    HYPERLPR_AVAILABLE = True
except ImportError:
    lpr3 = None
    HYPERLPR_AVAILABLE = False

# 导入 easyocr 库
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# 导入 google.genai 库，这是 Google Gemini API 的 Python 客户端。
import google.genai as genai

# 加载 .env 文件中的环境变量。
load_dotenv()

# 🔥🔥 请务必先填写这里！🔥🔥
# 通过以下方式获取您的 Gemini API 密钥：
# - 在侧边栏的 "Firebase Studio" 面板中选择 "Add Gemini API"
# - 或者访问 https://g.co/ai/idxGetGeminiKey
# 从环境变量中获取名为 'API_KEY' 的值。
API_KEY = os.environ.get('API_KEY')

# 使用获取到的 API 密钥初始化 Gemini 客户端。
ai = genai.Client(api_key=API_KEY)
# 创建一个 Flask 应用实例。
app = Flask(__name__)

# 设置会话密钥（用于安全会话管理）
app.secret_key = os.environ.get('SECRET_KEY', 'tianjin_renai_college_plate_recognition_2025')

# 管理员配置
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = hashlib.sha256('admin'.encode()).hexdigest()

# 鉴权装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# HTML模板
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>天津仁爱学院车牌识别系统 - 管理员登录</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Microsoft YaHei', sans-serif;
        }
        
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            width: 400px;
            text-align: center;
        }
        
        .logo {
            font-size: 3em;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .title {
            font-size: 1.8em;
            color: #4a5568;
            margin-bottom: 30px;
            font-weight: 600;
        }
        
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #4a5568;
            font-weight: 500;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .login-btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .error {
            background: #fed7d7;
            color: #c53030;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .footer {
            margin-top: 30px;
            color: #718096;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">🚗</div>
        <h1 class="title">天津仁爱学院<br>车牌识别系统</h1>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="username">管理员账号</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="login-btn">登录系统</button>
        </form>
        
        <div class="footer">
            <p>天津仁爱学院智能车牌识别管理系统</p>
            <p>© 2025 版权所有</p>
        </div>
    </div>
</body>
</html>
"""

ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>天津仁爱学院车牌识别系统 - 管理员控制台</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #f7fafc;
            font-family: 'Microsoft YaHei', sans-serif;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo-text {
            font-size: 1.5em;
            font-weight: 600;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        .logout-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .main-content {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
        }
        
        .dashboard-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        
        .card-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .card-title {
            font-size: 1.3em;
            margin-bottom: 10px;
            color: #2d3748;
        }
        
        .card-description {
            color: #718096;
            margin-bottom: 20px;
        }
        
        .card-button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        
        .card-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo-text">🚗 天津仁爱学院车牌识别系统</div>
            <div class="user-info">
                <span>欢迎，{{ username }} 管理员</span>
                <a href="/logout" class="logout-btn">退出登录</a>
            </div>
        </div>
    </div>
    
    <div class="main-content">
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-icon">🏠</div>
                <h3 class="card-title">系统主页</h3>
                <p class="card-description">访问系统主页，查看平台概览和功能介绍</p>
                <a href="/home" class="card-button">进入主页</a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">🔍</div>
                <h3 class="card-title">车牌识别</h3>
                <p class="card-description">上传图片进行智能车牌识别和OCR文字识别</p>
                <a href="/ocr" class="card-button">开始识别</a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">📊</div>
                <h3 class="card-title">系统状态</h3>
                <p class="card-description">查看系统运行状态和OCR引擎可用性</p>
                <a href="/api/ocr-engines" class="card-button">查看状态</a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">⚙️</div>
                <h3 class="card-title">系统设置</h3>
                <p class="card-description">管理系统配置和用户权限设置</p>
                <button class="card-button" onclick="alert('功能开发中...')">系统设置</button>
            </div>
        </div>
    </div>
</body>
</html>
"""

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 初始化 OCR 引擎 - 优化版本
ocr_engines = {}

def init_ocr_engines():
    """延迟初始化OCR引擎，避免启动时错误"""
    global ocr_engines, PADDLEOCR_AVAILABLE, EASYOCR_AVAILABLE, HYPERLPR_AVAILABLE
    
    # PaddleOCR初始化
    if PADDLEOCR_AVAILABLE and PaddleOCR is not None and 'paddleocr' not in ocr_engines:
        try:
            ocr_engines['paddleocr'] = PaddleOCR(lang='ch', show_log=False)
            print("✅ PaddleOCR 初始化成功")
        except Exception as e:
            print(f"❌ PaddleOCR 初始化失败: {e}")
            PADDLEOCR_AVAILABLE = False

    # HyperLPR3初始化
    if HYPERLPR_AVAILABLE and lpr3 is not None and 'hyperlpr3' not in ocr_engines:
        try:
            ocr_engines['hyperlpr3'] = lpr3.LicensePlateCatcher()
            print("✅ HyperLPR3 初始化成功")
        except Exception as e:
            print(f"❌ HyperLPR3 初始化失败: {e}")
            HYPERLPR_AVAILABLE = False

    # EasyOCR初始化（仅在需要时）
    if EASYOCR_AVAILABLE and 'easyocr' not in ocr_engines:
        try:
            import easyocr
            ocr_engines['easyocr'] = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            print("✅ EasyOCR 初始化成功")
        except Exception as e:
            print(f"❌ EasyOCR 初始化失败: {e}")
            EASYOCR_AVAILABLE = False

# 图像处理工具函数
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def base64_to_opencv(base64_string):
    """将 base64 字符串转换为 OpenCV 图像"""
    try:
        # 解码 base64
        image_data = base64.b64decode(base64_string)
        # 转换为 numpy 数组
        nparr = np.frombuffer(image_data, np.uint8)
        # 解码为 OpenCV 图像
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"Base64 转换错误: {e}")
        return None

def opencv_to_base64(image):
    """将 OpenCV 图像转换为 base64 字符串"""
    try:
        # 编码图像
        _, buffer = cv2.imencode('.jpg', image)
        # 转换为 base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
    except Exception as e:
        print(f"图像编码错误: {e}")
        return None

def apply_image_processing(image, operation, params=None):
    """应用图像处理操作"""
    if params is None:
        params = {}
    
    try:
        if operation == 'gray':
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif operation == 'blur':
            kernel_size = params.get('kernel_size', 5)
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif operation == 'edge':
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return cv2.Canny(gray, params.get('low', 50), params.get('high', 150))
        elif operation == 'threshold':
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, params.get('thresh', 127), 255, cv2.THRESH_BINARY)
            return thresh
        elif operation == 'resize':
            width = params.get('width', 400)
            height = params.get('height', 300)
            return cv2.resize(image, (width, height))
        elif operation == 'rotate':
            angle = params.get('angle', 90)
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            return cv2.warpAffine(image, M, (w, h))
        elif operation == 'enhance':
            # 增强对比度和亮度
            alpha = params.get('alpha', 1.2)  # 对比度
            beta = params.get('beta', 10)     # 亮度
            return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        else:
            return image
    except Exception as e:
        print(f"图像处理错误: {e}")
        return image


# 登录页面
@app.route("/login", methods=["GET", "POST"])
def login():
    """管理员登录页面"""
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 验证用户名和密码
        if username and password and username == ADMIN_USERNAME and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="用户名或密码错误")
    
    return render_template_string(LOGIN_TEMPLATE)

# 管理员仪表盘
@app.route("/admin")
@login_required
def admin_dashboard():
    """管理员仪表盘"""
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, username=session.get('username'))

# 登出
@app.route("/logout")
def logout():
    """管理员登出"""
    session.clear()
    return redirect(url_for('login'))

# 主页路由 - 需要登录
@app.route("/")
@login_required
def index():
    return redirect(url_for('home'))

# 主页路由 - 需要登录
@app.route("/home")
@login_required
def home():
    """主页"""
    response = send_from_directory('web', 'home.html')
    # 添加安全头
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

# OCR页面 - 需要登录
@app.route("/ocr")
@login_required
def ocr_page():
    """OCR识别页面"""
    response = send_from_directory('web', 'ocr.html')
    # 添加安全头
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


# 定义 /api/generate 路由的处理函数，只接受 POST 请求。
@app.route("/api/generate", methods=["POST"])
@login_required
def generate_api():
    # 确保请求方法是 POST。
    if request.method == "POST":
        # 检查 API_KEY 是否已经设置。
        if API_KEY == 'TODO':
            # 如果没有设置，返回一个错误信息，提示用户去获取密钥。
            return jsonify({ "error": '''
                要开始使用，请在 https://g.co/ai/idxGetGeminiKey 获取一个 API 密钥，
                并在 main.py 文件中填入。
                '''.replace('\n', '') })
        try:
            # 获取 POST 请求的 JSON Body。
            req_body = request.get_json()
            # 从请求体中提取 "contents" 字段。
            contents = req_body.get("contents")
            # 调用 Gemini API 的 generate_content_stream 方法，以流式方式生成内容。
            # model: 指定使用的模型，从请求体中获取。
            # contents: 传递给模型的内容（包含图片和文本）。
            response = ai.models.generate_content_stream(model=req_body.get("model"), contents=contents)
            
            # 定义一个生成器函数，用于逐块产生响应数据。
            def stream():
                # 遍历从 API 返回的流式响应的每一个数据块。
                for chunk in response:
                    # 将每个数据块格式化为 Server-Sent Events (SSE) 格式。
                    # 'data: ' 是 SSE 的标准前缀。
                    # json.dumps 将包含文本的字典转换为 JSON 字符串。
                    yield 'data: %s\n\n' % json.dumps({ "text": chunk.text })

            # 返回一个 Response 对象，内容是 stream() 函数生成的流。
            # mimetype='text/event-stream' 告诉浏览器这是一个事件流。
            return Response(stream(), mimetype='text/event-stream')

        except Exception as e:
            # 如果在与 API 交互过程中发生任何异常，返回一个包含错误信息的 JSON。
            return jsonify({ "error": str(e) })
    # 如果请求不是 POST（虽然路由已限制），返回一个 "方法不允许" 的错误。
    return jsonify({"error": "Method not allowed"}), 405


# 图像处理 API
@app.route("/api/process-image", methods=["POST"])
@login_required
def process_image_api():
    """处理图像的 API 端点"""
    if request.method == "POST":
        try:
            data = request.get_json()
            image_base64 = data.get('image')
            operation = data.get('operation', 'gray')
            params = data.get('params', {})
            
            if not image_base64:
                return jsonify({"error": "没有提供图像数据"}), 400
            
            # 转换为 OpenCV 图像
            image = base64_to_opencv(image_base64)
            if image is None:
                return jsonify({"error": "图像格式错误"}), 400
            
            # 应用图像处理
            processed_image = apply_image_processing(image, operation, params)
            
            # 如果处理后的图像是灰度图，需要转换为3通道
            if len(processed_image.shape) == 2:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
            
            # 转换回 base64
            result_base64 = opencv_to_base64(processed_image)
            if result_base64 is None:
                return jsonify({"error": "图像编码失败"}), 500
            
            return jsonify({
                "success": True,
                "processed_image": result_base64,
                "operation": operation,
                "params": params
            })
        
        except Exception as e:
            return jsonify({"error": f"图像处理失败: {str(e)}"}), 500
    
    return jsonify({"error": "Method not allowed"}), 405

# OCR 识别 API - 多引擎备用系统
@app.route("/api/ocr-simple", methods=["POST"])
def ocr_simple_api():
    """增强的OCR识别API，确保核心功能可用 - 多引擎备用系统"""
    try:
        data = request.get_json()
        image_base64 = data.get('image')
        engine = data.get('engine', 'auto')  # 改为自动选择最佳引擎
        
        if not image_base64:
            return jsonify({"error": "没有提供图像数据"}), 400
        
        # 转换为 OpenCV 图像
        try:
            image_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                return jsonify({"error": "图像格式错误"}), 400
        except Exception as e:
            return jsonify({"error": f"图像解码失败: {str(e)}"}), 400
        
        # 🔍 图像质量分析
        image_quality = analyze_image_quality(image)
        print(f"📊 图像质量评分: {image_quality['quality_score']}/100")
        if image_quality['suggestions']:
            print(f"💡 改进建议: {'; '.join(image_quality['suggestions'])}")
        
        # 根据图像质量调整识别策略
        use_enhanced_processing = image_quality['quality_score'] < 70
        
        # 🚀 智能引擎选择策略 - 增加备用系统
        def get_engines_priority(requested_engine):
            if requested_engine == 'auto':
                return ['hyperlpr3', 'paddleocr', 'easyocr', 'tesseract', 'fallback']
            elif requested_engine == 'hyperlpr3':
                return ['hyperlpr3', 'paddleocr', 'easyocr', 'tesseract', 'fallback']
            elif requested_engine == 'paddleocr':
                return ['paddleocr', 'easyocr', 'tesseract', 'hyperlpr3', 'fallback']
            elif requested_engine == 'easyocr':
                return ['easyocr', 'paddleocr', 'tesseract', 'hyperlpr3', 'fallback']
            else:  # tesseract
                return ['tesseract', 'paddleocr', 'easyocr', 'hyperlpr3', 'fallback']
        
        engines_to_try = get_engines_priority(engine)
        best_result = None
        best_confidence = 0
        
        # 🎯 多引擎识别循环
        for engine_name in engines_to_try:
            try:
                engine_result = None
                
                # HyperLPR3 专业车牌识别
                if engine_name == 'hyperlpr3' and HYPERLPR_AVAILABLE and 'hyperlpr3' in ocr_engines:
                    try:
                        catcher = ocr_engines['hyperlpr3']
                        
                        # 图像预处理增强，提高识别率
                        enhanced_image = enhance_image_for_ocr(image, 'plate')
                        rgb_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB) if len(enhanced_image.shape) == 3 else cv2.cvtColor(enhanced_image, cv2.COLOR_GRAY2RGB)
                        
                        plates = catcher(rgb_image)
                        
                        # 如果增强图像没有结果，尝试原图
                        if not plates or len(plates) == 0:
                            print("🔄 HyperLPR3: 尝试原图识别...")
                            rgb_original = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                            plates = catcher(rgb_original)
                        
                        if plates and len(plates) > 0:
                            plate_results = []
                            low_confidence_plates = []
                            
                            for plate in plates:
                                if plate and len(plate) >= 2:
                                    plate_no = str(plate[0]) if plate[0] else ''
                                    confidence = float(plate[1]) if isinstance(plate[1], (int, float)) else 0.0
                                    
                                    plate_info = {
                                        'text': plate_no,
                                        'confidence': confidence,
                                        'bbox': plate[2] if len(plate) > 2 else None
                                    }
                                    
                                    if plate_no and confidence > 0.1:  # 正常置信度车牌
                                        plate_results.append(plate_info)
                                    elif plate_no and confidence > 0.05:  # 低置信度但有内容的车牌
                                        low_confidence_plates.append(plate_info)
                            
                            # 处理正常置信度车牌
                            if plate_results:
                                best_plate = max(plate_results, key=lambda x: x['confidence'])
                                engine_result = {
                                    'engine': 'hyperlpr3',
                                    'text': best_plate['text'],
                                    'confidence': best_plate['confidence'],
                                    'plates': plate_results,
                                    'low_confidence_plates': low_confidence_plates,
                                    'engine_available': True,
                                    'enhanced_processing': True
                                }
                                print(f"✅ HyperLPR3识别成功: {best_plate['text']} (置信度: {best_plate['confidence']:.2f})")
                                if low_confidence_plates:
                                    print(f"📊 HyperLPR3低置信度候选: {', '.join([f'{p['text']}({p['confidence']:.2f})' for p in low_confidence_plates])}")
                            
                            # 处理只有低置信度车牌的情况
                            elif low_confidence_plates:
                                best_low_plate = max(low_confidence_plates, key=lambda x: x['confidence'])
                                print(f"⚠️ HyperLPR3: 检测到车牌数据但置信度过低")
                                print(f"📋 低置信度候选车牌: {', '.join([f'{p['text']}({p['confidence']:.2f})' for p in low_confidence_plates])}")
                                print(f"🎯 最高置信度候选: {best_low_plate['text']} (置信度: {best_low_plate['confidence']:.2f})")
                                
                                # 将低置信度结果作为备用信息保存
                                engine_result = {
                                    'engine': 'hyperlpr3_low_confidence',
                                    'text': best_low_plate['text'],
                                    'confidence': best_low_plate['confidence'] * 0.5,  # 降权处理
                                    'low_confidence_plates': low_confidence_plates,
                                    'engine_available': True,
                                    'is_low_confidence': True,
                                    'suggestion': '建议提高图片质量或调整光照条件'
                                }
                            else:
                                print("⚠️ HyperLPR3: 未检测到任何车牌")
                    except Exception as e:
                        print(f"❌ HyperLPR3失败: {e}")
                        import traceback
                        traceback.print_exc()
                
                # PaddleOCR 通用识别
                elif engine_name == 'paddleocr' and PADDLEOCR_AVAILABLE and 'paddleocr' in ocr_engines:
                    try:
                        # 使用新的PaddleOCR API，移除已弃用的cls参数
                        paddle_results = ocr_engines['paddleocr'].ocr(image)
                        
                        if paddle_results and paddle_results[0]:
                            texts = []
                            confidences = []
                            
                            for line in paddle_results[0]:
                                if line and len(line) >= 2 and line[1][1] > 0.3:  # 降低置信度阈值
                                    text = line[1][0].strip()
                                    conf = line[1][1]
                                    texts.append(text)
                                    confidences.append(conf)
                            
                            if texts:
                                full_text = ''.join(texts).replace(' ', '')  # 去除空格
                                avg_confidence = sum(confidences) / len(confidences)
                                
                                # 车牌格式检查加分
                                import re
                                plate_pattern = r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-Z0-9]{4,5}'
                                if re.search(plate_pattern, full_text):
                                    avg_confidence = min(avg_confidence + 0.3, 1.0)  # 格式匹配奖励
                                
                                engine_result = {
                                    'engine': 'paddleocr',
                                    'text': full_text,
                                    'confidence': avg_confidence,
                                    'texts': texts,
                                    'individual_confidences': confidences,
                                    'engine_available': True,
                                    'plate_format_matched': bool(re.search(plate_pattern, full_text))
                                }
                                print(f"✅ PaddleOCR识别成功: {full_text} (置信度: {avg_confidence:.2f})")
                                if len(texts) > 1:
                                    print(f"📋 PaddleOCR识别详情: {', '.join([f'{t}({c:.2f})' for t, c in zip(texts, confidences)])}")
                    except Exception as e:
                        print(f"❌ PaddleOCR失败: {e}")
                
                # Tesseract OCR 备用识别
                elif engine_name == 'tesseract' and TESSERACT_AVAILABLE:
                    try:
                        import pytesseract
                        from PIL import Image as PILImage
                        
                        # 图像预处理增强
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        
                        # 应用多种预处理尝试
                        processed_images = [
                            gray,  # 原始灰度
                            enhance_image_for_ocr(gray, 'plate'),  # 车牌专用增强
                            cv2.GaussianBlur(gray, (3, 3), 0),  # 轻微模糊
                        ]
                        
                        best_text = ""
                        best_conf = 0
                        
                        for processed_img in processed_images:
                            # 车牌专用配置
                            configs = [
                                '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼',
                                '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼',
                                '--psm 6'
                            ]
                            
                            for config in configs:
                                try:
                                    if len(processed_img.shape) == 3:
                                        pil_image = PILImage.fromarray(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB))
                                    else:
                                        pil_image = PILImage.fromarray(processed_img)
                                    
                                    text = pytesseract.image_to_string(pil_image, lang='chi_sim+eng', config=config)
                                    text = text.strip().replace(' ', '').replace('\n', '')
                                    
                                    if text and len(text) >= 5:
                                        # 更智能的置信度评估
                                        import re
                                        plate_chars = "京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                                        clean_text = ''.join(filter(lambda char: char in plate_chars, text))
                                        cleanliness_score = len(clean_text) / len(text) if len(text) > 0 else 0
                                        
                                        # 基础置信度基于清晰度
                                        confidence = cleanliness_score * 0.7
                                        
                                        # 车牌格式检查
                                        if re.search(r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z]', text):
                                            confidence += 0.25
                                        
                                        if confidence > best_conf:
                                            best_text = text
                                            best_conf = confidence
                                            
                                except Exception:
                                    continue
                        
                        if best_text:
                            # 车牌格式匹配检查
                            import re
                            plate_pattern = r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z]'
                            format_matched = bool(re.search(plate_pattern, best_text))
                            
                            engine_result = {
                                'engine': 'tesseract',
                                'text': best_text,
                                'confidence': best_conf,
                                'engine_available': True,
                                'plate_format_matched': format_matched,
                                'processing_method': 'multi_config_enhanced'
                            }
                            
                            status_icon = "🎯" if format_matched else "⚠️"
                            format_info = "车牌格式" if format_matched else "通用文本"
                            print(f"{status_icon} Tesseract识别成功: {best_text} (置信度: {best_conf:.2f}, {format_info})")
                            
                    except Exception as e:
                        print(f"❌ Tesseract失败: {e}")
                
                # EasyOCR 备用识别
                elif engine_name == 'easyocr' and EASYOCR_AVAILABLE and 'easyocr' in ocr_engines:
                    try:
                        # EasyOCR 返回一个列表，每个元素包含 [bbox, text, confidence]
                        easyocr_results = ocr_engines['easyocr'].readtext(image)
                        
                        if easyocr_results:
                            texts = [res[1] for res in easyocr_results]
                            confidences = [res[2] for res in easyocr_results]
                            bboxes = [res[0] for res in easyocr_results]
                            
                            if texts:
                                full_text = ''.join(texts).strip()
                                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                                
                                # 车牌格式检查
                                import re
                                plate_pattern = r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z]'
                                format_matched = bool(re.search(plate_pattern, full_text))
                                
                                if format_matched:
                                    avg_confidence = min(avg_confidence + 0.2, 1.0)  # 格式匹配奖励
                                
                                engine_result = {
                                    'engine': 'easyocr',
                                    'text': full_text,
                                    'confidence': avg_confidence,
                                    'engine_available': True,
                                    'texts': texts,
                                    'individual_confidences': confidences,
                                    'bboxes': bboxes,
                                    'plate_format_matched': format_matched
                                }
                                
                                status_icon = "🎯" if format_matched else "✅"
                                format_info = "车牌格式" if format_matched else "通用文本"
                                print(f"{status_icon} EasyOCR识别成功: {full_text} (置信度: {avg_confidence:.2f}, {format_info})")
                                if len(texts) > 1:
                                    print(f"📋 EasyOCR识别详情: {', '.join([f'{t}({c:.2f})' for t, c in zip(texts, confidences)])}")

                    except Exception as e:
                        print(f"❌ EasyOCR失败: {e}")

                # 🆘 终极备用方案 - fallback_ocr
                elif engine_name == 'fallback':
                    try:
                        from fallback_ocr import run_fallback_ocr
                        fallback_result = run_fallback_ocr(image_base64)
                        
                        if fallback_result.get('success'):
                            engine_result = {
                                'engine': 'fallback',
                                'text': fallback_result['text'],
                                'confidence': fallback_result['confidence'],
                                'message': fallback_result.get('message', '备用识别'),
                                'engine_available': True
                            }
                            print(f"🆘 备用系统识别: {fallback_result['text']} (置信度: {fallback_result['confidence']:.2f})")
                        else:
                            print(f"❌ 备用系统失败: {fallback_result.get('error', '未知错误')}")
                            
                    except Exception as e:
                        print(f"❌ 备用系统异常: {e}")
                
                # 评估当前引擎结果
                if engine_result and engine_result.get('confidence', 0) > best_confidence:
                    best_result = engine_result
                    best_confidence = engine_result['confidence']
                    
                    # 如果置信度足够高，并且格式正确，提前返回结果
                    is_plate_format = best_result.get('plate_format_matched', False)
                    # HyperLPR3 is always a plate format
                    if best_result.get('engine') and 'hyperlpr3' in best_result['engine']:
                        is_plate_format = True

                    if best_confidence > 0.75 and is_plate_format:
                        print(f"🎯 高置信度车牌结果，提前返回: {engine_result['text']}")
                        break
                        
            except Exception as e:
                print(f"💥 引擎 {engine_name} 运行失败: {e}")
                continue
        
        # 🎉 返回最佳结果
        if best_result and best_result.get('text'):
            response_data = {
                "success": True,
                "engine": best_result['engine'],
                "text": best_result['text'],
                "confidence": best_result['confidence'],
                "results": best_result,
                "image_quality": image_quality,
                "message": f"使用 {best_result['engine']} 引擎识别成功"
            }
            
            # 添加低置信度警告
            if best_result.get('is_low_confidence'):
                response_data['warning'] = "识别置信度较低，建议验证结果准确性"
                response_data['low_confidence_candidates'] = best_result.get('low_confidence_plates', [])
                response_data['suggestion'] = best_result.get('suggestion', '建议提高图片质量或调整光照条件')
            
            # 添加车牌格式匹配信息
            if 'plate_format_matched' in best_result:
                response_data['plate_format_matched'] = best_result['plate_format_matched']
                if not best_result['plate_format_matched']:
                    response_data['format_warning'] = "识别结果可能不是标准车牌格式"
            
            return jsonify(response_data)
        else:
            # 🔄 即使没有高置信度结果，也要检查是否有低置信度候选结果
            low_confidence_data = None
            for engine_name in engines_to_try:
                try:
                    if engine_name == 'hyperlpr3' and HYPERLPR_AVAILABLE and 'hyperlpr3' in ocr_engines:
                        catcher = ocr_engines['hyperlpr3']
                        enhanced_image = enhance_image_for_ocr(image, 'plate')
                        rgb_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB) if len(enhanced_image.shape) == 3 else cv2.cvtColor(enhanced_image, cv2.COLOR_GRAY2RGB)
                        plates = catcher(rgb_image)
                        
                        if plates and len(plates) > 0:
                            low_confidence_plates = []
                            for plate in plates:
                                if plate and len(plate) >= 2:
                                    plate_no = str(plate[0]) if plate[0] else ''
                                    confidence = float(plate[1]) if isinstance(plate[1], (int, float)) else 0.0
                                    if plate_no and confidence > 0.01:  # 即使很低的置信度也收集
                                        low_confidence_plates.append({
                                            'text': plate_no,
                                            'confidence': confidence,
                                            'bbox': plate[2] if len(plate) > 2 else None
                                        })
                            
                            if low_confidence_plates:
                                # 按置信度排序
                                low_confidence_plates.sort(key=lambda x: x['confidence'], reverse=True)
                                best_candidate = low_confidence_plates[0]
                                
                                low_confidence_data = {
                                    "success": False,
                                    "engine": "hyperlpr3_low_confidence",
                                    "text": best_candidate['text'],
                                    "confidence": best_candidate['confidence'],
                                    "low_confidence_candidates": low_confidence_plates,
                                    "image_quality": image_quality,
                                    "warning": "检测到车牌但置信度较低，以下是候选结果",
                                    "suggestion": "建议提高图片清晰度、调整光照条件或重新拍摄"
                                }
                                break
                except Exception as e:
                    print(f"💥 低置信度检查失败 {engine_name}: {e}")
                    continue
            
            # 如果有低置信度候选结果，返回它们
            if low_confidence_data:
                return jsonify(low_confidence_data)
            
            # 最后的备用处理
            try:
                # 基础图像分析
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                return jsonify({
                    "success": False,
                    "engine": "fallback",
                    "error": "所有OCR引擎识别失败",
                    "detected_objects": len(contours),
                    "image_quality": image_quality,
                    "suggestion": "检测到图像中有内容，建议：1. 提高图片清晰度 2. 调整光照条件 3. 确保车牌完整可见",
                    "quality_suggestions": image_quality.get('suggestions', []),
                    "available_engines": {
                        "tesseract": TESSERACT_AVAILABLE,
                        "paddleocr": PADDLEOCR_AVAILABLE and 'paddleocr' in ocr_engines,
                        "easyocr": EASYOCR_AVAILABLE and 'easyocr' in ocr_engines,
                        "hyperlpr3": HYPERLPR_AVAILABLE and 'hyperlpr3' in ocr_engines
                    }
                })
            except Exception as e:
                return jsonify({
                    "success": False,
                    "engine": "error",
                    "error": f"系统处理失败: {str(e)}",
                    "image_quality": image_quality
                })
        
    except Exception as e:
        print(f"💥 API系统错误: {e}")
        return jsonify({
            "success": False,
            "engine": "system",
            "error": f"系统错误: {str(e)}"
        }), 500

@app.route("/api/ocr", methods=["POST"])
def ocr_api():
    """简化的OCR识别API - MVP版本"""
    try:
        # 初始化OCR引擎（延迟加载）
        init_ocr_engines()
        
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "没有提供图像数据"}), 400
            
        image_base64 = data.get('image')
        engine = data.get('engine', 'paddleocr')
        
        # 转换图像
        image = base64_to_opencv(image_base64)
        if image is None:
            return jsonify({"error": "图像格式错误"}), 400

        # 核心识别逻辑
        results = {}
        
        # PaddleOCR
        if engine == 'paddleocr' and PADDLEOCR_AVAILABLE and 'paddleocr' in ocr_engines:
            try:
                ocr_results = ocr_engines['paddleocr'].ocr(image)
                texts = []
                
                if ocr_results and ocr_results[0]:
                    for line in ocr_results[0]:
                        if line and len(line) >= 2:
                            texts.append({
                                'text': line[1][0],
                                'confidence': line[1][1],
                                'bbox': line[0]
                            })
                
                results['paddleocr'] = {
                    'texts': texts,
                    'available': True,
                    'count': len(texts)
                }
            except Exception as e:
                results['paddleocr'] = {
                    'error': str(e),
                    'available': False
                }
        
        # Tesseract OCR
        elif engine == 'tesseract' and TESSERACT_AVAILABLE:
            try:
                import pytesseract
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                text = pytesseract.image_to_string(pil_image, lang='chi_sim+eng')
                
                results['tesseract'] = {
                    'full_text': text.strip(),
                    'texts': [{'text': text.strip(), 'confidence': 0.8}],
                    'available': True
                }
            except Exception as e:
                results['tesseract'] = {
                    'error': str(e),
                    'available': False
                }
        
        # HyperLPR3
        elif engine == 'hyperlpr3' and HYPERLPR_AVAILABLE and 'hyperlpr3' in ocr_engines:
            try:
                catcher = ocr_engines['hyperlpr3']
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                plates = catcher(rgb_image)
                
                plate_results = []
                if plates:
                    for plate in plates:
                        if plate and len(plate) >= 2:
                            plate_results.append({
                                'plate_no': str(plate[0]),
                                'confidence': float(plate[1])
                            })
                
                results['hyperlpr3'] = {
                    'plates': plate_results,
                    'available': True,
                    'count': len(plate_results)
                }
            except Exception as e:
                results['hyperlpr3'] = {
                    'error': str(e),
                    'available': False
                }
        
        # 检查是否有结果
        if engine not in results:
            available_engines = []
            if PADDLEOCR_AVAILABLE and 'paddleocr' in ocr_engines:
                available_engines.append('paddleocr')
            if TESSERACT_AVAILABLE:
                available_engines.append('tesseract')
            if HYPERLPR_AVAILABLE and 'hyperlpr3' in ocr_engines:
                available_engines.append('hyperlpr3')
            
            return jsonify({
                "error": f"OCR引擎 '{engine}' 不可用",
                "available_engines": available_engines
            }), 400
        
        return jsonify({
            "success": True,
            "engine": engine,
            "results": results[engine]
        })
        
    except Exception as e:
        return jsonify({"error": f"OCR识别失败: {str(e)}"}), 500
# 获取可用的 OCR 引擎列表
@app.route("/api/ocr-engines", methods=["GET"])
def get_ocr_engines():
    """获取可用的 OCR 引擎列表"""
    init_ocr_engines()  # 确保引擎已初始化
    
    engines = {}
    
    if PADDLEOCR_AVAILABLE and 'paddleocr' in ocr_engines:
        engines['paddleocr'] = {
            'name': 'PaddleOCR',
            'description': '百度开源 OCR，支持中英文识别',
            'available': True
        }
    else:
        engines['paddleocr'] = {
            'name': 'PaddleOCR',
            'description': '百度开源 OCR，支持中英文识别',
            'available': False,
            'error': 'PaddleOCR 未安装或初始化失败'
        }
    
    if TESSERACT_AVAILABLE:
        engines['tesseract'] = {
            'name': 'Tesseract OCR',
            'description': '传统 OCR 引擎，支持多种语言',
            'available': True
        }
    else:
        engines['tesseract'] = {
            'name': 'Tesseract OCR',
            'description': '传统 OCR 引擎，支持多种语言',
            'available': False,
            'error': 'Tesseract 未安装'
        }
    
    if HYPERLPR_AVAILABLE and 'hyperlpr3' in ocr_engines:
        engines['hyperlpr3'] = {
            'name': 'HyperLPR3',
            'description': '专门的车牌识别引擎',
            'available': True
        }
    else:
        engines['hyperlpr3'] = {
            'name': 'HyperLPR3',
            'description': '专门的车牌识别引擎',
            'available': False,
            'error': 'HyperLPR3 未安装或初始化失败'
        }
    
    return jsonify({
        "engines": engines,
        "total": len(engines),
        "available": len([e for e in engines.values() if e['available']])
    })

# 静态文件服务
@app.route('/<path:path>')
def serve_static(path):
    """提供静态文件服务"""
    try:
        response = send_from_directory('web', path)
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    except Exception:
        return jsonify({"error": "文件未找到"}), 404

# 简化的图像处理函数
def enhance_image_for_ocr(image, image_type='general'):
    """简单的图像增强处理"""
    try:
        # 转为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # 直方图均衡化
        enhanced = cv2.equalizeHist(gray)
        
        # 转回BGR格式
        if len(image.shape) == 3:
            result = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        else:
            result = enhanced
            
        return result
    except Exception as e:
        print(f"图像增强失败: {e}")
        return image

def analyze_image_quality(image):
    """分析图像质量，提供改进建议"""
    try:
        # 转为灰度图进行分析
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 计算图像统计信息
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        # 计算拉普拉斯方差（模糊度检测）
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 计算对比度
        contrast = std_brightness
        
        # 图像尺寸
        height, width = gray.shape
        
        # 评估和建议
        suggestions = []
        quality_score = 100
        
        if mean_brightness < 50:
            suggestions.append("图像过暗，建议增加亮度")
            quality_score -= 20
        elif mean_brightness > 200:
            suggestions.append("图像过亮，建议降低亮度或减少曝光")
            quality_score -= 15
            
        if laplacian_var < 100:
            suggestions.append("图像可能模糊，建议重新拍摄或使用防抖")
            quality_score -= 25
            
        if contrast < 20:
            suggestions.append("对比度不足，建议调整光照或增强对比度")
            quality_score -= 15
            
        if width < 200 or height < 200:
            suggestions.append("图像分辨率较低，建议使用更高分辨率")
            quality_score -= 10
            
        return {
            'quality_score': max(quality_score, 0),
            'brightness': mean_brightness,
            'contrast': contrast,
            'sharpness': laplacian_var,
            'resolution': f"{width}x{height}",
            'suggestions': suggestions
        }
        
    except Exception as e:
        print(f"图像质量分析失败: {e}")
        return {
            'quality_score': 50,
            'error': str(e),
            'suggestions': ['无法分析图像质量，请检查图像格式']
        }

# 应用启动
if __name__ == "__main__":
    print("🚀 启动天津仁爱学院车牌识别系统...")
    print(f"📊 OCR引擎状态:")
    print(f"   - PaddleOCR: {'✅' if PADDLEOCR_AVAILABLE else '❌'}")
    print(f"   - Tesseract: {'✅' if TESSERACT_AVAILABLE else '❌'}")
    print(f"   - HyperLPR3: {'✅' if HYPERLPR_AVAILABLE else '❌'}")
    print(f"   - EasyOCR: {'✅' if EASYOCR_AVAILABLE else '❌'}")
    print("🌐 访问 http://127.0.0.1:8081/login 开始使用")
    
    # 创建上传目录
    os.makedirs('uploads', exist_ok=True)
    
    # 启动Flask应用
    app.run(host="0.0.0.0", port=8081, debug=False)
