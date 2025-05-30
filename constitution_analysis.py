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
    """建立體質分析頁面"""    # 添加CSS樣式
    gr.HTML("""
    <style>        /* 問題標題樣式 - 針對動態生成的 Gradio 組件 */
        .constitution-question label,
        .constitution-textbox label,
        .gr-checkbox-group > label,
        .gr-textbox > label,
        fieldset > legend,
        .gr-group > label,
        div[data-testid="checkbox-group"] > label[data-testid="checkbox-group-label"],
        div[data-testid="textbox"] > label[data-testid="textbox-label"] {
            color: #1e293b !important;
            font-weight: 700 !important;
            font-size: 3.5rem !important;
            line-height: 1.2 !important;
            margin-bottom: 20px !important;
            display: block !important;
            padding: 15px 0 !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1) !important;
        }
        
        /* 強制設定所有包含數字的問題標題 */
        .constitution-question fieldset legend,
        .constitution-textbox label {
            font-size: 3.5rem !important;
            font-weight: 700 !important;
            color: #1e293b !important;
            margin-bottom: 20px !important;
        }
        
        /* CheckboxGroup 選項樣式 - 很小字體 */
        .gr-checkbox-group .gr-checkbox label,
        .gr-checkbox-group input[type="checkbox"] + label,
        .gr-checkbox-group .checkbox-item label,
        .gr-checkbox label:not([data-testid="checkbox-group-label"]),
        .constitution-question .gr-checkbox label {
            color: #374151 !important;
            font-weight: 400 !important;
            font-size: 0.65rem !important;
            line-height: 1.2 !important;
            margin: 1px 0 !important;
            padding: 3px 5px !important;
            border-radius: 4px !important;
            transition: all 0.3s ease !important;
            border: 1px solid #E5E7EB !important;
            background: #FFFFFF !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            min-height: 22px !important;
        }
        
        /* 選中狀態樣式 - 保持很小字體 */
        .gr-checkbox-group input[type="checkbox"]:checked + label,
        .constitution-question input[type="checkbox"]:checked + label {
            background: linear-gradient(135deg, #8FBC8F 0%, #7BAB7B 100%) !important;
            color: white !important;
            font-weight: 500 !important;
            border-color: #6A9A6A !important;
            box-shadow: 0 2px 8px rgba(143, 188, 143, 0.3) !important;
            font-size: 0.65rem !important;
        }
        
        /* 問卷分組標題 */
        .questionnaire-group-title {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 15px 20px;
            margin: 25px 0 15px 0;
            border-radius: 12px;
            border-left: 4px solid #4A6741;
            font-size: 1.2rem;
            font-weight: 600;
            color: #1e293b;
        }
        
        /* 問題容器 */
        .question-container {
            margin-bottom: 20px;
            padding: 20px;
            background: #fafafa;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
        }
        
        /* 進度指示器樣式 */
        .progress-indicator {
            background: linear-gradient(135deg, #e0f2e0 0%, #c8e6c8 100%);
            padding: 15px 25px;
            border-radius: 10px;
            border: 2px solid #4A6741;
            display: inline-block;
        }
        
        .progress-indicator-icon {
            font-size: 1.5rem;
            margin-right: 10px;
        }
        
        .progress-indicator-text {
            font-size: 1rem;
            font-weight: 500;
            color: #4A6741;
        }
    </style>
    """)
    
    # 問卷介紹區域
    gr.HTML("""
    <div class="questionnaire-section">
        <div style="text-align: center; margin-bottom: 25px;">
            <h2 style="color: #4A6741; font-size: 1.5rem; font-weight: 600; margin-bottom: 15px;">
                📋 中醫體質問卷調查
            </h2>
            <p style="color: #64748b; font-size: 1.1rem; line-height: 1.6;">
                請仔細閱讀每個問題，根據您最近三個月的實際情況作答。<br>
                問卷共20題，包含15道選擇題和5道簡答題。
            </p>
        </div>
    </div>
    """)
    
    with gr.Column():
        # 創建問題組件
        question_components = []
        
        # 選擇題區域
        gr.HTML("""
        <div class="questionnaire-group-title">
            🔍 選擇題部分（第1-15題）
        </div>
        """)
        
        for i, q in enumerate(CONSTITUTION_QUESTIONS[:15]):  # 前15題是選擇題
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
            ✍️ 簡答題部分（第16-20題）
        </div>
        """)
        
        for i, q in enumerate(CONSTITUTION_QUESTIONS[15:], 15):  # 後5題是簡答題
            with gr.Column(elem_classes=["question-container"]):
                question_components.append(
                    gr.Textbox(
                        label=f"{i+1}. {q['question']}",
                        placeholder=q["placeholder"],
                        lines=3,
                        elem_classes=["constitution-textbox"]
                    )
                )        # 分析按鈕區域
        gr.HTML("""
        <div style="text-align: center; margin: 40px 0 20px 0;">
            <div class="progress-indicator">
                <span class="progress-indicator-icon">🤖</span>
                <span class="progress-indicator-text">完成問卷後，AI將在30秒內為您分析體質類型</span>
            </div>
        </div>        <script>
            function applyConstitutionFontSizes() {
                try {
                    // 針對 CheckboxGroup 問題標題
                    const checkboxGroups = document.querySelectorAll('.constitution-question');
                    checkboxGroups.forEach(function(group) {
                        const legend = group.querySelector('fieldset legend');
                        const label = group.querySelector('label[data-testid="checkbox-group-label"]');                        if (legend && legend.textContent && legend.textContent.match(/^\\d+\\./)) {
                            legend.style.fontSize = '3.5rem';
                            legend.style.fontWeight = '700';
                            legend.style.color = '#1e293b';
                            legend.style.marginBottom = '20px';
                            legend.style.lineHeight = '1.2';
                        }
                        
                        if (label && label.textContent && label.textContent.match(/^\\d+\\./)) {
                            label.style.fontSize = '3.5rem';
                            label.style.fontWeight = '700';
                            label.style.color = '#1e293b';
                            label.style.marginBottom = '20px';
                            label.style.lineHeight = '1.2';
                        }
                    });
                    
                    // 針對 Textbox 問題標題
                    const textboxes = document.querySelectorAll('.constitution-textbox');
                    textboxes.forEach(function(box) {
                        const label = box.querySelector('label[data-testid="textbox-label"]');                        if (label && label.textContent && label.textContent.match(/^\\d+\\./)) {
                            label.style.fontSize = '3.5rem';
                            label.style.fontWeight = '700';
                            label.style.color = '#1e293b';
                            label.style.marginBottom = '20px';
                            label.style.lineHeight = '1.2';
                        }
                    });
                    
                    // 設置選項為很小字體
                    const optionLabels = document.querySelectorAll('.constitution-question .gr-checkbox label');
                    optionLabels.forEach(function(label) {
                        if (label.textContent && !label.textContent.match(/^\\d+\\./) && !label.hasAttribute('data-testid')) {
                            label.style.fontSize = '0.65rem';
                            label.style.fontWeight = '400';
                            label.style.padding = '3px 5px';
                            label.style.minHeight = '22px';
                        }
                    });
                    
                    // 通用選擇器強制設置問題標題                    const allLabels = document.querySelectorAll('label');
                    allLabels.forEach(function(label) {
                        if (label.textContent && label.textContent.match(/^\\d+\\./)) {
                            label.style.fontSize = '3.5rem';
                            label.style.fontWeight = '700';
                            label.style.color = '#1e293b';
                            label.style.marginBottom = '20px';
                            label.style.lineHeight = '1.2';
                        }
                    });
                    
                } catch(e) {
                    console.log('字體應用錯誤:', e);
                }
            }
            
            // 多次執行以確保樣式被應用
            setTimeout(applyConstitutionFontSizes, 300);
            setTimeout(applyConstitutionFontSizes, 1000);
            setTimeout(applyConstitutionFontSizes, 2000);
            setTimeout(applyConstitutionFontSizes, 4000);
        </script>
        """)
        
        analyze_btn = gr.Button(
            "🚀 開始AI體質分析", 
            variant="primary", 
            size="lg",
            elem_classes=["analyze-button"]
        )
        
        # 結果顯示區域
        with gr.Column(visible=False, elem_classes=["constitution-result-section"]) as result_row:
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #4A6741; font-size: 1.8rem; font-weight: 600;">
                    🎯 您的體質分析結果
                </h2>
            </div>
            """)
            
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
                    constitution_text = gr.Markdown(
                        value="",
                        container=True,
                        elem_classes=["constitution-result-text"]
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