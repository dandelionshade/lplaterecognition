#!/usr/bin/env python3
"""
测试详细OCR结果显示功能
验证低置信度候选结果是否正确返回和显示
"""

import requests
import base64
import cv2
import numpy as np
import json
from pathlib import Path

def create_test_plate_image(plate_text="京A12345"):
    """创建测试车牌图像"""
    # 创建一个简单的车牌图像
    img = np.ones((60, 200, 3), dtype=np.uint8) * 255  # 白色背景
    
    # 添加蓝色边框（模拟车牌）
    cv2.rectangle(img, (5, 5), (195, 55), (255, 100, 0), 2)  # 蓝色边框
    
    # 添加文字
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, plate_text, (20, 40), font, 1, (0, 0, 0), 2)
    
    return img

def create_blurry_plate_image(plate_text="京B56789"):
    """创建模糊的车牌图像，用于测试低置信度识别"""
    img = create_test_plate_image(plate_text)
    
    # 添加模糊效果
    img = cv2.GaussianBlur(img, (7, 7), 0)
    
    # 添加噪声
    noise = np.random.randint(0, 50, img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    
    return img

def image_to_base64(image):
    """将OpenCV图像转换为base64字符串"""
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def test_ocr_api(image, engine='hyperlpr3', endpoint='/api/ocr-simple'):
    """测试OCR API"""
    image_base64 = image_to_base64(image)
    
    try:
        response = requests.post(
            f"http://127.0.0.1:8081{endpoint}",
            json={
                "image": image_base64,
                "engine": engine
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "response": response.text
            }
    except Exception as e:
        return {"error": str(e)}

def print_detailed_result(result, test_name):
    """打印详细的测试结果"""
    print(f"\n{'='*60}")
    print(f"🧪 测试: {test_name}")
    print(f"{'='*60}")
    
    if "error" in result:
        print(f"❌ 错误: {result['error']}")
        return
    
    print(f"✅ 成功: {result.get('success', False)}")
    print(f"🔧 引擎: {result.get('engine', 'N/A')}")
    
    if result.get('text'):
        print(f"📝 识别结果: {result['text']}")
        print(f"📊 置信度: {result.get('confidence', 0):.2f} ({result.get('confidence', 0)*100:.1f}%)")
    
    # 显示警告信息
    if result.get('warning'):
        print(f"⚠️  警告: {result['warning']}")
    
    # 显示低置信度候选结果
    if result.get('low_confidence_candidates'):
        print(f"📋 低置信度候选结果:")
        for i, candidate in enumerate(result['low_confidence_candidates'], 1):
            print(f"   {i}. {candidate['text']} (置信度: {candidate['confidence']:.2f})")
    
    # 显示建议
    if result.get('suggestion'):
        print(f"💡 建议: {result['suggestion']}")
    
    # 显示图像质量分析
    if result.get('image_quality'):
        quality = result['image_quality']
        print(f"📊 图像质量评分: {quality.get('quality_score', 0)}/100")
        if quality.get('suggestions'):
            print(f"💡 质量改进建议: {'; '.join(quality['suggestions'])}")
    
    # 显示格式匹配信息
    if 'plate_format_matched' in result:
        format_status = "✅ 车牌格式" if result['plate_format_matched'] else "⚠️ 通用文本"
        print(f"🎯 格式匹配: {format_status}")

def main():
    """主测试函数"""
    print("🚗 天津仁爱学院车牌识别系统 - 详细结果显示测试")
    print("测试目标: 验证低置信度候选结果的正确显示")
    
    # 测试1: 清晰的车牌图像（应该有高置信度结果）
    clear_image = create_test_plate_image("京A12345")
    result1 = test_ocr_api(clear_image, 'hyperlpr3')
    print_detailed_result(result1, "清晰车牌图像测试")
    
    # 测试2: 模糊的车牌图像（可能产生低置信度结果）
    blurry_image = create_blurry_plate_image("京B56789")
    result2 = test_ocr_api(blurry_image, 'hyperlpr3')
    print_detailed_result(result2, "模糊车牌图像测试（低置信度）")
    
    # 测试3: 使用PaddleOCR测试详细结果
    result3 = test_ocr_api(clear_image, 'paddleocr')
    print_detailed_result(result3, "PaddleOCR详细结果测试")
    
    # 测试4: 使用EasyOCR测试详细结果
    result4 = test_ocr_api(clear_image, 'easyocr')
    print_detailed_result(result4, "EasyOCR详细结果测试")
    
    # 测试现有图片文件
    print(f"\n{'='*60}")
    print("🖼️  测试现有图片文件")
    print(f"{'='*60}")
    
    # 寻找车牌图片
    image_paths = []
    for pattern in ['*.jpg', '*.png', '*.jpeg']:
        image_paths.extend(Path('web').glob(pattern))
    
    if image_paths:
        for i, img_path in enumerate(image_paths[:2]):  # 测试前2张图片
            print(f"\n📸 测试图片: {img_path}")
            
            try:
                image = cv2.imread(str(img_path))
                if image is not None:
                    result = test_ocr_api(image, 'hyperlpr3')
                    print_detailed_result(result, f"真实图片测试 - {img_path.name}")
                else:
                    print("❌ 无法读取图片")
            except Exception as e:
                print(f"❌ 测试异常: {e}")
    else:
        print("❌ 未找到测试图片")
    
    print(f"\n{'='*60}")
    print("✅ 测试完成！")
    print("🎯 前端页面现在应该能显示:")
    print("   - 识别出的车牌号码（如C62N8）")
    print("   - 置信度信息和进度条")
    print("   - 低置信度候选结果列表")
    print("   - 图像质量分析和改进建议")
    print("   - 引擎类型和格式匹配状态")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
