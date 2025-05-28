# health_advice.py - 養生建議生成模組
import json
import gradio as gr
from typing import Dict
from utils import get_ai_client

def generate_health_advice_with_llm(constitution_result: Dict, food_result: Dict) -> str:
    """使用 LLM 生成個人化養生建議"""
    if not constitution_result or not food_result:
        return "⚠️ 請先完成體質分析和食物辨識"
    
    try:
        client = get_ai_client()
        if not client:
            return "❌ AI 服務未配置，請設置 GROQ_API_KEY 環境變數"
        
        # 構建 prompt
        constitution_info = json.dumps(constitution_result, ensure_ascii=False, indent=2)
        food_info = json.dumps(food_result, ensure_ascii=False, indent=2)
        
        prompt = f"""
你是一位專業的中醫師，請根據使用者的體質分析結果和食物辨識結果，生成個人化的養生建議。

體質分析結果：
{constitution_info}

食物辨識結果：
{food_info}

請提供以下內容：
1. 針對此體質與食物的具體飲食建議
2. 需要避免的食物或行為
3. 推薦的其他食物搭配

請以清晰的 Markdown 格式回答，內容要專業且實用。
"""
        
        response = client.chat.completions.create(
            model="groq/llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "你是一位經驗豐富的中醫師，擅長根據體質特點提供個人化養生建議。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=2000
        )
        
        advice = response.choices[0].message.content
        
        # 添加免責聲明
        advice += "\n\n---\n⚠️ **免責聲明：** 本建議僅供參考，不能替代專業醫療建議。如有健康問題，請諮詢合格的中醫師。"
        
        return advice
        
    except Exception as e:
        return f"❌ 生成建議時發生錯誤: {str(e)}"

def generate_health_advice(constitution_result: Dict, food_result: Dict) -> str:
    """生成個人化養生建議 - 主函數"""
    return generate_health_advice_with_llm(constitution_result, food_result)

def build_health_advice_page(constitution_result_state, food_result_state):
    """建立養生建議頁面"""
    with gr.Column():
        gr.Markdown("## 🌿 個人化養生建議")
        gr.Markdown("基於您的體質分析和食物辨識結果，AI將生成個人化養生建議")
        
        generate_advice_btn = gr.Button("🌿 生成養生建議", variant="primary", size="lg")
        advice_output = gr.Markdown(label="養生建議")
        
        def get_advice(constitution_result, food_result):
            if not constitution_result:
                return "⚠️ 請先完成體質分析"
            if not food_result:
                return "⚠️ 請先完成食物辨識"
            return generate_health_advice(constitution_result, food_result)
        
        generate_advice_btn.click(
            fn=get_advice,
            inputs=[constitution_result_state, food_result_state],
            outputs=[advice_output]
        )
        
        return advice_output 