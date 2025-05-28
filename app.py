# app.py - 主應用程式
import gradio as gr
from food_recognition import build_food_recognition_page
from constitution_analysis import build_constitution_analysis_page
from health_advice import build_health_advice_page

def build_main_app():
    """建立主應用程式"""
    with gr.Blocks(
        title="中醫食物寒熱辨識與體質分析系統",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        """
    ) as app:
        
        gr.Markdown("""
        # 🏥 中醫食物寒熱辨識與體質分析系統
        
        結合現代AI技術與傳統中醫理論，為您提供個人化的養生建議
        """)
        
        with gr.Tabs():
            # Tab 1: 食物辨識
            with gr.Tab("🍎 食物辨識"):
                food_result_display, food_result_state = build_food_recognition_page()
            
            # Tab 2: 體質分析
            with gr.Tab("🏥 體質分析"):
                constitution_result_display, constitution_result_state = build_constitution_analysis_page()
            
            # Tab 3: 養生建議
            with gr.Tab("🌿 養生建議"):
                build_health_advice_page(constitution_result_state, food_result_state)
        
        gr.Markdown("""
        ---
        💡 **使用說明：**
        1. 先在「食物辨識」頁面上傳食物圖片進行辨識
        2. 在「體質分析」頁面設置 API Key 並完成20題問卷
        3. 在「養生建議」頁面獲得 AI 生成的個人化建議
        
        ⚠️ **免責聲明：** 本系統僅供參考，不能替代專業醫療建議
        """)
    
    return app

# --------------------------------------------------------------------------
# 啟動應用
# --------------------------------------------------------------------------
if __name__ == "__main__":
    app = build_main_app()
    app.launch(share=True) 