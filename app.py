# app.py - 主應用程式
import gradio as gr
import os
from pathlib import Path
from food_recognition import build_food_recognition_page
from constitution_analysis import build_constitution_analysis_page
from health_advice import build_health_advice_page

# 設置靜態資源路徑
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

def create_hero_image():
    """提供預設的線上圖片或本地圖片"""
    img_path = STATIC_DIR / "main_vision.png"
    if img_path.exists():
        return str(img_path)
    
    # 使用線上的中醫相關圖片作為預設
    return "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=500&h=300&fit=crop&crop=center"

def build_main_app():
    """建立主應用程式"""
    hero_image_path = create_hero_image()
    
    with gr.Blocks(
        title="中醫食物寒熱辨識與體質分析系統",
        theme=gr.themes.Soft().set(
            body_background_fill="#F0F5F0",
            background_fill_primary="#F0F5F0",
            background_fill_secondary="#F0F5F0",
            block_background_fill="#F0F5F0",
            panel_background_fill="#F0F5F0"
        ),head="""
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        /* 移除字體相關的404錯誤 */
        * {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        }
        </style>
        <style id="force-body-bg">
        /* 強力覆蓋最外層背景 - 仿照成功案例 */
        html, body {
            background: #F0F5F0 !important;
            background-color: #F0F5F0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* 針對Gradio可能的根元素 */
        .gradio-app, gradio-app, .gradio-container, .contain,
        #root, #gradio-root, [data-testid="main"], 
        .app, .main, .container, .wrapper {
            background: transparent !important;
            background-color: transparent !important;
        }
        
        /* 極端測試方案 - 強制所有body內元素背景透明 */
        body * {
            background-color: transparent !important;
        }
        
        /* 然後重新設定需要背景的元素 */
        .main-content {
            background: #F8FBF6 !important;
        }
        
        .feature-card {
            background: #FEFCF8 !important;
        }
        
        .workflow-step {
            background: #f8fafc !important;
        }
        
        .disclaimer-section {
            background: #F8F5F0 !important;
        }
        
        .usage-section {
            background: #F0F7F0 !important;
        }
        
        .progress-section {
            background: #f8fafc !important;
        }
        
        .progress-item {
            background: rgba(255, 255, 255, 0.8) !important;
        }
        
        .step-number {
            background: #6A9A4E !important;
        }
        </style>
        <style>
        /* 確保SVG圖片正確顯示 */
        img[src*="data:image/svg+xml"] {
            max-width: 100% !important;
            height: auto !important;
            display: block !important;
            border-radius: 15px !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3) !important;
        }        /* 主容器設計 - 中醫風格 */
        .gradio-container {
            max-width: none !important;
            margin: 0 !important;
            padding: 0 !important;
            background: #F0F5F0 !important; /* 統一淺綠色背景 */
            min-height: 100vh;
            position: relative;
            overflow: hidden;
        }
          /* 創建中醫風格背景圖案 */
        .gradio-container::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 25% 25%, rgba(144, 180, 144, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, rgba(212, 175, 55, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(139, 69, 19, 0.08) 0%, transparent 40%),
                linear-gradient(45deg, rgba(106, 153, 78, 0.1) 25%, transparent 25%), 
                linear-gradient(-45deg, rgba(106, 153, 78, 0.1) 25%, transparent 25%);
            background-size: 150px 150px, 120px 120px, 200px 200px, 60px 60px, 60px 60px;
            background-position: 0 0, 60px 60px, 100px 100px, 0 0, 30px 30px;
            opacity: 0.5;
            z-index: 0;
        }        /* 移除所有白邊 */
        body {
            margin: 0 !important;
            padding: 0 !important;
            background: #F0F5F0 !important;
        }
        
        /* 確保全屏背景 */
        #root, .gradio-app {
            margin: 0 !important;
            padding: 0 !important;
            background: #F0F5F0 !important;
        }
        
        /* 修正根元素 */
        * {
            box-sizing: border-box;
        }
        
        /* 確保 gradio 元素透明 */
        .gr-panel, .gr-tab-nav {
            background: transparent !important;
        }        /* 主內容區域 */
        .main-content {
            background: #F8FBF6;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(106, 153, 78, 0.3);
            margin: 20px;
            width: calc(100% - 40px);
            box-sizing: border-box;
            position: relative;
            z-index: 1;
            overflow: hidden;
        }
        
        .main-content::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 20%, rgba(106, 153, 78, 0.05) 0%, transparent 30%),
                radial-gradient(circle at 80% 80%, rgba(212, 175, 55, 0.05) 0%, transparent 30%);
            z-index: -1;
        }
          /* 英雄區域 */
        .hero-section {
            text-align: center;
            margin-bottom: 20px;
            padding: 20px 0 10px 0;
            position: relative;
        }          /* 主圖 */
        .hero-image {
            max-width: 500px;
            margin: 0 auto 30px auto;
            display: block;
            border-radius: 15px;
            box-shadow: none;
            background: transparent;
        }        /* 確保主視覺圖片正確載入 - 融入背景樣式 */
        .hero-image img {
            width: 100% !important;
            max-width: 500px !important;
            height: 300px !important;
            object-fit: contain !important;
            margin: 0 auto 30px auto !important;
            display: block !important;
            border-radius: 15px !important;
            box-shadow: none !important;
            opacity: 0.9 !important;
            filter: blur(0.5px) brightness(1.1) contrast(0.95) !important;
            background: transparent !important;
            border: none !important;
        }
        
        /* 圖片容器融入背景 */
        .hero-image {
            position: relative !重要;
            margin: 0 auto 30px auto !重要;
            max-width: 500px !重要;
            background: transparent !重要;
        }
        
        .hero-image::before {
            content: '';
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
            background: linear-gradient(135deg, rgba(232, 111, 56, 0.1) 0%, rgba(249, 168, 38, 0.1) 100%);
            border-radius: 20px;
            z-index: -1;
            opacity: 0.3;
        }
        
        /* 如果圖片載入失敗，顯示替代的視覺元素 */
        .hero-visual-fallback {
            width: 100%;
            max-width: 500px;
            height: 300px;
            margin: 0 auto 30px auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #E86F38 0%, #F9A826 100%);
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            color: white;
            text-align: center;
        }
        
        .hero-visual-fallback h2 {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
            color: white !重要;
        }
        
        .hero-visual-fallback p {
            font-size: 1.2rem;
            opacity: 0.9;
            color: white !重要;
        }
        
        .hero-visual-fallback .feature-icons {
            display: flex;
            gap: 40px;
            margin-top: 20px;
        }
        
        .hero-visual-fallback .feature-icon-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: white;
        }
        
        .hero-visual-fallback .feature-icon-item .icon {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 8px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .hero-visual-fallback .feature-icon-item .label {
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .hero-visual-container {
            width: 100%;
            max-width: 500px;
            height: 300px;
            margin: 0 auto 30px auto;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .hero-visual-html {
            width: 100%;
            height: 100%;
            position: relative;
            background: linear-gradient(135deg, #E86F38 0%, #F9A826 100%);
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        .hero-visual-html::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.2;
        }
        
        .connecting-lines {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 1;
        }
        
        .line {
            position: absolute;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 2px;
        }
        
        .line-1 {
            width: 100px;
            height: 2px;
            top: 50%;
            left: 30%;
            transform: rotate(-30deg);
            animation: lineGlow 3s ease-in-out infinite;
        }
        
        .line-2 {
            width: 80px;
            height: 2px;
            bottom: 30%;
            left: 35%;
            transform: rotate(45deg);
            animation: lineGlow 3s ease-in-out infinite 1s;
        }
        
        .line-3 {
            width: 90px;
            height: 2px;
            bottom: 30%;
            right: 35%;
            transform: rotate(-45deg);
            animation: lineGlow 3s ease-in-out infinite 2s;
        }
        
        @keyframes lineGlow {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.7; }
        }
        
        .main-circle {
            width: 120px;
            height: 120px;
            background: rgba(255, 255, 255, 0.2);
            border: 3px solid rgba(255, 255, 255, 0.6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            position: relative;
            z-index: 2;
        }
        
        .sub-circle-1, .sub-circle-2, .sub-circle-3 {
            position: absolute;
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.15);
            border: 2px solid rgba(255, 255, 255, 0.4);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            color: white;
            font-weight: 500;
        }
        
        .sub-circle-1 {
            top: 30px;
            left: 80px;
        }
        
        .sub-circle-2 {
            bottom: 50px;
            left: 50px;
        }
        
        .sub-circle-3 {
            bottom: 50px;
            right: 50px;
        }
        
        /* 添加動畫效果 */
        .hero-visual .main-circle {
            animation: pulse 3s ease-in-out infinite;
        }
        
        .sub-circle-1 {
            animation: float 4s ease-in-out infinite;
        }
        
        .sub-circle-2 {
            animation: float 4s ease-in-out infinite 1s;
        }
        
        .sub-circle-3 {
            animation: float 4s ease-in-out infinite 2s;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }        /* 主標題 */
        .main-title {
            color: #6A9A4E;
            font-size: 4.8rem;
            font-weight: 700;
            margin-bottom: 30px;
            line-height: 1.2;
            position: relative;
            display: inline-block;
            text-align: center;
        }
        
        .main-title::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 25%;
            width: 50%;
            height: 4px;
            background: #D4AF37;
            border-radius: 2px;
        }/* 副標題 */
        .subtitle {
            color: #2D5016 !important;
            font-size: 1.3rem;
            margin-bottom: 40px;
            margin-top: 10px;
            font-weight: 400;
            line-height: 1.6;
        }
        
        /* 無上邊距樣式 */
        .no-top-margin {
            margin-top: 0;
            padding-top: 0;
        }
        
        /* 章節標題 */
        .section-title {
            text-align: center !重要;
            color: #1e293b !重要;
            font-size: 1.8rem !重要;
            font-weight: 600 !重要;
            margin: 50px 0 30px 0 !重要;
        }
        
        /* 功能卡片行 */
        .feature-cards-row {
            margin: 40px 0 !重要;
            gap: 30px !重要;
        }        /* 功能卡片 */
        .feature-card {
            background: #FEFCF8;
            border-radius: 20px;
            padding: 40px 30px;
            margin: 0 !重要;
            box-shadow: 0 12px 40px rgba(139, 69, 19, 0.12);
            border: 2px solid rgba(212, 175, 55, 0.2);
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            position: relative;
            overflow: hidden;
            min-height: 320px;
            display: flex !重要;
            flex-direction: column !重要;
        }
        
        .feature-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 24px 60px rgba(139, 69, 19, 0.2);
            border-color: rgba(212, 175, 55, 0.4);
        }        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: #6A9A4E;
        }
        
        /* 功能卡片內容 */
        .feature-card-content {
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .feature-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            display: block;
        }
        
        .feature-title {
            color: #1e293b !important;
            font-size: 1.6rem !important;
            font-weight: 600 !important;
            margin: 15px 0 !important;
        }
        
        .feature-description {
            color: #64748b !重要;
            font-size: 1rem !重要;
            line-height: 1.6 !重要;
            margin-bottom: 25px !重要;
        }
        
        /* 功能按鈕 */
        .feature-button {
            height: 50px !重要;
            font-size: 1rem !重要;
            font-weight: 600 !重要;
            border-radius: 12px !重要;
            transition: all 0.3s ease !重要;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !重要;
            margin-top: auto !重要;
        }
        
        .feature-button:hover {
            transform: translateY(-2px) !重要;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !重要;
        }        /* 按鈕顏色 - 中醫傳統配色 */
        .constitution-btn {
            background: #6A9A4E !important;
            color: white !important;
            border: none !important;
        }
        
        .secondary-btn {
            background: #8B4513 !important;
            color: white !important;
            border: none !important;
        }
        
        .tertiary-btn {
            background: #B22222 !important;
            color: white !important;
            border: none !important;
        }
        
        /* 強化按鈕樣式 - 覆蓋所有可能的Gradio默認樣式 */
        .gr-button.constitution-btn,
        button.constitution-btn,
        .constitution-btn button,
        [class*="constitution-btn"] {
            background-color: #6A9A4E !important;
            background: #6A9A4E !important;
            color: white !important;
            border: none !important;
        }
        
        .gr-button.secondary-btn,
        button.secondary-btn,
        .secondary-btn button,
        [class*="secondary-btn"] {
            background-color: #8B4513 !important;
            background: #8B4513 !important;
            color: white !important;
            border: none !important;
        }
        
        .gr-button.tertiary-btn,
        button.tertiary-btn,
        .tertiary-btn button,
        [class*="tertiary-btn"] {
            background-color: #B22222 !important;
            background: #B22222 !important;
            color: white !important;
            border: none !important;
        }
        
        /* 確保按鈕文字可見性 */
        .feature-button,
        .feature-button span,
        .feature-button *,
        .gr-button span,
        .gr-button * {
            color: white !important;
            text-shadow: none !important;
        }
        
        /* 覆蓋hover狀態 */
        .constitution-btn:hover,
        .gr-button.constitution-btn:hover {
            background-color: #5A8A3E !important;
            color: white !important;
        }
        
        .secondary-btn:hover,
        .gr-button.secondary-btn:hover {
            background-color: #7A3F12 !important;
            color: white !important;
        }
        
        .tertiary-btn:hover,
        .gr-button.tertiary-btn:hover {
            background-color: #A01F1F !important;
            color: white !important;
        }
        
        /* 返回按鈕強化 */
        .back-button,
        .gr-button.back-button {
            background-color: #6b7280 !important;
            color: white !important;
            border: none !important;
        }
        
        .back-button:hover,
        .gr-button.back-button:hover {
            background-color: #5b6470 !important;
            color: white !important;
        }
        
        /* 確保所有按鈕都有正確的顏色 */
        .gr-button {
            color: white !important;
        }
        
        /* 特別處理可能的文字顏色問題 */
        button, .gr-button {
            color: white !important;
        }
        
        button span, .gr-button span {
            color: white !important;
        }
          /* 工作流程區域 */
        .workflow-row {
            margin: 30px 0 !重要;
            gap: 25px !重要;
        }
        
        .workflow-step {
            background: #f8fafc;
            border-radius: 16px;
            padding: 30px 20px;
            text-align: center;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            position: relative;
        }
        
        .workflow-step:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        }        .step-number {
            background: #6A9A4E;
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            font-weight: 700;
            margin: 0 auto 20px auto;
        }
        
        .workflow-step h4 {
            color: #1e293b !重要;
            font-size: 1.2rem !重要;
            font-weight: 600 !重要;
            margin: 15px 0 10px 0 !重要;
        }
        
        .workflow-step p {
            color: #64748b !重要;
            font-size: 0.95rem !重要;
            line-height: 1.5 !重要;
            margin: 0 !重要;
        }
        
        /* 進度容器 */
        .progress-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            align-items: center;
        }
        
        .progress-item {
            display: flex !重要;
            align-items: center !重要;
            background: rgba(255, 255, 255, 0.8);
            padding: 15px 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.5);
            font-size: 1.1rem !重要;
            min-width: 300px;
            justify-content: flex-start;
        }
        
        .progress-icon {
            margin-right: 15px !重要;
            font-size: 1.2rem !重要;
        }
        
        .progress-text {
            font-weight: 500 !重要;
            color: #374151 !重要;
        }
          /* 進度區域 */
        .progress-section {
            background: #f8fafc;
            border-radius: 20px;
            padding: 40px;
            margin: 40px 0;
            border: 1px solid #e2e8f0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
        }        /* 使用說明區域 */
        .usage-section {
            background: #F0F7F0;
            border-radius: 20px;
            padding: 30px;
            margin: 25px 0;
            border: 2px solid rgba(106, 153, 78, 0.3);
            box-shadow: 0 6px 24px rgba(106, 153, 78, 0.1);
        }
        
        .usage-section h3 {
            color: #4A6741 !重要;
            font-size: 1.3rem !重要;
            font-weight: 600 !重要;
            margin-bottom: 20px !重要;
        }
        
        .usage-section ul {
            text-align: left !重要;
            color: #6A9A4E !重要;
        }
        
        .usage-section li {
            margin: 8px 0 !重要;
            color: #6A9A4E !重要;
        }        /* 免責聲明區域 - 改為更溫和的顏色 */
        .disclaimer-section {
            background: linear-gradient(135deg, #FFF8F5 0%, #F8F5F0 100%) !important;
            border-radius: 20px;
            padding: 30px;
            margin: 25px 0;
            border: 2px solid rgba(139, 69, 19, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .disclaimer-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 20%, rgba(139, 69, 19, 0.05) 0%, transparent 30%),
                radial-gradient(circle at 80% 80%, rgba(212, 175, 55, 0.03) 0%, transparent 30%);
            z-index: 0;
        }
        
        .disclaimer-section h3 {
            color: #8B4513 !important;
            font-size: 1.3rem !important;
            font-weight: 600 !important;
            margin-bottom: 20px !important;
            position: relative;
            z-index: 1;
        }
        
        .disclaimer-section ul {
            text-align: left !important;
            color: #5D2F0C !important;
            position: relative;
            z-index: 1;
        }
        
        .disclaimer-section li {
            margin: 8px 0 !important;
            color: #5D2F0C !important;
        }
          /* 返回按鈕 */
        .back-button {
            background: #6b7280 !重要;
            color: white !重要;
            border: none !重要;
            border-radius: 10px !重要;
            padding: 12px 24px !重要;
            margin-bottom: 30px !重要;
            font-size: 1rem !重要;
            font-weight: 500 !重要;
            transition: all 0.3s ease !重要;
        }
        
        .back-button:hover {
            transform: translateY(-2px) !重要;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !重要;
        }/* 頁面標題 */
        .page-title {
            color: #6A9A4E;
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 40px;
            text-align: center;
        }
          /* 響應式設計 */        @media (max-width: 1200px) {
            .gradio-container {
                max-width: 100% !重要;
                padding: 30px !重要;
            }
            .main-content {
                padding: 30px;
            }
            .feature-card {
                min-height: 280px;
            }
            .main-title {
                font-size: 3.5rem;
            }
            .hero-image, #main_vision {
                max-width: 400px;
            }
        }
        
        @media (max-width: 768px) {
            .gradio-container {
                padding: 20px !重要;
            }
            .main-content {
                padding: 25px;
            }
            .feature-card {
                min-height: 250px;
                padding: 25px 20px;
            }
            .main-title {
                font-size: 2.5rem;
            }
            .subtitle {
                font-size: 1.1rem;
            }
            .hero-image, #main_vision {
                max-width: 300px;
            }
        }
        
        /* 統一文字樣式 */
        h1, h2, h3 {
            color: #1e293b !重要;
        }
        
        /* 覆蓋 Gradio 默認樣式 */
        .gr-button {
            font-weight: 600 !重要;
        }
        
        .gr-markdown h1,
        .gr-markdown h2,
        .gr-markdown h3 {
            text-align: center !重要;
        }
          /* 強化字體顏色可見性 - 全面覆蓋 */
        .gr-markdown, .gr-markdown p, .gr-markdown h1, .gr-markdown h2, .gr-markdown h3 {
            color: #1e293b !important;
        }
        
        /* 確保所有文字都有明確的深色顏色 */
        p, div, span, li, strong, em, b, i {
            color: #1e293b !important;
        }
        
        /* 特別處理可能的白色文字問題 */
        .feature-title, .feature-description, .workflow-step h4, .workflow-step p {
            color: #1e293b !important;
        }
        
        /* 確保副標題顏色正確 */
        .subtitle {
            color: #2D5016 !important;
        }
        
        /* 確保章節標題顏色正確 */
        .section-title {
            color: #1e293b !important;
        }
        
        /* 強制所有 Markdown 內容為深色 */
        .gr-markdown * {
            color: #1e293b !important;
        }
        
        /* 修正主標題顏色 */
        .main-title {
            color: #6A9A4E !important;
        }
        
        /* 修正重要聲明區域文字顏色 */
        .disclaimer-section * {
            color: #5D2F0C !important;
        }
        
        .disclaimer-section h3 {
            color: #8B4513 !important;
        }
        
        /* 修正使用說明區域文字顏色 */
        .usage-section * {
            color: #4A6741 !important;
        }
        
        .usage-section h3 {
            color: #4A6741 !important;
        }
        
        /* 修正工作流程文字顏色 */
        .workflow-step-compact * {
            color: #1e293b !important;
        }
        
        .workflow-step-compact h4 {
            color: #1e293b !important;
        }
        
        .workflow-step-compact p {
            color: #64748b !important;
        }
        
        /* 修正功能卡片文字顏色 */
        .feature-card * {
            color: #1e293b !important;
        }
        
        .feature-title {
            color: #1e293b !important;
        }
        
        .feature-description {
            color: #64748b !important;
        }
        
        /* 覆蓋所有可能的白色文字 */
        [style*="color: white"], [style*="color: #fff"], [style*="color: #ffffff"] {
            color: #1e293b !important;
        }        /* 主視覺圖片和工作流程並排區域 */
        .main-visual-workflow-row {
            margin: 40px 0 !important;
            gap: 40px !important;
            align-items: center !important;
        }
        
        /* 左側視覺欄位 */
        .visual-column {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
          /* 右側工作流程欄位 */
        .workflow-column {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            position: relative !important;
        }
        
        /* 工作流程標題 */
        .workflow-title {
            color: #1e293b !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            margin-bottom: 25px !important;
            text-align: center !important;
            position: absolute !important;
            top: -60px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 100% !important;
        }
          /* 工作流程步驟容器 - 整體長方形區域 */
        .workflow-steps-container {
            background: #f8fafc;
            border-radius: 16px;
            padding: 30px 25px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            display: flex !important;
            flex-direction: column !important;
            gap: 15px !important;
            width: 100% !important;
            height: 100% !important;
            min-height: 350px !important;
            justify-content: center !important;
        }
        
        /* 緊湊型工作流程步驟 */
        .workflow-step-compact {
            background: #ffffff;
            border-radius: 12px;
            padding: 18px 20px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 15px;
            width: 100%;
        }
        
        .workflow-step-compact:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .workflow-step-compact .step-number {
            background: #6A9A4E;
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            font-weight: 700;
            margin: 0;
            flex-shrink: 0;
        }
        
        .workflow-step-compact .step-content {
            flex: 1;
        }
        
        .workflow-step-compact h4 {
            color: #1e293b !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            margin: 0 0 4px 0 !important;
        }
        
        .workflow-step-compact p {
            color: #64748b !important;
            font-size: 0.9rem !important;
            line-height: 1.4 !important;
            margin: 0 !important;
        }
          /* 有邊框的圖片樣式 - 無邊距 */
        .bordered-image img {
            border: 3px solid #6A9A4E !important;
            border-radius: 15px !important;
            box-shadow: 0 8px 30px rgba(106, 154, 78, 0.3) !important;
            padding: 0 !important;
            margin: 0 !important;
            background: white !important;
        }
        
        .bordered-image {
            margin: 0 !important;
            padding: 0 !important;
            display: block !important;
        }

        /* 強力修正所有文字顏色問題 */
        
        /* 修正 HTML 內容中的文字顏色 */
        .hero-section * {
            color: inherit !important;
        }
        
        .hero-section h1 {
            color: #6A9A4E !important;
        }
        
        .hero-section p {
            color: #2D5016 !important;
        }
        
        /* 修正所有可能的白色文字 */
        * {
            color: inherit;
        }
        
        /* 確保所有元素都有深色文字 */
        body, html {
            color: #1e293b !important;
        }
        
        /* 修正 Gradio 組件中的白色文字 */
        .gr-panel *, .gr-form *, .gr-box * {
            color: #1e293b !important;
        }
        
        /* 修正所有標題 */
        h1, h2, h3, h4, h5, h6 {
            color: #1e293b !important;
        }
        
        /* 除了主標題保持綠色 */
        .main-title {
            color: #6A9A4E !important;
        }
        
        /* 修正所有段落和文字 */
        p, span, div, li, ul, ol {
            color: #1e293b !important;
        }
        
        /* 特殊區域的文字顏色 */
        .disclaimer-section p,
        .disclaimer-section li,
        .disclaimer-section span,
        .disclaimer-section div {
            color: #5D2F0C !important;
        }
        
        .disclaimer-section h3,
        .disclaimer-section h4 {
            color: #8B4513 !important;
        }
        
        /* 使用說明區域文字 */
        .usage-section p,
        .usage-section li,
        .usage-section span,
        .usage-section div {
            color: #4A6741 !important;
        }
        
        .usage-section h3,
        .usage-section h4 {
            color: #4A6741 !important;
        }
        
        /* 工作流程區域文字 */
        .workflow-step-compact div,
        .workflow-step-compact span {
            color: #1e293b !important;
        }
        
        /* 功能卡片內的所有文字 */
        .feature-card div,
        .feature-card span,
        .feature-card p,
        .feature-card h3 {
            color: #1e293b !important;
        }
        
        /* 強制覆蓋所有可能的白色樣式 */
        [style*="color:white"],
        [style*="color: white"],
        [style*="color:#fff"],
        [style*="color: #fff"],
        [style*="color:#ffffff"],
        [style*="color: #ffffff"],
        [style*="color:White"],
        [style*="color: White"] {
            color: #1e293b !important;
        }
        """
    ) as app:        # 全局狀態管理
        constitution_result_state = gr.State()
        food_result_state = gr.State()
        current_page = gr.State("home")        # 主頁面
        with gr.Column(visible=True, elem_classes=["main-content"]) as home_page:
            # 主標題和介紹
            gr.HTML("""
            <div class="hero-section">
                <h1 class="main-title">中醫食物寒熱辨識與體質分析系統</h1>
                <p class="subtitle">結合現代AI技術與傳統中醫理論，依照您的個人體質，提供專屬的飲食養生建議</p>
            </div>
            """)
            
            # 三個主要功能按鈕
            with gr.Row(elem_classes=["feature-cards-row"]):
                with gr.Column(scale=1, elem_classes=["feature-card"]):
                    gr.Markdown("""                    <div class="feature-card-content">
                    <div class="feature-icon">🔍</div>
                    <h3 class="feature-title">智慧體質分析</h3>
                    <p class="feature-description">基於中醫理論的20題問卷調查，AI精準分析您的體質類型</p>
                    </div>
                    """)
                    
                    constitution_btn = gr.Button(
                        "開始體質分析", 
                        variant="primary", 
                        size="lg",
                        elem_classes=["feature-button", "constitution-btn"]
                    )
                
                with gr.Column(scale=1, elem_classes=["feature-card"]):
                    gr.Markdown("""
                    <div class="feature-card-content">
                    <div class="feature-icon">📸</div>
                    <h3 class="feature-title">食物寒熱辨識</h3>
                    <p class="feature-description">上傳食物圖片，AI識別食材並分析其中醫屬性</p>
                    </div>                    """)
                    
                    food_btn = gr.Button(
                        "食物辨識", 
                        variant="secondary", 
                        size="lg",
                        elem_classes=["feature-button", "secondary-btn"]
                    )
                
                with gr.Column(scale=1, elem_classes=["feature-card"]):
                    gr.Markdown("""
                    <div class="feature-card-content">
                    <div class="feature-icon">💡</div>
                    <h3 class="feature-title">個人化建議</h3>
                    <p class="feature-description">結合體質分析和食物屬性，量身定制飲食建議</p>
                    </div>
                    """)
                    
                    advice_btn = gr.Button(
                        "養生建議", 
                        variant="secondary", 
                        size="lg",
                        elem_classes=["feature-button", "tertiary-btn"]
                    )            # 主視覺圖片和使用流程並排區域
            with gr.Row(elem_classes=["main-visual-workflow-row"]):
                # 左側：主視覺圖片
                with gr.Column(scale=2, elem_classes=["visual-column"]):
                    gr.Image(
                        value=hero_image_path,
                        show_label=False,
                        container=False,
                        elem_id="main_vision",
                        elem_classes=["hero-image", "bordered-image"],
                        height=350,
                        width=500,
                        show_fullscreen_button=False,
                        show_download_button=False,
                        interactive=False
                    )
                  # 右側：使用流程說明
                with gr.Column(scale=3, elem_classes=["workflow-column"]):
                    gr.Markdown("### 使用流程", elem_classes=["workflow-title"])
                    
                    # 將三個步驟放在一個整體容器中
                    gr.HTML("""
                    <div class="workflow-steps-container">
                        <div class="workflow-step-compact">
                            <div class="step-number">1</div>
                            <div class="step-content">
                                <h4>完成體質問卷</h4>
                                <p>回答20個關於身體狀況的問題</p>
                            </div>
                        </div>
                        
                        <div class="workflow-step-compact">
                            <div class="step-number">2</div>
                            <div class="step-content">
                                <h4>上傳食物圖片</h4>
                                <p>拍攝或選擇想要分析的食物</p>
                            </div>
                        </div>
                        
                        <div class="workflow-step-compact">
                            <div class="step-number">3</div>
                            <div class="step-content">
                                <h4>獲得個人建議</h4>
                                <p>查看量身定制的養生指導</p>
                            </div>
                        </div>
                    </div>
                    """)
            # 注意事項
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("""                    ### 重要聲明
                    - 本系統僾供**健康參考**使用
                    - **不能替代**專業醫療診斷
                    - 如有健康問題請**諮詢醫師**
                    - 建議結合**個人實際情況**調整
                    """, elem_classes=["disclaimer-section"])
        
        # 體質分析頁面
        with gr.Column(visible=False, elem_classes=["main-content"]) as constitution_page:
            back_to_home_1 = gr.Button("返回主頁", elem_classes=["back-button"])
            gr.Markdown("# 中醫體質分析", elem_classes=["page-title"])
            
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
            back_to_home_2 = gr.Button("返回主頁", elem_classes=["back-button"])
            gr.Markdown("# 食物寒熱辨識", elem_classes=["page-title"])
            
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
            back_to_home_3 = gr.Button("返回主頁", elem_classes=["back-button"])
            gr.Markdown("# 個人化養生建議", elem_classes=["page-title"])
            
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
            constitution_status = "✅" if constitution_result else "⭕"
            constitution_text = "已完成" if constitution_result else "未完成"
            
            food_status = "✅" if food_result else "⭕"
            food_text = "已完成" if food_result else "未完成"
            
            advice_status = "✅" if (constitution_result and food_result) else "⭕"
            advice_text = "可生成" if (constitution_result and food_result) else "未完成"
            
            return f"""
            <div class="progress-container">
            <div class="progress-item">
                <span class="progress-icon">{constitution_status}</span>
                <span class="progress-text">體質分析：{constitution_text}</span>
            </div>
            <div class="progress-item">
                <span class="progress-icon">{food_status}</span>
                <span class="progress-text">食物辨識：{food_text}</span>
            </div>
            <div class="progress-item">
                <span class="progress-icon">{advice_status}</span>
                <span class="progress-text">養生建議：{advice_text}</span>
            </div>
            </div>
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
            outputs=[]
        )
        
        food_result_state.change(
            fn=update_progress,
            inputs=[constitution_result_state, food_result_state],
            outputs=[]
        )
    
    return app

# --------------------------------------------------------------------------
# 啟動應用
# --------------------------------------------------------------------------
if __name__ == "__main__":
    app = build_main_app()
    app.launch(
        share=True,
        server_name="127.0.0.1",
        server_port=7861,
        show_error=True,
        favicon_path=None,
        ssl_verify=False,
        inbrowser=True
    )