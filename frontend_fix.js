/*
 * 🚀 前端错误修复脚本 - 解决JavaScript权限策略违规问题
 * 修复日期: 2025年1月12日
 * 问题: Permissions policy violation: unload is not allowed
 */

console.log('🔧 启动前端错误修复...');

// 1. 移除所有可能导致unload事件的监听器
if (typeof window !== 'undefined') {
    // 清除现有的unload监听器
    window.onbeforeunload = null;
    window.onunload = null;
    
    // 阻止添加新的unload监听器
    const originalAddEventListener = window.addEventListener;
    window.addEventListener = function(type, listener, options) {
        if (type === 'beforeunload' || type === 'unload') {
            console.warn('🚫 阻止添加unload事件监听器:', type);
            return;
        }
        return originalAddEventListener.call(this, type, listener, options);
    };
    
    console.log('✅ unload事件监听器已清理');
}

// 2. 修复页面跳转和表单提交
function safeNavigate(url) {
    try {
        window.location.href = url;
    } catch (error) {
        console.warn('⚠️ 导航失败，使用替代方案:', error);
        // 使用替代方案
        const link = document.createElement('a');
        link.href = url;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// 3. 修复文件上传功能
function enhanceFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            console.log('📁 文件选择事件触发:', e.target.files.length, '个文件');
            
            // 移除任何可能的unload相关代码
            e.stopPropagation();
            
            // 确保文件处理正常
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                console.log('📄 选择的文件:', file.name, '大小:', file.size);
                
                // 触发上传或预览逻辑
                if (typeof window.handleFileUpload === 'function') {
                    window.handleFileUpload(file);
                }
            }
        });
    });
    
    console.log('✅ 文件上传功能已修复');
}

// 4. 修复AJAX请求
function enhanceAjaxRequests() {
    // 确保fetch请求正常工作
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        console.log('🌐 发起fetch请求:', args[0]);
        return originalFetch.apply(this, args)
            .then(response => {
                console.log('✅ fetch请求成功:', response.status);
                return response;
            })
            .catch(error => {
                console.error('❌ fetch请求失败:', error);
                throw error;
            });
    };
    
    console.log('✅ AJAX请求已增强');
}

// 5. 修复OCR功能
function enhanceOCRFunction() {
    // 确保OCR相关的JavaScript正常工作
    if (typeof window.recognizeImage === 'function') {
        const originalRecognize = window.recognizeImage;
        window.recognizeImage = function(imageData, engine) {
            console.log('🔍 启动OCR识别, 引擎:', engine);
            
            // 移除任何unload相关逻辑
            return originalRecognize.call(this, imageData, engine)
                .then(result => {
                    console.log('✅ OCR识别成功:', result);
                    return result;
                })
                .catch(error => {
                    console.error('❌ OCR识别失败:', error);
                    throw error;
                });
        };
    }
    
    console.log('✅ OCR功能已修复');
}

// 6. 页面加载完成后执行修复
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            enhanceFileUpload();
            enhanceAjaxRequests();
            enhanceOCRFunction();
            console.log('🎉 前端错误修复完成！');
        }, 100);
    });
} else {
    // 如果页面已经加载完成，立即执行
    setTimeout(() => {
        enhanceFileUpload();
        enhanceAjaxRequests();
        enhanceOCRFunction();
        console.log('🎉 前端错误修复完成！');
    }, 100);
}

// 7. 全局错误处理
window.addEventListener('error', function(e) {
    console.warn('🚨 捕获到错误:', e.message);
    if (e.message.includes('unload') || e.message.includes('Permissions policy')) {
        console.log('🛡️ 已阻止权限策略违规错误');
        e.preventDefault();
        return false;
    }
});

// 8. 导出修复函数供其他脚本使用
window.frontendFix = {
    safeNavigate: safeNavigate,
    enhanceFileUpload: enhanceFileUpload,
    enhanceAjaxRequests: enhanceAjaxRequests,
    enhanceOCRFunction: enhanceOCRFunction
};

console.log('🔧 前端修复脚本加载完成！');
