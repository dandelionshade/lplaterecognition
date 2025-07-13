#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实图像测试HyperLPR3优化效果
"""

import cv2
import numpy as np
import os
from fix_hyperlpr3 import optimized_hyperlpr3_call

def test_hyperlpr3_with_real_images():
    """使用真实图像测试HyperLPR3"""
    print("🚗 使用真实车牌图像测试HyperLPR3优化效果...")
    
    try:
        # 导入HyperLPR3
        import hyperlpr3 as lpr3
        
        # 初始化识别器
        catcher = lpr3.LicensePlateCatcher()
        print("✅ HyperLPR3 引擎初始化成功")
        
        # 测试图像路径
        test_images = [
            "/Users/zhenzhang/Documents/GitHub/lplaterecognition/web/car2.jpg",
            "/Users/zhenzhang/Documents/GitHub/lplaterecognition/web/car3.jpg", 
            "/Users/zhenzhang/Documents/GitHub/lplaterecognition/web/car4.jpg",
            "/Users/zhenzhang/Documents/GitHub/lplaterecognition/web/car7.jpg"
        ]
        
        print(f"\n🔍 找到 {len(test_images)} 张测试图像")
        
        for i, image_path in enumerate(test_images, 1):
            if not os.path.exists(image_path):
                print(f"❌ 图像不存在: {image_path}")
                continue
                
            print(f"\n--- 测试图像 {i}: {os.path.basename(image_path)} ---")
            
            try:
                # 读取图像
                image = cv2.imread(image_path)
                if image is None:
                    print(f"❌ 无法读取图像: {image_path}")
                    continue
                
                print(f"📷 图像尺寸: {image.shape}")
                
                # 使用原始HyperLPR3方法
                print("🔄 原始HyperLPR3识别...")
                try:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    original_results = catcher(rgb_image)
                    if original_results:
                        for plate in original_results:
                            print(f"  原始结果: {plate[0]} (置信度: {plate[1]:.3f})")
                    else:
                        print("  原始方法未识别出车牌")
                except Exception as e:
                    print(f"  原始方法失败: {e}")
                
                # 使用优化后的方法
                print("🚀 优化HyperLPR3识别...")
                texts, confidences = optimized_hyperlpr3_call(catcher, image)
                
                if texts:
                    for text, conf in zip(texts, confidences):
                        print(f"  ✅ 优化结果: {text} (置信度: {conf:.3f})")
                else:
                    print("  ❌ 优化方法也未识别出车牌")
                
            except Exception as e:
                print(f"❌ 处理图像失败: {e}")
        
        print("\n🏁 真实图像测试完成")
        
    except ImportError:
        print("❌ HyperLPR3 未安装或导入失败")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def debug_hyperlpr3_detection():
    """调试HyperLPR3检测过程"""
    print("\n🔧 调试HyperLPR3检测过程...")
    
    try:
        import hyperlpr3 as lpr3
        
        # 初始化识别器
        catcher = lpr3.LicensePlateCatcher()
        
        # 测试一张图像
        image_path = "/Users/zhenzhang/Documents/GitHub/lplaterecognition/web/car2.jpg"
        
        if os.path.exists(image_path):
            image = cv2.imread(image_path)
            print(f"📷 测试图像: {os.path.basename(image_path)}, 尺寸: {image.shape}")
            
            # 尝试不同的预处理方式
            processes = [
                ("原始BGR", image),
                ("转RGB", cv2.cvtColor(image, cv2.COLOR_BGR2RGB)),
                ("灰度转RGB", cv2.cvtColor(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2RGB)),
                ("缩放2倍", cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), None, fx=2, fy=2))
            ]
            
            for name, processed_image in processes:
                print(f"\n🔄 测试 {name} (尺寸: {processed_image.shape})...")
                try:
                    results = catcher(processed_image)
                    if results:
                        print(f"  ✅ 检测到 {len(results)} 个结果:")
                        for j, plate in enumerate(results):
                            print(f"    {j+1}. {plate[0]} (置信度: {plate[1]:.3f})")
                    else:
                        print("  ❌ 未检测到车牌")
                except Exception as e:
                    print(f"  ❌ 处理失败: {e}")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")

if __name__ == "__main__":
    test_hyperlpr3_with_real_images()
    debug_hyperlpr3_detection()
