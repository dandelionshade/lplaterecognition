#!/usr/bin/env python3
"""
测试fallback OCR系统的完整性
"""

import requests
import json
import base64
import cv2
import numpy as np
from pathlib import Path

def create_test_image():
    """创建一个包含车牌号的测试图像"""
    # 创建一个简单的车牌图像
    img = np.ones((100, 300, 3), dtype=np.uint8) * 255  # 白色背景
    
    # 添加蓝色车牌背景
    cv2.rectangle(img, (20, 20), (280, 80), (255, 100, 0), -1)
    
    # 添加白色文字（模拟车牌号）
    cv2.putText(img, 'XY123ABC', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    
    return img

def image_to_base64(image):
    """将OpenCV图像转换为base64字符串"""
    _, buffer = cv2.imencode('.jpg', image)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64

def test_ocr_api(base_url="http://127.0.0.1:8080"):
    """测试OCR API的所有引擎"""
    
    print("🚀 开始测试OCR系统...")
    
    # 创建测试图像
    test_image = create_test_image()
    image_base64 = image_to_base64(test_image)
    
    # 测试不同引擎
    engines = ['auto', 'fallback', 'paddleocr', 'tesseract', 'hyperlpr3']
    
    results = {}
    
    for engine in engines:
        print(f"\n📱 测试引擎: {engine}")
        
        try:
            response = requests.post(
                f"{base_url}/api/ocr-simple",
                json={
                    "image": image_base64,
                    "engine": engine
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                results[engine] = {
                    'success': True,
                    'data': result
                }
                print(f"✅ {engine} 成功: {result.get('text', 'N/A')}")
            else:
                results[engine] = {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'data': response.text
                }
                print(f"❌ {engine} 失败: HTTP {response.status_code}")
                
        except Exception as e:
            results[engine] = {
                'success': False,
                'error': str(e),
                'data': None
            }
            print(f"❌ {engine} 异常: {e}")
    
    # 测试结果总结
    print("\n" + "="*50)
    print("📊 测试结果总结")
    print("="*50)
    
    successful_engines = []
    failed_engines = []
    
    for engine, result in results.items():
        if result['success']:
            successful_engines.append(engine)
            print(f"✅ {engine}: 可用")
        else:
            failed_engines.append(engine)
            print(f"❌ {engine}: {result['error']}")
    
    print(f"\n📈 成功率: {len(successful_engines)}/{len(engines)} ({len(successful_engines)/len(engines)*100:.1f}%)")
    
    # 核心功能验证
    if 'fallback' in successful_engines:
        print("🛡️  核心功能保证: ✅ Fallback系统可用")
    else:
        print("⚠️  核心功能风险: ❌ Fallback系统不可用")
    
    if 'auto' in successful_engines:
        print("🎯 自动选择: ✅ 智能引擎选择可用")
    else:
        print("⚠️  自动选择: ❌ 智能引擎选择不可用")
    
    return results

def test_image_files():
    """测试现有的车牌图片文件"""
    print("\n🖼️  测试现有图片文件...")
    
    # 寻找车牌图片
    image_paths = []
    for pattern in ['*.jpg', '*.png', '*.jpeg']:
        image_paths.extend(Path('web').glob(pattern))
        image_paths.extend(Path('plate_-detect/chepai').glob(pattern) if Path('plate_-detect/chepai').exists() else [])
    
    if not image_paths:
        print("❌ 未找到测试图片")
        return
    
    # 测试前3张图片
    for i, img_path in enumerate(image_paths[:3]):
        print(f"\n📸 测试图片: {img_path}")
        
        try:
            # 读取图片
            image = cv2.imread(str(img_path))
            if image is None:
                print("❌ 无法读取图片")
                continue
            
            # 转换为base64
            image_base64 = image_to_base64(image)
            
            # 使用fallback引擎测试
            response = requests.post(
                "http://127.0.0.1:8080/api/ocr-simple",
                json={
                    "image": image_base64,
                    "engine": "fallback"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 识别结果: {result.get('text', 'N/A')}")
            else:
                print(f"❌ 识别失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    print("🚗 天津仁爱学院车牌识别系统 - 完整性测试")
    print("=" * 60)
    
    # 基础API测试
    results = test_ocr_api()
    
    # 真实图片测试
    test_image_files()
    
    print("\n✅ 测试完成！")
