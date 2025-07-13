/**
 * 前端错误修复脚本
 * 解决Chrome扩展兼容性和权限策略问题
 */

(function() {
    'use strict';
    
    console.log('🔧 前端修复脚本已加载');

    // 1. 修复Chrome扩展runtime.lastError问题
    function fixChromeExtensionErrors() {
        // 监听和捕获未处理的Promise rejection
        window.addEventListener('unhandledrejection', function(event) {
            if (event.reason && event.reason.message && 
                event.reason.message.includes('message channel closed')) {
                // 静默处理Chrome扩展相关错误
                event.preventDefault();
                console.warn('🔇 已静默处理Chrome扩展通信错误');
            }
        });

        // 重写chrome.runtime调用以避免错误
        if (typeof chrome !== 'undefined' && chrome.runtime) {
            const originalSendMessage = chrome.runtime.sendMessage;
            chrome.runtime.sendMessage = function(...args) {
                try {
                    return originalSendMessage.apply(this, args);
                } catch (error) {
                    console.warn('🔇 Chrome扩展通信被阻止:', error.message);
                    return Promise.resolve();
                }
            };
        }
    }

    // 2. 禁用可能导致权限策略违规的事件监听器
    function fixPermissionsPolicyViolations() {
        // 重写addEventListener以过滤unload相关事件
        const originalAddEventListener = window.addEventListener;
        window.addEventListener = function(type, listener, options) {
            if (type === 'unload' || type === 'beforeunload') {
                console.warn('🚫 已阻止添加可能违反权限策略的事件监听器:', type);
                return;
            }
            return originalAddEventListener.call(this, type, listener, options);
        };

        // 重写document.addEventListener
        const originalDocAddEventListener = document.addEventListener;
        document.addEventListener = function(type, listener, options) {
            if (type === 'unload' || type === 'beforeunload') {
                console.warn('🚫 已阻止添加可能违反权限策略的事件监听器:', type);
                return;
            }
            return originalDocAddEventListener.call(this, type, listener, options);
        };
    }

    // 3. 修复aria-hidden问题
    function fixAriaHiddenIssues() {
        // 监听DOM变化，移除body上的aria-hidden属性
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && 
                    mutation.attributeName === 'aria-hidden' &&
                    mutation.target === document.body) {
                    document.body.removeAttribute('aria-hidden');
                    console.log('🔧 已移除body上的aria-hidden属性');
                }
            });
        });

        // 立即移除aria-hidden
        if (document.body && document.body.hasAttribute('aria-hidden')) {
            document.body.removeAttribute('aria-hidden');
            console.log('🔧 已移除body上的aria-hidden属性');
        }

        // 开始观察
        if (document.body) {
            observer.observe(document.body, {
                attributes: true,
                attributeFilter: ['aria-hidden']
            });
        }
    }

    // 4. 错误日志收集和过滤
    function setupErrorHandling() {
        // 过滤已知的无害错误
        const originalConsoleError = console.error;
        console.error = function(...args) {
            const message = args.join(' ');
            
            // 过滤Chrome扩展相关错误
            if (message.includes('runtime.lastError') ||
                message.includes('message channel closed') ||
                message.includes('chextloader') ||
                message.includes('chext_driver')) {
                return; // 静默处理
            }
            
            // 过滤权限策略错误（已在meta中处理）
            if (message.includes('Permissions policy violation: unload')) {
                return; // 静默处理
            }
            
            return originalConsoleError.apply(console, args);
        };
    }

    // 5. 网络请求重试机制
    function setupNetworkRetry() {
        // 重写fetch以添加重试机制
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            const maxRetries = 3;
            const retryDelay = 1000;
            
            async function fetchWithRetry(attempt = 1) {
                try {
                    const response = await originalFetch(url, options);
                    return response;
                } catch (error) {
                    if (attempt < maxRetries && 
                        (error.name === 'NetworkError' || error.name === 'TypeError')) {
                        console.warn(`🔄 网络请求重试 ${attempt}/${maxRetries}: ${url}`);
                        await new Promise(resolve => setTimeout(resolve, retryDelay * attempt));
                        return fetchWithRetry(attempt + 1);
                    }
                    throw error;
                }
            }
            
            return fetchWithRetry();
        };
    }

    // 初始化所有修复
    function initializeFixes() {
        try {
            fixChromeExtensionErrors();
            fixPermissionsPolicyViolations();
            fixAriaHiddenIssues();
            setupErrorHandling();
            setupNetworkRetry();
            
            console.log('✅ 所有前端修复已应用');
        } catch (error) {
            console.error('❌ 前端修复初始化失败:', error);
        }
    }

    // DOM加载完成后执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeFixes);
    } else {
        initializeFixes();
    }

    // 导出修复函数供其他脚本使用
    window.frontendFix = {
        init: initializeFixes,
        fixChromeExtensions: fixChromeExtensionErrors,
        fixPermissions: fixPermissionsPolicyViolations,
        fixAria: fixAriaHiddenIssues
    };

})();
