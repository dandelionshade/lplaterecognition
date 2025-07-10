'''
Author: 张震 116089016+dandelionshade@users.noreply.github.com
Date: 2025-07-10 15:44:41
LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
LastEditTime: 2025-07-10 16:32:02
FilePath: /lplaterecognition/main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import json
import os

import google.genai as genai
from flask import Flask, jsonify, request, send_file, send_from_directory, Response

# 🔥🔥 FILL THIS OUT FIRST! 🔥🔥
# Get your Gemini API key by:
# - Selecting "Add Gemini API" in the "Firebase Studio" panel in the sidebar
# - Or by visiting https://g.co/ai/idxGetGeminiKey
API_KEY = 'TODO'

ai = genai.Client(api_key=API_KEY)
app = Flask(__name__)


@app.route("/")
def index():
    return send_file('web/index.html')


@app.route("/api/generate", methods=["POST"])
def generate_api():
    if request.method == "POST":
        if API_KEY == 'TODO':
            return jsonify({ "error": '''
                To get started, get an API key at
                https://g.co/ai/idxGetGeminiKey and enter it in
                main.py
                '''.replace('\n', '') })
        try:
            req_body = request.get_json()
            contents = req_body.get("contents")
            response = ai.models.generate_content_stream(model=req_body.get("model"), contents=contents)
            def stream():
                for chunk in response:
                    yield 'data: %s\n\n' % json.dumps({ "text": chunk.text })

            return Response(stream(), mimetype='text/event-stream')

        except Exception as e:
            return jsonify({ "error": str(e) })
    # Default response if not POST (though the route is POST-only)
    return jsonify({"error": "Method not allowed"}), 405


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)


if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 80)))
