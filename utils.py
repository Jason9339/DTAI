# utils.py - 工具函數
import aisuite as ai
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def get_ai_client():
    """初始化 aisuite 客戶端"""
    try:
        # 優先從環境變數獲取 API key
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if not groq_api_key:
            print("錯誤：GROQ API Key 未設置。請在 .env 文件或環境變數中設置它。")
            return None
        
        client = ai.Client() # aisuite Client 會自動從環境變數讀取
        print("AI 客戶端初始化成功。")
        return client
    except Exception as e:
        print(f"AI 客戶端初始化失敗: {e}")
        return None 