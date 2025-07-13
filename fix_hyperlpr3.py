#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HyperLPR3 引擎优化修复脚本
用于解决HyperLPR3识别不准确的问题
"""

import cv2
import numpy as np
import re
from typing import List, Dict, Tuple, Optional, Any

def prepare_image_for_hyperlpr3(image: np.ndarray, force_rgb: bool = False) -> np.ndarray:
    """为HyperLPR3准备图像格式"""
    # 确保图像是正确的色彩空间
    if len(image.shape) == 2:
        # 灰度图转BGR
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif len(image.shape) == 3 and image.shape[2] == 4:
        # RGBA转BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    
    # 根据参数决定是否转换为RGB
    if force_rgb and len(image.shape) == 3 and image.shape[2] == 3:
        # 假设输入是BGR，转换为RGB
        result_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        # 保持原格式（通常是BGR）
        result_image = image
    
    # 确保数据类型正确
    if result_image.dtype != np.uint8:
        result_image = result_image.astype(np.uint8)
    
    return result_image

def optimize_image_size_for_plate_detection(image: np.ndarray) -> np.ndarray:
    """优化图像尺寸以提高车牌检测效果"""
    height, width = image.shape[:2]
    
    # HyperLPR3推荐的最小尺寸
    min_height = 240
    min_width = 320
    
    if height < min_height or width < min_width:
        # 计算缩放比例
        scale_h = min_height / height if height < min_height else 1.0
        scale_w = min_width / width if width < min_width else 1.0
        scale = max(scale_h, scale_w)
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # 使用高质量插值
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    return image

def enhance_image_for_hyperlpr3(image: np.ndarray) -> np.ndarray:
    """专门为HyperLPR3优化的图像预处理"""
    
    # 如果是RGB，转换为BGR进行OpenCV处理
    if len(image.shape) == 3 and image.shape[2] == 3:
        # 假设输入是RGB，转换为BGR
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        bgr_image = image
    
    # 1. 亮度和对比度调整
    lab = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # CLAHE对比度增强
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # 2. 去噪
    denoised = cv2.fastNlMeansDenoising(enhanced)
    
    # 3. 锐化
    kernel = np.array([[-1,-1,-1],
                       [-1, 9,-1],
                       [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    # 转换回RGB
    return cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB)

def validate_hyperlpr3_result(plates: List[Any]) -> List[Dict[str, Any]]:
    """验证HyperLPR3识别结果的有效性"""
    valid_plates = []
    
    if not plates:
        return valid_plates
    
    for plate in plates:
        if plate and len(plate) >= 2:
            plate_no = str(plate[0]) if plate[0] else ''
            confidence = float(plate[1]) if isinstance(plate[1], (int, float)) else 0.0
            
            # 基本格式验证
            if len(plate_no) >= 6:
                # 中国车牌号格式验证
                pattern = r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-Z0-9]{4,5}$'
                if re.match(pattern, plate_no):
                    valid_plates.append({
                        'text': plate_no,
                        'confidence': confidence,
                        'bbox': plate[2] if len(plate) > 2 else None
                    })
                else:
                    # 即使格式不完全匹配，如果置信度足够高也保留
                    if confidence > 0.5:
                        valid_plates.append({
                            'text': plate_no,
                            'confidence': confidence,
                            'bbox': plate[2] if len(plate) > 2 else None,
                            'warning': 'format_mismatch'
                        })
    
    return valid_plates

def multi_scale_hyperlpr3_detection(catcher: Any, image: np.ndarray) -> List[Dict[str, Any]]:
    """多尺度HyperLPR3检测以提高识别率"""
    results = []
    
    # 原始尺寸
    try:
        plates = catcher(image)
        if plates:
            results.extend(validate_hyperlpr3_result(plates))
    except Exception as e:
        print(f"原始尺寸检测失败: {e}")
    
    # 放大1.5倍
    try:
        scaled_up = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        plates = catcher(scaled_up)
        if plates:
            results.extend(validate_hyperlpr3_result(plates))
    except Exception as e:
        print(f"放大检测失败: {e}")
    
    # 放大2倍
    try:
        scaled_up2 = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        plates = catcher(scaled_up2)
        if plates:
            results.extend(validate_hyperlpr3_result(plates))
    except Exception as e:
        print(f"放大2倍检测失败: {e}")
    
    # 缩小0.8倍
    try:
        scaled_down = cv2.resize(image, None, fx=0.8, fy=0.8, interpolation=cv2.INTER_AREA)
        plates = catcher(scaled_down)
        if plates:
            results.extend(validate_hyperlpr3_result(plates))
    except Exception as e:
        print(f"缩小检测失败: {e}")
    
    # 去重并返回最佳结果
    if results:
        # 按置信度排序
        results.sort(key=lambda x: x['confidence'], reverse=True)
        # 去除重复结果
        unique_results = []
        seen = set()
        for result in results:
            if result['text'] not in seen:
                unique_results.append(result)
                seen.add(result['text'])
        return unique_results[:3]  # 最多返回3个结果
    
    return []

def robust_hyperlpr3_recognition(catcher: Any, original_image: np.ndarray) -> Optional[Dict[str, Any]]:
    """鲁棒的HyperLPR3识别，包含多种策略"""
    
    strategies = [
        ("原始图像", lambda img: img),
        ("尺寸优化", optimize_image_size_for_plate_detection),
        ("图像增强", enhance_image_for_hyperlpr3),
        ("组合优化", lambda img: enhance_image_for_hyperlpr3(optimize_image_size_for_plate_detection(img)))
    ]
    
    best_result = None
    best_confidence = 0
    all_results = []
    
    for strategy_name, preprocess_func in strategies:
        try:
            processed_image = preprocess_func(original_image)
            rgb_image = prepare_image_for_hyperlpr3(processed_image)
            
            results = multi_scale_hyperlpr3_detection(catcher, rgb_image)
            
            if results:
                for result in results:
                    result['strategy'] = strategy_name
                    all_results.append(result)
                    
                    if result['confidence'] > best_confidence:
                        best_result = result
                        best_confidence = result['confidence']
                        print(f"✅ {strategy_name} 获得更好结果: {best_result['text']} (置信度: {best_confidence:.3f})")
                        
                        # 如果置信度足够高，可以考虑提前返回
                        if best_confidence > 0.9:
                            break
                            
        except Exception as e:
            print(f"❌ {strategy_name} 失败: {e}")
            continue
    
    # 如果有多个结果，进行额外验证
    if len(all_results) > 1:
        # 统计最频繁出现的车牌号
        text_counts = {}
        for result in all_results:
            text = result['text']
            if text in text_counts:
                text_counts[text]['count'] += 1
                text_counts[text]['max_confidence'] = max(text_counts[text]['max_confidence'], result['confidence'])
            else:
                text_counts[text] = {'count': 1, 'max_confidence': result['confidence']}
        
        # 如果某个车牌号出现多次且置信度不错，优先选择
        for text, stats in text_counts.items():
            if stats['count'] >= 2 and stats['max_confidence'] > 0.3:
                # 找到对应的最佳结果
                for result in all_results:
                    if result['text'] == text and result['confidence'] == stats['max_confidence']:
                        print(f"🎯 多策略验证选择: {text} (出现{stats['count']}次, 最高置信度: {stats['max_confidence']:.3f})")
                        return result
    
    return best_result

def optimized_hyperlpr3_call(catcher: Any, image: np.ndarray) -> Tuple[List[str], List[float]]:
    """优化的HyperLPR3调用函数，用于替换main.py中的原始调用"""
    
    try:
        # 使用鲁棒识别
        result = robust_hyperlpr3_recognition(catcher, image)
        
        if result:
            return [result['text']], [result['confidence']]
        else:
            print("⚠️ HyperLPR3 未识别出任何车牌")
            return [], []
            
    except Exception as e:
        print(f"❌ HyperLPR3 识别过程出错: {e}")
        return [], []

# 测试函数
def test_optimized_hyperlpr3():
    """测试优化后的HyperLPR3"""
    print("🧪 测试优化后的HyperLPR3引擎...")
    
    try:
        # 导入HyperLPR3
        import hyperlpr3 as lpr3
        
        # 初始化识别器
        catcher = lpr3.LicensePlateCatcher()
        print("✅ HyperLPR3 引擎初始化成功")
        
        # 创建测试图像
        from PIL import Image, ImageDraw, ImageFont
        import requests
        
        def create_test_plate_image(plate_text: str, width: int = 400, height: int = 150) -> np.ndarray:
            """创建测试车牌图像"""
            # 创建白色背景
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # 绘制车牌背景（蓝色）
            plate_x, plate_y = 50, 30
            plate_w, plate_h = 300, 90
            draw.rectangle([plate_x, plate_y, plate_x + plate_w, plate_y + plate_h], fill='#0066CC')
            
            # 添加车牌号文字（白色）
            try:
                # 尝试使用较大字体
                font_size = 36
                font = ImageFont.load_default()
                
                # 计算文字位置
                text_bbox = draw.textbbox((0, 0), plate_text, font=font)
                text_w = text_bbox[2] - text_bbox[0]
                text_h = text_bbox[3] - text_bbox[1]
                text_x = plate_x + (plate_w - text_w) // 2
                text_y = plate_y + (plate_h - text_h) // 2
                
                draw.text((text_x, text_y), plate_text, fill='white', font=font)
                
            except Exception as e:
                print(f"字体加载失败，使用默认方式: {e}")
                draw.text((plate_x + 30, plate_y + 30), plate_text, fill='white')
            
            # 转换为numpy数组
            img_array = np.array(img)
            return img_array
        
        # 测试车牌
        test_plates = ["京A12345", "沪B88888", "粤C99999", "川D12345"]
        
        print("\n🔍 开始测试各种车牌...")
        
        for plate_text in test_plates:
            print(f"\n--- 测试车牌: {plate_text} ---")
            
            # 创建测试图像
            test_image = create_test_plate_image(plate_text)
            
            # 使用优化的识别
            texts, confidences = optimized_hyperlpr3_call(catcher, test_image)
            
            if texts:
                for text, conf in zip(texts, confidences):
                    print(f"🎯 识别结果: {text} (置信度: {conf:.3f})")
                    if text == plate_text:
                        print("✅ 识别正确！")
                    else:
                        print(f"❌ 识别错误，期望: {plate_text}")
            else:
                print("❌ 未识别出车牌")
        
        print("\n✅ 优化测试完成")
        
    except ImportError:
        print("❌ HyperLPR3 未安装或导入失败")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_optimized_hyperlpr3()
