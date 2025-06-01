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
    """格式化體質分析結果，返回圖片路徑、標題文本和詳細內容文本"""
    if "錯誤" in result:
        return None, f"❌ 錯誤：{result['錯誤']}", ""
    
    if "分析結果" in result:
        # 如果返回的是原始文本而非JSON
        return None, f"📋 分析結果：\n{result['分析結果']}", ""
    
    # 獲取主要體質信息
    main_constitution = result.get("主要體質", "")
    secondary_constitution = result.get("次要體質", "")
    
    # 查找體質圖片
    image_path = None
    title_text = ""
    details_text = ""
    
    if main_constitution in CONSTITUTION_INFO:
        info = CONSTITUTION_INFO[main_constitution]
        image_path = info["image_path"]
        
        # 簡化的標題區域（只顯示主要體質）- 添加外框容器
        title_text = f"""
<div style="background: #FFFFFF; padding: 20px; border-radius: 25px; border: 1px solid rgba(106, 153, 78, 0.2); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);">
    <div style="background: linear-gradient(135deg, #6A9A4E 0%, #8FBC8F 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(106, 154, 78, 0.3);">
        <div style="font-size: 2.2rem; font-weight: 700; margin-bottom: 15px;">
             您的體質類型
        </div>
        <div style="font-size: 2rem; font-weight: 600; margin-bottom: 10px;">
            {main_constitution}
        </div>
        <div style="font-size: 1.3rem; opacity: 0.9;">
            {info['alias']} （{info['nickname']}）
        </div>
    </div>
</div>
"""
    else:
        # 沒有找到體質信息的情況 - 添加外框容器
        title_text = f"""
<div style="background: #FFFFFF; padding: 20px; border-radius: 25px; border: 1px solid rgba(106, 153, 78, 0.2); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);">
    <div style="background: linear-gradient(135deg, #6A9A4E 0%, #8FBC8F 100%); color: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(106, 154, 78, 0.3);">
        <div style="font-size: 2.2rem; font-weight: 700; margin-bottom: 15px;">
            您的體質分析結果
        </div>
        <div style="font-size: 1.8rem; font-weight: 600;">
            {main_constitution}
        </div>
    </div>
</div>
"""
    
    # 構建詳細分析內容（顯示在下方）
    content_sections = []
    
    if "體質描述" in result:
        content_sections.append(f"""
<div style="background: #FFFFFF; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid #6A9A4E; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);">
    <h3 style="color: #4A6741; font-size: 1.4rem; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center;">
        <span style="background: #6A9A4E; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-size: 1.1rem;"></span>
        體質描述
    </h3>
    <div style="color: #1e293b; line-height: 1.7; font-size: 1.05rem;">
        {result['體質描述']}
    </div>
</div>
""")
    
    if "分析理由" in result:
        content_sections.append(f"""
<div style="background: #FFFFFF; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 5px solid #8FBC8F; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);">
    <h3 style="color: #4A6741; font-size: 1.4rem; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center;">
        <span style="background: #8FBC8F; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-size: 1.1rem;"></span>
        分析理由
    </h3>
    <div style="color: #1e293b; line-height: 1.7; font-size: 1.05rem;">
        {result['分析理由']}
    </div>
</div>
""")
    
    if "養生建議" in result:
        content_sections.append(f"""
<div style="background: linear-gradient(135deg, #F0F8F0 0%, #FFFFFF 100%); padding: 25px; border-radius: 15px; margin-bottom: 20px; border: 2px solid rgba(106, 153, 78, 0.2); box-shadow: 0 6px 20px rgba(106, 153, 78, 0.1);">
    <h3 style="color: #4A6741; font-size: 1.4rem; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center;">
        <span style="background: linear-gradient(135deg, #D4AF37 0%, #F9A826 100%); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-size: 1.1rem;"></span>
        養生建議
    </h3>
    <div style="color: #1e293b; line-height: 1.7; font-size: 1.05rem; background: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid rgba(106, 153, 78, 0.1);">
        {result['養生建議']}
    </div>
</div>
""")
    
    if "注意事項" in result:
        content_sections.append(f"""
<div style="background: linear-gradient(135deg, #FFF8F5 0%, #FFFFFF 100%); padding: 25px; border-radius: 15px; margin-bottom: 20px; border: 2px solid rgba(239, 68, 68, 0.2); box-shadow: 0 6px 20px rgba(239, 68, 68, 0.1);">
    <h3 style="color: #DC2626; font-size: 1.4rem; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center;">
        <span style="background: linear-gradient(135deg, #EF4444 0%, #F87171 100%); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-size: 1.1rem;"></span>
        注意事項
    </h3>
    <div style="color: #1e293b; line-height: 1.7; font-size: 1.05rem; background: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.1);">
        {result['注意事項']}
    </div>
</div>
""")
    
    # 時間戳
    if "分析時間" in result:
        content_sections.append(f"""
<div style="background: #F8FAFC; padding: 20px; border-radius: 12px; text-align: center; margin-top: 25px; border: 1px solid #E2E8F0;">
    <div style="color: #64748B; font-size: 0.95rem; font-weight: 500;">
        <span style="margin-right: 8px;"></span>
        分析完成時間：{result['分析時間']}
    </div>
</div>
""")
    
    # 組合詳細內容
    details_text = "\n".join(content_sections)
    
    return image_path, title_text, details_text

def build_constitution_analysis_page():
    """建立體質分析頁面"""
    
    # 優化的CSS樣式
    gr.HTML("""
    <style>
        /* ===== 基本容器重置 ===== */
        .constitution-analysis-container .gradio-container,
        .constitution-analysis-container .svelte-phx28p,
        .constitution-analysis-container > div,
        .constitution-analysis-container .gr-column {
            padding: 0 !important;
            margin: 0 !important;
            gap: 0 !important;
        }
        
        /* ===== 問卷整體容器 ===== */
        .questionnaire-main-container {
            background: linear-gradient(135deg, #F8FBF6 0%, #FEFEFE 100%);
            border-radius: 25px;
            padding: 40px;
            margin: 20px 0;
            border: 2px solid rgba(106, 153, 78, 0.2);
            box-shadow: 0 15px 40px rgba(106, 153, 78, 0.15);
            position: relative;
            overflow: hidden;
        }
        
        .questionnaire-main-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 25% 25%, rgba(106, 153, 78, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 75% 75%, rgba(212, 175, 55, 0.03) 0%, transparent 40%);
            border-radius: 25px;
            z-index: 0;
        }
        
        .questionnaire-main-container > * {
            position: relative;
            z-index: 1;
        }
        
        /* ===== 問卷標題區域 ===== */
        .questionnaire-header {
            text-align: center;
            margin-bottom: 35px;
            padding: 25px;
            background: linear-gradient(135deg, #E8F5E8 0%, #F0F8F0 100%);
            border-radius: 20px;
            border: 1px solid rgba(106, 153, 78, 0.2);
        }
        
        .questionnaire-header h2 {
            color: #4A6741 !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            margin-bottom: 15px !important;
            margin-top: 0 !important;
        }
        
        .questionnaire-header p {
            color: #5A7A4A !important;
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
            margin: 0 !important;
        }
        
        /* ===== 問卷分組標題 ===== */
        .questionnaire-group-title {
            background: linear-gradient(135deg, #6A9A4E 0%, #5A8A3E 100%);
            color: white !important;
            padding: 20px 25px;
            margin: 35px 0 20px 0;
            border-radius: 15px;
            font-size: 1.3rem !important;
            font-weight: 600 !important;
            text-align: center;
            box-shadow: 0 8px 25px rgba(106, 154, 78, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .questionnaire-group-title::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: shimmer 3s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .questionnaire-group-title .group-icon {
            font-size: 1.5rem;
            margin-right: 10px;
        }
        
        .questionnaire-group-title .group-description {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 5px;
            font-weight: 400;
        }
        
        /* ===== 問題容器 ===== */
        .question-container {
            background: #FFFFFF;
            border-radius: 18px;
            padding: 25px;
            margin: 15px 0;
            border: 2px solid rgba(106, 153, 78, 0.1);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
            position: relative;
            overflow: hidden;
        }
        
        .question-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(180deg, #6A9A4E 0%, #8FBC8F 100%);
        }
        
        /* ===== 問題標題樣式 ===== */
        .gr-checkbox-group fieldset legend,
        .gr-textbox > label,
        .constitution-question fieldset legend,
        .constitution-textbox > label {
            color: #1e293b !important;
            font-weight: 600 !important;
            font-size: 1.25rem !important;
            line-height: 1.5 !important;
            margin-bottom: 20px !important;
            padding: 0 !important;
            display: block !important;
        }
        
        /* ===== CheckboxGroup 優化 ===== */
        .gr-checkbox-group fieldset {
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        .gr-checkbox-group .wrap {
            gap: 12px !important;
            margin-top: 10px !important;
        }
        
        /* Checkbox 選項樣式 - 強化優先級 */
        .gr-checkbox-group label:not([data-testid]),
        .checkbox-group label:not([data-testid]),
        [data-testid*="checkbox"] label:not([data-testid]),
        .gr-checkbox-group .wrap label,
        .checkbox-group .wrap label,
        .gr-checkbox-group div label,
        .checkbox-group div label {
            color: #374151 !important;
            font-weight: 400 !important;
            font-size: 0.9rem !important;
            line-height: 1.4 !important;
            margin: 0 !important;
            padding: 15px 20px !important;
            border-radius: 12px !important;
            transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
            border: 2px solid #E5E7EB !important;
            background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%) !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            min-height: 56px !important;
            box-sizing: border-box !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        /* 特別針對選項文字的強化設定 */
        .gr-checkbox-group label span,
        .checkbox-group label span,
        [data-testid*="checkbox"] label span,
        .gr-checkbox-group .wrap label span,
        .gr-checkbox-group div label span {
            color: #374151 !important;
            font-weight: 400 !important;
            font-size: 0.9rem !important;
            line-height: 1.4 !important;
        }
        
        /* 覆蓋可能的 Gradio 默認樣式 */
        .constitution-question .gr-checkbox-group label,
        .constitution-question .checkbox-group label,
        .constitution-question [data-testid*="checkbox"] label {
            font-size: 0.9rem !important;
            font-weight: 400 !important;
        }
        
        /* 確保問題標題比選項大 - 強化版 */
        .constitution-question fieldset legend,
        .constitution-question .gr-checkbox-group fieldset legend,
        .constitution-question > label:first-child,
        .question-container > div > fieldset > legend,
        .question-container fieldset legend {
            color: #1e293b !important;
            font-weight: 600 !important;
            font-size: 1.25rem !important;
            line-height: 1.5 !important;
            margin-bottom: 20px !important;
            padding: 0 !important;
            display: block !important;
        }
        
        /* Checkbox 選項懸停效果 */
        .gr-checkbox-group label:hover:not([data-testid]),
        .checkbox-group label:hover:not([data-testid]),
        [data-testid*="checkbox"] label:hover:not([data-testid]) {
            background: linear-gradient(135deg, #F0F8F0 0%, #E8F5E8 100%) !important;
            border-color: rgba(106, 153, 78, 0.4) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(106, 153, 78, 0.15) !important;
            font-size: 0.9rem !important;
        }
        
        /* Checkbox 輸入框 */
        .gr-checkbox-group input[type="checkbox"],
        .checkbox-group input[type="checkbox"],
        [data-testid*="checkbox"] input[type="checkbox"] {
            width: 22px !important;
            height: 22px !important;
            margin-right: 15px !important;
            accent-color: #6A9A4E !important;
            cursor: pointer !important;
            flex-shrink: 0 !important;
            border: 2px solid #D1D5DB !important;
            border-radius: 6px !important;
            background-color: #FFFFFF !important;
            transition: all 0.3s ease !important;
        }
        
        .gr-checkbox-group input[type="checkbox"]:checked,
        .checkbox-group input[type="checkbox"]:checked,
        [data-testid*="checkbox"] input[type="checkbox"]:checked {
            background-color: #6A9A4E !important;
            border-color: #6A9A4E !important;
            transform: scale(1.1) !important;
        }
        
        /* 選中狀態的標籤樣式 */
        .gr-checkbox-group label.selected:not([data-testid]),
        .checkbox-group label.selected:not([data-testid]),
        [data-testid*="checkbox"] label.selected:not([data-testid]),
        .gr-checkbox-group label:has(input[type="checkbox"]:checked):not([data-testid]),
        .checkbox-group label:has(input[type="checkbox"]:checked):not([data-testid]),
        [data-testid*="checkbox"] label:has(input[type="checkbox"]:checked):not([data-testid]) {
            background: linear-gradient(135deg, #6A9A4E 0%, #8FBC8F 100%) !important;
            color: white !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            border-color: #5A8A3E !important;
            box-shadow: 0 8px 25px rgba(106, 154, 78, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        
        .gr-checkbox-group label.selected *:not([data-testid]),
        .checkbox-group label.selected *:not([data-testid]),
        [data-testid*="checkbox"] label.selected *:not([data-testid]) {
            color: white !important;
            font-size: 0.9rem !important;
        }
        
        /* ===== 文字輸入框樣式 ===== */
        .gr-textbox,
        .gr-textbox textarea,
        .gr-textbox input {
            border: 2px solid rgba(106, 153, 78, 0.2) !important;
            border-radius: 12px !important;
            padding: 15px 20px !important;
            font-size: 1rem !important;
            color: #1e293b !important;
            background: #FFFFFF !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        }
        
        .gr-textbox:focus-within,
        .gr-textbox textarea:focus,
        .gr-textbox input:focus {
            border-color: #6A9A4E !important;
            box-shadow: 0 0 0 4px rgba(106, 153, 78, 0.1), 0 4px 15px rgba(106, 153, 78, 0.2) !important;
            transform: translateY(-1px) !important;
        }
        
        .gr-textbox::placeholder,
        .gr-textbox textarea::placeholder,
        .gr-textbox input::placeholder {
            color: #9CA3AF !important;
        }
        
        /* ===== 分析按鈕區域 ===== */
        
        .analyze-button {
            background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 18px !important;
            padding: 18px 50px !important;
            font-size: 0.9rem !important;
            font-weight: 700 !important;
            margin: 20px auto !important;
            display: block !important;
            box-shadow: 0 12px 35px rgba(45, 55, 72, 0.4) !important;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
            text-transform: none !important;
            min-width: 250px !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        /* 強化按鈕文字顏色 - 覆蓋所有可能的Gradio樣式 */
        .analyze-button,
        .analyze-button span,
        .analyze-button *,
        .gr-button.analyze-button,
        .gr-button.analyze-button span,
        .gr-button.analyze-button *,
        button.analyze-button,
        button.analyze-button span,
        button.analyze-button *,
        [class*="analyze-button"],
        [class*="analyze-button"] span,
        [class*="analyze-button"] * {
            color: white !important;
            text-shadow: none !important;
        }
        
        /* 特別針對primary按鈕和svelte動態class */
        button.lg.primary.analyze-button,
        button.primary.analyze-button,
        button.analyze-button.primary,
        button[class*="svelte"][class*="analyze-button"],
        .gr-button.primary.analyze-button,
        .primary.analyze-button,
        .analyze-button.primary,
        button.lg.primary.analyze-button *,
        button.primary.analyze-button *,
        button.analyze-button.primary *,
        button[class*="svelte"][class*="analyze-button"] *,
        .gr-button.primary.analyze-button *,
        .primary.analyze-button *,
        .analyze-button.primary * {
            color: white !important;
            background-color: #2D3748 !important;
            text-shadow: none !important;
        }
        
        .analyze-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .analyze-button:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 20px 50px rgba(45, 55, 72, 0.5) !important;
            background: linear-gradient(135deg, #1A202C 0%, #2D3748 100%) !important;
            color: white !important;
        }
        
        .analyze-button:hover::before {
            left: 100%;
        }
        
        /* 確保hover狀態下文字也是白色 */
        .analyze-button:hover,
        .analyze-button:hover span,
        .analyze-button:hover *,
        .gr-button.analyze-button:hover,
        .gr-button.analyze-button:hover span,
        .gr-button.analyze-button:hover * {
            color: white !important;
        }
        
        /* ===== 結果顯示區域 ===== */
        .constitution-result-section {
            background: linear-gradient(135deg, #F8FBF6 0%, #FEFEFE 100%) !important;
            border-radius: 25px !important;
            padding: 40px !important;
            margin: 40px 0 !important;
            border: 2px solid rgba(106, 153, 78, 0.2) !important;
            box-shadow: 0 20px 50px rgba(106, 153, 78, 0.2) !important;
            position: relative !important;
        }
        
        .constitution-result-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 25% 25%, rgba(106, 153, 78, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 75% 75%, rgba(212, 175, 55, 0.03) 0%, transparent 40%);
            border-radius: 25px;
            z-index: 0;
        }
        
        .constitution-result-section > * {
            position: relative;
            z-index: 1;
        }
        
        .result-header {
            text-align: center;
            margin-bottom: 40px;
            padding: 25px;
            background: linear-gradient(135deg, #E8F5E8 0%, #F0F8F0 100%);
            border-radius: 20px;
            border: 1px solid rgba(106, 153, 78, 0.2);
        }
        
        .result-header h2 {
            color: #4A6741 !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
        }
        
        /* ===== 體質圖片 ===== */
        .constitution-image {
            border-radius: 20px !important;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2) !important;
            border: 4px solid #6A9A4E !important;
            background: white !important;
            transition: transform 0.3s ease !important;
        }
        
        .constitution-image:hover {
            transform: scale(1.02) !important;
        }
        
        /* ===== 體質結果文字 ===== */
        .constitution-result-text {
            background: #FFFFFF !important;
            border-radius: 20px !important;
            padding: 30px !important;
            border: 1px solid rgba(106, 153, 78, 0.2) !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1) !important;
        }
        
        .constitution-result-text h1,
        .constitution-result-text h2,
        .constitution-result-text h3 {
            color: #4A6741 !important;
            margin-top: 25px !important;
            margin-bottom: 15px !important;
        }
        
        .constitution-result-text p {
            color: #1e293b !important;
            line-height: 1.7 !important;
            margin-bottom: 18px !important;
        }
        
        .constitution-result-text strong {
            color: #6A9A4E !important;
        }
        
        /* ===== 體質標題文字 ===== */
        .constitution-title-text {
            background: #FFFFFF !important;
            border-radius: 20px !important;
            padding: 25px !important;
            border: 1px solid rgba(106, 153, 78, 0.2) !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1) !important;
        }
        
        .constitution-title-text h1,
        .constitution-title-text h2,
        .constitution-title-text h3 {
            color: #4A6741 !important;
            margin-top: 0 !important;
            margin-bottom: 15px !important;
        }
        
        .constitution-title-text p {
            color: #1e293b !important;
            line-height: 1.7 !important;
            margin-bottom: 18px !important;
        }
        
        /* 移除Gradio HTML組件的默認外框，但保留我們的自定義樣式 */
        #component-100,
        #component-101,
        #component-102,
        [id*="component-"].constitution-title-text,
        [id*="component-"].constitution-details-text {
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }
        
        /* 移除svelte動態class的外框 */
        .constitution-title-text.svelte-ydeks8,
        .constitution-details-text.svelte-ydeks8,
        [class*="svelte-"].constitution-title-text,
        [class*="svelte-"].constitution-details-text {
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }
        
        /* 確保內容div保留我們的樣式 */
        .constitution-title-text > div {
            /* 保留我們定義的樣式 */
        }
        
        /* 移除prose樣式干擾，但保留基本結構 */
        .prose.constitution-title-text,
        .prose.constitution-details-text,
        .constitution-title-text.prose,
        .constitution-details-text.prose {
            max-width: none !important;
            color: inherit !important;
            line-height: inherit !important;
            font-size: inherit !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }
        
        /* 確保內容容器保留樣式 */
        .constitution-title-text .prose,
        .constitution-details-text .prose {
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }
        
        /* ===== 體質詳細內容 ===== */
        .constitution-details-text {
            background: #FFFFFF !important;
            border-radius: 20px !important;
            padding: 30px !important;
            margin-top: 30px !important;
            border: 1px solid rgba(106, 153, 78, 0.2) !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1) !important;
        }
        
        .constitution-details-text h1,
        .constitution-details-text h2,
        .constitution-details-text h3 {
            color: #4A6741 !important;
            margin-top: 25px !important;
            margin-bottom: 15px !important;
        }
        
        .constitution-details-text p {
            color: #1e293b !important;
            line-height: 1.7 !important;
            margin-bottom: 18px !important;
        }
        
        .constitution-details-text strong {
            color: #6A9A4E !important;
        }
        
        /* ===== 響應式設計 ===== */
        @media (max-width: 768px) {
            .questionnaire-main-container {
                padding: 25px;
                margin: 15px 0;
            }
            
        .question-container {
            padding: 20px;
                margin: 12px 0;
            }
            
            .gr-checkbox-group label,
            .checkbox-group label {
                padding: 12px 16px !important;
                font-size: 0.9rem !important;
                min-height: 50px !important;
            }
            
            .analyze-button {
                padding: 15px 35px !important;
                font-size: 1.1rem !important;
                min-width: 200px !important;
            }
            
            .questionnaire-group-title {
                padding: 18px 20px;
                font-size: 1.2rem !important;
            }
        }
        
        /* 超級強化 - 直接針對按鈕ID和所有可能的class組合 */
        #component-93,
        button#component-93,
        button[id*="component-"].analyze-button,
        button.lg.primary.analyze-button[class*="svelte"],
        button.primary[class*="svelte"].analyze-button,
        button[class*="svelte-"][class*="analyze-button"],
        #component-93 *,
        button#component-93 *,
        button[id*="component-"].analyze-button *,
        button.lg.primary.analyze-button[class*="svelte"] *,
        button.primary[class*="svelte"].analyze-button *,
        button[class*="svelte-"][class*="analyze-button"] * {
            color: white !important;
            background-color: #2D3748 !important;
            text-shadow: none !important;
        }
    </style>
    """)
    
    with gr.Column(elem_classes=["questionnaire-main-container"]):
        # 問卷標題區域
        gr.HTML("""
        <div class="questionnaire-header">
            <h2>中醫體質問卷調查</h2>
            <p>請根據您最近三個月的實際情況認真作答<br>
            問卷共20題，包含15道選擇題和5道簡答題，完成後AI將為您精準分析體質類型</p>
    </div>
    """)
    
        # 創建問題組件
        question_components = []
        
        # 選擇題區域
        gr.HTML("""
        <div class="questionnaire-group-title">
            <span class="group-icon"></span>
            選擇題部分（第1-15題）
            <div class="group-description">請根據您的實際情況選擇最符合的選項，可多選</div>
        </div>
        """)
        
        for i, q in enumerate(CONSTITUTION_QUESTIONS[:15]):
            with gr.Column(elem_classes=["question-container"]):
                question_components.append(
                    gr.CheckboxGroup(
                        choices=q["options"],
                        label=f"{i+1}. {q['question']}",
                        value=[],
                        elem_classes=["constitution-question"]
                    )
                )
        
        # 簡答題區域
        gr.HTML("""
        <div class="questionnaire-group-title">
            <span class="group-icon"></span>
            簡答題部分（第16-20題）
            <div class="group-description">請根據您的實際情況簡要描述，有助於更精準的分析</div>
        </div>
        """)
        
        for i, q in enumerate(CONSTITUTION_QUESTIONS[15:], 15):
            with gr.Column(elem_classes=["question-container"]):
                question_components.append(
                    gr.Textbox(
                        label=f"{i+1}. {q['question']}",
                        placeholder=q["placeholder"],
                        lines=3,
                        elem_classes=["constitution-textbox"]
                    )
                )
        
        # 分析按鈕區域
        
        analyze_btn = gr.Button(
            "開始AI體質分析(點擊後請下拉查看結果)", 
            variant="primary", 
            size="lg",
            elem_classes=["analyze-button"]
        )
        
        # 結果顯示區域
        with gr.Column(visible=False, elem_classes=["constitution-result-section"]) as result_row:
            gr.HTML("""
            <div class="result-header">
                <h2>您的體質分析結果</h2>
            </div>
            """)
            
            # 上方：圖片和體質類型標題
            with gr.Row():
                with gr.Column(scale=2):
                    constitution_image = gr.Image(
                        label="體質特徵圖", 
                        height=400,
                        width=400,
                        show_download_button=False,
                        container=True,
                        elem_classes=["constitution-image"]
                    )
                with gr.Column(scale=3):
                    constitution_title = gr.HTML(
                        value="",
                        elem_classes=["constitution-title-text"]
                    )
            
            # 下方：詳細分析內容
            with gr.Column():
                constitution_details = gr.HTML(
                    value="",
                    elem_classes=["constitution-details-text"]
                    )
        
        # 原始JSON結果（隱藏，僅供調試）
        constitution_result_display = gr.JSON(label="詳細分析數據", visible=False)
        
        # 優化的JavaScript
        gr.HTML("""
        <script>
            (function() {
                let isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                
                // 處理 Checkbox 樣式
                function handleCheckboxInteraction() {
                    // 處理選擇題
                    const checkboxGroups = document.querySelectorAll('.gr-checkbox-group');
                    checkboxGroups.forEach((group, groupIndex) => {
                        if (groupIndex < 15) { // 只處理前15個選擇題
                            const checkboxes = group.querySelectorAll('input[type="checkbox"]');
                            
                            // 更新視覺效果
                            checkboxes.forEach((checkbox) => {
                                const label = checkbox.closest('label');
                                if (label) {
                                    // 確保選項字體大小正確
                                    label.style.fontSize = '0.9rem';
                                    label.style.fontWeight = '400';
                                    
                                    if (checkbox.checked) {
                                        label.classList.add('selected');
                                        label.style.background = 'linear-gradient(135deg, #6A9A4E 0%, #8FBC8F 100%)';
                                        label.style.color = 'white';
                                        label.style.fontWeight = '500';
                                        label.style.fontSize = '0.9rem';
                                        label.style.borderColor = '#5A8A3E';
                                        label.style.transform = 'translateY(-2px)';
                                        label.style.boxShadow = '0 8px 25px rgba(106, 154, 78, 0.4)';
                                        label.style.animation = 'selectPulse 0.3s ease';
                                    } else {
                                        label.classList.remove('selected');
                                        label.style.background = 'linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%)';
                                        label.style.color = '#374151';
                                        label.style.fontWeight = '400';
                                        label.style.fontSize = '0.9rem';
                                        label.style.borderColor = '#E5E7EB';
                                        label.style.transform = '';
                                        label.style.boxShadow = '';
                                        label.style.animation = '';
                                    }
                                }
                            });
                        }
                    });
                }
                
                // 添加交互效果
                function addInteractionEffects() {
                    // 為文字輸入框添加焦點效果
                    const textInputs = document.querySelectorAll('.constitution-textbox textarea, .constitution-textbox input');
                    textInputs.forEach(input => {
                        if (!input.hasAttribute('data-focus-added')) {
                            input.setAttribute('data-focus-added', 'true');
                            
                            input.addEventListener('focus', function() {
                                this.parentElement.style.transform = 'translateY(-2px)';
                                this.parentElement.style.boxShadow = '0 8px 30px rgba(106, 153, 78, 0.2)';
                            });
                            
                            input.addEventListener('blur', function() {
                                this.parentElement.style.transform = '';
                                this.parentElement.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.05)';
                            });
                        }
                    });
                }
                
                // 添加動畫樣式
                function addAnimationStyles() {
                    const styleSheet = document.createElement('style');
                    styleSheet.textContent = `
                        @keyframes selectPulse {
                            0% { transform: translateY(-2px) scale(1); }
                            50% { transform: translateY(-2px) scale(1.05); }
                            100% { transform: translateY(-2px) scale(1); }
                        }
                    `;
                    document.head.appendChild(styleSheet);
                }
                
                // 初始化
                function init() {
                    addAnimationStyles();
                    handleCheckboxInteraction();
                    addInteractionEffects();
                    
                    // 強制設定所有選項的字體大小
                    const allOptionLabels = document.querySelectorAll('.gr-checkbox-group label, .checkbox-group label');
                    allOptionLabels.forEach(label => {
                        if (!label.querySelector('fieldset') && !label.closest('fieldset')) {
                            label.style.fontSize = '0.9rem !important';
                            label.style.fontWeight = '400 !important';
                            
                            const textElements = label.querySelectorAll('span, div');
                            textElements.forEach(elem => {
                                elem.style.fontSize = '0.9rem !important';
                                elem.style.fontWeight = '400 !important';
                            });
                        }
                    });
                    
                    // 確保問題標題字體正確
                    const questionTitles = document.querySelectorAll('fieldset legend, .constitution-question fieldset legend, .constitution-textbox > label');
                    questionTitles.forEach(title => {
                        title.style.fontSize = '1.25rem !important';
                        title.style.fontWeight = '600 !important';
                    });
                    
                    // 強制設置分析按鈕文字為白色
                    const analyzeButtons = document.querySelectorAll('.analyze-button, .gr-button.analyze-button, button.analyze-button');
                    analyzeButtons.forEach(button => {
                        button.style.color = 'white !important';
                        button.style.backgroundColor = '#2D3748 !important';
                        
                        // 設置按鈕內所有文字元素為白色
                        const textElements = button.querySelectorAll('*');
                        textElements.forEach(elem => {
                            elem.style.color = 'white !important';
                            elem.style.textShadow = 'none !important';
                        });
                        
                        // 直接設置按鈕文字
                        if (button.textContent) {
                            button.style.color = 'white !important';
                        }
                    });
                    
                    // 特別針對primary按鈕
                    const primaryAnalyzeButtons = document.querySelectorAll(
                        'button.lg.primary.analyze-button, button.primary.analyze-button, button[class*="svelte"][class*="analyze-button"]'
                    );
                    primaryAnalyzeButtons.forEach(button => {
                        button.style.setProperty('color', 'white', 'important');
                        button.style.setProperty('background-color', '#2D3748', 'important');
                        button.style.setProperty('text-shadow', 'none', 'important');
                        
                        // 強制設置所有子元素
                        const allElements = button.querySelectorAll('*');
                        allElements.forEach(elem => {
                            elem.style.setProperty('color', 'white', 'important');
                        });
                        
                        // 如果是文字節點，直接設置父元素樣式
                        if (button.childNodes) {
                            button.childNodes.forEach(node => {
                                if (node.nodeType === 3) { // 文字節點
                                    button.style.setProperty('color', 'white', 'important');
                                }
                            });
                        }
                    });
                    
                    console.log('體質分析UI初始化完成，檢測到' + (isMobile ? '移動端' : '桌面端') + '設備');
                }
                
                // 監聽變化事件
                ['change', 'input', 'click'].forEach(eventType => {
                    document.addEventListener(eventType, function(e) {
                        if (e.target.type === 'checkbox' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') {
                            setTimeout(handleCheckboxInteraction, 100);
                        }
                    });
                });
                
                // DOM 變化監聽
                const observer = new MutationObserver(function(mutations) {
                    let shouldUpdate = false;
                    mutations.forEach(mutation => {
                        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                            for (let node of mutation.addedNodes) {
                                if (node.nodeType === 1 && (
                                    (node.querySelector && node.querySelector('input[type="checkbox"]')) ||
                                    (node.classList && node.classList.contains('gr-checkbox-group'))
                                )) {
                                    shouldUpdate = true;
                                    break;
                                }
                            }
                        }
                    });
                    
                    if (shouldUpdate) {
                        setTimeout(() => {
                            init();
                        }, 500);
                    }
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
                
                // 延遲初始化確保 DOM 載入完成
                setTimeout(init, 1000);
                setTimeout(init, 2000);
                setTimeout(init, 3000);
                
                // 定期檢查
                setInterval(handleCheckboxInteraction, 5000);
                
                // 定期檢查並強制設置按鈕文字顏色
                setInterval(() => {
                    const analyzeButtons = document.querySelectorAll('.analyze-button, .gr-button.analyze-button, button.analyze-button');
                    analyzeButtons.forEach(button => {
                        button.style.setProperty('color', 'white', 'important');
                        button.style.setProperty('background-color', '#2D3748', 'important');
                        
                        // 強制設置所有子元素文字顏色
                        const allElements = button.querySelectorAll('*');
                        allElements.forEach(elem => {
                            elem.style.setProperty('color', 'white', 'important');
                        });
                        
                        // 直接設置textContent的樣式
                        if (button.firstChild && button.firstChild.nodeType === 3) {
                            button.style.setProperty('color', 'white', 'important');
                        }
                    });
                    
                    // 特別處理primary和svelte按鈕
                    const primaryButtons = document.querySelectorAll(
                        'button.lg.primary.analyze-button, button.primary.analyze-button, button[class*="svelte"][class*="analyze-button"], #component-93'
                    );
                    primaryButtons.forEach(button => {
                        // 使用最強的方式設置樣式
                        button.style.setProperty('color', 'white', 'important');
                        button.style.setProperty('background-color', '#2D3748', 'important');
                        button.style.setProperty('text-shadow', 'none', 'important');
                        
                        // 強制所有子元素和文字節點
                        if (button.childNodes) {
                            button.childNodes.forEach(node => {
                                if (node.nodeType === 3) { // 文字節點
                                    button.style.setProperty('color', 'white', 'important');
                                } else if (node.nodeType === 1) { // 元素節點
                                    node.style && node.style.setProperty('color', 'white', 'important');
                                }
                            });
                        }
                    });
                }, 2000);
                
                console.log('簡化版體質分析UI腳本已載入');
                
                // 立即強制設置按鈕樣式（不等待任何延遲）
                (function forceButtonStyle() {
                    const buttons = document.querySelectorAll(
                        '.analyze-button, #component-93, button[class*="analyze-button"], button.primary.analyze-button'
                    );
                    buttons.forEach(button => {
                        button.style.setProperty('color', 'white', 'important');
                        button.style.setProperty('background-color', '#2D3748', 'important');
                        button.style.setProperty('text-shadow', 'none', 'important');
                        button.style.setProperty('border', 'none', 'important');
                        
                        // 強制所有文字節點
                        const walker = document.createTreeWalker(
                            button,
                            NodeFilter.SHOW_TEXT,
                            null,
                            false
                        );
                        let node;
                        while (node = walker.nextNode()) {
                            if (node.parentElement) {
                                node.parentElement.style.setProperty('color', 'white', 'important');
                            }
                        }
                    });
                })();
            })();
        </script>
        """)
        
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
            image_path, title_text, details_text = format_constitution_result(result)
            
            # 直接返回6個值，包括 constitution_state 的更新
            if image_path and os.path.exists(image_path):
                return (
                    gr.update(value=image_path, visible=True),  # constitution_image
                    gr.update(value=title_text, visible=True),  # constitution_title
                    gr.update(value=details_text, visible=True),  # constitution_details
                    gr.update(visible=True),  # result_row
                    result,  # constitution_result_display
                    result   # constitution_state - 將分析結果存儲到狀態中
                )
            else:
                return (
                    gr.update(value=None, visible=False),  # constitution_image
                    gr.update(value=title_text, visible=True),  # constitution_title
                    gr.update(value=details_text, visible=True),  # constitution_details
                    gr.update(visible=True),  # result_row
                    result,  # constitution_result_display
                    result   # constitution_state - 將分析結果存儲到狀態中
                )
        
        constitution_state = gr.State()
        
        analyze_btn.click(
            fn=process_and_display,
            inputs=question_components,
            outputs=[constitution_image, constitution_title, constitution_details, result_row, constitution_result_display, constitution_state]
        )
        
        return constitution_result_display, constitution_state