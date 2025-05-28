# utils.py - 工具函數
import aisuite as ai
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def get_ai_client():
    """初始化 aisuite 客戶端"""
    try:
        # 從環境變數或 Gradio 用戶數據獲取 API key
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            return None
        
        client = ai.Client()
        return client
    except Exception as e:
        print(f"AI 客戶端初始化失敗: {e}")
        return None 