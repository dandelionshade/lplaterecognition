'''
Author: 张震 116089016+dandelionshade@users.noreply.github.com
Date: 2025-07-10 15:44:41
LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
LastEditTime: 2025-07-11 16:04:35
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
# 从 flask 库导入 Flask 类和一些辅助函数，用于构建 Web 应用。
from flask import Flask, jsonify, request, send_file, send_from_directory, Response
from werkzeug.utils import secure_filename

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


# 定义根路由 ("/") 的处理函数。
@app.route("/")
def index():
    # 当用户访问网站根目录时，发送 web/index.html 文件作为响应。
    return send_file('web/index.html')

# 新增主页路由
@app.route("/home")
def home():
    """主页"""
    return send_file('web/home.html')

# 新增 OCR 页面路由
@app.route("/ocr")
def ocr_page():
    """OCR 功能页面"""
    return send_file('web/ocr.html')


# 定义 /api/generate 路由的处理函数，只接受 POST 请求。
@app.route("/api/generate", methods=["POST"])
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
def ocr_api():
    """OCR 识别的 API 端点"""
    if request.method == "POST":
        try:
            data = request.get_json()
            image_base64 = data.get('image')
            engine = data.get('engine', 'paddleocr')
            
            if not image_base64:
                return jsonify({"error": "没有提供图像数据"}), 400
            
            # 转换为 OpenCV 图像
            image = base64_to_opencv(image_base64)
            if image is None:
                return jsonify({"error": "图像格式错误"}), 400
            
            results = {}
            
            # PaddleOCR
            if engine == 'paddleocr' and 'paddleocr' in ocr_engines:
                try:
                    ocr_results = ocr_engines['paddleocr'].ocr(image, cls=True)
                    texts = []
                    for line in ocr_results[0] if ocr_results and ocr_results[0] else []:
                        if line:
                            texts.append({
                                'text': line[1][0],
                                'confidence': line[1][1],
                                'bbox': line[0]
                            })
                    results['paddleocr'] = {
                        'texts': texts,
                        'available': True
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
                    # 转换为 PIL 图像
                    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    text = pytesseract.image_to_string(pil_image, lang='chi_sim+eng')
                    
                    # 获取详细信息
                    data_dict = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT, lang='chi_sim+eng')
                    texts = []
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
                                ]
                            })
                    
                    results['tesseract'] = {
                        'full_text': text.strip(),
                        'texts': texts,
                        'available': True
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
