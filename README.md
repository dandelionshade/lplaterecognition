# 智能车牌识别与图像处理平台

一个集成多种OCR引擎、OpenCV图像处理和Gemini AI的车牌识别解决方案。

## ✨ 主要功能

### 🧠 Gemini AI 智能分析
- 使用 Google Gemini 2.0 Flash 模型
- 支持图像和文本多模态分析
- 智能识别车辆信息、车牌号码等
- 实时流式输出结果

### 📖 多种 OCR 引擎
- **PaddleOCR**: 百度开源OCR，支持中英文识别
- **Tesseract OCR**: 传统OCR引擎，支持多种语言
- 自动选择最适合的识别引擎

### 🚗 专业车牌识别
- **HyperLPR3**: 专门针对车牌优化的识别引擎
- 高精度车牌定位和识别
- 支持多种车牌格式

### 🖼️ OpenCV 图像处理
- **灰度化**: 转换为灰度图像
- **高斯模糊**: 图像平滑处理
- **边缘检测**: Canny边缘检测
- **二值化**: 阈值分割
- **对比度增强**: 调整图像对比度和亮度
- **图像旋转**: 按角度旋转图像

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- 支持的操作系统: Windows, macOS, Linux

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置API密钥
创建 `.env` 文件并添加 Gemini API 密钥：
```
API_KEY=your_gemini_api_key_here
```

获取API密钥：
- 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
- 或者在 [Firebase Studio](https://console.firebase.google.com/) 中添加 Gemini API

### 4. 启动服务
```bash
python main.py
```

服务将在 `http://127.0.0.1:8080` 启动

### 5. 访问界面
- **主页**: `http://127.0.0.1:8080/home` - 功能介绍页面
- **OCR平台**: `http://127.0.0.1:8080/ocr` - 完整功能页面
- **原始演示**: `http://127.0.0.1:8080/` - Gemini API 演示

## 📱 使用指南

### Gemini AI 分析
1. 选择预设图片或上传自定义图片
2. 输入分析指令（如："分析这张图片中的车辆信息"）
3. 点击"开始分析"获取AI分析结果

### OCR 文字识别
1. 上传包含文字的图片
2. 选择OCR引擎（PaddleOCR 或 Tesseract）
3. 点击"开始识别"获取文字识别结果

### 车牌识别
1. 上传包含车辆的图片
2. 点击"识别车牌"
3. 查看识别出的车牌号码和置信度

### 图像处理
1. 上传原始图片
2. 选择处理操作（灰度化、模糊、边缘检测等）
3. 实时查看处理结果对比

## 🛠️ 技术架构

### 后端技术栈
- **Flask**: Web框架
- **OpenCV**: 图像处理
- **NumPy**: 数值计算
- **Pillow**: 图像操作
- **PaddleOCR**: 百度OCR引擎
- **Tesseract**: 传统OCR引擎
- **HyperLPR3**: 车牌识别引擎
- **Google Genai**: Gemini API客户端

### 前端技术栈
- **HTML5**: 结构化标记
- **CSS3**: 现代样式设计
- **JavaScript ES6+**: 交互逻辑
- **Font Awesome**: 图标库
- **Markdown-it**: Markdown渲染

### API接口
- `POST /api/generate` - Gemini AI 内容生成
- `POST /api/process-image` - 图像处理
- `POST /api/ocr` - OCR 识别
- `GET /api/ocr-engines` - 获取可用OCR引擎
- `POST /api/upload` - 文件上传

## 📁 项目结构

```
lplaterecognition/
├── main.py                 # Flask应用主文件
├── requirements.txt        # Python依赖列表
├── .env                   # 环境变量配置
├── README.md              # 项目说明文档
├── ANALYSIS.md            # 技术分析文档
├── web/                   # 前端文件目录
│   ├── index.html         # 原始Gemini演示页面
│   ├── home.html          # 项目主页
│   ├── ocr.html          # OCR功能页面
│   ├── ocr-main.js       # OCR页面JavaScript
│   ├── ocr-style.css     # OCR页面样式
│   ├── gemini-api.js     # Gemini API客户端
│   ├── style.css         # 基础样式
│   ├── main.js           # 原始演示JavaScript
│   └── *.jpg, *.png      # 示例图片
└── uploads/               # 文件上传目录
```

## 🔧 开发指南

### 添加新的图像处理功能
在 `apply_image_processing` 函数中添加新的操作：

```python
def apply_image_processing(image, operation, params=None):
    # ... 现有代码 ...
    elif operation == 'new_operation':
        # 实现新的图像处理逻辑
        return processed_image
```

### 集成新的OCR引擎
1. 在 `requirements.txt` 中添加依赖
2. 在 `main.py` 中添加引擎检测逻辑
3. 在 `ocr_api` 函数中添加处理逻辑

### 自定义前端样式
- 修改 `web/ocr-style.css` 调整整体样式
- 修改 `web/ocr-main.js` 添加新的交互功能

## 🚨 常见问题

### Q: OCR引擎显示不可用
A: 请确保已正确安装相关依赖包：
```bash
pip install paddleocr pytesseract hyperlpr3
```

### Q: Gemini API调用失败
A: 请检查：
1. `.env` 文件中的API密钥是否正确
2. 网络连接是否正常
3. API配额是否用完

### Q: 图像上传失败
A: 请确保：
1. 图像文件小于16MB
2. 文件格式为支持的类型（jpg, png, gif, bmp, tiff）

### Q: 车牌识别效果不佳
A: 建议：
1. 使用清晰的车辆图片
2. 确保车牌在图片中清晰可见
3. 先进行图像预处理（如增强对比度）

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

- GitHub: [@dandelionshade](https://github.com/dandelionshade)
- 项目链接: [https://github.com/dandelionshade/lplaterecognition](https://github.com/dandelionshade/lplaterecognition)

---

⭐ 如果这个项目对您有帮助，请给个 Star！
