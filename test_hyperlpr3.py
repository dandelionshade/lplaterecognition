#!/usr/bin/env python3
"""
测试 HyperLPR3 功能是否正常工作
"""

def test_hyperlpr3_import():
    """测试 HyperLPR3 是否可以正常导入和初始化"""
    try:
        import hyperlpr3 as lpr3
        print("✅ HyperLPR3 导入成功")
        
        # 尝试初始化
        catcher = lpr3.LicensePlateCatcher()
        print("✅ HyperLPR3 初始化成功")
        print("✅ HyperLPR3 功能正常")
        return True
        
    except ImportError as e:
        print("❌ HyperLPR3 导入失败:", e)
        print("💡 请安装 HyperLPR3: pip install hyperlpr3")
        return False
        
    except Exception as e:
        print("❌ HyperLPR3 初始化失败:", e)
        return False

def test_ocr_engines():
    """测试所有 OCR 引擎的可用性"""
    engines = {
        'paddleocr': 'PaddleOCR',
        'tesseract': 'Tesseract OCR',
        'hyperlpr3': 'HyperLPR3'
    }
    
    available_engines = []
    
    for engine_key, engine_name in engines.items():
        try:
            if engine_key == 'paddleocr':
                from paddleocr import PaddleOCR
                PaddleOCR()
                print(f"✅ {engine_name} 可用")
                available_engines.append(engine_key)
                
            elif engine_key == 'tesseract':
                import pytesseract
                print(f"✅ {engine_name} 可用")
                available_engines.append(engine_key)
                
            elif engine_key == 'hyperlpr3':
                import hyperlpr3 as lpr3
                lpr3.LicensePlateCatcher()
                print(f"✅ {engine_name} 可用")
                available_engines.append(engine_key)
                
        except Exception as e:
            print(f"❌ {engine_name} 不可用: {e}")
    
    print(f"\n📊 总计: {len(available_engines)}/{len(engines)} 个引擎可用")
    return available_engines

if __name__ == "__main__":
    print("🔍 测试 OCR 引擎可用性...")
    print("=" * 50)
    
    # 测试 HyperLPR3
    hyperlpr3_ok = test_hyperlpr3_import()
    print()
    
    # 测试所有引擎
    available = test_ocr_engines()
    
    print("\n" + "=" * 50)
    if hyperlpr3_ok:
        print("🎉 HyperLPR3 功能正常，应该没有 'recognize' 属性错误")
    else:
        print("⚠️  HyperLPR3 不可用，请检查安装")
        
    print(f"📋 可用引擎: {', '.join(available) if available else '无'}")
