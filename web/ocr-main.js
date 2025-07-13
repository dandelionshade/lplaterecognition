// 导入 Gemini API 功能
import { streamGemini } from "./gemini-api.js";

// 全局变量
let tabButtons = [];
let tabContents = [];
let currentImages = {
  gemini: null,
  ocr: null,
  plate: null,
  process: null,
};
let enginesStatus = {};
let recognitionHistory = [];
let processingQueue = [];
let currentToasts = [];

// 高级Toast通知系统
function showToast(message, type = "info", options = {}) {
  const {
    duration = getDefaultDuration(type),
    showProgressBar = false,
    actions = [],
    position = "top-right",
    closable = true,
    icon = getDefaultIcon(type),
  } = options;

  // 创建toast容器
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.style.cssText = `
    position: fixed;
    ${getPositionStyles(position)}
    background: ${getBackgroundColor(type)};
    color: ${getTextColor(type)};
    padding: 16px 20px;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(10px);
    border: 1px solid ${getBorderColor(type)};
    z-index: 10003;
    max-width: 400px;
    min-width: 300px;
    opacity: 0;
    transform: translateX(${
      position.includes("right") ? "100%" : "-100%"
    }) scale(0.8);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 14px;
    line-height: 1.4;
  `;

  // 创建内容结构
  const content = document.createElement("div");
  content.style.cssText = `
    display: flex;
    align-items: flex-start;
    gap: 12px;
  `;

  // 图标
  const iconElement = document.createElement("div");
  iconElement.innerHTML = icon;
  iconElement.style.cssText = `
    font-size: 18px;
    margin-top: 2px;
    flex-shrink: 0;
  `;

  // 消息内容
  const messageContainer = document.createElement("div");
  messageContainer.style.cssText = `
    flex: 1;
    min-width: 0;
  `;

  const messageText = document.createElement("div");
  messageText.textContent = message;
  messageText.style.cssText = `
    font-weight: 500;
    margin-bottom: ${showProgressBar || actions.length ? "8px" : "0"};
    word-wrap: break-word;
  `;

  messageContainer.appendChild(messageText);

  // 进度条
  if (showProgressBar) {
    const progressContainer = document.createElement("div");
    progressContainer.style.cssText = `
      background: rgba(255, 255, 255, 0.2);
      height: 4px;
      border-radius: 2px;
      overflow: hidden;
      margin-bottom: ${actions.length ? "8px" : "0"};
    `;

    const progressBar = document.createElement("div");
    progressBar.className = "toast-progress";
    progressBar.style.cssText = `
      background: ${getProgressColor(type)};
      height: 100%;
      width: 0%;
      transition: width 0.3s ease;
      border-radius: 2px;
    `;

    progressContainer.appendChild(progressBar);
    messageContainer.appendChild(progressContainer);

    // 动画进度条
    setTimeout(() => {
      progressBar.style.width = "100%";
    }, 100);

    // 存储进度条引用
    toast.progressBar = progressBar;
  }

  // 操作按钮
  if (actions.length > 0) {
    const actionsContainer = document.createElement("div");
    actionsContainer.style.cssText = `
      display: flex;
      gap: 8px;
      margin-top: 4px;
    `;

    actions.forEach((action) => {
      const button = document.createElement("button");
      button.textContent = action.label;
      button.style.cssText = `
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: currentColor;
        padding: 4px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 12px;
        font-weight: 500;
        transition: all 0.2s ease;
      `;

      button.addEventListener("click", () => {
        if (action.onClick) {
          action.onClick(toast);
        }
        if (action.autoClose !== false) {
          removeToast(toast);
        }
      });

      button.addEventListener("mouseenter", () => {
        button.style.background = "rgba(255, 255, 255, 0.3)";
      });

      button.addEventListener("mouseleave", () => {
        button.style.background = "rgba(255, 255, 255, 0.2)";
      });

      actionsContainer.appendChild(button);
    });

    messageContainer.appendChild(actionsContainer);
  }

  content.appendChild(iconElement);
  content.appendChild(messageContainer);

  // 关闭按钮
  if (closable) {
    const closeButton = document.createElement("button");
    closeButton.innerHTML = "×";
    closeButton.style.cssText = `
      position: absolute;
      top: 8px;
      right: 8px;
      background: none;
      border: none;
      color: currentColor;
      font-size: 20px;
      cursor: pointer;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0.7;
      transition: all 0.2s ease;
    `;

    closeButton.addEventListener("click", () => removeToast(toast));
    closeButton.addEventListener("mouseenter", () => {
      closeButton.style.opacity = "1";
      closeButton.style.background = "rgba(255, 255, 255, 0.2)";
    });
    closeButton.addEventListener("mouseleave", () => {
      closeButton.style.opacity = "0.7";
      closeButton.style.background = "none";
    });

    toast.appendChild(closeButton);
  }

  toast.appendChild(content);

  // 添加到DOM
  document.body.appendChild(toast);
  currentToasts.push(toast);

  // 调整现有toast位置
  adjustToastPositions(position);

  // 动画显示
  setTimeout(() => {
    toast.style.opacity = "1";
    toast.style.transform = "translateX(0) scale(1)";
  }, 10);

  // 自动移除
  if (duration > 0) {
    setTimeout(() => {
      removeToast(toast);
    }, duration);
  }

  // 添加自定义方法
  toast.updateProgress = (percentage) => {
    if (toast.progressBar) {
      toast.progressBar.style.width = percentage + "%";
    }
  };

  toast.updateMessage = (newMessage) => {
    messageText.textContent = newMessage;
  };

  return toast;
}

// 移除Toast
function removeToast(toast) {
  if (!toast.parentNode) return;

  toast.style.opacity = "0";
  toast.style.transform = "translateX(100%) scale(0.8)";

  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast);
    }
    const index = currentToasts.indexOf(toast);
    if (index > -1) {
      currentToasts.splice(index, 1);
    }
    adjustToastPositions("top-right");
  }, 400);
}

// 调整Toast位置
function adjustToastPositions(position) {
  const toasts = currentToasts.filter((toast) => toast.parentNode);
  let offset = 20;

  toasts.forEach((toast, index) => {
    if (position.includes("top")) {
      toast.style.top = offset + "px";
    } else {
      toast.style.bottom = offset + "px";
    }
    offset += toast.offsetHeight + 12;
  });
}

// 获取默认持续时间
function getDefaultDuration(type) {
  const durations = {
    success: 3000,
    info: 4000,
    warning: 5000,
    error: 0, // 手动关闭
    loading: 0,
  };
  return durations[type] || 4000;
}

// 获取默认图标
function getDefaultIcon(type) {
  const icons = {
    success: '<i class="fas fa-check-circle"></i>',
    info: '<i class="fas fa-info-circle"></i>',
    warning: '<i class="fas fa-exclamation-triangle"></i>',
    error: '<i class="fas fa-times-circle"></i>',
    loading: '<i class="fas fa-spinner fa-spin"></i>',
  };
  return icons[type] || icons.info;
}

// 获取背景颜色
function getBackgroundColor(type) {
  const colors = {
    success: "rgba(72, 187, 120, 0.95)",
    info: "rgba(102, 126, 234, 0.95)",
    warning: "rgba(237, 137, 54, 0.95)",
    error: "rgba(229, 62, 62, 0.95)",
    loading: "rgba(113, 128, 150, 0.95)",
  };
  return colors[type] || colors.info;
}

// 获取文本颜色
function getTextColor(type) {
  return "white";
}

// 获取边框颜色
function getBorderColor(type) {
  const colors = {
    success: "rgba(72, 187, 120, 0.3)",
    info: "rgba(102, 126, 234, 0.3)",
    warning: "rgba(237, 137, 54, 0.3)",
    error: "rgba(229, 62, 62, 0.3)",
    loading: "rgba(113, 128, 150, 0.3)",
  };
  return colors[type] || colors.info;
}

// 获取进度条颜色
function getProgressColor(type) {
  return "rgba(255, 255, 255, 0.8)";
}

// 获取位置样式
function getPositionStyles(position) {
  const positions = {
    "top-right": "top: 20px; right: 20px;",
    "top-left": "top: 20px; left: 20px;",
    "bottom-right": "bottom: 20px; right: 20px;",
    "bottom-left": "bottom: 20px; left: 20px;",
    "top-center": "top: 20px; left: 50%; transform: translateX(-50%);",
    "bottom-center": "bottom: 20px; left: 50%; transform: translateX(-50%);",
  };
  return positions[position] || positions["top-right"];
}

// 初始化应用
document.addEventListener("DOMContentLoaded", function () {
  // 初始化DOM元素
  tabButtons = Array.from(document.querySelectorAll(".tab-btn"));
  tabContents = Array.from(document.querySelectorAll(".tab-content"));

  // 首先初始化基础功能
  initializeProgressTracking(); // 优先初始化进度条
  initializeKeyboardShortcuts();
  initializeDragAndDrop();
  initializeImageComparison();
  initializeThemeToggle();

  // 然后初始化标签页和内容
  initializeTabs();
  initializeGeminiTab();
  initializeOCRTab();
  initializePlateTab();
  initializeProcessTab();

  // 最后加载状态和显示动画
  loadEnginesStatus();
  showWelcomeAnimation();
});

// 标签页切换功能（增强版）
function initializeTabs() {
  if (!tabButtons.length || !tabContents.length) {
    console.warn("Tab elements not found");
    return;
  }

  tabButtons.forEach((button, index) => {
    button.addEventListener("click", () => {
      const targetTab = button.getAttribute("data-tab");

      // 添加切换动画
      const activeContent = document.querySelector(".tab-content.active");
      if (activeContent) {
        activeContent.style.opacity = "0";
        activeContent.style.transform = "translateY(10px)";
      }

      setTimeout(() => {
        // 移除所有活动状态
        tabButtons.forEach((btn) => btn.classList.remove("active"));
        tabContents.forEach((content) => content.classList.remove("active"));

        // 激活选中的标签
        button.classList.add("active");
        const newActiveContent = document.getElementById(targetTab);
        if (newActiveContent) {
          newActiveContent.classList.add("active");

          // 显示新内容的动画
          setTimeout(() => {
            newActiveContent.style.opacity = "1";
            newActiveContent.style.transform = "translateY(0)";
          }, 50);
        }

        // 更新键盘快捷键提示
        showTabShortcutHint(index + 1);
      }, 150);
    });

    // 添加快捷键提示
    const shortcutHint = document.createElement("span");
    shortcutHint.style.cssText = `
      position: absolute;
      top: -8px;
      right: -8px;
      background: #667eea;
      color: white;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      font-size: 0.7em;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0.7;
    `;
    shortcutHint.textContent = (index + 1).toString();
    button.style.position = "relative";
    button.appendChild(shortcutHint);
  });

  // 添加CSS过渡效果
  tabContents.forEach((content) => {
    content.style.transition = "opacity 0.3s ease, transform 0.3s ease";
  });
}

// 增强标签页切换功能
function enhanceTabSwitching() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      showToast(`切换到 ${tab.textContent} 标签页`, "info", { duration: 1500 });
    });

    // 添加鼠标悬停效果
    tab.addEventListener("mouseenter", () => {
      if (!tab.classList.contains("active")) {
        tab.style.transform = "translateY(-2px)";
        tab.style.boxShadow = "0 4px 15px rgba(0,0,0,0.1)";
      }
    });

    tab.addEventListener("mouseleave", () => {
      if (!tab.classList.contains("active")) {
        tab.style.transform = "translateY(0)";
        tab.style.boxShadow = "none";
      }
    });
  });
}

// 显示标签页快捷键提示
function showTabShortcutHint(tabNumber) {
  const hint = document.createElement("div");
  hint.style.cssText = `
    position: fixed;
    top: 100px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 8px 15px;
    border-radius: 5px;
    font-size: 0.9em;
    z-index: 1001;
    opacity: 0;
    transition: opacity 0.3s ease;
  `;
  hint.textContent = `快捷键：Ctrl+${tabNumber}`;

  document.body.appendChild(hint);

  setTimeout(() => {
    hint.style.opacity = "1";
  }, 100);
  setTimeout(() => {
    hint.style.opacity = "0";
    setTimeout(() => {
      if (hint.parentNode) {
        hint.parentNode.removeChild(hint);
      }
    }, 300);
  }, 1500);
}

// 加载引擎状态（增强版）
async function loadEnginesStatus() {
  try {
    showProgress(10);
    const response = await fetch("/api/ocr-engines");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    showProgress(50);
    const data = await response.json();
    enginesStatus = data.engines;
    showProgress(80);
    updateEnginesStatusDisplay();
    showProgress(100);

    // 显示引擎状态汇总
    const availableCount = Object.values(enginesStatus).filter(
      (e) => e.available
    ).length;
    const totalCount = Object.keys(enginesStatus).length;

    showToast(
      `引擎状态加载完成：${availableCount}/${totalCount} 可用`,
      "success"
    );

    // 如果没有可用引擎，显示警告
    if (availableCount === 0) {
      showToast("警告：没有可用的OCR引擎，请检查系统配置", "warning");
    }
  } catch (error) {
    console.error("加载引擎状态失败:", error);
    showProgress(100);

    // 设置默认引擎状态，避免页面崩溃
    enginesStatus = {
      paddleocr: { name: "PaddleOCR", available: false, error: "连接失败" },
      tesseract: { name: "Tesseract OCR", available: false, error: "连接失败" },
      hyperlpr3: { name: "HyperLPR3", available: false, error: "连接失败" },
    };
    updateEnginesStatusDisplay();

    if (
      error.name === "TypeError" &&
      error.message.includes("Failed to fetch")
    ) {
      showToast("无法连接到服务器，请检查网络连接或启动后端服务", "error");
    } else {
      showToast("无法加载引擎状态：" + error.message, "error");
    }
  }
}

// 更新引擎状态显示（增强版）
function updateEnginesStatusDisplay() {
  const statusContainer = document.getElementById("engines-status");
  if (!statusContainer) {
    console.warn("Engines status container not found");
    return;
  }

  statusContainer.innerHTML = "";

  Object.entries(enginesStatus).forEach(([key, engine]) => {
    const statusDiv = document.createElement("div");
    statusDiv.className = "engine-status";
    statusDiv.style.cssText = `
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      padding: 8px;
      border-radius: 5px;
      transition: background-color 0.3s ease;
      cursor: pointer;
    `;

    statusDiv.innerHTML = `
      <i class="fas fa-circle ${
        engine.available ? "status-available" : "status-unavailable"
      }" 
         style="margin-right: 8px; width: 12px;"></i>
      <span style="font-size: 0.9em; font-weight: 500;">${engine.name}</span>
      ${
        !engine.available
          ? `<i class="fas fa-exclamation-triangle" style="margin-left: auto; color: #e53e3e; font-size: 0.8em;" title="${
              engine.error || "不可用"
            }"></i>`
          : ""
      }
    `;

    // 添加悬停效果
    statusDiv.addEventListener("mouseenter", () => {
      statusDiv.style.backgroundColor = "rgba(102, 126, 234, 0.1)";
    });

    statusDiv.addEventListener("mouseleave", () => {
      statusDiv.style.backgroundColor = "transparent";
    });

    // 点击显示详细信息
    statusDiv.addEventListener("click", () => {
      showEngineDetails(key, engine);
    });

    statusContainer.appendChild(statusDiv);
  });

  // 添加状态刷新按钮
  const refreshBtn = document.createElement("button");
  refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> 刷新状态';
  refreshBtn.style.cssText = `
    width: 100%;
    margin-top: 10px;
    padding: 8px;
    border: none;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.85em;
    transition: all 0.3s ease;
  `;

  refreshBtn.addEventListener("click", async () => {
    refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 刷新中...';
    refreshBtn.disabled = true;
    await loadEnginesStatus();
    refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> 刷新状态';
    refreshBtn.disabled = false;
  });

  statusContainer.appendChild(refreshBtn);
}

// 显示引擎详细信息
function showEngineDetails(engineKey, engine) {
  const modal = document.createElement("div");
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10002;
  `;

  const content = document.createElement("div");
  content.style.cssText = `
    background: white;
    border-radius: 15px;
    padding: 30px;
    max-width: 400px;
    width: 90%;
    max-height: 80%;
    overflow-y: auto;
    position: relative;
  `;

  content.innerHTML = `
    <button style="position: absolute; top: 15px; right: 15px; border: none; background: none; font-size: 1.2em; cursor: pointer; color: #718096;">
      <i class="fas fa-times"></i>
    </button>
    <h3 style="color: #4a5568; margin-bottom: 20px;">
      <i class="fas fa-cog"></i> ${engine.name}
    </h3>
    <div style="margin-bottom: 15px;">
      <strong>状态：</strong>
      <span style="color: ${engine.available ? "#48bb78" : "#e53e3e"};">
        ${engine.available ? "可用" : "不可用"}
      </span>
    </div>
    <div style="margin-bottom: 15px;">
      <strong>描述：</strong> ${engine.description}
    </div>
    ${
      !engine.available && engine.error
        ? `
      <div style="margin-bottom: 15px;">
        <strong>错误信息：</strong>
        <div style="background: #fed7d7; padding: 10px; border-radius: 5px; color: #e53e3e; font-size: 0.9em; margin-top: 5px;">
          ${engine.error}
        </div>
      </div>
    `
        : ""
    }
    <div style="background: #f7fafc; padding: 15px; border-radius: 8px; margin-top: 20px;">
      <strong>引擎ID：</strong> ${engineKey}<br>
      <strong>支持语言：</strong> ${
        engineKey === "paddleocr"
          ? "中文、英文"
          : engineKey === "tesseract"
          ? "多语言"
          : "车牌专用"
      }
    </div>
  `;

  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      document.body.removeChild(modal);
    }
  });

  content.querySelector("button").addEventListener("click", () => {
    document.body.removeChild(modal);
  });

  modal.appendChild(content);
  document.body.appendChild(modal);
}

// Gemini AI 标签页初始化（增强版）
function initializeGeminiTab() {
  const geminiUpload = document.getElementById("gemini-upload");
  const geminiAnalyze = document.getElementById("gemini-analyze");
  const geminiPrompt = document.getElementById("gemini-prompt");
  const geminiResult = document.getElementById("gemini-result");

  // 添加预设提示词
  addPromptPresets(geminiPrompt);

  // 文件上传处理（增强版）
  geminiUpload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      try {
        showProgress(20);

        // 文件大小和类型检查
        if (file.size > 16 * 1024 * 1024) {
          throw new Error("文件大小不能超过16MB");
        }

        if (!file.type.startsWith("image/")) {
          throw new Error("请选择图片文件");
        }

        const base64 = await fileToBase64(file);
        currentImages.gemini = base64;
        showProgress(60);

        // 取消选中的预设图片
        document
          .querySelectorAll('input[name="chosen-image"]')
          .forEach((input) => {
            input.checked = false;
          });

        // 添加图片预览显示 - 这是新增的关键功能！
        const geminiContainer = document.getElementById("gemini");
        let previewContainer = geminiContainer.querySelector(
          ".custom-image-preview"
        );

        if (!previewContainer) {
          previewContainer = document.createElement("div");
          previewContainer.className = "custom-image-preview";
          previewContainer.style.cssText = `
            margin: 20px 0;
            padding: 15px;
            border: 2px dashed #667eea;
            border-radius: 10px;
            background: rgba(102, 126, 234, 0.05);
            text-align: center;
            position: relative;
          `;

          // 插入到图片选择器后面
          const imagePicker = geminiContainer.querySelector(".image-picker");
          imagePicker.parentNode.insertBefore(
            previewContainer,
            imagePicker.nextSibling
          );
        }

        previewContainer.innerHTML = `
          <div class="preview-header">
            <h4 style="color: #667eea; margin: 0 0 10px 0;">
              <i class="fas fa-image"></i> 已上传的自定义图片
            </h4>
          </div>
          <div class="image-display">
            <img src="data:${file.type};base64,${base64}" 
                 alt="自定义上传图片" 
                 style="max-width: 100%; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
          </div>
          <div class="image-info" style="margin-top: 10px; font-size: 0.9em; color: #666;">
            <span><i class="fas fa-file"></i> ${file.name}</span> | 
            <span><i class="fas fa-weight-hanging"></i> ${(
              file.size / 1024
            ).toFixed(1)}KB</span> |
            <span><i class="fas fa-expand-arrows-alt"></i> <span id="img-dimensions">加载中...</span></span>
          </div>
          <div class="preview-actions" style="margin-top: 10px;">
            <button onclick="viewImageFullscreen('data:${
              file.type
            };base64,${base64}')" 
                    style="background: #667eea; color: white; border: none; padding: 5px 10px; border-radius: 5px; margin-right: 10px; cursor: pointer;">
              <i class="fas fa-expand"></i> 全屏查看
            </button>
            <button onclick="removeCustomImage()" 
                    style="background: #e53e3e; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">
              <i class="fas fa-trash"></i> 移除图片
            </button>
          </div>
        `;

        // 获取图片尺寸
        const img = new Image();
        img.onload = function () {
          const dimensionsSpan =
            previewContainer.querySelector("#img-dimensions");
          if (dimensionsSpan) {
            dimensionsSpan.textContent = `${img.width}×${img.height}`;
          }
        };
        img.src = `data:${file.type};base64,${base64}`;

        showProgress(100);
        showToast(`自定义图片上传成功：${file.name}`, "success");
        addToHistory("upload", {
          filename: file.name,
          type: file.type,
          size: file.size,
          tab: "gemini",
        });
      } catch (error) {
        showProgress(100);
        showToast("图片上传失败：" + error.message, "error");
      }
    }
  });

  // 预设图片选择增强
  document.querySelectorAll('input[name="chosen-image"]').forEach((input) => {
    input.addEventListener("change", () => {
      if (input.checked) {
        currentImages.gemini = null; // 清除自定义上传
        showToast(`已选择预设图片：${input.nextElementSibling.alt}`, "info");
      }
    });
  });

  // 分析按钮处理（增强版）
  geminiAnalyze.addEventListener("click", async () => {
    const prompt = geminiPrompt.value.trim();
    if (!prompt) {
      showToast("请输入分析指令", "error");
      return;
    }

    // 创建分析进度显示
    const progressContainer = createGeminiProgressContainer(geminiResult);
    const startTime = Date.now();

    let progressInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(85, (elapsed / 8000) * 100);
      showProgress(progress);
    }, 100);

    try {
      let imageBase64;

      // 获取图像数据
      if (currentImages.gemini) {
        imageBase64 = currentImages.gemini;
      } else {
        // 使用选中的预设图片
        const selectedImage = document.querySelector(
          'input[name="chosen-image"]:checked'
        );
        if (selectedImage) {
          const imageUrl = selectedImage.value;
          imageBase64 = await fetchImageAsBase64(imageUrl);
        } else {
          throw new Error("请选择或上传一张图片");
        }
      }

      // 构建 Gemini API 请求内容
      const contents = [
        {
          role: "user",
          parts: [
            { inline_data: { mime_type: "image/jpeg", data: imageBase64 } },
            { text: prompt },
          ],
        },
      ];

      // 调用 Gemini API
      const stream = streamGemini({
        model: "gemini-1.5-flash",
        contents,
      });

      clearInterval(progressInterval);
      showProgress(90);

      let buffer = [];
      const md = new markdownit({
        html: true,
        linkify: true,
        typographer: true,
        highlight: function (str, lang) {
          if (lang && hljs.getLanguage(lang)) {
            try {
              return hljs.highlight(str, { language: lang }).value;
            } catch (__) {}
          }
          return "";
        },
      });

      // 创建流式显示容器
      createStreamingDisplay(geminiResult);

      for await (let chunk of stream) {
        buffer.push(chunk);
        const content = buffer.join("");
        const renderedHTML = md.render(content);

        // 添加打字机效果
        updateStreamingDisplay(geminiResult, renderedHTML);
      }

      showProgress(100);
      geminiResult.className = "result-box success";

      const endTime = Date.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);

      showToast(`AI分析完成，耗时 ${duration} 秒`, "success");
      addToHistory("gemini", {
        prompt: prompt.substring(0, 50) + (prompt.length > 50 ? "..." : ""),
        duration: duration,
        wordCount: buffer.join("").length,
      });
    } catch (error) {
      clearInterval(progressInterval);
      showProgress(100);
      geminiResult.textContent = "分析失败：" + error.message;
      geminiResult.className = "result-box error";
      showToast("AI分析失败：" + error.message, "error");
    }
  });
}

// 添加预设提示词
function addPromptPresets(promptInput) {
  const presetsContainer = document.createElement("div");
  presetsContainer.style.cssText = `
    margin-bottom: 15px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  `;

  const presets = [
    "请详细分析这张车辆图片，包括车牌号码、车辆类型、颜色等信息",
    "识别图片中的车牌号码",
    "分析车辆的品牌和型号",
    "描述图片中车辆的外观特征",
    "检测图片中是否有交通违规行为",
    "分析停车环境和位置信息",
  ];

  presets.forEach((preset) => {
    const presetBtn = document.createElement("button");
    presetBtn.textContent =
      preset.length > 20 ? preset.substring(0, 20) + "..." : preset;
    presetBtn.title = preset;
    presetBtn.style.cssText = `
      padding: 6px 12px;
      background: rgba(102, 126, 234, 0.1);
      border: 1px solid #667eea;
      border-radius: 15px;
      cursor: pointer;
      font-size: 0.85em;
      color: #667eea;
      transition: all 0.3s ease;
    `;

    presetBtn.addEventListener("click", () => {
      promptInput.value = preset;
      promptInput.focus();
      showToast("已应用预设提示词", "info");
    });

    presetBtn.addEventListener("mouseenter", () => {
      presetBtn.style.background = "#667eea";
      presetBtn.style.color = "white";
    });

    presetBtn.addEventListener("mouseleave", () => {
      presetBtn.style.background = "rgba(102, 126, 234, 0.1)";
      presetBtn.style.color = "#667eea";
    });

    presetsContainer.appendChild(presetBtn);
  });

  promptInput.parentNode.insertBefore(presetsContainer, promptInput);
}

// 创建Gemini进度容器
function createGeminiProgressContainer(container) {
  container.innerHTML = `
    <div style="text-align: center; padding: 30px;">
      <div style="margin-bottom: 20px;">
        <div style="width: 60px; height: 60px; margin: 0 auto; position: relative;">
          <div style="width: 100%; height: 100%; border: 3px solid #e2e8f0; border-radius: 50%; position: absolute;"></div>
          <div style="width: 100%; height: 100%; border: 3px solid #667eea; border-top: 3px solid transparent; border-radius: 50%; animation: enhanced-spin 1s linear infinite; position: absolute;"></div>
          <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.5em;">🤖</div>
        </div>
      </div>
      <div style="color: #667eea; font-weight: 600; font-size: 1.1em; margin-bottom: 15px;">Gemini AI 正在分析...</div>
      <div style="font-size: 0.9em; color: #718096; margin-bottom: 20px;">
        正在运用先进的多模态AI技术分析您的图片
      </div>
      <div class="analysis-steps" style="text-align: left; max-width: 300px; margin: 0 auto;">
        <div class="step active" style="margin-bottom: 8px; padding: 8px 12px; background: rgba(102, 126, 234, 0.1); border-radius: 5px; font-size: 0.85em;">
          <i class="fas fa-image"></i> 图像预处理
        </div>
        <div class="step" style="margin-bottom: 8px; padding: 8px 12px; background: #f7fafc; border-radius: 5px; font-size: 0.85em; opacity: 0.6;">
          <i class="fas fa-brain"></i> 特征提取
        </div>
        <div class="step" style="margin-bottom: 8px; padding: 8px 12px; background: #f7fafc; border-radius: 5px; font-size: 0.85em; opacity: 0.6;">
          <i class="fas fa-search"></i> 内容理解
        </div>
        <div class="step" style="margin-bottom: 8px; padding: 8px 12px; background: #f7fafc; border-radius: 5px; font-size: 0.85em; opacity: 0.6;">
          <i class="fas fa-pen"></i> 生成回答
        </div>
      </div>
    </div>
  `;

  // 模拟步骤进度
  const steps = container.querySelectorAll(".step");
  let currentStep = 0;

  const stepInterval = setInterval(() => {
    if (currentStep < steps.length - 1) {
      steps[currentStep].style.opacity = "0.6";
      steps[currentStep].style.background = "#f7fafc";

      currentStep++;
      steps[currentStep].style.opacity = "1";
      steps[currentStep].style.background = "rgba(102, 126, 234, 0.1)";
      steps[currentStep].classList.add("active");
    } else {
      clearInterval(stepInterval);
    }
  }, 2000);

  return stepInterval;
}

// 创建流式显示
function createStreamingDisplay(container) {
  container.innerHTML = `
    <div class="streaming-content" style="line-height: 1.8; font-size: 1.05em; color: #2d3748;">
      <div class="typing-indicator" style="display: inline-block; width: 8px; height: 20px; background: #667eea; animation: blink 1s infinite;"></div>
    </div>
    <style>
      @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
      }
    </style>
  `;
}

// 更新流式显示
function updateStreamingDisplay(container, content) {
  const streamingContent = container.querySelector(".streaming-content");
  if (streamingContent) {
    streamingContent.innerHTML =
      content +
      '<span style="display: inline-block; width: 8px; height: 20px; background: #667eea; animation: blink 1s infinite; margin-left: 4px;"></span>';
  }
}

// OCR 标签页初始化（增强版）
function initializeOCRTab() {
  const ocrUpload = document.getElementById("ocr-upload");
  const ocrPreview = document.getElementById("ocr-preview");
  const ocrRecognize = document.getElementById("ocr-recognize");
  const ocrResult = document.getElementById("ocr-result");

  // 文件上传处理（增强版）
  ocrUpload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      try {
        showProgress(20);

        // 文件大小检查
        if (file.size > 16 * 1024 * 1024) {
          throw new Error("文件大小不能超过16MB");
        }

        // 文件类型检查
        if (!file.type.startsWith("image/")) {
          throw new Error("请选择图片文件");
        }

        showProgress(40);
        const base64 = await fileToBase64(file);
        currentImages.ocr = base64;
        showProgress(70);

        // 使用高级预览功能
        createAdvancedImagePreview(ocrPreview, base64, `OCR图片: ${file.name}`);
        ocrRecognize.disabled = false;
        showProgress(100);

        showToast(
          `图片上传成功：${file.name} (${(file.size / 1024).toFixed(1)}KB)`,
          "success"
        );
        addToHistory("upload", {
          filename: file.name,
          type: file.type,
          size: file.size,
          tab: "ocr",
        });

        // 自动分析图片属性
        analyzeImageProperties(file, base64);
      } catch (error) {
        showProgress(100);
        showToast("图片上传失败：" + error.message, "error");
      }
    }
  });

  // OCR 识别处理（增强版）
  ocrRecognize.addEventListener("click", async () => {
    if (!currentImages.ocr) {
      showToast("请先上传图片", "error");
      return;
    }

    const selectedEngine = document.querySelector(
      'input[name="ocr-engine"]:checked'
    ).value;
    const extractPlate =
      document.getElementById("extract-plate-checkbox")?.checked || false;

    // 检查选择的引擎是否可用
    if (
      !enginesStatus[selectedEngine] ||
      !enginesStatus[selectedEngine].available
    ) {
      showToast(
        `${
          enginesStatus[selectedEngine]?.name || selectedEngine
        } 引擎不可用，请检查是否已正确安装`,
        "error"
      );
      return;
    }

    // 创建识别进度显示
    const progressContainer = createProgressContainer(
      ocrResult,
      "正在识别文字..."
    );

    const startTime = Date.now();
    let progressInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(90, (elapsed / 5000) * 100);
      showProgress(progress);
    }, 100);

    try {
      const response = await fetch("/api/ocr-simple", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image: currentImages.ocr,
          engine: selectedEngine,
        }),
      });

      clearInterval(progressInterval);
      showProgress(100);

      const data = await response.json();

      if (data.success) {
        // 显示详细的OCR结果
        displayDetailedOCRResults(data, ocrResult);
        ocrResult.className = "result-box success";

        const endTime = Date.now();
        const duration = ((endTime - startTime) / 1000).toFixed(2);

        showToast(`OCR识别完成，耗时 ${duration} 秒`, "success");
        addToHistory("ocr", {
          engine: selectedEngine,
          duration: duration,
          extractPlate: extractPlate,
          resultCount: data.results.texts?.length || 0,
        });
      } else {
        // 检查是否有EasyOCR等备用引擎的识别结果或低置信度候选结果
        if (data.text || data.low_confidence_candidates || data.results) {
          // 有识别结果，但可能置信度较低或来自备用引擎
          displayDetailedOCRResults(data, ocrResult);
          ocrResult.className = "result-box warning"; // 使用警告样式表示低置信度

          const endTime = Date.now();
          const duration = ((endTime - startTime) / 1000).toFixed(2);

          // 根据识别结果类型显示相应的提示
          if (data.engine && data.engine.includes("easyocr")) {
            showToast(
              `EasyOCR备用引擎识别到: ${data.text}，耗时 ${duration} 秒`,
              "warning"
            );
          } else if (data.low_confidence_candidates) {
            showToast(
              `识别到候选结果，但置信度较低，耗时 ${duration} 秒`,
              "warning"
            );
          } else {
            showToast(
              `OCR识别完成（低置信度），耗时 ${duration} 秒`,
              "warning"
            );
          }

          addToHistory("ocr", {
            engine: selectedEngine,
            duration: duration,
            extractPlate: extractPlate,
            resultCount: data.results?.texts?.length || 1,
            lowConfidence: true,
          });
        } else {
          throw new Error(data.error || "识别失败");
        }
      }
    } catch (error) {
      clearInterval(progressInterval);
      showProgress(100);
      ocrResult.textContent = "识别失败：" + error.message;
      ocrResult.className = "result-box error";
      showToast("OCR 识别失败：" + error.message, "error");
    }
  });

  // 引擎选择变化处理
  document.querySelectorAll('input[name="ocr-engine"]').forEach((radio) => {
    radio.addEventListener("change", (e) => {
      const engineKey = e.target.value;
      const engine = enginesStatus[engineKey];

      if (engine) {
        showToast(`已选择 ${engine.name} 引擎`, "info");

        // 显示引擎特性提示
        const tips = {
          paddleocr: "适合中英文混合识别，识别精度高",
          tesseract: "支持多种语言，适合标准印刷体",
          hyperlpr3: "专业车牌识别引擎",
        };

        if (tips[engineKey]) {
          setTimeout(() => {
            showToast(tips[engineKey], "info");
          }, 1000);
        }
      }
    });
  });
}

// 车牌识别标签页初始化
function initializePlateTab() {
  const plateUpload = document.getElementById("plate-upload");
  const platePreview = document.getElementById("plate-preview");
  const plateRecognize = document.getElementById("plate-recognize");
  const plateResult = document.getElementById("plate-result");

  // 文件上传处理
  plateUpload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      try {
        const base64 = await fileToBase64(file);
        currentImages.plate = base64;

        // 显示预览
        platePreview.innerHTML = `<img src="data:image/jpeg;base64,${base64}" alt="上传的车辆图片">`;
        plateRecognize.disabled = false;

        showToast("图片上传成功！", "success");
      } catch (error) {
        showToast("图片上传失败：" + error.message, "error");
      }
    }
  });

  // 车牌识别处理
  plateRecognize.addEventListener("click", async () => {
    if (!currentImages.plate) {
      showToast("请先上传车辆图片", "error");
      return;
    }

    // 检查 HyperLPR3 引擎是否可用
    if (!enginesStatus.hyperlpr3 || !enginesStatus.hyperlpr3.available) {
      showToast("HyperLPR3 引擎不可用，请检查是否已正确安装", "error");
      return;
    }

    plateResult.innerHTML =
      '<div class="loading-spinner"></div>正在识别车牌...';
    plateResult.className = "result-box loading";

    try {
      const response = await fetch("/api/ocr-simple", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image: currentImages.plate,
          engine: "hyperlpr3",
        }),
      });

      const data = await response.json();

      if (data.success && data.results) {
        displayDetailedPlateResults(data, plateResult);
        plateResult.className = "result-box success";
      } else {
        // 即使失败也要显示详细信息（如果有低置信度候选结果）
        if (
          data.low_confidence_candidates &&
          data.low_confidence_candidates.length > 0
        ) {
          displayDetailedPlateResults(data, plateResult);
          plateResult.className = "result-box warning";
        } else {
          throw new Error(data.error || "未识别到车牌");
        }
      }
    } catch (error) {
      plateResult.textContent = "识别失败：" + error.message;
      plateResult.className = "result-box error";
      showToast("车牌识别失败：" + error.message, "error");
    }
  });
}

// 图像处理标签页初始化
function initializeProcessTab() {
  const processUpload = document.getElementById("process-upload");
  const originalPreview = document.getElementById("original-preview");
  const processedPreview = document.getElementById("processed-preview");
  const operationBtns = document.querySelectorAll(".operation-btn");
  const processResult = document.getElementById("process-result");

  // 文件上传处理
  processUpload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
      try {
        const base64 = await fileToBase64(file);
        currentImages.process = base64;

        // 显示原图预览
        originalPreview.innerHTML = `<img src="data:image/jpeg;base64,${base64}" alt="原图">`;
        processedPreview.innerHTML = "<p>请选择处理操作</p>";

        showToast("图片上传成功！", "success");
      } catch (error) {
        showToast("图片上传失败：" + error.message, "error");
      }
    }
  });

  // 操作按钮处理
  operationBtns.forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!currentImages.process) {
        showToast("请先上传图片", "error");
        return;
      }

      const operation = btn.getAttribute("data-operation");

      // 移除其他按钮的活动状态
      operationBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      processedPreview.innerHTML =
        '<div class="loading-spinner"></div>处理中...';
      processResult.innerHTML =
        '<div class="loading-spinner"></div>正在处理图像...';
      processResult.className = "result-box loading";

      try {
        const params = getOperationParams(operation);

        const response = await fetch("/api/process-image", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            image: currentImages.process,
            operation: operation,
            params: params,
          }),
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
          processResult.className = "result-box success";
        } else {
          throw new Error(data.error || "处理失败");
        }
      } catch (error) {
        processedPreview.innerHTML = "<p>处理失败</p>";
        processResult.textContent = "处理失败：" + error.message;
        processResult.className = "result-box error";
      }
    });
  });
}

// 新增功能函数

// 初始化键盘快捷键
function initializeKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Ctrl/Cmd + 数字键 切换标签页
    if ((e.ctrlKey || e.metaKey) && e.key >= "1" && e.key <= "4") {
      e.preventDefault();
      const tabIndex = parseInt(e.key) - 1;
      const tabButton = tabButtons[tabIndex];
      if (tabButton) {
        tabButton.click();
        showToast(`切换到 ${tabButton.textContent.trim()}`, "info");
      }
    }

    // Ctrl/Cmd + U 上传文件
    if ((e.ctrlKey || e.metaKey) && e.key === "u") {
      e.preventDefault();
      const activeTab = document.querySelector(".tab-content.active");
      const uploadInput = activeTab.querySelector('input[type="file"]');
      if (uploadInput) {
        uploadInput.click();
        showToast("快捷键上传：选择文件", "info");
      }
    }

    // Esc 键关闭所有提示
    if (e.key === "Escape") {
      currentToasts.forEach((toast) => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      });
      currentToasts = [];
    }
  });
}

// 初始化进度跟踪
function initializeProgressTracking() {
  // 创建全局进度条
  const progressBar = document.createElement("div");
  progressBar.id = "global-progress";
  progressBar.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 0%;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    z-index: 10001;
    transition: width 0.3s ease;
    opacity: 0;
  `;
  document.body.appendChild(progressBar);
}

// 显示进度
function showProgress(percentage = 0) {
  const progressBar = document.getElementById("global-progress");
  if (!progressBar) {
    console.warn("Progress bar not found, initializing...");
    initializeProgressTracking();
    return;
  }

  progressBar.style.opacity = "1";
  progressBar.style.width = percentage + "%";

  if (percentage >= 100) {
    setTimeout(() => {
      if (progressBar) {
        progressBar.style.opacity = "0";
        progressBar.style.width = "0%";
      }
    }, 500);
  }
}

// 初始化拖拽上传
function initializeDragAndDrop() {
  const uploadAreas = document.querySelectorAll(
    ".upload-section, .image-picker"
  );

  uploadAreas.forEach((area) => {
    // 防止默认拖拽行为
    ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
      area.addEventListener(eventName, preventDefaults, false);
    });

    // 高亮拖拽区域
    ["dragenter", "dragover"].forEach((eventName) => {
      area.addEventListener(eventName, highlight, false);
    });

    ["dragleave", "drop"].forEach((eventName) => {
      area.addEventListener(eventName, unhighlight, false);
    });

    // 处理文件拖拽
    area.addEventListener("drop", handleDrop, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function highlight(e) {
    e.currentTarget.classList.add("drag-over");
  }

  function unhighlight(e) {
    e.currentTarget.classList.remove("drag-over");
  }

  async function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
      const file = files[0];
      if (file.type.startsWith("image/")) {
        const activeTab = document.querySelector(".tab-content.active");
        const tabId = activeTab.id;

        try {
          const base64 = await fileToBase64(file);
          currentImages[tabId] = base64;

          // 更新对应的预览
          const preview = activeTab.querySelector(".image-preview");
          if (preview) {
            preview.innerHTML = `<img src="data:${file.type};base64,${base64}" alt="拖拽上传的图片">`;
          }

          // 启用操作按钮
          const actionBtn = activeTab.querySelector(".action-btn");
          if (actionBtn) {
            actionBtn.disabled = false;
          }

          showToast(`拖拽上传成功：${file.name}`, "success");
          addToHistory("upload", {
            filename: file.name,
            type: file.type,
            size: file.size,
          });
        } catch (error) {
          showToast("拖拽上传失败：" + error.message, "error");
        }
      } else {
        showToast("请上传图片文件", "warning");
      }
    }
  }
}

// 初始化图像对比功能
function initializeImageComparison() {
  // 为处理标签页添加图像对比滑块
  const processTab = document.getElementById("process");
  if (processTab) {
    const imageContainer = processTab.querySelector(".image-container");
    if (imageContainer) {
      // 添加对比滑块容器
      const comparisonContainer = document.createElement("div");
      comparisonContainer.className = "image-comparison";
      comparisonContainer.style.cssText = `
        position: relative;
        display: none;
        margin-top: 20px;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      `;

      const comparisonSlider = document.createElement("div");
      comparisonSlider.className = "comparison-slider";
      comparisonSlider.style.cssText = `
        position: relative;
        width: 100%;
        height: 400px;
        overflow: hidden;
        cursor: ew-resize;
      `;

      comparisonContainer.appendChild(comparisonSlider);
      imageContainer.appendChild(comparisonContainer);
    }
  }
}

// 初始化主题切换
function initializeThemeToggle() {
  const themeToggle = document.createElement("button");
  themeToggle.id = "theme-toggle";
  themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
  themeToggle.style.cssText = `
    position: fixed;
    top: 20px;
    left: 20px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    border: none;
    background: rgba(255, 255, 255, 0.9);
    color: #667eea;
    font-size: 1.2em;
    cursor: pointer;
    z-index: 1000;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  `;

  themeToggle.addEventListener("click", toggleTheme);
  document.body.appendChild(themeToggle);

  // 检查本地存储的主题设置
  const savedTheme = localStorage.getItem("theme") || "light";
  if (savedTheme === "dark") {
    toggleTheme();
  }
}

// 主题切换功能
function toggleTheme() {
  const body = document.body;
  const themeToggle = document.getElementById("theme-toggle");

  body.classList.toggle("dark-theme");
  const isDark = body.classList.contains("dark-theme");

  themeToggle.innerHTML = isDark
    ? '<i class="fas fa-sun"></i>'
    : '<i class="fas fa-moon"></i>';
  localStorage.setItem("theme", isDark ? "dark" : "light");

  showToast(`已切换到${isDark ? "深色" : "浅色"}主题`, "info");
}

// 显示欢迎动画
function showWelcomeAnimation() {
  const welcome = document.createElement("div");
  welcome.className = "welcome-animation";
  welcome.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    opacity: 1;
    transition: opacity 0.5s ease;
  `;

  welcome.innerHTML = `
    <div style="text-align: center; color: white;">
      <div style="font-size: 4em; margin-bottom: 20px; animation: bounce 1s infinite;">
        <i class="fas fa-car"></i>
      </div>
      <h1 style="font-size: 2.5em; margin-bottom: 10px;">天津仁爱学院</h1>
      <h2 style="font-size: 1.8em; margin-bottom: 20px;">智能车牌识别系统</h2>
      <div class="loading-dots" style="display: flex; justify-content: center; gap: 8px;">
        <div style="width: 12px; height: 12px; border-radius: 50%; background: white; animation: pulse 1.5s infinite;"></div>
        <div style="width: 12px; height: 12px; border-radius: 50%; background: white; animation: pulse 1.5s infinite 0.3s;"></div>
        <div style="width: 12px; height: 12px; border-radius: 50%; background: white; animation: pulse 1.5s infinite 0.6s;"></div>
      </div>
    </div>
    <style>
      @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-20px); }
        60% { transform: translateY(-10px); }
      }
      @keyframes pulse {
        0%, 100% { opacity: 0.3; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.2); }
      }
    </style>
  `;

  document.body.appendChild(welcome);

  setTimeout(() => {
    welcome.style.opacity = "0";
    setTimeout(() => {
      if (welcome.parentNode) {
        welcome.parentNode.removeChild(welcome);
      }
    }, 500);
  }, 2000);
}

// 添加到历史记录
function addToHistory(action, data) {
  const historyItem = {
    id: Date.now(),
    timestamp: new Date(),
    action: action,
    data: data,
  };

  recognitionHistory.unshift(historyItem);

  // 保持历史记录在100条以内
  if (recognitionHistory.length > 100) {
    recognitionHistory = recognitionHistory.slice(0, 100);
  }

  // 更新历史记录显示
  updateHistoryDisplay();
}

// 更新历史记录显示
function updateHistoryDisplay() {
  let historyPanel = document.getElementById("history-panel");
  if (!historyPanel) {
    historyPanel = document.createElement("div");
    historyPanel.id = "history-panel";
    historyPanel.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 300px;
      max-height: 400px;
      background: rgba(255, 255, 255, 0.95);
      border-radius: 10px;
      padding: 15px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      backdrop-filter: blur(10px);
      z-index: 999;
      overflow-y: auto;
      display: none;
    `;

    const toggleBtn = document.createElement("button");
    toggleBtn.innerHTML = '<i class="fas fa-history"></i>';
    toggleBtn.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 340px;
      width: 50px;
      height: 50px;
      border-radius: 50%;
      border: none;
      background: rgba(255, 255, 255, 0.9);
      color: #667eea;
      font-size: 1.2em;
      cursor: pointer;
      z-index: 1000;
      transition: all 0.3s ease;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    `;

    toggleBtn.addEventListener("click", () => {
      historyPanel.style.display =
        historyPanel.style.display === "none" ? "block" : "none";
    });

    document.body.appendChild(toggleBtn);
    document.body.appendChild(historyPanel);
  }

  historyPanel.innerHTML = `
    <h4 style="margin-bottom: 15px; color: #4a5568;">
      <i class="fas fa-history"></i> 操作历史
    </h4>
    ${recognitionHistory
      .slice(0, 10)
      .map(
        (item) => `
      <div style="margin-bottom: 10px; padding: 8px; background: rgba(102, 126, 234, 0.1); border-radius: 5px; font-size: 0.85em;">
        <strong>${getActionName(item.action)}</strong><br>
        <small style="color: #718096;">${item.timestamp.toLocaleTimeString()}</small>
      </div>
    `
      )
      .join("")}
  `;
}

// 获取操作参数
function getOperationParams(operation) {
  const params = {};

  switch (operation) {
    case "blur":
      params.kernel_size = 15;
      params.sigma = 5;
      break;
    case "sharpen":
      params.factor = 1.5;
      break;
    case "brightness":
      params.factor = 1.2;
      break;
    case "contrast":
      params.factor = 1.3;
      break;
    case "grayscale":
      // 无需参数
      break;
    case "edge":
      params.threshold1 = 100;
      params.threshold2 = 200;
      break;
    case "denoise":
      params.h = 10;
      params.template_window_size = 7;
      params.search_window_size = 21;
      break;
    case "rotate":
      params.angle = 90;
      break;
    case "resize":
      params.width = 800;
      params.height = 600;
      break;
    default:
      break;
  }

  return params;
}

// 获取操作名称
function getOperationName(operation) {
  const names = {
    blur: "模糊处理",
    sharpen: "锐化",
    brightness: "亮度调整",
    contrast: "对比度调整",
    grayscale: "灰度转换",
    edge: "边缘检测",
    denoise: "降噪处理",
    rotate: "旋转",
    resize: "尺寸调整",
  };
  return names[operation] || operation;
}

// 显示详细的OCR识别结果
function displayDetailedOCRResults(data, container) {
  let resultHtml = `
    <div class="ocr-result-detailed">
      <div class="result-header">
        <h4>🔍 OCR识别结果</h4>
        <div class="engine-badge">${getEngineBadge(data.engine)}</div>
      </div>
  `;

  // 显示引擎状态信息（特别是EasyOCR等备用引擎）
  if (
    data.engine &&
    (data.engine === "easyocr" || data.engine.includes("fallback"))
  ) {
    const engineIcon = data.engine === "easyocr" ? "🔄" : "🆘";
    const engineName =
      data.engine === "easyocr" ? "EasyOCR备用引擎" : "备用系统";
    resultHtml += `
      <div class="engine-status-info">
        <div class="engine-status-icon">${engineIcon}</div>
        <div class="engine-status-text">
          <strong>${engineName}识别成功</strong>
          <small>主引擎无法识别，已启用备用引擎完成识别</small>
        </div>
      </div>
    `;
  }

  // 主要识别结果
  if (data.text) {
    const confidenceClass = getConfidenceClass(data.confidence);
    const confidenceIcon = getConfidenceIcon(data.confidence);

    // 特别标识来自EasyOCR的结果
    const isEasyOCR = data.engine === "easyocr";
    const resultTitle = isEasyOCR ? "📝 EasyOCR识别内容:" : "📝 识别内容:";

    resultHtml += `
      <div class="main-result ${isEasyOCR ? "easyocr-result" : ""}">
        <div class="text-result">
          <div class="result-label">${resultTitle}</div>
          <div class="recognized-text ${confidenceClass}">
            ${confidenceIcon} <span class="result-text-highlight">${
      data.text
    }</span>
            ${isEasyOCR ? '<span class="easyocr-badge">EasyOCR</span>' : ""}
          </div>
        </div>
        <div class="confidence-info">
          <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${(
              data.confidence * 100
            ).toFixed(1)}%"></div>
          </div>
          <span class="confidence-text">置信度: ${(
            data.confidence * 100
          ).toFixed(1)}%</span>
        </div>
      </div>
    `;

    // 如果是EasyOCR且是车牌格式，特别提醒
    if (isEasyOCR && data.results && data.results.plate_format_matched) {
      resultHtml += `
        <div class="plate-detection-success">
          <div class="success-icon">🎯</div>
          <div class="success-text">
            <strong>检测到车牌格式</strong>
            <small>EasyOCR成功识别车牌: ${data.text}</small>
          </div>
        </div>
      `;
    }
  }

  // 显示警告信息
  if (data.warning) {
    resultHtml += `
      <div class="result-warning">
        <div class="warning-icon">⚠️</div>
        <div class="warning-text">${data.warning}</div>
      </div>
    `;
  }

  // 显示低置信度候选结果
  if (
    data.low_confidence_candidates &&
    data.low_confidence_candidates.length > 0
  ) {
    resultHtml += `
      <div class="low-confidence-section">
        <div class="section-title">📋 低置信度候选结果:</div>
        <div class="candidates-list">
    `;

    data.low_confidence_candidates.forEach((candidate) => {
      resultHtml += `
        <div class="candidate-item">
          <span class="candidate-text">${candidate.text}</span>
          <span class="candidate-confidence">(${(
            candidate.confidence * 100
          ).toFixed(1)}%)</span>
        </div>
      `;
    });

    resultHtml += `
        </div>
        <div class="suggestion-text">💡 建议提高图片质量或调整光照条件</div>
      </div>
    `;
  }

  // 显示详细识别信息（针对EasyOCR等多段文本识别）
  if (data.results && data.results.texts && data.results.texts.length > 1) {
    resultHtml += `
      <div class="detailed-results">
        <div class="section-title">📊 详细识别信息:</div>
        <div class="texts-list">
    `;

    data.results.texts.forEach((textInfo, index) => {
      const itemClass =
        textInfo.confidence > 0.5 ? "high-confidence" : "low-confidence";
      resultHtml += `
        <div class="text-item ${itemClass}">
          <span class="item-number">${index + 1}.</span>
          <span class="item-text">${textInfo.text || textInfo}</span>
          <span class="item-confidence">${
            textInfo.confidence
              ? (textInfo.confidence * 100).toFixed(1) + "%"
              : ""
          }</span>
        </div>
      `;
    });

    resultHtml += `
        </div>
      </div>
    `;
  }

  // 显示EasyOCR分段识别信息（如果有多个文本块）
  if (
    data.results &&
    data.results.individual_confidences &&
    data.results.individual_confidences.length > 1
  ) {
    resultHtml += `
      <div class="easyocr-segments">
        <div class="section-title">📋 EasyOCR分段识别:</div>
        <div class="segments-list">
    `;

    data.results.texts.forEach((text, index) => {
      const confidence = data.results.individual_confidences[index];
      const confidenceClass =
        confidence > 0.7
          ? "high-confidence"
          : confidence > 0.4
          ? "medium-confidence"
          : "low-confidence";
      resultHtml += `
        <div class="segment-item ${confidenceClass}">
          <span class="segment-number">${index + 1}.</span>
          <span class="segment-text">${text}</span>
          <span class="segment-confidence">${(confidence * 100).toFixed(
            1
          )}%</span>
        </div>
      `;
    });

    resultHtml += `
        </div>
        <div class="merge-info">
          <small>合并结果: ${data.text}</small>
        </div>
      </div>
    `;
  }

  // 显示图像质量分析
  if (data.image_quality) {
    const quality = data.image_quality;
    resultHtml += `
      <div class="quality-analysis">
        <div class="section-title">📊 图像质量分析:</div>
        <div class="quality-score">
          <span class="score-label">质量评分:</span>
          <span class="score-value ${getQualityClass(quality.quality_score)}">${
      quality.quality_score
    }/100</span>
        </div>
    `;

    if (quality.suggestions && quality.suggestions.length > 0) {
      resultHtml += `
        <div class="quality-suggestions">
          <div class="suggestions-title">💡 改进建议:</div>
          <ul class="suggestions-list">
      `;

      quality.suggestions.forEach((suggestion) => {
        resultHtml += `<li>${suggestion}</li>`;
      });

      resultHtml += `
          </ul>
        </div>
      `;
    }

    resultHtml += `</div>`;
  }

  // 显示车牌格式匹配信息
  if (data.results && "plate_format_matched" in data.results) {
    const formatIcon = data.results.plate_format_matched ? "🎯" : "⚠️";
    const formatText = data.results.plate_format_matched
      ? "车牌格式"
      : "通用文本";
    const formatClass = data.results.plate_format_matched
      ? "format-matched"
      : "format-unmatched";

    resultHtml += `
      <div class="format-info ${formatClass}">
        <span class="format-icon">${formatIcon}</span>
        <span class="format-text">格式识别: ${formatText}</span>
      </div>
    `;
  }

  resultHtml += `
      <div class="result-footer">
        <div class="engine-info">引擎: ${getEngineDisplayName(
          data.engine
        )}</div>
        <div class="timestamp">时间: ${new Date().toLocaleTimeString()}</div>
      </div>
    </div>
  `;

  container.innerHTML = resultHtml;
}

// 获取引擎显示名称
function getEngineDisplayName(engine) {
  const engineNames = {
    paddleocr: "PaddleOCR",
    tesseract: "Tesseract OCR",
    hyperlpr3: "HyperLPR3",
    easyocr: "EasyOCR (备用引擎)",
    fallback: "备用识别系统",
    hyperlpr3_low_confidence: "HyperLPR3 (低置信度)",
  };
  return engineNames[engine] || engine;
}

// 获取引擎徽章
function getEngineBadge(engine) {
  const badges = {
    hyperlpr3: '<span class="engine-badge hyperlpr3">🚗 HyperLPR3</span>',
    paddleocr: '<span class="engine-badge paddleocr">🔤 PaddleOCR</span>',
    easyocr: '<span class="engine-badge easyocr">👁️ EasyOCR</span>',
    tesseract: '<span class="engine-badge tesseract">📝 Tesseract</span>',
    fallback: '<span class="engine-badge fallback">🆘 备用系统</span>',
    hyperlpr3_low_confidence:
      '<span class="engine-badge hyperlpr3-low">🚗 HyperLPR3 (低置信度)</span>',
  };
  return (
    badges[engine] || `<span class="engine-badge default">${engine}</span>`
  );
}

// 获取置信度类别
function getConfidenceClass(confidence) {
  if (confidence >= 0.8) return "confidence-high";
  if (confidence >= 0.5) return "confidence-medium";
  return "confidence-low";
}

// 获取置信度图标
function getConfidenceIcon(confidence) {
  if (confidence >= 0.8) return "✅";
  if (confidence >= 0.5) return "⚠️";
  return "❌";
}

// 显示详细的车牌识别结果
function displayDetailedPlateResults(data, container) {
  let resultHtml = `
    <div class="plate-result-detailed">
      <div class="result-header">
        <h4>🚗 车牌识别结果</h4>
        <div class="engine-badge">${getEngineBadge(data.engine)}</div>
      </div>
  `;

  // 主要识别结果
  if (data.text && data.success) {
    const confidenceClass = getConfidenceClass(data.confidence);
    const confidenceIcon = getConfidenceIcon(data.confidence);

    resultHtml += `
      <div class="main-result">
        <div class="plate-result">
          <div class="result-label">车牌号码:</div>
          <div class="recognized-plate ${confidenceClass}">
            ${confidenceIcon} ${data.text}
          </div>
        </div>
        <div class="confidence-info">
          <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${(
              data.confidence * 100
            ).toFixed(1)}%"></div>
          </div>
          <span class="confidence-text">置信度: ${(
            data.confidence * 100
          ).toFixed(1)}%</span>
        </div>
      </div>
    `;
  }

  // 显示警告信息
  if (data.warning) {
    resultHtml += `
      <div class="result-warning">
        <div class="warning-icon">⚠️</div>
        <div class="warning-text">${data.warning}</div>
      </div>
    `;
  }

  // 显示低置信度候选结果（这是关键部分）
  if (
    data.low_confidence_candidates &&
    data.low_confidence_candidates.length > 0
  ) {
    resultHtml += `
      <div class="low-confidence-section">
        <div class="section-title">📋 检测到的车牌候选:</div>
        <div class="candidates-list">
    `;

    data.low_confidence_candidates.forEach((candidate, index) => {
      const isHighest = index === 0; // 假设已排序，第一个是最高置信度
      resultHtml += `
        <div class="candidate-item ${isHighest ? "highest-candidate" : ""}">
          <span class="candidate-number">${index + 1}.</span>
          <span class="candidate-text">${candidate.text}</span>
          <span class="candidate-confidence">(${(
            candidate.confidence * 100
          ).toFixed(1)}%)</span>
          ${isHighest ? '<span class="best-candidate">🎯 最佳候选</span>' : ""}
        </div>
      `;
    });

    resultHtml += `
        </div>
        <div class="suggestion-text">
          💡 建议: 虽然置信度较低，但${data.low_confidence_candidates[0].text}可能是正确的车牌号码
        </div>
      </div>
    `;
  }

  // 显示多个车牌结果（如果有）
  if (data.results && data.results.plates && data.results.plates.length > 1) {
    resultHtml += `
      <div class="multiple-plates">
        <div class="section-title">🚗 检测到多个车牌:</div>
        <div class="plates-list">
    `;

    data.results.plates.forEach((plate, index) => {
      resultHtml += `
        <div class="plate-item">
          <span class="plate-number">${index + 1}.</span>
          <span class="plate-text">${plate.text}</span>
          <span class="plate-confidence">${(plate.confidence * 100).toFixed(
            1
          )}%</span>
        </div>
      `;
    });

    resultHtml += `
        </div>
      </div>
    `;
  }

  // 显示图像质量分析
  if (data.image_quality) {
    const quality = data.image_quality;
    resultHtml += `
      <div class="quality-analysis">
        <div class="section-title">📊 图像质量分析:</div>
        <div class="quality-score">
          <span class="score-label">质量评分:</span>
          <span class="score-value ${getQualityClass(quality.quality_score)}">${
      quality.quality_score
    }/100</span>
        </div>
    `;

    if (quality.suggestions && quality.suggestions.length > 0) {
      resultHtml += `
        <div class="quality-suggestions">
          <div class="suggestions-title">💡 改进建议:</div>
          <ul class="suggestions-list">
      `;

      quality.suggestions.forEach((suggestion) => {
        resultHtml += `<li>${suggestion}</li>`;
      });

      resultHtml += `
          </ul>
        </div>
      `;
    }

    resultHtml += `</div>`;
  }

  // 显示处理状态
  if (!data.success && !data.low_confidence_candidates) {
    resultHtml += `
      <div class="no-results">
        <div class="no-results-icon">❌</div>
        <div class="no-results-text">未检测到车牌信息</div>
        <div class="no-results-suggestion">请确保图片中包含清晰的车牌</div>
      </div>
    `;
  }

  resultHtml += `
      <div class="result-footer">
        <div class="engine-info">引擎: HyperLPR3 专业车牌识别</div>
        <div class="timestamp">时间: ${new Date().toLocaleTimeString()}</div>
      </div>
    </div>
  `;

  container.innerHTML = resultHtml;
}

// 获取质量评分类别
function getQualityClass(score) {
  if (score >= 80) return "quality-excellent";
  if (score >= 60) return "quality-good";
  if (score >= 40) return "quality-fair";
  return "quality-poor";
}

// 获取操作名称（历史记录用）
function getActionName(action) {
  const names = {
    upload: "图片上传",
    gemini: "AI分析",
    ocr: "OCR识别",
    plate: "车牌识别",
    process: "图像处理",
  };
  return names[action] || action;
}

// 全屏查看图片
function viewImageFullscreen(imageSrc) {
  const modal = document.createElement("div");
  modal.className = "fullscreen-modal";
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
    cursor: pointer;
  `;

  modal.innerHTML = `
    <div style="position: relative; max-width: 90%; max-height: 90%;">
      <img src="${imageSrc}" style="max-width: 100%; max-height: 100%; border-radius: 8px;">
      <button onclick="this.parentElement.parentElement.remove()" 
              style="position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.8); border: none; border-radius: 50%; width: 40px; height: 40px; cursor: pointer; font-size: 18px;">
        ×
      </button>
    </div>
  `;

  modal.onclick = (e) => {
    if (e.target === modal) {
      modal.remove();
    }
  };

  document.body.appendChild(modal);
}

// 移除自定义图片
function removeCustomImage() {
  currentImages.gemini = null;
  const previewContainer = document.querySelector(".custom-image-preview");
  if (previewContainer) {
    previewContainer.remove();
  }
  showToast("已移除自定义图片", "info");
}

// 文件转换为Base64
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(",")[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// 创建高级图像预览
function createAdvancedImagePreview(container, base64, title) {
  container.innerHTML = `
    <div style="position: relative; display: inline-block;">
      <img src="data:image/jpeg;base64,${base64}" alt="${title}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
      <div style="position: absolute; bottom: 5px; left: 5px; background: rgba(0,0,0,0.7); color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">
        ${title}
      </div>
    </div>
  `;
}

// 分析图像属性
function analyzeImageProperties(file, base64) {
  const img = new Image();
  img.onload = function () {
    const properties = {
      width: img.width,
      height: img.height,
      size: file.size,
      type: file.type,
      aspectRatio: (img.width / img.height).toFixed(2),
    };

    showToast(
      `图像信息：${img.width}×${img.height}，比例${properties.aspectRatio}:1`,
      "info",
      {
        duration: 3000,
      }
    );
  };
  img.src = `data:${file.type};base64,${base64}`;
}

// 显示增强的OCR结果
function displayEnhancedOCRResults(results, container, engine) {
  let html = `<h4><i class="fas fa-text-width"></i> OCR识别结果 (${engine})</h4>`;

  if (results.texts && results.texts.length > 0) {
    html += '<div class="ocr-results">';
    results.texts.forEach((text, index) => {
      html += `
        <div class="text-result" style="margin-bottom: 10px; padding: 8px; background: rgba(102, 126, 234, 0.1); border-radius: 5px;">
          <div style="font-weight: bold; color: #667eea;">文本 ${
            index + 1
          }:</div>
          <div style="margin: 5px 0; font-family: monospace;">${text}</div>
          <button onclick="copyText('${text}', this)" style="padding: 2px 6px; background: #667eea; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 0.8em;">
            <i class="fas fa-copy"></i> 复制
          </button>
        </div>
      `;
    });
    html += "</div>";
  } else {
    html += '<p style="color: #e53e3e;">未识别到文本内容</p>';
  }

  if (results.confidence) {
    html += `<p style="margin-top: 10px; color: #718096;">识别置信度: ${(
      results.confidence * 100
    ).toFixed(1)}%</p>`;
  }

  container.innerHTML = html;
}

// 复制文本功能
function copyText(text, button) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      const originalText = button.innerHTML;
      button.innerHTML = '<i class="fas fa-check"></i> 已复制';
      button.style.background = "#48bb78";
      setTimeout(() => {
        button.innerHTML = originalText;
        button.style.background = "#667eea";
      }, 2000);
      showToast("文本已复制到剪贴板", "success", { duration: 1500 });
    })
    .catch(() => {
      showToast("复制失败，请手动选择复制", "error");
    });
}

// 创建通用进度容器
function createProgressContainer(container, message = "正在处理...") {
  container.innerHTML = `
    <div style="text-align: center; padding: 30px;">
      <div style="margin-bottom: 20px;">
        <div style="width: 60px; height: 60px; margin: 0 auto; position: relative;">
          <div style="width: 100%; height: 100%; border: 3px solid #e2e8f0; border-radius: 50%; position: absolute;"></div>
          <div style="width: 100%; height: 100%; border: 3px solid #667eea; border-top: 3px solid transparent; border-radius: 50%; animation: enhanced-spin 1s linear infinite; position: absolute;"></div>
          <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1.2em;">⚙️</div>
        </div>
      </div>
      <div style="color: #667eea; font-weight: 600; font-size: 1.1em; margin-bottom: 15px;">${message}</div>
      <div style="font-size: 0.9em; color: #718096; margin-bottom: 20px;">
        请稍候，正在处理您的请求...
      </div>
      <style>
        @keyframes enhanced-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      </style>
    </div>
  `;
  container.className = "result-box loading";
  return container;
}

// 显示车牌识别结果
function displayPlateResults(plates, container) {
  let html = '<h4><i class="fas fa-id-card"></i> 车牌识别结果</h4>';

  if (plates && plates.length > 0) {
    html += '<div class="plate-results">';
    plates.forEach((plate, index) => {
      html += `
        <div class="plate-result" style="margin-bottom: 10px; padding: 10px; background: rgba(72, 187, 120, 0.1); border-radius: 5px; border-left: 4px solid #48bb78;">
          <div style="font-weight: bold; font-size: 1.2em; color: #2d3748;">车牌 ${
            index + 1
          }: ${plate.text}</div>
          <div style="margin: 5px 0; color: #718096;">置信度: ${(
            plate.confidence * 100
          ).toFixed(1)}%</div>
          ${
            plate.position
              ? `<div style="color: #718096; font-size: 0.9em;">位置: x:${plate.position.x}, y:${plate.position.y}</div>`
              : ""
          }
          <button onclick="copyText('${
            plate.text
          }', this)" style="margin-top: 5px; padding: 4px 8px; background: #48bb78; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 0.8em;">
            <i class="fas fa-copy"></i> 复制车牌号
          </button>
        </div>
      `;
    });
    html += "</div>";
  } else {
    html += '<p style="color: #e53e3e;">未识别到车牌</p>';
  }

  container.innerHTML = html;
}

// 获取图片Base64
async function fetchImageAsBase64(imageUrl) {
  try {
    const response = await fetch(imageUrl);
    const blob = await response.blob();
    return await fileToBase64(blob);
  } catch (error) {
    throw new Error("获取图片失败: " + error.message);
  }
}

// 增强的帮助系统
function initializeHelpSystem() {
  // 创建帮助按钮
  const helpButton = document.createElement("button");
  helpButton.id = "help-toggle";
  helpButton.innerHTML = '<i class="fas fa-question-circle"></i>';
  helpButton.style.cssText = `
    position: fixed;
    bottom: 80px;
    right: 20px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    border: none;
    background: rgba(102, 126, 234, 0.9);
    color: white;
    font-size: 1.2em;
    cursor: pointer;
    z-index: 1000;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  `;

  helpButton.addEventListener("click", showHelpModal);
  document.body.appendChild(helpButton);

  // 添加悬停效果
  helpButton.addEventListener("mouseenter", () => {
    helpButton.style.transform = "scale(1.1)";
    helpButton.style.boxShadow = "0 6px 20px rgba(102, 126, 234, 0.4)";
  });

  helpButton.addEventListener("mouseleave", () => {
    helpButton.style.transform = "scale(1)";
    helpButton.style.boxShadow = "0 4px 15px rgba(102, 126, 234, 0.3)";
  });
}

// 显示帮助模态框
function showHelpModal() {
  const modal = document.createElement("div");
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10005;
    opacity: 0;
    transition: opacity 0.3s ease;
  `;

  const content = document.createElement("div");
  content.style.cssText = `
    background: white;
    border-radius: 20px;
    padding: 30px;
    max-width: 600px;
    width: 90%;
    max-height: 80%;
    overflow-y: auto;
    position: relative;
    transform: scale(0.8);
    transition: transform 0.3s ease;
  `;

  content.innerHTML = `
    <button style="position: absolute; top: 15px; right: 15px; border: none; background: none; font-size: 1.5em; cursor: pointer; color: #718096;">
      <i class="fas fa-times"></i>
    </button>
    
    <div style="text-align: center; margin-bottom: 30px;">
      <h2 style="color: #4a5568; margin-bottom: 10px;">
        <i class="fas fa-graduation-cap"></i> 系统使用指南
      </h2>
      <p style="color: #718096;">天津仁爱学院智能车牌识别系统</p>
    </div>
    
    <div class="help-tabs" style="display: flex; margin-bottom: 20px; border-bottom: 2px solid #e2e8f0;">
      <button class="help-tab active" data-tab="basic" style="flex: 1; padding: 10px; border: none; background: none; cursor: pointer; color: #667eea; border-bottom: 2px solid #667eea;">基础操作</button>
      <button class="help-tab" data-tab="advanced" style="flex: 1; padding: 10px; border: none; background: none; cursor: pointer; color: #718096;">高级功能</button>
      <button class="help-tab" data-tab="shortcuts" style="flex: 1; padding: 10px; border: none; background: none; cursor: pointer; color: #718096;">快捷键</button>
      <button class="help-tab" data-tab="tips" style="flex: 1; padding: 10px; border: none; background: none; cursor: pointer; color: #718096;">使用技巧</button>
    </div>
    
    <div class="help-content">
      <div class="help-panel active" data-panel="basic">
        <h4><i class="fas fa-play-circle"></i> 基础操作指南</h4>
        <div class="help-item">
          <h5>1. Gemini AI 分析</h5>
          <ul>
            <li>上传图片或选择预设图片</li>
            <li>输入分析指令或选择预设提示词</li>
            <li>点击"开始分析"获得AI智能分析结果</li>
          </ul>
        </div>
        
        <div class="help-item">
          <h5>2. OCR 文字识别</h5>
          <ul>
            <li>上传包含文字的图片</li>
            <li>选择合适的OCR引擎(PaddleOCR推荐中文)</li>
            <li>可选择启用车牌区域提取功能</li>
          </ul>
        </div>
        
        <div class="help-item">
          <h5>3. 车牌识别</h5>
          <ul>
            <li>上传包含车牌的车辆图片</li>
            <li>使用HyperLPR3专业引擎识别</li>
            <li>获得车牌号码和置信度信息</li>
          </ul>
        </div>
        
        <div class="help-item">
          <h5>4. 图像处理</h5>
          <ul>
            <li>上传需要处理的图片</li>
            <li>选择处理操作(模糊、锐化、边缘检测等)</li>
            <li>对比查看处理前后效果</li>
          </ul>
        </div>
      </div>
      
      <div class="help-panel" data-panel="advanced">
        <h4><i class="fas fa-cogs"></i> 高级功能</h4>
        <div class="help-item">
          <h5>拖拽上传</h5>
          <p>直接将图片文件拖拽到上传区域，支持所有标签页</p>
        </div>
        
        <div class="help-item">
          <h5>实时预览</h5>
          <p>上传后立即显示图片预览，支持全屏查看和下载</p>
        </div>
        
        <div class="help-item">
          <h5>引擎状态监控</h5>
          <p>实时显示各OCR引擎状态，点击查看详细信息</p>
        </div>
        
        <div class="help-item">
          <h5>操作历史</h5>
          <p>记录所有操作历史，点击右下角历史按钮查看</p>
        </div>
        
        <div class="help-item">
          <h5>主题切换</h5>
          <p>左上角按钮可切换深色/浅色主题</p>
        </div>
      </div>
      
      <div class="help-panel" data-panel="shortcuts">
        <h4><i class="fas fa-keyboard"></i> 快捷键指南</h4>
        <div class="shortcuts-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
          <div class="shortcut-item">
            <kbd>Ctrl + 1</kbd>
            <span>Gemini AI 标签页</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl + 2</kbd>
            <span>OCR 识别标签页</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl + 3</kbd>
            <span>车牌识别标签页</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl + 4</kbd>
            <span>图像处理标签页</span>
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl + U</kbd>
            <span>快速上传文件</span>
          </div>
          <div class="shortcut-item">
            <kbd>Esc</kbd>
            <span>关闭所有提示</span>
          </div>
        </div>
      </div>
      
      <div class="help-panel" data-panel="tips">
        <h4><i class="fas fa-lightbulb"></i> 使用技巧</h4>
        <div class="tips-list">
          <div class="tip-item">
            <i class="fas fa-camera"></i>
            <div>
              <h5>图片质量建议</h5>
              <p>使用清晰、光线充足的图片能显著提高识别准确率</p>
            </div>
          </div>
          
          <div class="tip-item">
            <i class="fas fa-crop"></i>
            <div>
              <h5>车牌拍摄角度</h5>
              <p>正面拍摄车牌，避免过度倾斜或反光</p>
            </div>
          </div>
          
          <div class="tip-item">
            <i class="fas fa-file-image"></i>
            <div>
              <h5>支持的格式</h5>
              <p>支持 JPG、PNG、GIF 等常见图片格式，建议大小不超过16MB</p>
            </div>
          </div>
          
          <div class="tip-item">
            <i class="fas fa-language"></i>
            <div>
              <h5>OCR引擎选择</h5>
              <p>中文文档推荐PaddleOCR，多语言文档推荐Tesseract</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <style>
      .help-item { margin-bottom: 20px; }
      .help-item h5 { color: #4a5568; margin-bottom: 8px; }
      .help-item ul { margin-left: 20px; }
      .help-item li { margin-bottom: 5px; color: #718096; }
      
      .help-tab.active { color: #667eea; border-bottom-color: #667eea; }
      .help-panel { display: none; }
      .help-panel.active { display: block; }
      
      .shortcut-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background: #f7fafc;
        border-radius: 8px;
      }
      
      kbd {
        background: #2d3748;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-family: monospace;
      }
      
      .tip-item {
        display: flex;
        align-items: flex-start;
        gap: 15px;
        margin-bottom: 20px;
        padding: 15px;
        background: #f8faff;
        border-radius: 10px;
        border-left: 4px solid #667eea;
      }
      
      .tip-item i {
        font-size: 1.5em;
        color: #667eea;
        margin-top: 5px;
      }
      
      .tip-item h5 {
        margin: 0 0 5px 0;
        color: #4a5568;
      }
      
      .tip-item p {
        margin: 0;
        color: #718096;
        font-size: 0.9em;
      }
    </style>
  `;

  // 标签页切换功能
  const helpTabs = content.querySelectorAll(".help-tab");
  const helpPanels = content.querySelectorAll(".help-panel");

  helpTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetPanel = tab.getAttribute("data-tab");

      helpTabs.forEach((t) => {
        t.classList.remove("active");
        t.style.color = "#718096";
        t.style.borderBottomColor = "transparent";
      });

      helpPanels.forEach((p) => {
        p.classList.remove("active");
      });

      tab.classList.add("active");
      tab.style.color = "#667eea";
      tab.style.borderBottomColor = "#667eea";

      const panel = content.querySelector(`[data-panel="${targetPanel}"]`);
      if (panel) {
        panel.classList.add("active");
      }
    });
  });

  // 关闭按钮
  content.querySelector("button").addEventListener("click", () => {
    modal.style.opacity = "0";
    setTimeout(() => {
      if (modal.parentNode) {
        modal.parentNode.removeChild(modal);
      }
    }, 300);
  });

  // 点击背景关闭
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.opacity = "0";
      setTimeout(() => {
        if (modal.parentNode) {
          modal.parentNode.removeChild(modal);
        }
      }, 300);
    }
  });

  modal.appendChild(content);
  document.body.appendChild(modal);

  // 显示动画
  setTimeout(() => {
    modal.style.opacity = "1";
    content.style.transform = "scale(1)";
  }, 10);
}

// 性能监控和优化提示
function initializePerformanceMonitor() {
  const monitor = {
    startTime: Date.now(),
    operationCount: 0,
    totalProcessingTime: 0,
  };

  // 监控函数执行时间
  const originalFetch = window.fetch;
  window.fetch = async function (...args) {
    const start = Date.now();
    monitor.operationCount++;

    try {
      const response = await originalFetch.apply(this, args);
      const duration = Date.now() - start;
      monitor.totalProcessingTime += duration;

      // 如果请求时间过长，显示优化建议
      if (duration > 5000) {
        showToast(
          "检测到处理时间较长，建议：压缩图片大小或检查网络连接",
          "warning",
          {
            duration: 6000,
          }
        );
      }

      return response;
    } catch (error) {
      const duration = Date.now() - start;
      monitor.totalProcessingTime += duration;
      throw error;
    }
  };

  // 每分钟显示性能统计
  setInterval(() => {
    if (monitor.operationCount > 0) {
      const avgTime = (
        monitor.totalProcessingTime / monitor.operationCount
      ).toFixed(0);
      const uptime = ((Date.now() - monitor.startTime) / 1000 / 60).toFixed(1);

      console.log(
        `性能统计 - 运行时间: ${uptime}分钟, 操作次数: ${monitor.operationCount}, 平均响应时间: ${avgTime}ms`
      );
    }
  }, 60000);

  return monitor;
}

// 初始化所有增强功能
document.addEventListener("DOMContentLoaded", () => {
  // 修复aria-hidden问题
  if (document.body.hasAttribute("aria-hidden")) {
    document.body.removeAttribute("aria-hidden");
  }

  // 处理Chrome扩展错误
  if (typeof chrome !== "undefined" && chrome.runtime) {
    // 忽略Chrome扩展的连接错误
    const originalError = console.error;
    console.error = function (...args) {
      const message = args.join(" ");
      if (
        message.includes("message channel closed") ||
        message.includes("runtime.lastError") ||
        message.includes("Extension context invalidated") ||
        message.includes("Failed to fetch") ||
        message.includes("httpError: false")
      ) {
        return; // 忽略这些扩展相关的错误
      }
      originalError.apply(console, args);
    };

    // 处理未捕获的Promise拒绝
    window.addEventListener("unhandledrejection", function (event) {
      const message = event.reason?.message || event.reason?.toString() || "";
      if (
        message.includes("message channel closed") ||
        message.includes("runtime.lastError") ||
        message.includes("Extension context invalidated") ||
        message.includes("Failed to fetch")
      ) {
        event.preventDefault(); // 阻止错误显示
        return;
      }
    });
  }

  // 显示欢迎动画
  showWelcomeAnimation();

  // 延迟初始化帮助系统和性能监控，避免阻塞页面加载
  setTimeout(() => {
    initializeHelpSystem();
    initializePerformanceMonitor();

    showToast("智能车牌识别系统已就绪", "success", {
      duration: 3000,
    });
  }, 2500);
});

// 确保外部库可用
if (typeof markdownit === "undefined") {
  window.markdownit = function (options) {
    return {
      render: function (markdown) {
        return markdown
          .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
          .replace(/\*(.*?)\*/g, "<em>$1</em>")
          .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
          .replace(/`(.*?)`/g, "<code>$1</code>");
      },
    };
  };
}

if (typeof hljs === "undefined") {
  window.hljs = {
    getLanguage: function () {
      return null;
    },
    highlight: function (code, options) {
      return { value: code };
    },
  };
}
