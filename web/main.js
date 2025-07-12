/*
 * @Author: 张震 116089016+dandelionshade@users.noreply.github.com
 * @Date: 2025-07-10 15:44:41
 * @LastEditors: 张震 116089016+dandelionshade@users.noreply.github.com
 * @LastEditTime: 2025-07-11 18:02:51
 * @FilePath: /lplaterecognition/web/main.js
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
// 导入 gemini-api.js 文件中的 streamGemini 函数，用于与后端 API 通信。
import { streamGemini } from './gemini-api.js';

// 获取页面中的表单元素。
let form = document.querySelector('form');
// 获取 name 属性为 "prompt" 的输入框元素。
let promptInput = document.querySelector('input[name="prompt"]');
// 获取 class 为 "output" 的元素，用于显示结果。
let output = document.querySelector('.output');

// 为表单的 onsubmit 事件设置一个异步处理函数。
form.onsubmit = async (ev) => {
  // 阻止表单的默认提交行为（即页面刷新）。
  ev.preventDefault();
  // 在等待结果时，向用户显示 "Generating..."。
  output.textContent = 'Generating...';

  try {
    // 获取当前被选中的图片单选按钮的值，即图片的 URL。
    let imageUrl = form.elements.namedItem('chosen-image').value;
    // 使用 fetch API 异步获取图片数据。
    let imageBase64 = await fetch(imageUrl)
      // 将响应体转换为 ArrayBuffer（二进制数据）。
      .then(r => r.arrayBuffer())
      // 将 ArrayBuffer 转换为 Base64 编码的字符串。
      // Uint8Array 是一个类型化数组，表示一个8位无符号整数数组。
      .then(a => base64js.fromByteArray(new Uint8Array(a)));

    // 构建要发送给 Gemini API 的内容（contents）。
    // 这是一个包含用户角色的对象数组。
    let contents = [
      {
        role: 'user', // 指定角色为用户
        parts: [ // parts 是一个数组，可以包含多种类型的数据
          // 第一个部分是图片数据
          { inline_data: { mime_type: 'image/jpeg', data: imageBase64, } },
          // 第二个部分是用户输入的文本
          { text: promptInput.value }
        ]
      }
    ];

    // 调用 streamGemini 函数，向多模态模型发送请求，并获取一个结果流。
    // model: 指定要使用的模型名称。
    // contents: 传递我们刚刚构建好的多模态内容。
    let stream = streamGemini({
      model: 'gemini-1.5-flash', // 注意：这里可以根据需要更换模型
      contents,
    });

    // 创建一个缓冲区数组，用于存储从流中接收到的数据块。
    let buffer = [];
    // 初始化 markdown-it 库，用于将 Markdown 文本转换为 HTML。
    let md = new markdownit();
    // 使用 for-await-of 循环异步遍历流中的每一个数据块。
    for await (let chunk of stream) {
      // 将每个数据块推入缓冲区。
      buffer.push(chunk);
      // 将缓冲区中的所有数据块连接成一个完整的字符串，
      // 然后使用 markdown-it 将其渲染为 HTML，并更新到 output 元素中。
      output.innerHTML = md.render(buffer.join(''));
    }
  } catch (e) {
    // 如果在请求过程中发生任何错误，将错误信息附加到 output 元素中。
    output.innerHTML += '<hr>' + e;
  }
};
