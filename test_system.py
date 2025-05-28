#!/usr/bin/env python3
# test_system.py - 系統測試腳本

import sys
import os

# 測試配置載入
print("🔧 測試配置載入...")
try:
    from config import FOOD_DATABASE, CONSTITUTION_TYPES, CONSTITUTION_QUESTIONS
    print(f"✅ 成功載入食物資料庫，共 {len(FOOD_DATABASE)} 項食物")
    print(f"✅ 成功載入體質類型，共 {len(CONSTITUTION_TYPES)} 種體質")
    print(f"✅ 成功載入問卷，共 {len(CONSTITUTION_QUESTIONS)} 題")
    
    # 顯示前5項食物
    print("\n前5項食物：")
    for i, (name, info) in enumerate(list(FOOD_DATABASE.items())[:5]):
        print(f"  {i+1}. {name}: {info}")
        
except Exception as e:
    print(f"❌ 配置載入失敗: {e}")
    sys.exit(1)

# 測試工具函數
print("\n🔧 測試工具函數...")
try:
    from utils import get_ai_client
    client = get_ai_client()
    if client:
        print("✅ AI 客戶端初始化成功")
    else:
        print("⚠️ AI 客戶端未配置（需要 GROQ_API_KEY）")
except Exception as e:
    print(f"❌ 工具函數測試失敗: {e}")

# 測試食物辨識
print("\n🍎 測試食物辨識模組...")
try:
    from food_recognition import classify_food_image
    from PIL import Image
    import numpy as np
    
    # 創建一個虛擬圖片進行測試
    test_image = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
    result = classify_food_image(test_image)
    print(f"✅ 食物辨識測試成功: {result}")
except Exception as e:
    print(f"❌ 食物辨識測試失敗: {e}")

# 測試體質分析
print("\n🏥 測試體質分析模組...")
try:
    from constitution_analysis import analyze_constitution
    
    # 創建測試答案
    test_answers = ["無特別異常"] * 15 + ["無特別說明"] * 5
    result = analyze_constitution(test_answers)
    
    if "錯誤" in result:
        print(f"⚠️ 體質分析測試結果: {result}")
    else:
        print(f"✅ 體質分析測試成功")
except Exception as e:
    print(f"❌ 體質分析測試失敗: {e}")

# 測試養生建議
print("\n🌿 測試養生建議模組...")
try:
    from health_advice import generate_health_advice
    
    # 創建測試數據
    test_constitution = {"主要體質": "平和質", "分析理由": "測試"}
    test_food = {"辨識食物": "蘋果", "五性屬性": "平性"}
    
    result = generate_health_advice(test_constitution, test_food)
    
    if "錯誤" in result:
        print(f"⚠️ 養生建議測試結果: {result}")
    else:
        print(f"✅ 養生建議測試成功")
except Exception as e:
    print(f"❌ 養生建議測試失敗: {e}")

print("\n🎯 系統測試完成！")
print("\n💡 如要測試完整功能，請設置 GROQ_API_KEY 環境變數")
print("💡 然後運行: python3 app.py") 