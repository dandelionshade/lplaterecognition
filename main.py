'''
Author: 张震 116089016+dandelionshade@users.noreply.github.com
Date: 2025-07-10 15:44:41
LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
LastEditTime: 2025-07-11 17:12:27
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

# 导入 OpenCV 用于图像处理
import cv2
# 导入 numpy 用于数值计算
import numpy as np
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

# 初始化 OCR 引擎
ocr_engines = {}
if PADDLEOCR_AVAILABLE and PaddleOCR is not None:
    try:
        ocr_engines['paddleocr'] = PaddleOCR(use_angle_cls=True, lang='ch')
    except Exception as e:
        print(f"PaddleOCR 初始化失败: {e}")
        try:
            # 尝试更简单的初始化
            ocr_engines['paddleocr'] = PaddleOCR()
        except Exception as e2:
            print(f"PaddleOCR 简化初始化也失败: {e2}")
            PADDLEOCR_AVAILABLE = False

if HYPERLPR_AVAILABLE and lpr3 is not None:
    try:
        # 初始化 HyperLPR3 车牌识别器
        ocr_engines['hyperlpr3'] = lpr3.LicensePlateCatcher()
    except Exception as e:
        print(f"HyperLPR3 初始化失败: {e}")
        HYPERLPR_AVAILABLE = False

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
    return send_from_directory('web', 'home.html')

# OCR页面 - 需要登录
@app.route("/ocr")
@login_required
def ocr_page():
    """OCR识别页面"""
    return send_from_directory('web', 'ocr.html')


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

# OCR 识别 API
@app.route("/api/ocr", methods=["POST"])
@login_required
def ocr_api():
    """OCR 识别的 API 端点"""
    if request.method == "POST":
        try:
            data = request.get_json()
            image_base64 = data.get('image')
            engine = data.get('engine', 'paddleocr')
            extract_plate = data.get('extract_plate', False)  # 是否提取车牌区域
            
            if not image_base64:
                return jsonify({"error": "没有提供图像数据"}), 400
            
            # 转换为 OpenCV 图像
            image = base64_to_opencv(image_base64)
            if image is None:
                return jsonify({"error": "图像格式错误"}), 400
            
            results = {}
            plate_regions = []
            
            # 如果启用车牌提取功能
            if extract_plate:
                print("开始检测车牌区域...")
                plate_regions = detect_license_plate_regions(image)
                print(f"检测到 {len(plate_regions)} 个可能的车牌区域")
            
            # PaddleOCR
            if engine == 'paddleocr' and 'paddleocr' in ocr_engines:
                try:
                    texts = []
                    
                    # 如果启用车牌提取，先尝试在车牌区域识别
                    if extract_plate and plate_regions:
                        print("使用PaddleOCR识别车牌区域...")
                        for i, region_info in enumerate(plate_regions[:2]):  # 最多处理前2个区域
                            extracted = extract_and_enhance_plate_region(image, region_info['bbox'])
                            if extracted:
                                # 在增强的车牌区域上运行OCR
                                plate_results = ocr_engines['paddleocr'].ocr(extracted['enhanced'], cls=True)
                                for line in plate_results[0] if plate_results and plate_results[0] else []:
                                    if line and line[1][1] > 0.5:  # 置信度阈值
                                        # 调整坐标到原图
                                        bbox_orig = region_info['bbox']
                                        adjusted_bbox = []
                                        for point in line[0]:
                                            adjusted_bbox.append([
                                                point[0] + bbox_orig[0],
                                                point[1] + bbox_orig[1]
                                            ])
                                        
                                        texts.append({
                                            'text': line[1][0],
                                            'confidence': line[1][1],
                                            'bbox': adjusted_bbox,
                                            'region_source': f'plate_region_{i}',
                                            'detection_method': region_info['method']
                                        })
                    
                    # 如果车牌区域没有识别到内容，或者没有启用车牌提取，在整图上识别
                    if not texts:
                        print("在整图上使用PaddleOCR识别...")
                        ocr_results = ocr_engines['paddleocr'].ocr(image, cls=True)
                        for line in ocr_results[0] if ocr_results and ocr_results[0] else []:
                            if line:
                                texts.append({
                                    'text': line[1][0],
                                    'confidence': line[1][1],
                                    'bbox': line[0],
                                    'region_source': 'full_image'
                                })
                    
                    results['paddleocr'] = {
                        'texts': texts,
                        'available': True,
                        'plate_regions_used': len(plate_regions) if extract_plate else 0
                    }
                except Exception as e:
                    results['paddleocr'] = {
                        'error': str(e),
                        'available': False
                    }
            
            # Tesseract OCR
            if engine == 'tesseract' and TESSERACT_AVAILABLE:
                try:
                    import pytesseract
                    texts = []
                    full_text = ""
                    
                    # 如果启用车牌提取，先尝试在车牌区域识别
                    if extract_plate and plate_regions:
                        print("使用Tesseract识别车牌区域...")
                        for i, region_info in enumerate(plate_regions[:2]):  # 最多处理前2个区域
                            extracted = extract_and_enhance_plate_region(image, region_info['bbox'])
                            if extracted:
                                # 转换为 PIL 图像
                                pil_image = Image.fromarray(cv2.cvtColor(extracted['enhanced'], cv2.COLOR_BGR2RGB))
                                
                                # 使用专门的车牌识别配置
                                config = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                                text = pytesseract.image_to_string(pil_image, config=config, lang='eng')
                                
                                if text.strip():
                                    # 获取详细信息
                                    data_dict = pytesseract.image_to_data(pil_image, config=config, output_type=pytesseract.Output.DICT, lang='eng')
                                    for j in range(len(data_dict['text'])):
                                        if int(data_dict['conf'][j]) > 30:  # 降低置信度阈值
                                            bbox_orig = region_info['bbox']
                                            texts.append({
                                                'text': data_dict['text'][j],
                                                'confidence': float(data_dict['conf'][j]) / 100,
                                                'bbox': [
                                                    data_dict['left'][j] + bbox_orig[0],
                                                    data_dict['top'][j] + bbox_orig[1],
                                                    data_dict['left'][j] + data_dict['width'][j] + bbox_orig[0],
                                                    data_dict['top'][j] + data_dict['height'][j] + bbox_orig[1]
                                                ],
                                                'region_source': f'plate_region_{i}',
                                                'detection_method': region_info['method']
                                            })
                                    full_text += text.strip() + " "
                    
                    # 如果车牌区域没有识别到内容，或者没有启用车牌提取，在整图上识别
                    if not texts:
                        print("在整图上使用Tesseract识别...")
                        # 转换为 PIL 图像
                        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                        text = pytesseract.image_to_string(pil_image, lang='chi_sim+eng')
                        full_text = text.strip()
                        
                        # 获取详细信息
                        data_dict = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT, lang='chi_sim+eng')
                        for i in range(len(data_dict['text'])):
                            if int(data_dict['conf'][i]) > 0:
                                texts.append({
                                    'text': data_dict['text'][i],
                                    'confidence': float(data_dict['conf'][i]) / 100,
                                    'bbox': [
                                        data_dict['left'][i],
                                        data_dict['top'][i],
                                        data_dict['left'][i] + data_dict['width'][i],
                                        data_dict['top'][i] + data_dict['height'][i]
                                    ],
                                    'region_source': 'full_image'
                                })
                    
                    results['tesseract'] = {
                        'full_text': full_text,
                        'texts': texts,
                        'available': True,
                        'plate_regions_used': len(plate_regions) if extract_plate else 0
                    }
                except Exception as e:
                    results['tesseract'] = {
                        'error': str(e),
                        'available': False
                    }
            
            # HyperLPR3 车牌识别
            if engine == 'hyperlpr3' and HYPERLPR_AVAILABLE and 'hyperlpr3' in ocr_engines:
                try:
                    # 使用预初始化的车牌识别器
                    catcher = ocr_engines['hyperlpr3']
                    
                    # 确保输入图像格式正确
                    if len(image.shape) == 3:
                        # 如果是彩色图像，转换为RGB格式（HyperLPR3可能需要RGB）
                        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        plates = catcher(rgb_image)
                    else:
                        # 如果是灰度图像，转换为RGB
                        rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                        plates = catcher(rgb_image)
                    
                    plate_results = []
                    if plates and len(plates) > 0:
                        for plate in plates:
                            if plate and len(plate) >= 2:  # 确保有车牌号和置信度
                                plate_info = {
                                    'plate_no': str(plate[0]) if plate[0] else '',
                                    'confidence': float(plate[1]) if isinstance(plate[1], (int, float)) else 0.0
                                }
                                # 添加边界框信息（如果有）
                                if len(plate) > 2 and plate[2] is not None:
                                    plate_info['bbox'] = plate[2]
                                plate_results.append(plate_info)
                    
                    results['hyperlpr3'] = {
                        'plates': plate_results,
                        'available': True,
                        'count': len(plate_results)
                    }
                except Exception as e:
                    results['hyperlpr3'] = {
                        'error': str(e),
                        'available': False,
                        'count': 0
                    }
            
            # 如果请求的引擎不可用
            if engine not in results:
                available_engines = []
                if PADDLEOCR_AVAILABLE and 'paddleocr' in ocr_engines:
                    available_engines.append('paddleocr')
                if TESSERACT_AVAILABLE:
                    available_engines.append('tesseract')
                if HYPERLPR_AVAILABLE and 'hyperlpr3' in ocr_engines:
                    available_engines.append('hyperlpr3')
                
                return jsonify({
                    "error": f"OCR 引擎 '{engine}' 不可用",
                    "available_engines": available_engines
                }), 400
            
            return jsonify({
                "success": True,
                "engine": engine,
                "results": results[engine]
            })
        
        except Exception as e:
            return jsonify({"error": f"OCR 识别失败: {str(e)}"}), 500
    
    return jsonify({"error": "Method not allowed"}), 405

# 获取可用的 OCR 引擎列表
@app.route("/api/ocr-engines", methods=["GET"])
@login_required
def get_ocr_engines():
    """获取可用的 OCR 引擎列表"""
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

# 文件上传 API
@app.route("/api/upload", methods=["POST"])
@login_required
def upload_file():
    """文件上传 API"""
    if 'file' not in request.files:
        return jsonify({"error": "没有选择文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "没有选择文件"}), 400
    
    if file and allowed_file(file.filename):
        try:
            # 读取文件内容
            file_content = file.read()
            
            # 转换为 base64
            image_base64 = base64.b64encode(file_content).decode('utf-8')
            
            return jsonify({
                "success": True,
                "image": image_base64,
                "filename": secure_filename(file.filename or "unknown"),
                "size": len(file_content)
            })
        except Exception as e:
            return jsonify({"error": f"文件处理失败: {str(e)}"}), 500
    else:
        return jsonify({"error": "不支持的文件格式"}), 400

# 定义一个能匹配所有路径的路由，用于提供静态文件。
@app.route('/<path:path>')
def serve_static(path):
    # 从 'web' 目录下发送与请求路径匹配的文件。
    # 例如，请求 /style.css 会返回 web/style.css 文件。
    return send_from_directory('web', path)


# 这是一个标准的 Python 入口点检查。
# 只有当这个脚本被直接执行时（而不是被导入时），下面的代码才会运行。
if __name__ == "__main__":
    # 运行 Flask 应用。
    # port: 设置监听的端口，从环境变量 'PORT' 获取，如果不存在则默认为 8080。
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 8080)), debug=True)

# 车牌检测和处理函数
def detect_license_plate_regions(image):
    """
    使用多种方法检测车牌区域
    返回检测到的车牌区域列表
    """
    plate_regions = []
    
    try:
        # 方法1：使用HyperLPR3检测车牌区域
        if HYPERLPR_AVAILABLE and 'hyperlpr3' in ocr_engines:
            try:
                catcher = ocr_engines['hyperlpr3']
                if len(image.shape) == 3:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                
                plates = catcher(rgb_image)
                for plate in plates:
                    if plate and len(plate) > 2 and plate[2] is not None:
                        # HyperLPR3返回的边界框格式可能是[x1,y1,x2,y2]
                        bbox = plate[2]
                        if len(bbox) >= 4:
                            plate_regions.append({
                                'method': 'hyperlpr3',
                                'bbox': bbox,
                                'confidence': float(plate[1]) if len(plate) > 1 else 0.0
                            })
            except Exception as e:
                print(f"HyperLPR3检测失败: {e}")
        
        # 方法2：使用OpenCV传统图像处理方法检测车牌区域
        plate_regions.extend(detect_plate_by_opencv(image))
        
    except Exception as e:
        print(f"车牌检测错误: {e}")
    
    return plate_regions

def detect_plate_by_opencv(image):
    """
    使用OpenCV传统方法检测可能的车牌区域
    """
    regions = []
    
    try:
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 边缘检测
        edges = cv2.Canny(blurred, 50, 150)
        
        # 形态学操作
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 筛选可能的车牌轮廓
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 车牌的宽高比通常在2.5-4.5之间
            aspect_ratio = w / h if h > 0 else 0
            area = w * h
            
            # 筛选条件：合适的宽高比和面积
            if (2.0 <= aspect_ratio <= 5.0 and 
                area > 500 and  # 最小面积
                w > 50 and h > 15):  # 最小尺寸
                
                regions.append({
                    'method': 'opencv',
                    'bbox': [x, y, x + w, y + h],
                    'confidence': min(aspect_ratio / 3.5, 1.0),  # 简单的置信度计算
                    'area': area,
                    'aspect_ratio': aspect_ratio
                })
        
        # 按置信度排序
        regions.sort(key=lambda x: x['confidence'], reverse=True)
        
    except Exception as e:
        print(f"OpenCV车牌检测失败: {e}")
    
    return regions[:3]  # 最多返回3个候选区域

def extract_and_enhance_plate_region(image, bbox, padding=10):
    """
    提取并增强车牌区域
    """
    try:
        h, w = image.shape[:2]
        
        # 解析边界框
        if len(bbox) >= 4:
            x1, y1, x2, y2 = map(int, bbox[:4])
        else:
            return None
        
        # 添加padding并确保不越界
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(w, x2 + padding)
        y2 = min(h, y2 + padding)
        
        # 提取区域
        plate_region = image[y1:y2, x1:x2]
        
        if plate_region.size == 0:
            return None
        
        # 增强处理
        enhanced_region = enhance_plate_image(plate_region)
        
        return {
            'original': plate_region,
            'enhanced': enhanced_region,
            'bbox': [x1, y1, x2, y2]
        }
        
    except Exception as e:
        print(f"区域提取失败: {e}")
        return None

def enhance_plate_image(plate_image):
    """
    增强车牌图像以提高OCR识别率
    """
    try:
        # 转换为灰度
        if len(plate_image.shape) == 3:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_image
        
        # 调整尺寸 - 放大图像
        scale_factor = 3
        height, width = gray.shape
        new_width = width * scale_factor
        new_height = height * scale_factor
        resized = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(resized, (3, 3), 0)
        
        # 对比度增强
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)
        
        # 二值化
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学操作去除噪点
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 转换回BGR格式以便OCR处理
        enhanced_bgr = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
        
        return enhanced_bgr
        
    except Exception as e:
        print(f"图像增强失败: {e}")
        return plate_image
