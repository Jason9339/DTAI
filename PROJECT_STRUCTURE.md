# 項目結構說明

## 📁 文件組織

```
DTAI/
├── app.py                    # 主應用程式入口
├── main.py                   # 舊版單文件應用（已重構）
├── config.py                 # 配置文件（常量、資料庫、問卷）
├── utils.py                  # 工具函數（AI 客戶端初始化）
├── food_recognition.py       # 食物辨識模組
├── constitution_analysis.py  # 體質分析模組
├── health_advice.py         # 養生建議生成模組
├── requirements.txt         # 依賴包列表
├── README.md               # 項目說明文件
└── PROJECT_STRUCTURE.md    # 本文件
```

## 🔧 模組說明

### `app.py` - 主應用程式
- 整合所有功能模組
- 建立 Gradio 界面
- 處理模組間的狀態傳遞
- **運行方式**: `python3 app.py`

### `config.py` - 配置文件
- 中醫食物屬性資料庫 (`FOOD_DATABASE`)
- 體質類型定義 (`CONSTITUTION_TYPES`)
- 20題體質問卷 (`CONSTITUTION_QUESTIONS`)

### `utils.py` - 工具函數
- AI 客戶端初始化 (`get_ai_client()`)
- 環境變數載入
- 共用工具函數

### `food_recognition.py` - 食物辨識模組
- 食物圖片辨識功能 (`classify_food_image()`)
- 食物辨識頁面建構 (`build_food_recognition_page()`)
- 返回辨識結果和狀態

### `constitution_analysis.py` - 體質分析模組
- AI 體質分析功能 (`analyze_constitution_with_llm()`)
- 問卷處理和 prompt 生成
- 體質分析頁面建構 (`build_constitution_analysis_page()`)
- API Key 設置功能

### `health_advice.py` - 養生建議生成模組
- AI 養生建議生成 (`generate_health_advice_with_llm()`)
- 結合體質和食物資訊
- 養生建議頁面建構 (`build_health_advice_page()`)

## 🚀 使用方式

### 開發模式
```bash
# 運行新的模組化版本
python3 app.py

# 或運行舊版單文件版本
python3 main.py
```

### 模組導入
```python
# 在其他項目中使用
from food_recognition import classify_food_image
from constitution_analysis import analyze_constitution
from health_advice import generate_health_advice
```

## 🔄 狀態管理

各模組通過 Gradio State 組件進行狀態傳遞：

1. **食物辨識** → `food_result_state`
2. **體質分析** → `constitution_result_state`
3. **養生建議** ← 接收前兩個狀態

## 📦 依賴管理

所有依賴統一在 `requirements.txt` 中管理：
- `gradio>=4.0.0` - Web 界面框架
- `aisuite>=0.1.0` - AI 模型統一接口
- `python-dotenv>=0.19.0` - 環境變數管理
- `Pillow>=9.0.0` - 圖片處理
- `docstring_parser>=0.16` - aisuite 依賴

## 🎯 優勢

1. **模組化設計**: 每個功能獨立，易於維護和擴展
2. **清晰分離**: 配置、工具、業務邏輯分離
3. **可重用性**: 各模組可獨立使用
4. **易於測試**: 每個模組可單獨測試
5. **團隊協作**: 不同開發者可負責不同模組 