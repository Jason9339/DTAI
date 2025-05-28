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
            margin: 0 auto !important;
            padding: 20px !important;
        }
        .main-button {
            height: 80px !important;
            font-size: 16px !important;
            margin: 10px !important;
            min-width: 200px !important;
        }
        .step-indicator {
            background: linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .main-content {
            text-align: center;
            max-width: 100%;
        }
        .progress-section {
            text-align: center;
            background: #f8fafc;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .disclaimer-section {
            text-align: center;
            background: #fef7f0;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }
        h1, h2, h3 {
            text-align: center !important;
        }
        .gr-markdown {
            text-align: center;
        }
        .step-row {
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 15px !important;
        }
        .step-column {
            flex: 1 !important;
            min-width: 0 !important;
        }
        """
    ) as app:
        
        # 全局狀態管理
        constitution_result_state = gr.State()
        food_result_state = gr.State()
        current_page = gr.State("home")
        
        # 主頁面
        with gr.Column(visible=True, elem_classes=["main-content"]) as home_page:
            gr.Markdown("""
            # 🏥 中醫食物寒熱辨識與體質分析系統
            
            結合現代AI技術與傳統中醫理論，為您提供個人化的養生建議
            
            ## 📋 使用流程
            """, elem_classes=["main-content"])
            
            with gr.Row(elem_classes=["step-row"]):
                with gr.Column(elem_classes=["step-column"]):
                    gr.Markdown("""
                    <div class="step-indicator">
                    <h3>🔸 第一步：體質分析</h3>
                    <p>完成20題中醫體質問卷，AI將分析您的體質類型</p>
                    </div>
                    """)
                    constitution_btn = gr.Button(
                        "🏥 開始體質分析", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["main-button"]
                    )
                
                with gr.Column(elem_classes=["step-column"]):
                    gr.Markdown("""
                    <div class="step-indicator">
                    <h3>🔸 第二步：食物辨識</h3>
                    <p>上傳食物圖片，系統將辨識食材的中醫屬性</p>
                    </div>
                    """)
                    food_btn = gr.Button(
                        "🍎 食物辨識", 
                        variant="secondary", 
                        size="lg",
                        elem_classes=["main-button"]
                    )
                
                with gr.Column(elem_classes=["step-column"]):
                    gr.Markdown("""
                    <div class="step-indicator">
                    <h3>🔸 第三步：養生建議</h3>
                    <p>基於體質和食物分析，獲得個人化養生建議</p>
                    </div>
                    """)
                    advice_btn = gr.Button(
                        "🌿 養生建議", 
                        variant="secondary", 
                        size="lg",
                        elem_classes=["main-button"]
                    )
            
            # 進度顯示
            progress_display = gr.Markdown("""
            ### 📊 當前進度
            - ⭕ 體質分析：未完成
            - ⭕ 食物辨識：未完成
            - ⭕ 養生建議：未完成
            """, elem_classes=["progress-section"])
            
            gr.Markdown("""
            ---
            💡 **使用說明：**
            1. 建議按順序完成：體質分析 → 食物辨識 → 養生建議
            2. 體質分析需要設置 Groq API Key
            3. 所有功能都可以獨立使用
            
            ⚠️ **免責聲明：** 本系統僅供參考，不能替代專業醫療建議
            """, elem_classes=["disclaimer-section"])
        
        # 體質分析頁面
        with gr.Column(visible=False, elem_classes=["main-content"]) as constitution_page:
            gr.Markdown("# 🏥 中醫體質分析", elem_classes=["main-content"])
            
            back_to_home_1 = gr.Button("🏠 返回主頁", variant="secondary")
            constitution_result_display, constitution_state_internal = build_constitution_analysis_page()
            
            def update_constitution_state(result):
                return result
            
            constitution_state_internal.change(
                fn=update_constitution_state,
                inputs=[constitution_state_internal],
                outputs=[constitution_result_state]
            )
        
        # 食物辨識頁面
        with gr.Column(visible=False, elem_classes=["main-content"]) as food_page:
            gr.Markdown("# 🍎 食物辨識", elem_classes=["main-content"])
            
            back_to_home_2 = gr.Button("🏠 返回主頁", variant="secondary")
            food_result_display, food_state_internal = build_food_recognition_page()
            
            def update_food_state(result):
                return result
            
            food_state_internal.change(
                fn=update_food_state,
                inputs=[food_state_internal],
                outputs=[food_result_state]
            )
        
        # 養生建議頁面
        with gr.Column(visible=False, elem_classes=["main-content"]) as advice_page:
            gr.Markdown("# 🌿 個人化養生建議", elem_classes=["main-content"])
            
            back_to_home_3 = gr.Button("🏠 返回主頁", variant="secondary")
            build_health_advice_page(constitution_result_state, food_result_state)
        
        # 頁面切換函數
        def show_constitution_page():
            return (
                gr.update(visible=False),  # home_page
                gr.update(visible=True),   # constitution_page
                gr.update(visible=False),  # food_page
                gr.update(visible=False),  # advice_page
                "constitution"
            )
        
        def show_food_page():
            return (
                gr.update(visible=False),  # home_page
                gr.update(visible=False),  # constitution_page
                gr.update(visible=True),   # food_page
                gr.update(visible=False),  # advice_page
                "food"
            )
        
        def show_advice_page():
            return (
                gr.update(visible=False),  # home_page
                gr.update(visible=False),  # constitution_page
                gr.update(visible=False),  # food_page
                gr.update(visible=True),   # advice_page
                "advice"
            )
        
        def show_home_page():
            return (
                gr.update(visible=True),   # home_page
                gr.update(visible=False),  # constitution_page
                gr.update(visible=False),  # food_page
                gr.update(visible=False),  # advice_page
                "home"
            )
        
        def update_progress(constitution_result, food_result):
            """更新進度顯示"""
            constitution_status = "✅ 體質分析：已完成" if constitution_result else "⭕ 體質分析：未完成"
            food_status = "✅ 食物辨識：已完成" if food_result else "⭕ 食物辨識：未完成"
            advice_status = "✅ 養生建議：可生成" if (constitution_result and food_result) else "⭕ 養生建議：未完成"
            
            return f"""
            ### 📊 當前進度
            - {constitution_status}
            - {food_status}
            - {advice_status}
            """
        
        # 綁定按鈕事件
        constitution_btn.click(
            fn=show_constitution_page,
            outputs=[home_page, constitution_page, food_page, advice_page, current_page]
        )
        
        food_btn.click(
            fn=show_food_page,
            outputs=[home_page, constitution_page, food_page, advice_page, current_page]
        )
        
        advice_btn.click(
            fn=show_advice_page,
            outputs=[home_page, constitution_page, food_page, advice_page, current_page]
        )
        
        # 返回主頁按鈕
        for back_btn in [back_to_home_1, back_to_home_2, back_to_home_3]:
            back_btn.click(
                fn=show_home_page,
                outputs=[home_page, constitution_page, food_page, advice_page, current_page]
            )
        
        # 更新進度顯示
        constitution_result_state.change(
            fn=update_progress,
            inputs=[constitution_result_state, food_result_state],
            outputs=[progress_display]
        )
        
        food_result_state.change(
            fn=update_progress,
            inputs=[constitution_result_state, food_result_state],
            outputs=[progress_display]
        )
    
    return app

# --------------------------------------------------------------------------
# 啟動應用
# --------------------------------------------------------------------------
if __name__ == "__main__":
    app = build_main_app()
    app.launch(share=True) 