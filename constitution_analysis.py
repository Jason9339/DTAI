# constitution_analysis.py - 體質分析模組
import json
import gradio as gr
import os
from typing import Dict, List
from datetime import datetime
from config import CONSTITUTION_QUESTIONS, CONSTITUTION_TYPES
from utils import get_ai_client

def create_constitution_prompt(answers: List[str]) -> str:
    """創建體質分析的 prompt"""
    if not answers or len(answers) != len(CONSTITUTION_QUESTIONS):
        return ""
    
    # 構建問答對
    qa_pairs = []
    for i, answer in enumerate(answers):
        question = CONSTITUTION_QUESTIONS[i]
        qa_pairs.append(f"問題{i+1}: {question['question']}")
        qa_pairs.append(f"回答: {answer}")
        qa_pairs.append("")
    
    prompt = f"""
你是一位專業的中醫師，請根據以下問卷回答分析使用者的中醫體質類型。

中醫九種體質類型：
1. 平和質：陰陽氣血調和，體質平和
2. 氣虛質：元氣不足，易疲勞乏力
3. 陽虛質：陽氣不足，畏寒怕冷
4. 陰虛質：陰液虧少，虛熱內擾
5. 痰濕質：痰濕凝聚，形體肥胖
6. 濕熱質：濕熱內蘊，面垢油膩
7. 血瘀質：血行不暢，膚色晦暗
8. 氣鬱質：氣機鬱滯，神情抑鬱
9. 特稟質：先天稟賦不足，過敏體質

使用者問卷回答：
{chr(10).join(qa_pairs)}

請根據以上回答，分析使用者的體質類型。請注意：
1. 大多數人都是混合體質，請找出主要體質和次要體質
2. 提供詳細的分析理由
3. 給出具體的養生建議

請以以下 JSON 格式回答：
{{
    "主要體質": "體質名稱",
    "次要體質": "體質名稱（如果有）",
    "體質描述": "詳細描述主要體質特徵",
    "分析理由": "根據問卷回答的具體分析",
    "養生建議": "針對此體質的具體建議",
    "注意事項": "需要特別注意的事項",
    "分析時間": "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
}}
"""
    return prompt

def analyze_constitution_with_llm(answers: List[str]) -> Dict:
    """使用 LLM 分析體質類型"""
    if not answers or len(answers) != len(CONSTITUTION_QUESTIONS):
        return {"錯誤": "請完成所有問題"}
    
    # 檢查是否有空答案
    if any(not answer.strip() for answer in answers):
        return {"錯誤": "請完成所有問題，不能留空"}
    
    try:
        client = get_ai_client()
        if not client:
            return {"錯誤": "AI 服務未配置，請設置 GROQ_API_KEY 環境變數"}
        
        prompt = create_constitution_prompt(answers)
        
        # 調用 Groq API
        response = client.chat.completions.create(
            model="groq:llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "你是一位專業的中醫師，擅長體質分析。請根據問卷回答進行準確的中醫體質分析。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        # 解析回應
        result_text = response.choices[0].message.content
        
        # 嘗試解析 JSON
        try:
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError:
            # 如果不是有效的 JSON，返回原始文本
            return {
                "分析結果": result_text,
                "分析時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
    except Exception as e:
        return {"錯誤": f"分析過程中發生錯誤: {str(e)}"}

def analyze_constitution(answers: List[str]) -> Dict:
    """分析體質類型 - 主函數"""
    return analyze_constitution_with_llm(answers)

def build_constitution_analysis_page():
    """建立體質分析頁面"""
    with gr.Column():
        gr.Markdown("## 🏥 中醫體質分析")
        gr.Markdown("請完成以下20題問卷，系統將使用AI分析您的中醫體質類型")
        
        # API Key 設置
        with gr.Row():
            api_key_input = gr.Textbox(
                label="🔑 Groq API Key",
                placeholder="請輸入您的 Groq API Key（可選，如已設置環境變數則不需要）",
                type="password",
                scale=3
            )
            set_key_btn = gr.Button("設置", scale=1)
        
        # 創建問題組件
        question_components = []
        
        gr.Markdown("### 📋 選擇題（1-15題）")
        for i, q in enumerate(CONSTITUTION_QUESTIONS[:15]):  # 前15題是選擇題
            question_components.append(
                gr.CheckboxGroup(
                    choices=q["options"],
                    label=f"{i+1}. {q['question']}",
                    value=[]
                )
            )
        
        gr.Markdown("### ✍️ 簡答題（16-20題）")
        for i, q in enumerate(CONSTITUTION_QUESTIONS[15:], 15):  # 後5題是簡答題
            question_components.append(
                gr.Textbox(
                    label=f"{i+1}. {q['question']}",
                    placeholder=q["placeholder"],
                    lines=2
                )
            )
        
        def set_api_key(key):
            if key.strip():
                os.environ['GROQ_API_KEY'] = key.strip()
                return "✅ API Key 已設置"
            return "❌ 請輸入有效的 API Key"
        
        set_key_status = gr.Textbox(label="狀態", interactive=False)
        set_key_btn.click(
            fn=set_api_key,
            inputs=[api_key_input],
            outputs=[set_key_status]
        )
        
        analyze_btn = gr.Button("🤖 AI 分析體質", variant="primary", size="lg")
        constitution_result_display = gr.JSON(label="AI 體質分析結果")
        
        def process_answers(*inputs):
            """處理問卷答案"""
            answers = []
            
            # 處理選擇題（可複選）
            for i in range(15):
                selected = inputs[i] if inputs[i] else []
                if selected:
                    answers.append(", ".join(selected))
                else:
                    answers.append("無特別異常")  # 預設答案
            
            # 處理簡答題
            for i in range(15, 20):
                text_answer = inputs[i] if inputs[i] and inputs[i].strip() else "無特別說明"
                answers.append(text_answer)
            
            result = analyze_constitution(answers)
            return result, result
        
        constitution_state = gr.State()
        
        def process_and_update(*inputs):
            """處理問卷答案並更新狀態"""
            answers = []
            
            # 處理選擇題（可複選）
            for i in range(15):
                selected = inputs[i] if inputs[i] else []
                if selected:
                    answers.append(", ".join(selected))
                else:
                    answers.append("無特別異常")  # 預設答案
            
            # 處理簡答題
            for i in range(15, 20):
                text_answer = inputs[i] if inputs[i] and inputs[i].strip() else "無特別說明"
                answers.append(text_answer)
            
            result = analyze_constitution(answers)
            return result, result
        
        analyze_btn.click(
            fn=process_and_update,
            inputs=question_components,
            outputs=[constitution_result_display, constitution_state]
        )
        
        return constitution_result_display, constitution_state 