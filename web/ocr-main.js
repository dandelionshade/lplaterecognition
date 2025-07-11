// 导入 Gemini API 功能
import { streamGemini } from './gemini-api.js';

// 全局变量
let currentImages = {
  gemini: null,
  ocr: null,
  plate: null,
  process: null
};

let enginesStatus = {};

// DOM 元素
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
  initializeTabs();
  initializeGeminiTab();
  initializeOCRTab();
  initializePlateTab();
  initializeProcessTab();
  loadEnginesStatus();
});

// 标签页切换功能
function initializeTabs() {
  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const targetTab = button.getAttribute('data-tab');
      
      // 移除所有活动状态
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabContents.forEach(content => content.classList.remove('active'));
      
      // 激活选中的标签
      button.classList.add('active');
      document.getElementById(targetTab).classList.add('active');
    });
  });
}

// 加载引擎状态
async function loadEnginesStatus() {
  try {
    const response = await fetch('/api/ocr-engines');
    const data = await response.json();
    enginesStatus = data.engines;
    updateEnginesStatusDisplay();
  } catch (error) {
    console.error('加载引擎状态失败:', error);
  }
}

// 更新引擎状态显示
function updateEnginesStatusDisplay() {
  const statusContainer = document.getElementById('engines-status');
  statusContainer.innerHTML = '';
  
  Object.entries(enginesStatus).forEach(([key, engine]) => {
    const statusDiv = document.createElement('div');
    statusDiv.className = 'engine-status';
    statusDiv.innerHTML = `
      <i class="fas fa-circle ${engine.available ? 'status-available' : 'status-unavailable'}"></i>
      <span>${engine.name}</span>
    `;
    statusContainer.appendChild(statusDiv);
  });
}

// Gemini AI 标签页初始化
function initializeGeminiTab() {
  const geminiUpload = document.getElementById('gemini-upload');
  const geminiAnalyze = document.getElementById('gemini-analyze');
  const geminiPrompt = document.getElementById('gemini-prompt');
  const geminiResult = document.getElementById('gemini-result');
  
  // 文件上传处理
  geminiUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
      try {
        const base64 = await fileToBase64(file);
        currentImages.gemini = base64;
        
        // 取消选中的预设图片
        document.querySelectorAll('input[name="chosen-image"]').forEach(input => {
          input.checked = false;
        });
        
        showToast('图片上传成功！', 'success');
      } catch (error) {
        showToast('图片上传失败：' + error.message, 'error');
      }
    }
  });
  
  // 分析按钮处理
  geminiAnalyze.addEventListener('click', async () => {
    const prompt = geminiPrompt.value.trim();
    if (!prompt) {
      showToast('请输入分析指令', 'error');
      return;
    }
    
    geminiResult.textContent = '正在分析...';
    geminiResult.className = 'result-box loading';
    
    try {
      let imageBase64;
      
      // 获取图像数据
      if (currentImages.gemini) {
        imageBase64 = currentImages.gemini;
      } else {
        // 使用选中的预设图片
        const selectedImage = document.querySelector('input[name="chosen-image"]:checked');
        if (selectedImage) {
          const imageUrl = selectedImage.value;
          imageBase64 = await fetchImageAsBase64(imageUrl);
        } else {
          throw new Error('请选择或上传一张图片');
        }
      }
      
      // 构建 Gemini API 请求内容
      const contents = [{
        role: 'user',
        parts: [
          { inline_data: { mime_type: 'image/jpeg', data: imageBase64 } },
          { text: prompt }
        ]
      }];
      
      // 调用 Gemini API
      const stream = streamGemini({
        model: 'gemini-1.5-flash',
        contents
      });
      
      let buffer = [];
      const md = new markdownit();
      
      for await (let chunk of stream) {
        buffer.push(chunk);
        geminiResult.innerHTML = md.render(buffer.join(''));
      }
      
      geminiResult.className = 'result-box success';
      
    } catch (error) {
      geminiResult.textContent = '分析失败：' + error.message;
      geminiResult.className = 'result-box error';
    }
  });
}

// OCR 标签页初始化
function initializeOCRTab() {
  const ocrUpload = document.getElementById('ocr-upload');
  const ocrPreview = document.getElementById('ocr-preview');
  const ocrRecognize = document.getElementById('ocr-recognize');
  const ocrResult = document.getElementById('ocr-result');
  
  // 文件上传处理
  ocrUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
      try {
        const base64 = await fileToBase64(file);
        currentImages.ocr = base64;
        
        // 显示预览
        ocrPreview.innerHTML = `<img src="data:image/jpeg;base64,${base64}" alt="上传的图片">`;
        ocrRecognize.disabled = false;
        
        showToast('图片上传成功！', 'success');
      } catch (error) {
        showToast('图片上传失败：' + error.message, 'error');
      }
    }
  });
  
  // OCR 识别处理
  ocrRecognize.addEventListener('click', async () => {
    if (!currentImages.ocr) {
      showToast('请先上传图片', 'error');
      return;
    }
    
    const selectedEngine = document.querySelector('input[name="ocr-engine"]:checked').value;
    const extractPlate = document.getElementById('extract-plate-checkbox')?.checked || false;
    
    // 检查选择的引擎是否可用
    if (!enginesStatus[selectedEngine] || !enginesStatus[selectedEngine].available) {
      showToast(`${enginesStatus[selectedEngine]?.name || selectedEngine} 引擎不可用，请检查是否已正确安装`, 'error');
      return;
    }
    
    ocrResult.innerHTML = '<div class="loading-spinner"></div>正在识别文字...';
    ocrResult.className = 'result-box loading';
    
    try {
      const response = await fetch('/api/ocr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          image: currentImages.ocr,
          engine: selectedEngine,
          extract_plate: extractPlate  // 添加车牌提取选项
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        displayOCRResults(data.results, ocrResult);
        ocrResult.className = 'result-box success';
      } else {
        throw new Error(data.error || '识别失败');
      }
      
    } catch (error) {
      ocrResult.textContent = '识别失败：' + error.message;
      ocrResult.className = 'result-box error';
      showToast('OCR 识别失败：' + error.message, 'error');
    }
  });
}

// 车牌识别标签页初始化
function initializePlateTab() {
  const plateUpload = document.getElementById('plate-upload');
  const platePreview = document.getElementById('plate-preview');
  const plateRecognize = document.getElementById('plate-recognize');
  const plateResult = document.getElementById('plate-result');
  
  // 文件上传处理
  plateUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
      try {
        const base64 = await fileToBase64(file);
        currentImages.plate = base64;
        
        // 显示预览
        platePreview.innerHTML = `<img src="data:image/jpeg;base64,${base64}" alt="上传的车辆图片">`;
        plateRecognize.disabled = false;
        
        showToast('图片上传成功！', 'success');
      } catch (error) {
        showToast('图片上传失败：' + error.message, 'error');
      }
    }
  });
  
  // 车牌识别处理
  plateRecognize.addEventListener('click', async () => {
    if (!currentImages.plate) {
      showToast('请先上传车辆图片', 'error');
      return;
    }
    
    // 检查 HyperLPR3 引擎是否可用
    if (!enginesStatus.hyperlpr3 || !enginesStatus.hyperlpr3.available) {
      showToast('HyperLPR3 引擎不可用，请检查是否已正确安装', 'error');
      return;
    }
    
    plateResult.innerHTML = '<div class="loading-spinner"></div>正在识别车牌...';
    plateResult.className = 'result-box loading';
    
    try {
      const response = await fetch('/api/ocr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          image: currentImages.plate,
          engine: 'hyperlpr3'
        })
      });
      
      const data = await response.json();
      
      if (data.success && data.results.plates) {
        displayPlateResults(data.results.plates, plateResult);
        plateResult.className = 'result-box success';
      } else {
        throw new Error(data.error || '未识别到车牌');
      }
      
    } catch (error) {
      plateResult.textContent = '识别失败：' + error.message;
      plateResult.className = 'result-box error';
      showToast('车牌识别失败：' + error.message, 'error');
    }
  });
}

// 图像处理标签页初始化
function initializeProcessTab() {
  const processUpload = document.getElementById('process-upload');
  const originalPreview = document.getElementById('original-preview');
  const processedPreview = document.getElementById('processed-preview');
  const operationBtns = document.querySelectorAll('.operation-btn');
  const processResult = document.getElementById('process-result');
  
  // 文件上传处理
  processUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
      try {
        const base64 = await fileToBase64(file);
        currentImages.process = base64;
        
        // 显示原图预览
        originalPreview.innerHTML = `<img src="data:image/jpeg;base64,${base64}" alt="原图">`;
        processedPreview.innerHTML = '<p>请选择处理操作</p>';
        
        showToast('图片上传成功！', 'success');
      } catch (error) {
        showToast('图片上传失败：' + error.message, 'error');
      }
    }
  });
  
  // 操作按钮处理
  operationBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!currentImages.process) {
        showToast('请先上传图片', 'error');
        return;
      }
      
      const operation = btn.getAttribute('data-operation');
      
      // 移除其他按钮的活动状态
      operationBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      processedPreview.innerHTML = '<div class="loading-spinner"></div>处理中...';
      processResult.innerHTML = '<div class="loading-spinner"></div>正在处理图像...';
      processResult.className = 'result-box loading';
      
      try {
        const params = getOperationParams(operation);
        
        const response = await fetch('/api/process-image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            image: currentImages.process,
            operation: operation,
            params: params
          })
        });
        
        const data = await response.json();
        
        if (data.success) {
          // 显示处理后的图像
          processedPreview.innerHTML = `<img src="data:image/jpeg;base64,${data.processed_image}" alt="处理后">`;
          
          // 显示处理信息
          processResult.innerHTML = `
            <h5>处理操作：${getOperationName(operation)}</h5>
            <p>参数：${JSON.stringify(params)}</p>
            <p>处理完成时间：${new Date().toLocaleString()}</p>
          `;
          processResult.className = 'result-box success';
        } else {
          throw new Error(data.error || '处理失败');
        }
        
      } catch (error) {
        processedPreview.innerHTML = '<p>处理失败</p>';
        processResult.textContent = '处理失败：' + error.message;
        processResult.className = 'result-box error';
      }
    });
  });
}

// 工具函数

// 文件转 Base64
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// 获取网络图片的 Base64
async function fetchImageAsBase64(url) {
  const response = await fetch(url);
  const arrayBuffer = await response.arrayBuffer();
  const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
  return base64;
}

// 显示 OCR 结果
function displayOCRResults(results, container) {
  let html = '';
  
  // 显示车牌区域使用信息
  if (results.plate_regions_used > 0) {
    html += `<div class="info-badge">🎯 已使用车牌区域检测 (${results.plate_regions_used}个区域)</div>`;
  }
  
  if (results.texts && results.texts.length > 0) {
    html += '<h5>识别到的文字：</h5>';
    results.texts.forEach((item, index) => {
      const confidenceClass = getConfidenceClass(item.confidence);
      const sourceIcon = item.region_source === 'full_image' ? '🖼️' : '🎯';
      const sourceText = item.region_source === 'full_image' ? '整图识别' : '车牌区域识别';
      
      html += `
        <div class="ocr-text-item">
          <div class="ocr-text">${index + 1}. ${item.text}</div>
          <div class="ocr-meta">
            <span class="ocr-confidence ${confidenceClass}">
              置信度: ${(item.confidence * 100).toFixed(1)}%
            </span>
            <span class="ocr-source">
              ${sourceIcon} ${sourceText}
            </span>
            ${item.detection_method ? `<span class="detection-method">检测方法: ${item.detection_method}</span>` : ''}
          </div>
        </div>
      `;
    });
  } else if (results.full_text) {
    html += `<h5>识别结果：</h5><p>${results.full_text}</p>`;
  } else {
    html += '<p>未识别到文字内容</p>';
    if (results.plate_regions_used === 0) {
      html += '<div class="tip">💡 提示：尝试启用"车牌区域提取"功能可以提高车牌识别精度</div>';
    }
  }
  
  container.innerHTML = html;
}

// 显示车牌识别结果
function displayPlateResults(plates, container) {
  let html = '';
  
  if (plates && plates.length > 0) {
    html += '<h5>识别到的车牌：</h5>';
    plates.forEach((plate, index) => {
      html += `
        <div class="plate-item">
          <div class="plate-number">${plate.plate_no}</div>
          <div class="plate-confidence">置信度: ${(plate.confidence * 100).toFixed(1)}%</div>
        </div>
      `;
    });
  } else {
    html += '<p>未识别到车牌</p>';
  }
  
  container.innerHTML = html;
}

// 获取置信度样式类
function getConfidenceClass(confidence) {
  if (confidence >= 0.8) return 'high';
  if (confidence >= 0.5) return 'medium';
  return 'low';
}

// 获取操作参数
function getOperationParams(operation) {
  const params = {};
  
  switch (operation) {
    case 'blur':
      params.kernel_size = 15;
      break;
    case 'edge':
      params.low = 50;
      params.high = 150;
      break;
    case 'threshold':
      params.thresh = 127;
      break;
    case 'resize':
      params.width = 400;
      params.height = 300;
      break;
    case 'rotate':
      params.angle = 90;
      break;
    case 'enhance':
      params.alpha = 1.5;
      params.beta = 20;
      break;
  }
  
  return params;
}

// 获取操作名称
function getOperationName(operation) {
  const names = {
    'gray': '灰度化',
    'blur': '高斯模糊',
    'edge': '边缘检测',
    'threshold': '二值化',
    'resize': '尺寸调整',
    'rotate': '旋转',
    'enhance': '对比度增强'
  };
  return names[operation] || operation;
}

// 显示提示消息
function showToast(message, type = 'info') {
  // 创建提示元素
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    top: 50px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 600;
    z-index: 10000;
    max-width: 300px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    transform: translateX(100%);
    transition: transform 0.3s ease;
  `;
  
  // 设置颜色
  const colors = {
    success: '#48bb78',
    error: '#e53e3e',
    info: '#667eea',
    warning: '#ed8936'
  };
  toast.style.background = colors[type] || colors.info;
  toast.textContent = message;
  
  // 添加到页面
  document.body.appendChild(toast);
  
  // 显示动画
  setTimeout(() => {
    toast.style.transform = 'translateX(0)';
  }, 100);
  
  // 自动移除
  setTimeout(() => {
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }, 3000);
}

// 导出供其他模块使用
export { showToast, currentImages, enginesStatus };
