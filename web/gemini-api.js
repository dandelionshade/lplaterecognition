/**
 * @fileoverview 封装了与后端 Gemini API 代理的通信逻辑。
 */

/**
 * 调用后端代理的 Gemini API，可以传入图片和/或文本内容，
 * 并以流式（通过异步生成器函数）的方式返回模型的输出。
 *
 * @param {object} options - 配置选项。
 * @param {string} [options.model='gemini-1.5-flash'] - 要使用的 Gemini 模型名称，例如 'gemini-1.5-pro'。
 * @param {Array<object>} [options.contents=[]] - 发送给模型的内容数组，包含角色和部件。
 * @returns {AsyncGenerator<string, void, undefined>} - 一个异步生成器，逐块产生模型生成的文本。
 */
export async function* streamGemini({
  model = 'gemini-1.5-flash', // 默认使用的模型
  contents = [],
} = {}) {
  // 将用户的 prompt 发送到在 main.py 中定义的 Python 后端 API。
  let response = await fetch("/api/generate", {
    method: "POST", // 使用 POST 方法
    headers: { "content-type": "application/json" }, // 设置请求头为 JSON
    body: JSON.stringify({ model, contents }) // 将模型和内容序列化为 JSON 字符串作为请求体
  });

  // 使用 streamResponseChunks 辅助函数处理流式响应。
  // yield* 会将另一个生成器或可迭代对象的所有值委托出去。
  yield* streamResponseChunks(response);
}

/**
 * 一个辅助函数，用于从 fetch() 的响应体中流式读取和解析文本块。
 * 这个函数专门处理 Server-Sent Events (SSE) 格式的响应。
 *
 * @param {Response} response - fetch API 返回的 Response 对象。
 * @returns {AsyncGenerator<string, void, undefined>} - 一个异步生成器，逐块产生解析后的文本。
 */
async function* streamResponseChunks(response) {
  // 用于缓存从流中读取的数据的缓冲区。
  let buffer = '';

  // SSE 中消息块之间的分隔符。
  const CHUNK_SEPARATOR = '\n\n';

  /**
   * 内部处理函数，用于解析缓冲区中的数据块。
   * @param {boolean} [streamDone=false] - 标志流是否已经结束。
   */
  let processBuffer = async function* (streamDone = false) {
    // 持续循环，直到缓冲区中没有完整的块。
    while (true) {
      let flush = false; // 是否强制刷新最后一个不完整的块
      let chunkSeparatorIndex = buffer.indexOf(CHUNK_SEPARATOR);

      // 如果流已结束且缓冲区中再也找不到分隔符，说明剩下的是最后一块数据。
      if (streamDone && chunkSeparatorIndex < 0) {
        flush = true;
        chunkSeparatorIndex = buffer.length; // 将块的末尾设置为缓冲区的末尾
      }

      // 如果找不到分隔符，则退出循环，等待更多数据。
      if (chunkSeparatorIndex < 0) {
        break;
      }

      // 提取一个完整的块。
      let chunk = buffer.substring(0, chunkSeparatorIndex);
      // 从缓冲区中移除已提取的块。
      buffer = buffer.substring(chunkSeparatorIndex + CHUNK_SEPARATOR.length);
      // 移除 SSE 格式的 "data: " 前缀并去除首尾空格。
      chunk = chunk.replace(/^data:\s*/, '').trim();

      // 如果块为空，则跳过。
      if (!chunk) {
        if (flush) break; // 如果是强制刷新且块为空，则结束。
        continue;
      }

      // 解析 JSON 格式的块。
      let { error, text } = JSON.parse(chunk);
      if (error) {
        // 如果块中包含错误信息，打印错误并抛出异常。
        console.error(error);
        throw new Error(error?.message || JSON.stringify(error));
      }
      // 产生（yield）解析出的文本。
      yield text;
      // 如果是强制刷新，则在产生最后一个块后结束。
      if (flush) break;
    }
  };

  // 获取响应体的 ReadableStream 读取器。
  const reader = response.body.getReader();
  try {
    // 无限循环，直到流被读完。
    while (true) {
      // 读取一块数据。
      const { done, value } = await reader.read();
      // 如果流已结束 (done is true)，则跳出循环。
      if (done) break;
      // 将读取到的 Uint8Array 数据解码为字符串并追加到缓冲区。
      buffer += new TextDecoder().decode(value);
      // 调用 processBuffer 处理当前缓冲区中的数据。
      yield* processBuffer();
    }
  } finally {
    // 确保在任何情况下都释放读取器的锁。
    reader.releaseLock();
  }

  // 流结束后，最后一次调用 processBuffer 以处理缓冲区中可能剩余的任何数据。
  yield* processBuffer(true);
}
