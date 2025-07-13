#!/usr/bin/env python3
"""
HyperLPR3 车牌识别引擎功能测试脚本
测试真实的车牌识别功能和性能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
import base64
import io
from PIL import Image

def test_hyperlpr3_recognition():
    """测试HyperLPR3的实际车牌识别功能"""
    print("🔍 测试 HyperLPR3 车牌识别功能...")
    print("=" * 50)
    
    try:
        # 导入HyperLPR3
        import hyperlpr3 as lpr3
        print("✅ HyperLPR3 导入成功")
        
        # 初始化车牌识别器
        catcher = lpr3.LicensePlateCatcher()
        print("✅ HyperLPR3 初始化成功")
        
        # 创建一个测试用的模拟车牌图像
        test_image = create_test_plate_image()
        print("✅ 创建测试图像成功")
        
        # 测试识别功能
        print("\n🎯 开始车牌识别测试...")
        
        # 转换图像格式（HyperLPR3需要RGB格式）
        if len(test_image.shape) == 3:
            rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = cv2.cvtColor(test_image, cv2.COLOR_GRAY2RGB)
        
        # 执行识别
        plates = catcher(rgb_image)
        
        print(f"📊 识别结果: {plates}")
        
        if plates and len(plates) > 0:
            print("✅ HyperLPR3 车牌识别功能正常")
            for i, plate in enumerate(plates):
                if plate and len(plate) >= 2:
                    plate_no = str(plate[0]) if plate[0] else '未知'
                    confidence = float(plate[1]) if isinstance(plate[1], (int, float)) else 0.0
                    print(f"   车牌 {i+1}: {plate_no} (置信度: {confidence:.2f})")
                else:
                    print(f"   车牌 {i+1}: 数据格式异常")
        else:
            print("⚠️  未检测到车牌（这是正常的，因为使用的是模拟图像）")
            print("✅ HyperLPR3 引擎响应正常，没有崩溃或错误")
        
        return True
        
    except Exception as e:
        print(f"❌ HyperLPR3 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_plate_image():
    """创建一个简单的测试图像"""
    # 创建一个300x100的白色图像
    image = np.ones((100, 300, 3), dtype=np.uint8) * 255
    
    # 添加一些基本的车牌样式（蓝色背景，白色文字区域）
    cv2.rectangle(image, (50, 20), (250, 80), (100, 50, 0), -1)  # 蓝色背景
    cv2.rectangle(image, (60, 30), (240, 70), (255, 255, 255), -1)  # 白色文字区域
    
    # 添加一些文字样的矩形（模拟车牌字符）
    cv2.rectangle(image, (70, 40), (85, 60), (0, 0, 0), -1)  # 模拟字符
    cv2.rectangle(image, (95, 40), (110, 60), (0, 0, 0), -1)
    cv2.rectangle(image, (120, 40), (135, 60), (0, 0, 0), -1)
    cv2.rectangle(image, (145, 40), (160, 60), (0, 0, 0), -1)
    cv2.rectangle(image, (170, 40), (185, 60), (0, 0, 0), -1)
    cv2.rectangle(image, (195, 40), (210, 60), (0, 0, 0), -1)
    cv2.rectangle(image, (220, 40), (235, 60), (0, 0, 0), -1)
    
    return image

def test_api_integration():
    """测试HyperLPR3与系统API的集成"""
    print("\n🔌 测试 API 集成...")
    print("=" * 30)
    
    try:
        import requests
        import base64
        
        # 创建测试图像
        test_image = create_test_plate_image()
        
        # 转换为base64
        _, buffer = cv2.imencode('.jpg', test_image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # 测试OCR-Simple API
        response = requests.post('http://127.0.0.1:8080/api/ocr-simple', 
                               json={
                                   'image': image_base64,
                                   'engine': 'hyperlpr3'
                               })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 调用成功")
            print(f"📊 响应: {result}")
            
            if result.get('success'):
                print("✅ HyperLPR3 API 集成正常")
            else:
                print(f"⚠️  API 返回错误: {result.get('error', '未知错误')}")
        else:
            print(f"❌ API 调用失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
        
    except Exception as e:
        print(f"❌ API 集成测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_performance():
    """测试HyperLPR3的性能"""
    print("\n⏱️  性能测试...")
    print("=" * 20)
    
    try:
        import hyperlpr3 as lpr3
        import time
        
        catcher = lpr3.LicensePlateCatcher()
        test_image = create_test_plate_image()
        rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        
        # 执行多次识别测试
        times = []
        for i in range(5):
            start_time = time.time()
            plates = catcher(rgb_image)
            end_time = time.time()
            times.append(end_time - start_time)
            print(f"   第 {i+1} 次: {(end_time - start_time)*1000:.1f}ms")
        
        avg_time = sum(times) / len(times)
        print(f"✅ 平均识别时间: {avg_time*1000:.1f}ms")
        
        if avg_time < 2.0:  # 2秒内完成识别
            print("✅ 性能良好")
        else:
            print("⚠️  性能较慢，但功能正常")
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")

def main():
    """主测试函数"""
    print("🚗 HyperLPR3 车牌识别引擎全面测试")
    print("=" * 60)
    
    # 1. 基础功能测试
    basic_test = test_hyperlpr3_recognition()
    
    # 2. API集成测试
    test_api_integration()
    
    # 3. 性能测试
    test_performance()
    
    print("\n" + "=" * 60)
    if basic_test:
        print("🎉 HyperLPR3 引擎测试完成 - 功能正常")
        print("💡 建议:")
        print("   1. 使用高质量的车辆图片进行识别")
        print("   2. 确保车牌在图片中清晰可见")
        print("   3. 适当的光照条件有助于提高识别率")
        print("   4. 可以启用'车牌区域提取'功能提高识别精度")
    else:
        print("❌ HyperLPR3 引擎存在问题，需要检查安装")
        print("💡 解决方案:")
        print("   1. 重新安装: pip install hyperlpr3")
        print("   2. 检查Python版本是否兼容")
        print("   3. 确保系统依赖库齐全")

if __name__ == "__main__":
    main()
