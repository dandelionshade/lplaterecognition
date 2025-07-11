<!--
 * @Author: 张震 116089016+dandelionshade@users.noreply.github.com
 * @Date: 2025-07-11 13:52:36
 * @LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
 * @LastEditTime: 2025-07-11 13:55:00
 * @FilePath: /lplaterecognition/ANALYSIS.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
# 项目分析文档

## 1. 项目概述

本项目是一个基于 Web 的 AI 应用，利用 Google Gemini Pro Vision 多模态模型的强大功能，实现了根据用户选择的图片和输入的文本提示，动态生成相关内容的交互式体验。具体来说，前端页面展示了三种烘焙食品的图片，用户可以选择其中一张，并输入问题或指令（例如，询问食谱），后端会调用 Gemini API，将图片和文本结合起来进行分析，并将生成的文本结果以流式的方式实时返回给前端展示。

## 2. 核心功能

*   **图片选择**：用户可以在三个预设的烘焙食品图片中进行选择。
*   **自定义文本输入**：用户可以输入自定义的文本提示，向 AI 提出具体要求。
*   **多模态输入**：应用将用户选择的图片和输入的文本 prompt 结合，作为多模态内容发送给 Gemini API。
*   **流式响应**：后端从 Gemini API接收流式数据，并将其直接转发到前端，实现了类似打字机效果的实时文本显示，提升了用户体验。
*   **Markdown 渲染**：前端能够将 AI 返回的 Markdown 格式文本渲染成格式化的 HTML，使内容展示更美观。
*   **静态文件服务**：后端使用 Flask 框架，不仅处理 API 请求，还能提供 HTML、CSS、JavaScript 和图片等静态资源。

## 3. 技术栈

*   **后端**：
    *   **Python**: 主要编程语言。
    *   **Flask**: 轻量级的 Web 服务器框架，用于处理 HTTP 请求和路由。
    *   **google-genai**: Google 官方提供的 Python 客户端库，用于与 Gemini API 进行交互。
*   **前端**：
    *   **HTML/CSS/JavaScript**: 构建用户界面的基础技术。
    *   **markdown-it**: 一个流行的 JavaScript 库，用于将 Markdown 文本转换为 HTML。
    *   **base64-js**: 用于将图片文件编码为 Base64 字符串，以便通过 JSON 发送到后端。
*   **AI 模型**：
    *   **Gemini Pro Vision**: Google 的多模态大语言模型，能够同时理解图像和文本信息。

## 4. 关键文件解析

*   `main.py`: 项目的后端核心。它创建了一个 Flask 应用，定义了三个路由：
    1.  `/`: 返回主页面 `index.html`。
    2.  `/api/generate`: 接收前端发来的 POST 请求（包含图片和文本），调用 Gemini API，并以事件流（Event Stream）的形式将结果返回。
    3.  `/<path:path>`: 提供 `web` 目录下的所有静态文件（如 JS, CSS, 图片）。
*   `web/index.html`: 应用的入口页面，定义了页面的基本结构，包括图片选择器、文本输入框和结果显示区域。
*   `web/main.js`: 前端的核心逻辑。它处理表单提交事件，获取用户选择的图片并将其转换为 Base64 编码，然后连同用户输入的文本一起，通过 `gemini-api.js` 发送到后端 API。最后，它以流式方式接收并渲染返回的 Markdown 文本。
*   `web/gemini-api.js`: 封装了与后端 `/api/generate` 接口的通信逻辑，使得 `main.js` 可以方便地调用。
*   `requirements.txt`: 定义了项目所需的 Python 依赖库，方便一键安装。
*   `devserver.sh`: 一个便捷的启动脚本，用于在开发环境中以调试模式启动 Flask 服务器。

## 5. 如何运行项目

1.  **设置 API 密钥**:
    *   访问 `https://g.co/ai/idxGetGeminiKey` 获取你的 Gemini API 密钥。
    *   在项目根目录下创建一个名为 `.env` 的文件，并添加以下内容，将 `YOUR_API_KEY` 替换为你的密钥：
        ```
        API_KEY=YOUR_API_KEY
        ```
    *   或者，你也可以直接在 `main.py` 文件中修改 `API_KEY = os.environ.get('API_KEY')` 这一行，但不推荐这样做。

2.  **安装依赖**:
    *   确保你已经安装了 Python 3。
    *   打开终端，在项目根目录下运行以下命令来安装所有必需的 Python 包：
        ```bash
        pip install -r requirements.txt
        ```

3.  **启动服务器**:
    *   在终端中运行以下命令：
        ```bash
        sh devserver.sh
        ```
    *   或者直接运行 Flask 命令：
        ```bash
        flask --app main run -p 8000 --debug
        ```

4.  **访问应用**:
    *   打开你的浏览器，访问 `http://127.0.0.1:8000` 即可开始使用。
