import random
import gradio as gr
import json
from typing import Dict, List, Tuple
import aisuite as ai
import os
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# --------------------------------------------------------------------------
# 中醫食物屬性資料庫
# --------------------------------------------------------------------------
FOOD_DATABASE = {
    "蘋果": {"五性": "平性", "歸經": "脾、胃", "功效": "生津潤燥、健脾益胃"},
    "香蕉": {"五性": "寒性", "歸經": "脾、胃、大腸", "功效": "清熱潤腸、解毒"},
    "橘子": {"五性": "溫性", "歸經": "肺、胃", "功效": "理氣化痰、開胃"},
    "西瓜": {"五性": "寒性", "歸經": "心、胃、膀胱", "功效": "清熱解暑、利尿"},
    "龍眼": {"五性": "溫性", "歸經": "心、脾", "功效": "補血安神、益智"},
    "梨子": {"五性": "涼性", "歸經": "肺、胃", "功效": "清熱潤肺、化痰"},
    "桃子": {"五性": "溫性", "歸經": "肺、大腸", "功效": "生津潤腸、活血"},
    "葡萄": {"五性": "平性", "歸經": "肺、脾、腎", "功效": "補氣血、強筋骨"},
    "白蘿蔔": {"五性": "涼性", "歸經": "肺、胃", "功效": "清熱化痰、消食"},
    "胡蘿蔔": {"五性": "平性", "歸經": "肺、脾", "功效": "健脾消食、養肝明目"},
    "番茄": {"五性": "涼性", "歸經": "肝、胃", "功效": "清熱解毒、生津止渴"},
    "黃瓜": {"五性": "涼性", "歸經": "胃、小腸", "功效": "清熱利水、解毒"},
    "茄子": {"五性": "涼性", "歸經": "脾、胃、大腸", "功效": "清熱活血、消腫"},
    "菠菜": {"五性": "涼性", "歸經": "肝、胃、大腸、小腸", "功效": "養血滋陰、潤燥"},
    "韭菜": {"五性": "溫性", "歸經": "肝、胃、腎", "功效": "溫腎助陽、益脾健胃"},
}

# 體質類型定義
CONSTITUTION_TYPES = {
    "平和質": "陰陽氣血調和，體質平和",
    "氣虛質": "元氣不足，易疲勞乏力",
    "陽虛質": "陽氣不足，畏寒怕冷",
    "陰虛質": "陰液虧少，虛熱內擾",
    "痰濕質": "痰濕凝聚，形體肥胖",
    "濕熱質": "濕熱內蘊，面垢油膩",
    "血瘀質": "血行不暢，膚色晦暗",
    "氣鬱質": "氣機鬱滯，神情抑鬱",
    "特稟質": "先天稟賦不足，過敏體質"
}

# --------------------------------------------------------------------------
# 1. 食物辨識模組
# --------------------------------------------------------------------------
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
        "英文名": food_info.get("英文名", "unknown"),
        "五性屬性": food_info["五性"],
        "歸經": food_info.get("歸經", "資料庫中無此資訊"),
        "功效": food_info.get("功效", "資料庫中無此資訊"),
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
                result_json = gr.JSON(label="辨識結果")
        
        recognize_btn.click(
            fn=classify_food_image,
            inputs=[food_image],
            outputs=[result_json]
        )

# --------------------------------------------------------------------------
# 2. 體質推理模組 - 使用 LLM 分析
# --------------------------------------------------------------------------

# 中醫體質混合型問卷（共20題）
CONSTITUTION_QUESTIONS = [
    # 選擇題（15題）
    {
        "question": "您最近的精神與體力狀況？",
        "type": "multiple_choice",
        "options": ["精力充沛、體力佳", "易疲倦、提不起勁", "情緒低落、常無明顯原因感到不快", "無特別異常"]
    },
    {
        "question": "您的睡眠狀況？",
        "type": "multiple_choice",
        "options": ["睡眠淺、易醒、多夢", "難入睡或易失眠", "晚上醒後難再入睡", "睡眠安穩"]
    },
    {
        "question": "您的情緒狀態？",
        "type": "multiple_choice",
        "options": ["焦慮緊張、易煩躁", "情緒波動大、感情脆弱", "常嘆氣、悶悶不樂", "心情穩定"]
    },
    {
        "question": "您是否容易出汗？",
        "type": "multiple_choice",
        "options": ["稍微活動就出虛汗", "出汗多且黏膩", "不易出汗", "出汗正常"]
    },
    {
        "question": "您是否容易感冒或過敏？",
        "type": "multiple_choice",
        "options": ["容易感冒", "對天氣、花粉、食物等過敏", "換季時易咳嗽、鼻癢", "體質穩定不易感冒或過敏"]
    },
    {
        "question": "您的四肢感受？",
        "type": "multiple_choice",
        "options": ["手腳冰冷", "手腳心發熱", "四肢沉重、無力", "四肢正常溫和有力"]
    },
    {
        "question": "您是否常感口乾、口苦或嘴巴不適？",
        "type": "multiple_choice",
        "options": ["口乾咽燥", "嘴巴有黏感", "嘴苦、口臭", "口腔狀況正常"]
    },
    {
        "question": "您的皮膚狀況？",
        "type": "multiple_choice",
        "options": ["容易長痘、粉刺", "易癢或有紅疹", "皮膚一抓就紅或有抓痕", "皮膚正常清爽"]
    },
    {
        "question": "您是否有肩頸、頭部不適？",
        "type": "multiple_choice",
        "options": ["肩頸僵硬、痠痛", "經常頭痛或頭暈", "無此問題"]
    },
    {
        "question": "您的腹部與消化情形？",
        "type": "multiple_choice",
        "options": ["腹部鬆軟或肥滿", "易腹脹、消化不良", "吃涼易腹瀉", "消化正常"]
    },
    {
        "question": "您的排便與小便狀況？",
        "type": "multiple_choice",
        "options": ["大便乾燥或黏滯不爽", "小便黃或灼熱感", "排便無力或解不乾淨", "排便小便正常"]
    },
    {
        "question": "您的眼睛與視覺感受？",
        "type": "multiple_choice",
        "options": ["容易乾澀或模糊", "常有紅血絲", "視覺與眼睛舒適"]
    },
    {
        "question": "您的面部特徵？",
        "type": "multiple_choice",
        "options": ["臉色暗沉、易出斑", "臉部油膩、長痘", "臉頰潮紅或泛紅", "面色紅潤自然"]
    },
    {
        "question": "您的舌頭或嘴唇觀察？",
        "type": "multiple_choice",
        "options": ["舌苔厚膩", "舌邊有齒痕", "嘴唇暗紫或蒼白", "舌紅苔薄，嘴唇紅潤"]
    },
    {
        "question": "您的日常活動狀況？",
        "type": "multiple_choice",
        "options": ["活動後易喘或出汗", "經常感覺身體沉重", "容易覺得累，想躺著", "活動正常，不易疲倦"]
    },
    # 開放式簡答題（5題）
    {
        "question": "您平時最常感受到身體哪一部分不適？（如：肩膀、腸胃、頭部、皮膚等）",
        "type": "text",
        "placeholder": "請簡單描述..."
    },
    {
        "question": "您的飲食習慣與偏好是什麼？（如：愛吃冷食、重口味、喜甜食、蔬果攝取習慣）",
        "type": "text",
        "placeholder": "請簡單描述..."
    },
    {
        "question": "當您壓力大或疲倦時，身體會有什麼反應？（如：失眠、便秘、冒痘、胸悶等）",
        "type": "text",
        "placeholder": "請簡單描述..."
    },
    {
        "question": "請描述您最近一次生病或身體不適的經驗。（包括症狀、持續時間、是否容易復原）",
        "type": "text",
        "placeholder": "請簡單描述..."
    },
    {
        "question": "您認為自己整體的健康狀況如何？（可自由描述，也可給分數，如滿分10分您給幾分）",
        "type": "text",
        "placeholder": "請簡單描述..."
    }
]

# 初始化 AI 客戶端
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
        
        set_key_btn.click(
            fn=set_api_key,
            inputs=[api_key_input],
            outputs=[gr.Textbox(label="狀態", interactive=False)]
        )
        
        analyze_btn = gr.Button("🤖 AI 分析體質", variant="primary", size="lg")
        constitution_result = gr.JSON(label="AI 體質分析結果")
        
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
            
            return analyze_constitution(answers)
        
        analyze_btn.click(
            fn=process_answers,
            inputs=question_components,
            outputs=[constitution_result]
        )
        
        return constitution_result

# --------------------------------------------------------------------------
# 3. 養生建議生成模組
# --------------------------------------------------------------------------
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
2. 生活作息建議
3. 運動養生建議
4. 情緒調理建議
5. 季節養生要點
6. 需要避免的食物或行為
7. 推薦的其他食物搭配

請以清晰的 Markdown 格式回答，內容要專業且實用。
"""
        
        response = client.chat.completions.create(
            model="groq:llama-3.3-70b-versatile",
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

# --------------------------------------------------------------------------
# 主應用程式
# --------------------------------------------------------------------------
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
                food_result_state = gr.State()
                
                with gr.Column():
                    gr.Markdown("## 食物辨識模組")
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
                    
                    recognize_btn.click(
                        fn=update_food_result,
                        inputs=[food_image],
                        outputs=[food_result_display, food_result_state]
                    )
            
            # Tab 2: 體質分析
            with gr.Tab("🏥 體質分析"):
                constitution_result_state = gr.State()
                
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
                    
                    analyze_btn.click(
                        fn=process_answers,
                        inputs=question_components,
                        outputs=[constitution_result_display, constitution_result_state]
                    )
            
            # Tab 3: 養生建議
            with gr.Tab("🌿 養生建議"):
                with gr.Column():
                    gr.Markdown("## 個人化養生建議")
                    gr.Markdown("基於您的體質分析和食物辨識結果，生成個人化養生建議")
                    
                    generate_advice_btn = gr.Button("🌿 生成養生建議", variant="primary")
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
        
        gr.Markdown("""
        ---
        💡 **使用說明：**
        1. 先在「食物辨識」頁面上傳食物圖片進行辨識
        2. 在「體質分析」頁面完成體質問卷
        3. 在「養生建議」頁面獲得個人化建議
        
        ⚠️ **免責聲明：** 本系統僅供參考，不能替代專業醫療建議
        """)
    
    return app

# --------------------------------------------------------------------------
# 啟動應用
# --------------------------------------------------------------------------
if __name__ == "__main__":
    app = build_main_app()
    app.launch(share=True)

