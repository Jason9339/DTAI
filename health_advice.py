# health_advice.py - 養生建議生成模組
import json
import gradio as gr
from typing import Dict
from utils import get_ai_client

# 添加自定義CSS樣式
ADVICE_PAGE_CSS = """
<style>
/* 養生建議頁面專用樣式 */
.advice-output-container {
    background: #FFFFFF !important;
    border-radius: 15px !important;
    padding: 25px !important;
    margin: 20px 0 !important;
    border: 2px solid rgba(106, 153, 78, 0.2) !important;
    box-shadow: 0 8px 32px rgba(106, 153, 78, 0.1) !important;
    position: relative !important;
}

.advice-output-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(circle at 20% 20%, rgba(106, 153, 78, 0.02) 0%, transparent 30%),
        radial-gradient(circle at 80% 80%, rgba(212, 175, 55, 0.02) 0%, transparent 30%);
    border-radius: 15px;
    z-index: 0;
}

.advice-output-container > * {
    position: relative;
    z-index: 1;
}

/* 建議內容文字樣式 */
.advice-output-container h1,
.advice-output-container h2,
.advice-output-container h3 {
    color: #4A6741 !important;
    font-weight: 600 !important;
    margin: 20px 0 15px 0 !important;
}

.advice-output-container h1 {
    font-size: 1.8rem !important;
    border-bottom: 3px solid #6A9A4E !important;
    padding-bottom: 10px !important;
}

.advice-output-container h2 {
    font-size: 1.5rem !important;
    color: #6A9A4E !important;
}

.advice-output-container h3 {
    font-size: 1.3rem !important;
    color: #8B4513 !important;
}

.advice-output-container p {
    color: #2D5016 !important;
    line-height: 1.8 !important;
    margin: 10px 0 !important;
    font-size: 1.05rem !important;
}

.advice-output-container ul,
.advice-output-container ol {
    color: #2D5016 !important;
    padding-left: 25px !important;
    margin: 15px 0 !important;
}

.advice-output-container li {
    margin: 8px 0 !important;
    line-height: 1.7 !important;
}

.advice-output-container strong {
    color: #6A9A4E !important;
    font-weight: 600 !important;
}

.advice-output-container em {
    color: #8B4513 !important;
    font-style: italic !important;
}

/* 免責聲明特殊樣式 */
.advice-output-container hr + p {
    background: #FFF8DC !important;
    border: 2px solid #D4AF37 !important;
    border-radius: 10px !important;
    padding: 15px !important;
    color: #8B4513 !important;
    font-weight: 500 !important;
    margin: 20px 0 !important;
}

/* 建議項目標籤 */
.advice-tag {
    display: inline-block;
    background: #6A9A4E;
    color: white;
    padding: 4px 12px;
    border-radius: 15px;
    font-size: 0.9rem;
    font-weight: 500;
    margin: 5px 5px 5px 0;
}

/* 進度指示器樣式 */
.progress-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    margin: 30px 0;
    padding: 20px;
    background: rgba(106, 153, 78, 0.1);
    border-radius: 12px;
    border: 1px solid rgba(106, 153, 78, 0.2);
}

.progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}

.progress-step-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #6A9A4E;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: bold;
}

.progress-step-icon.completed {
    background: #4A6741;
}

.progress-step-icon.current {
    background: #D4AF37;
    animation: pulse 2s infinite;
}

.progress-step-label {
    color: #4A6741;
    font-size: 0.9rem;
    font-weight: 500;
    text-align: center;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

/* 響應式設計 */
@media (max-width: 768px) {
    .feature-card {
        margin: 10px 0 !important;
    }
    
    .progress-indicator {
        flex-direction: column;
        gap: 20px;
    }
    
    .advice-output-container {
        padding: 15px !important;
        margin: 10px 0 !important;
    }
}
</style>
"""

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

請按照以下結構提供詳細的養生建議，使用清晰的 Markdown 格式：

# 🌟 您的個人化養生建議

## 📊 體質與食物分析摘要
- **主要體質**：[體質類型]
- **食物五性**：[食物屬性]
- **搭配評估**：[是否適合此體質]

## 🍽️ 飲食調理建議

### ✅ 推薦食物搭配
[列出3-5種適合的食物，說明原因]

### ⚠️ 需要避免的食物
[列出需要謹慎或避免的食物類型]

### 🕐 用餐時間建議
[給出具體的用餐時間和頻率建議]

## 💪 生活方式調理

### 🧘‍♀️ 運動建議
[適合此體質的運動類型和強度]

### 😴 作息調理
[睡眠時間和生活節奏建議]

### 🌡️ 季節調養
[不同季節的注意事項]

## 🌿 中藥茶飲推薦
[推薦2-3種適合的茶飲或湯方，含具體配方]

## 📈 調理進程建議
- **第1-2週**：[初期調理重點]
- **第3-4週**：[中期調理重點] 
- **第5-8週**：[長期調理重點]

## 🚨 注意事項與禁忌
[列出重要的注意事項和禁忌]

請確保建議實用、具體、易執行，並體現中醫辨證施治的特點。
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

def build_health_advice_page(constitution_result_state, food_result_state):
    """建立養生建議頁面"""
    with gr.Column():
        # 添加自定義CSS樣式
        gr.HTML(ADVICE_PAGE_CSS)
        
        # 移除被漂浮按鈕遮擋的頁面標題區域
        # gr.HTML("""
        # <div class="main-content">
        #     <div class="hero-section">
        #         <h1 class="page-title">🌿 個人化養生建議</h1>
        #         <p class="page-subtitle">基於您的體質分析和食物辨識結果，AI將生成專屬的中醫養生建議</p>
        #     </div>
        # </div>
        # """)
        
        # 功能說明區域
        with gr.Row():
            gr.HTML("""
            <div class="feature-card">
                <div class="feature-card-content">
                    <div class="feature-icon">🧘‍♀️</div>
                    <h3 class="feature-title">體質調理</h3>
                    <p class="feature-description">根據您的中醫體質特點，提供個性化的調理建議</p>
                </div>
            </div>
            """)
            
            gr.HTML("""
            <div class="feature-card">
                <div class="feature-card-content">
                    <div class="feature-icon">🍃</div>
                    <h3 class="feature-title">食療養生</h3>
                    <p class="feature-description">結合食物五性屬性，制定適合的飲食搭配方案</p>
                </div>
            </div>
            """)
            
            gr.HTML("""
            <div class="feature-card">
                <div class="feature-card-content">
                    <div class="feature-icon">⚖️</div>
                    <h3 class="feature-title">平衡調和</h3>
                    <p class="feature-description">協助您達到陰陽平衡，改善體質狀態</p>
                </div>
            </div>
            """)
        
        # 生成建議區域
        gr.HTML("""
        <div class="questionnaire-section">
            <h3 class="questionnaire-group-title">🌟 智能養生建議生成</h3>
            <p style="color: #64748b; font-size: 1.1rem; line-height: 1.6; margin-bottom: 20px;">
                系統將結合您的體質分析結果和食物辨識結果，運用中醫理論和現代營養學知識，
                為您量身定制個人化的養生建議。
            </p>
        </div>
        """)
        
        # 生成按鈕
        generate_advice_btn = gr.Button(
            "🌿 生成個人化養生建議", 
            variant="primary", 
            size="lg",
            elem_classes=["feature-button", "constitution-btn"]
        )
        
        # 建議輸出區域
        gr.HTML("""
        <div class="questionnaire-section">
            <h3 class="questionnaire-group-title">📋 您的專屬養生建議</h3>
        </div>
        """)
        
        advice_output = gr.Markdown(
            label="養生建議詳情",
            elem_classes=["advice-output-container"]
        )
        
        # 使用說明
        gr.HTML("""
        <div class="usage-section">
            <h3>📖 建議使用指南</h3>
            <ul>
                <li>🔍 請確保已完成體質分析和食物辨識</li>
                <li>📱 建議可截圖保存或分享給專業中醫師</li>
                <li>⏰ 建議實施過程中密切關注身體反應</li>
                <li>🔄 可根據季節變化重新生成建議</li>
                <li>💡 結合個人實際情況靈活調整</li>
            </ul>
        </div>
        """)
          # 免責聲明
        gr.HTML("""
        <div class="disclaimer-section">
            <h3>⚠️ 重要聲明</h3>
            <ul>
                <li>本系統提供的建議僅供參考，不能替代專業醫療診斷</li>
                <li>如有嚴重健康問題，請及時就醫諮詢</li>
                <li>體質調理需要時間，請耐心堅持</li>
                <li>個體差異較大，效果因人而異</li>
                <li>建議在專業中醫師指導下進行體質調理</li>
            </ul>
        </div>
        """)
        
        def get_advice(constitution_result, food_result):
            if not constitution_result:
                return """
## ⚠️ 體質分析未完成

請先前往 **體質分析** 頁面完成體質測試，了解您的中醫體質特點。

### 📋 體質分析包含：
- 🔍 20題專業體質問卷
- 📊 九大體質類型評估  
- 🎯 個人體質特徵分析
- 💡 基礎調理建議

完成體質分析後，即可獲得更精確的個人化養生建議。
"""
            if not food_result:
                return """
## ⚠️ 食物辨識未完成

請先前往 **食物辨識** 頁面上傳食物圖片，分析食物的五性屬性。

### 📸 食物辨識包含：
- 🍎 智能食物識別
- 🌡️ 五性屬性分析（寒、涼、平、溫、熱）
- ⚖️ 體質適配度評估
- 📈 營養價值分析

完成食物辨識後，結合體質分析，即可生成完整的養生建議。
"""
            
            try:
                # 生成建議
                advice = generate_health_advice(constitution_result, food_result)
                
                # 在建議前添加完成的進度指示器
                final_progress = """
<div class="progress-indicator">
    <div class="progress-step">
        <div class="progress-step-icon completed">✓</div>
        <div class="progress-step-label">體質分析</div>
    </div>
    <div class="progress-step">
        <div class="progress-step-icon completed">✓</div>
        <div class="progress-step-label">食物辨識</div>
    </div>
    <div class="progress-step">
        <div class="progress-step-icon completed">✓</div>
        <div class="progress-step-label">AI分析</div>
    </div>
    <div class="progress-step">
        <div class="progress-step-icon completed">✓</div>
        <div class="progress-step-label">建議生成</div>
    </div>
</div>

---

"""
                return final_progress + advice
                
            except Exception as e:
                return f"""
## ❌ 建議生成失敗

生成養生建議時遇到了問題：{str(e)}

### 💡 解決方案：
- 🔄 請檢查網絡連接後重試
- ⚙️ 確認AI服務配置正確
- 📞 如問題持續，請聯繫技術支援

您也可以：
- 📱 截圖保存已有的體質和食物分析結果
- 👨‍⚕️ 諮詢專業中醫師進行人工分析
"""
        
        generate_advice_btn.click(
            fn=get_advice,
            inputs=[constitution_result_state, food_result_state],
            outputs=[advice_output]
        )
        
        return advice_output 