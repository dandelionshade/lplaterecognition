'''
Author: 张震 116089016+dandelionshade@users.noreply.github.com
Date: 2025-07-10 15:44:41
LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
LastEditTime: 2025-07-11 14:37:56
FilePath: /lplaterecognition/main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# 导入 json 库，用于处理 JSON 数据格式。
import json
# 导入 os 库，用于与操作系统交互，如此处用于获取环境变量。
import os

# 导入 google.genai 库，这是 Google Gemini API 的 Python 客户端。
import google.genai as genai
# 从 flask 库导入 Flask 类和一些辅助函数，用于构建 Web 应用。
from flask import Flask, jsonify, request, send_file, send_from_directory, Response

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


# 定义根路由 ("/") 的处理函数。
@app.route("/")
def index():
    # 当用户访问网站根目录时，发送 web/index.html 文件作为响应。
    return send_file('web/index.html')


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
    # port: 设置监听的端口，从环境变量 'PORT' 获取，如果不存在则默认为 80。
    app.run(port=int(os.environ.get('PORT', 80)))
