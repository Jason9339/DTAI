# 🏥 中醫食物寒熱辨識與體質分析系統

## 📺 Demo 影片
[![Demo 影片](https://img.shields.io/badge/YouTube-Demo%20影片-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=qI0ZI-kMEPA)

結合現代AI技術與傳統中醫理論，為您提供個人化的養生建議。

---

## 🚀 快速開始

### 1. 設置虛擬環境（推薦）
為了避免依賴包衝突，建議使用虛擬環境：

```bash
# 創建虛擬環境
python3 -m venv dtai_env

# 啟動虛擬環境
# Linux/Mac:
source dtai_env/bin/activate
# Windows:
# dtai_env\Scripts\activate
```

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 下載 AI 模型
為了使用完整的食物辨識功能，請下載預訓練的 AI 模型：

```bash
chmod +x model.sh
./model.sh
```

**⚠️ 注意**：
- 模型檔案總大小約 2GB，下載需要時間。
- 模型檔案是系統正常運行的必要組件。
- 模型下載完成後，系統會自動使用真實的 AI 模型進行食物辨識。
- 包含 8 個不同架構的預訓練模型（ResNet、ConvNeXt、DenseNet、EfficientNet、Swin Transformer、SwinV2、ViT、VGG）。

### 4. 設置 API Key
1. 到 [Groq Console](https://console.groq.com/) 註冊並獲取免費的 API Key。
2. 設置環境變數：
   ```bash
   export GROQ_API_KEY=your_api_key_here
   ```
   或者在 Gradio 界面中直接輸入 API Key。

### 5. 運行應用
```bash
python3 app.py
```

系統將自動啟動並提供一個可分享的 Gradio 連結。

---

### 🏠 主頁面導航

系統採用主頁面導航設計，提供清晰的使用流程指引：

1.  **第一步：體質分析** 🏥
    *   點擊「開始體質分析」按鈕。
    *   完成20題問卷（15題選擇題 + 5題簡答題）。
    *   獲得 AI 生成的詳細體質分析報告。

2.  **第二步：食物辨識** 🍎
    *   點擊「食物辨識」按鈕。
    *   上傳食物圖片或選擇範例圖片。
    *   查看辨識結果和中醫屬性。

3.  **第三步：養生建議** 🌿
    *   點擊「養生建議」按鈕。
    *   AI 將結合體質分析和食物辨識結果生成個人化建議。

### 📊 進度追蹤

*   主頁面顯示當前完成進度。
*   支援任意順序使用各功能。
*   建議按順序完成以獲得最佳體驗。

---

## 🌟 主要功能

### 1. 🍎 食物辨識模組

*   **功能描述**：上傳食物圖片，系統自動辨識食材並提供中醫五性屬性。
*   **技術架構**：支援 ResNet、ConvNeXt、Swin Transformer、EfficientNet、VGG、DenseNet、ViT 等深度學習模型。
*   **輸出資訊**：
    *   食物名稱辨識（支援 183 種食物）
    *   五性屬性（寒、涼、平、溫、熱）
    *   歸經資訊
    *   功效說明
    *   辨識信心度
*   **模型效能**：
    *   Swin Transformer V2: 94% 準確率
    *   Swin Transformer: 94% 準確率
    *   ConvNeXt: 90% 準確率
    *   DenseNet: 86% 準確率
    *   EfficientNet: 84% 準確率

### AI 模型架構
*   **ResNet50**: 經典卷積神經網路，準確率 78%
*   **ConvNeXt**: 現代化卷積架構，準確率 90%
*   **DenseNet**: 密集連接網路，準確率 86%
*   **EfficientNet**: 高效能架構，準確率 84%
*   **Swin Transformer**: 視覺Transformer，準確率 94%
*   **Swin Transformer V2**: 改進版本，準確率 94%
*   **Vision Transformer (ViT)**: 純Transformer架構，準確率 74%
*   **VGG16**: 經典深度網路，準確率 78%

### 2. 🏥 體質推理模組

*   **功能描述**：透過20題中醫體質問卷分析使用者體質類型。
*   **分析方法**：使用 AI (Groq Llama-3.3-70B) 進行分析。
*   **問卷內容**：
    *   15題選擇題（可複選）
    *   5題開放式簡答題
*   **體質類型**：
    *   平和質：陰陽氣血調和，體質平和
    *   氣虛質：元氣不足，易疲勞乏力
    *   陽虛質：陽氣不足，畏寒怕冷
    *   陰虛質：陰液虧少，虛熱內擾
    *   痰濕質：痰濕凝聚，形體肥胖
    *   濕熱質：濕熱內蘊，面垢油膩
    *   血瘀質：血行不暢，膚色晦暗
    *   氣鬱質：氣機鬱滯，神情抑鬱
    *   特稟質：先天稟賦不足，過敏體質

### 3. 🌿 養生建議生成模組

*   **功能描述**：結合體質分析與食物屬性，使用 AI 生成個人化養生建議。
*   **AI 技術**：Groq Llama-3.3-70B 模型。
*   **建議內容**：
    *   針對性飲食建議
    *   需要避免的食物或行為
    *   推薦的其他食物搭配
---

## ⚠️ 免責聲明

本系統僅供學習和參考使用，不能替代專業醫療建議。如有健康問題，請諮詢合格的中醫師或醫療專業人員。

---

## 📄 授權

本項目採用 MIT 授權條款。

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個項目！