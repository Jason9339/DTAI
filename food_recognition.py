# food_recognition.py - 食物辨識模組
import random
import gradio as gr
from typing import Dict
from PIL import Image
from config import FOOD_DATABASE

def classify_food_image(image: Image.Image) -> Dict:
    """
    模擬食物辨識功能
    實際應用中這裡會載入訓練好的 ResNet/CNN/Swin Transformer 模型
    """
    if image is None:
        return {"錯誤": "請上傳食物圖片"}
    
    # 模擬辨識結果 - 實際應用中會使用深度學習模型
    food_names = list(FOOD_DATABASE.keys())
    recognized_food = random.choice(food_names)
    
    food_info = FOOD_DATABASE[recognized_food]
    
    result = {
        "辨識食物": recognized_food,
        "五性屬性": food_info["五性"],
        "歸經": food_info["歸經"],
        "功效": food_info["功效"],
        "信心度": f"{random.randint(85, 98)}%"
    }
    
    return result

def build_food_recognition_page():
    """建立食物辨識頁面"""
    with gr.Column():
        gr.Markdown("## 🍎 食物辨識模組")
        gr.Markdown("上傳食物圖片，系統將辨識食材並提供中醫五性屬性資訊")
        
        with gr.Row():
            with gr.Column():
                food_image = gr.Image(
                    type="pil", 
                    label="請上傳食物照片",
                    height=300
                )
                recognize_btn = gr.Button("🔍 開始辨識", variant="primary")
            
            with gr.Column():
                food_result_display = gr.JSON(label="辨識結果")
        
        def update_food_result(image):
            result = classify_food_image(image)
            return result, result
        
        food_state = gr.State()
        
        recognize_btn.click(
            fn=update_food_result,
            inputs=[food_image],
            outputs=[food_result_display, food_state]
        )
        
        return food_result_display, food_state 