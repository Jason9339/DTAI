# constitution_analysis.py - 體質分析模組
import json
import gradio as gr
import os
from typing import Dict, List
from datetime import datetime
from config import CONSTITUTION_QUESTIONS, CONSTITUTION_TYPES, CONSTITUTION_INFO
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
平和體質（健康派）：平和體質的人體形勻稱健壯，面色、膚色潤澤，頭髮稠密有光澤，目光有神，不易疲勞，精力充沛，睡眠、食慾好。個性隨和開朗，對外界環境適應良好。
氣虛體質（氣短派）：體型鬆軟不實，元氣不足，經常感覺疲勞乏力。氣短、講話的聲音低弱，容易出汗，舌邊有齒痕。身體抵抗力較差，容易感冒。性格較為內向。
陽虛體質（怕冷派）：容易精神不振，畏寒、時感手腳冰冷，背部或腰膝部怕冷。進食寒涼的食物容易腸胃不適，容易手足浮腫、腹瀉、陽痿等。個性多沉悶和內向。
陰虛體質（缺水派）：陰虛體質的人經常感到手腳心發熱、面頰潮紅或偏紅、眼睛乾澀、口乾咽燥，而且容易頭暈、耳鳴及失眠，睡眠品質較差。活潑外向好動，但容易性情急躁。
痰濕體質（痰多派）：形體肥胖、腹部肥滿、鬆軟，容易浮腫、血壓較高。容易出汗且多黏膩，嘴裡常有黏膩感，痰多。喜吃甜食，經常感到肢體沉重、易睏倦。性格比較溫和。
濕熱體質（長痘派）：體型中等或偏瘦，身重睏倦，面垢油光，易生粉刺暗瘡，皮膚容易瘙癢。常感到口苦、口臭或嘴裡有異味。脾氣比較急躁，經常有緊張、焦慮的心情。
血瘀體質（長斑派）：血瘀體質的人皮膚粗糙、暗沉，容易有斑點，嘴唇顏色偏暗，舌下靜脈有瘀紫。眼睛血絲較多，牙齦易出血，時常頭痛、腰痛及肩頸僵硬現象。個性容易煩躁及健忘。
氣鬱體質（鬱悶派）：神情抑鬱低沉，容易緊張、焦慮不安，多愁善感。容易胸悶和失眠，常覺得咽喉有東西卡住。常嘆氣、放屁。容易有情緒問題、神經衰弱、失眠等問題。
特稟體質（過敏派）：多有過敏症狀，容易氣喘、咽喉發癢、鼻塞、打噴嚏。皮膚容易發癢，一抓就出現紅抓痕。對藥物、食物、氣味、花粉、季節過敏，對外界環境變化適應差。

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

def format_constitution_result(result: Dict) -> tuple:
    """格式化體質分析結果，返回圖片路徑和格式化的文本"""
    if "錯誤" in result:
        return None, f"❌ 錯誤：{result['錯誤']}"
    
    if "分析結果" in result:
        # 如果返回的是原始文本而非JSON
        return None, f"📋 分析結果：\n{result['分析結果']}"
    
    # 獲取主要體質信息
    main_constitution = result.get("主要體質", "")
    secondary_constitution = result.get("次要體質", "")
    
    # 查找體質圖片
    image_path = None
    display_text = ""
    
    if main_constitution in CONSTITUTION_INFO:
        info = CONSTITUTION_INFO[main_constitution]
        image_path = info["image_path"]
        
        # 構建標題
        title = f"🎯 **{main_constitution} | {info['alias']}（{info['nickname']}）**"
        if secondary_constitution and secondary_constitution in CONSTITUTION_INFO:
            sec_info = CONSTITUTION_INFO[secondary_constitution]
            title += f"\n🔸 次要體質：{secondary_constitution} | {sec_info['alias']}（{sec_info['nickname']}）"
        
        display_text = f"{title}\n\n"
    else:
        display_text = f"🎯 **主要體質：{main_constitution}**\n"
        if secondary_constitution:
            display_text += f"🔸 次要體質：{secondary_constitution}\n"
        display_text += "\n"
    
    # 添加其他分析結果
    if "體質描述" in result:
        display_text += f"📄 **體質描述**\n{result['體質描述']}\n\n"
    
    if "分析理由" in result:
        display_text += f"🔍 **分析理由**\n{result['分析理由']}\n\n"
    
    if "養生建議" in result:
        display_text += f"💡 **養生建議**\n{result['養生建議']}\n\n"
    
    if "注意事項" in result:
        display_text += f"⚠️ **注意事項**\n{result['注意事項']}\n\n"
    
    if "分析時間" in result:
        display_text += f"⏰ **分析時間**：{result['分析時間']}"
    
    return image_path, display_text

def build_constitution_analysis_page():
    """建立體質分析頁面"""
    with gr.Column():
        gr.Markdown("## 🏥 中醫體質分析")
        gr.Markdown("請完成以下20題問卷，系統將使用AI分析您的中醫體質類型")
        
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
        
        analyze_btn = gr.Button("🤖 AI 分析體質", variant="primary", size="lg")
        
        # 結果顯示區域 - 使用Row布局
        with gr.Row(visible=False) as result_row:
            with gr.Column(scale=2):
                constitution_image = gr.Image(
                    label="體質圖像", 
                    height=400,
                    width=400,
                    show_download_button=False,
                    container=False
                )
            with gr.Column(scale=3):
                constitution_text = gr.Markdown(
                    label="分析結果",
                    value="",
                    container=False
                )
        
        # 原始JSON結果（隱藏，僅供調試）
        constitution_result_display = gr.JSON(label="詳細分析數據", visible=False)
        
        def process_and_display(*inputs):
            """處理問卷答案並顯示結果"""
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
            
            # 分析體質
            result = analyze_constitution(answers)
            
            # 格式化結果
            image_path, formatted_text = format_constitution_result(result)
            
            # 更新顯示
            updates = []
            
            # 如果有圖片，顯示圖片，否則顯示佔位圖
            if image_path and os.path.exists(image_path):
                updates.extend([
                    gr.update(value=image_path, visible=True),  # constitution_image
                    gr.update(value=formatted_text, visible=True),  # constitution_text
                    gr.update(visible=True),  # result_row
                    result  # constitution_result_display
                ])
            else:
                updates.extend([
                    gr.update(value=None, visible=False),  # constitution_image
                    gr.update(value=formatted_text, visible=True),  # constitution_text
                    gr.update(visible=True),  # result_row
                    result  # constitution_result_display
                ])
            
            return updates
        
        constitution_state = gr.State()
        
        analyze_btn.click(
            fn=process_and_display,
            inputs=question_components,
            outputs=[constitution_image, constitution_text, result_row, constitution_result_display]
        )
        
        return constitution_result_display, constitution_state 