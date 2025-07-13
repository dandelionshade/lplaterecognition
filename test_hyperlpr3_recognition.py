#!/usr/bin/env python3
"""
HyperLPR3 车牌识别功能验证脚本
"""

import requests
import json
import base64
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_license_plate_image(plate_text="京A12345"):
    """创建一个模拟车牌图像"""
    # 创建蓝色车牌背景 (中国标准车牌蓝色)
    width, height = 280, 80
    image = Image.new('RGB', (width, height), color=(0, 83, 159))  # 中国车牌蓝色
    draw = ImageDraw.Draw(image)
    
    # 添加白色边框
    draw.rectangle([2, 2, width-3, height-3], outline='white', width=2)
    
    # 使用白色文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", 36)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
    
    # 绘制车牌号码
    text_bbox = draw.textbbox((0, 0), plate_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), plate_text, fill='white', font=font)
    
    # 转换为numpy数组
    return np.array(image)

def create_car_with_plate_image():
    """创建一个包含车牌的车辆图像"""
    # 创建一个模拟的车辆图像
    car_width, car_height = 400, 300
    car_image = np.ones((car_height, car_width, 3), dtype=np.uint8) * 128  # 灰色背景
    
    # 创建车牌
    plate_img = create_license_plate_image()
    plate_h, plate_w = plate_img.shape[:2]
    
    # 将车牌放置在图像下方中央
    start_y = car_height - plate_h - 20
    start_x = (car_width - plate_w) // 2
    
    # 添加车牌到车辆图像
    car_image[start_y:start_y+plate_h, start_x:start_x+plate_w] = plate_img
    
    return car_image

def image_to_base64(image):
    """将图像转换为base64编码"""
    # 转换为PIL图像
    if isinstance(image, np.ndarray):
        pil_image = Image.fromarray(image)
    else:
        pil_image = image
    
    # 保存到内存缓冲区
    from io import BytesIO
    buffer = BytesIO()
    pil_image.save(buffer, format='PNG')
    
    # 编码为base64
    import base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_base64

def test_hyperlpr3_recognition():
    """测试HyperLPR3车牌识别功能"""
    print("🚗 测试HyperLPR3车牌识别功能")
    print("=" * 50)
    
    # 创建测试图像
    print("📷 创建测试车牌图像...")
    test_cases = [
        ("京A12345", "标准蓝牌"),
        ("沪B88888", "上海蓝牌"),
        ("粤C99999", "广东蓝牌")
    ]
    
    base_url = "http://127.0.0.1:8080"
    
    for plate_text, description in test_cases:
        print(f"\n🔍 测试 {description}: {plate_text}")
        
        # 创建包含车牌的图像
        car_image = create_car_with_plate_image()
        
        # 将车牌号码添加到图像中
        plate_img = create_license_plate_image(plate_text)
        car_h, car_w = car_image.shape[:2]
        plate_h, plate_w = plate_img.shape[:2]
        
        start_y = car_h - plate_h - 20
        start_x = (car_w - plate_w) // 2
        car_image[start_y:start_y+plate_h, start_x:start_x+plate_w] = plate_img
        
        # 转换为base64
        image_base64 = image_to_base64(car_image)
        
        try:
            # 测试HyperLPR3识别
            response = requests.post(
                f"{base_url}/api/ocr-simple",
                json={
                    "image": image_base64,
                    "engine": "hyperlpr3"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    recognized_text = result.get('text', '未识别')
                    confidence = result.get('confidence', 0)
                    
                    print(f"  ✅ 识别成功: {recognized_text}")
                    print(f"  📊 置信度: {confidence:.2f}")
                    print(f"  🎯 准确性: {'✅ 正确' if plate_text in recognized_text else '❌ 错误'}")
                    
                    if 'plates' in result:
                        print(f"  🚗 检测到 {len(result['plates'])} 个车牌")
                else:
                    print(f"  ❌ 识别失败: {result.get('error', '未知错误')}")
            else:
                print(f"  ❌ API错误: HTTP {response.status_code}")
                print(f"  📝 响应: {response.text}")
                
        except Exception as e:
            print(f"  💥 异常错误: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 HyperLPR3测试完成")

def test_hyperlpr3_engine_status():
    """测试HyperLPR3引擎状态"""
    print("🔧 检查HyperLPR3引擎状态...")
    
    try:
        response = requests.get("http://127.0.0.1:8080/api/ocr-engines", timeout=10)
        if response.status_code == 200:
            data = response.json()
            hyperlpr3_info = data['engines'].get('hyperlpr3', {})
            
            if hyperlpr3_info.get('available'):
                print("✅ HyperLPR3引擎状态: 可用")
                print(f"📋 描述: {hyperlpr3_info.get('description', '')}")
                return True
            else:
                print("❌ HyperLPR3引擎状态: 不可用")
                print(f"🚫 错误: {hyperlpr3_info.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ 无法获取引擎状态: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 连接失败: {e}")
        return False

if __name__ == "__main__":
    print("🎯 HyperLPR3车牌识别引擎验证")
    print("=" * 60)
    
    # 1. 检查引擎状态
    engine_ok = test_hyperlpr3_engine_status()
    
    if engine_ok:
        print("\n")
        # 2. 进行实际识别测试
        test_hyperlpr3_recognition()
    else:
        print("\n❌ HyperLPR3引擎不可用，跳过识别测试")
        print("\n💡 解决建议:")
        print("   1. 确保已安装HyperLPR3: pip install hyperlpr3")
        print("   2. 检查服务器是否正常启动")
        print("   3. 查看服务器日志中的错误信息")
