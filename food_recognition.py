# food_recognition.py - 食物辨識模組
import random
import gradio as gr
from typing import Dict
from PIL import Image
import os
import pandas as pd
from config import FOOD_DATABASE
import numpy as np

# 嘗試導入PyTorch，如果失敗則使用模擬模式
try:
    import torch
    import torch.nn as nn
    from torchvision import transforms
    import timm  # 用於載入預訓練模型架構
    TORCH_AVAILABLE = True
    print("✅ PyTorch已載入，使用完整AI模型功能")
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch未安裝，使用模擬模式")
    # 創建模擬的torch模組
    class MockTorch:
        @staticmethod
        def device(device_type):
            return "cpu"
        
        @staticmethod  
        def no_grad():
            class MockContext:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            return MockContext()
    
    torch = MockTorch()

# 全域變數來快取已載入的模型
_loaded_models = {}

# 訓練時使用的標籤列表 (必須與訓練時一致)
TRAINING_LABELS = ['Abalone', 'Abalonemushroom', 'Achoy', 'Adzukibean', 'Alfalfasprouts', 'Almond', 'Apple', 'Asparagus', 'Avocado', 'Babycorn', 'Bambooshoot', 'Banana', 'Beeftripe', 'Beetroot', 'Birds-nestfern', 'Birdsnest', 'Bittermelon', 'Blackmoss', 'Blackpepper', 'Blacksoybean', 'Blueberry', 'Bokchoy', 'Brownsugar', 'Buckwheat', 'Cabbage', 'Cardamom', 'Carrot', 'Cashewnut', 'Cauliflower', 'Celery', 'Centuryegg', 'Cheese', 'Cherry', 'Chestnut', 'Chilipepper', 'Chinesebayberry', 'Chinesechiveflowers', 'Chinesechives', 'Chinesekale', 'Cilantro', 'Cinnamon', 'Clove', 'Cocoa', 'Coconut', 'Corn', 'Cowpea', 'Crab', 'Cream', 'Cucumber', 'Daikon', 'Dragonfruit', 'Driedpersimmon', 'Driedscallop', 'Driedshrimp', 'Duckblood', 'Durian', 'Eggplant', 'Enokimushroom', 'Fennel', 'Fig', 'Fishmint', 'Freshwaterclam', 'Garlic', 'Ginger', 'Glutinousrice', 'Gojileaves', 'Grape', 'Grapefruit', 'GreenSoybean', 'Greenbean', 'Greenbellpepper', 'Greenonion', 'Guava', 'Gynuradivaricata', 'Headingmustard', 'Honey', 'Jicama', 'Jobstears', 'Jujube', 'Kale', 'Kelp', 'Kidneybean', 'Kingoystermushroom', 'Kiwifruit', 'Kohlrabi', 'Kumquat', 'Lettuce', 'Limabean', 'Lime', 'Lobster', 'Longan', 'Lotusroot', 'Lotusseed', 'Luffa', 'Lychee', 'Madeira_vine', 'Maitakemushroom', 'Mandarin', 'Mango', 'Mangosteen', 'Milk', 'Millet', 'Minongmelon', 'Mint', 'Mungbean', 'Napacabbage', 'Natto', 'Nori', 'Nutmeg', 'Oat', 'Octopus', 'Okinawaspinach', 'Okra', 'Olive', 'Onion', 'Orange', 'Oystermushroom', 'Papaya', 'Parsley', 'Passionfruit', 'Pea', 'Peach', 'Peanut', 'Pear', 'Pepper', 'Perilla', 'Persimmon', 'Pickledmustardgreens', 'Pineapple', 'Pinenut', 'Plum', 'Pomegranate', 'Pomelo', 'Porktripe', 'Potato', 'Pumpkin', 'Pumpkinseed', 'Quailegg', 'Radishsprouts', 'Rambutan', 'Raspberry', 'Redamaranth', 'Reddate', 'Rice', 'Rosemary', 'Safflower', 'Saltedpotherbmustard', 'Seacucumber', 'Seaurchin', 'Sesameseed', 'Shaggymanemushroom', 'Shiitakemushroom', 'Shrimp', 'Snowfungus', 'Soybean', 'Soybeansprouts', 'Soysauce', 'Staranise', 'Starfruit', 'Strawberry', 'Strawmushroom', 'Sugarapple', 'Sunflowerseed', 'Sweetpotato', 'Sweetpotatoleaves', 'Taro', 'Thyme', 'Tofu', 'Tomato', 'Wasabi', 'Waterbamboo', 'Watercaltrop', 'Watermelon', 'Waterspinach', 'Waxapple', 'Wheatflour', 'Wheatgrass', 'Whitepepper', 'Wintermelon', 'Woodearmushroom', 'Yapear', 'Yauchoy', 'spinach']

def normalize_name(name):
    """
    將英文名稱轉換為正規化格式（移除空格、連字符等，轉為小寫）
    Args:
        name: 需要正規化的名稱
    Returns:
        正規化後的名稱
    """
    if pd.isna(name) or not name:
        return ""
    # 移除空格、連字符、底線，轉為小寫
    normalized = str(name).replace(" ", "").replace("-", "").replace("_", "").lower()
    return normalized

def map_training_label_to_database(training_label: str) -> str:
    """
    將訓練標籤映射到資料庫中的食物名稱
    Args:
        training_label: 從模型預測得到的訓練標籤 (英文)
    Returns:
        對應的資料庫食物名稱 (中文)，如果找不到則返回 None
    """
    # 模型輸出是英文，直接使用正規化名稱匹配英文名稱
    normalized_training = normalize_name(training_label)
    
    # 檢查資料庫中所有英文名稱的正規化版本
    for chinese_name, food_info in FOOD_DATABASE.items():
        english_name = food_info.get("英文名", "")
        if english_name:
            normalized_english = normalize_name(english_name)
            if normalized_training == normalized_english:
                print(f"英文名稱匹配成功: '{training_label}' -> '{chinese_name}' (通過英文名: '{english_name}')")
                return chinese_name
    
    # 如果找不到匹配項目，返回 None
    print(f"無法找到匹配項目: '{training_label}'")
    return None

def create_model_architecture(model_name: str, num_classes: int = None, state_dict: dict = None):
    """
    根據模型名稱創建對應的模型架構
    Args:
        model_name: 模型名稱
        num_classes: 分類數量，如果為 None 則自動推測
        state_dict: 模型的 state_dict，用於檢測架構變體
    """
    # 如果沒有指定 num_classes，使用 183 個類別
    if num_classes is None:
        num_classes = 183
    
    if 'swinv2' in model_name.lower():
        # Swin Transformer V2 - 使用與訓練時相同的模型架構
        model = timm.create_model('swinv2_base_window12_192', 
                                pretrained=False, 
                                num_classes=num_classes)
    elif 'swin' in model_name.lower() and 'swinv2' not in model_name.lower():
        # Swin Transformer V1 - 確保不是 V2
        model = timm.create_model('swin_base_patch4_window7_224', 
                                pretrained=False, 
                                num_classes=num_classes)
    elif 'vit' in model_name.lower():
        # Vision Transformer
        model = timm.create_model('vit_base_patch16_224', 
                                pretrained=False, 
                                num_classes=num_classes)
    elif 'convnext' in model_name.lower():
        # ConvNeXt - 使用 torchvision（與用戶訓練程式碼一致）
        from torchvision import models
        import torch.nn as nn
        
        model = models.convnext_base(weights=None)
        
        # 修改分類器的最後一層以匹配類別數
        model.classifier[2] = nn.Linear(model.classifier[2].in_features, num_classes)
    elif 'efficientnet' in model_name.lower():
        # EfficientNet - 使用 torchvision（與用戶訓練程式碼一致）
        from torchvision import models
        import torch.nn as nn
        
        if 'b5' in model_name.lower():
            model = models.efficientnet_b5(weights=None)
        elif 'b4' in model_name.lower():
            model = models.efficientnet_b4(weights=None)
        elif 'b3' in model_name.lower():
            model = models.efficientnet_b3(weights=None)
        elif 'b2' in model_name.lower():
            model = models.efficientnet_b2(weights=None)
        elif 'b1' in model_name.lower():
            model = models.efficientnet_b1(weights=None)
        else:
            # 預設使用 B0
            model = models.efficientnet_b0(weights=None)
        
        # 修改分類器的最後一層以匹配類別數
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif 'vgg' in model_name.lower():
        # VGG
        model = timm.create_model('vgg16', 
                                pretrained=False, 
                                num_classes=num_classes)
    elif 'densenet' in model_name.lower():
        # DenseNet - 檢測變體
        if state_dict is not None:
            densenet_variant = detect_densenet_variant(state_dict)
            print(f"檢測到 DenseNet 變體: {densenet_variant}")
        else:
            # 嘗試從模型名稱推測
            if 'densenet201' in model_name.lower():
                densenet_variant = 'densenet201'
            elif 'densenet169' in model_name.lower():
                densenet_variant = 'densenet169'
            elif 'densenet161' in model_name.lower():
                densenet_variant = 'densenet161'
            else:
                densenet_variant = 'densenet121'  # 預設值
        
        model = timm.create_model(densenet_variant, 
                                pretrained=False, 
                                num_classes=num_classes)
    elif 'resnet' in model_name.lower():
        # ResNet
        model = timm.create_model('resnet50', 
                                pretrained=False, 
                                num_classes=num_classes)
    else:
        # 默認使用 ResNet50
        model = timm.create_model('resnet50', 
                                pretrained=False, 
                                num_classes=num_classes)
    
    return model

def clean_state_dict_keys(state_dict):
    """
    清理 state_dict 中的鍵名，移除可能的前綴（如 "module."）
    Args:
        state_dict: 原始的 state_dict
    Returns:
        清理後的 state_dict
    """
    cleaned_state_dict = {}
    for key, value in state_dict.items():
        # 移除 "module." 前綴
        clean_key = key
        if key.startswith('module.'):
            clean_key = key[7:]  # 移除 "module." (7個字符)
        
        # 移除其他可能的前綴
        if clean_key.startswith('model.'):
            clean_key = clean_key[6:]  # 移除 "model."
            
        cleaned_state_dict[clean_key] = value
    
    return cleaned_state_dict

def filter_incompatible_keys(state_dict, model_architecture):
    """
    過濾 state_dict 中與模型架構不相容的鍵
    特別處理 Swin Transformer 模型的問題鍵
    Args:
        state_dict: 原始的 state_dict
        model_architecture: 模型架構物件
    Returns:
        過濾後的 state_dict
    """
    # 定義需要過濾掉的鍵模式（這些是訓練時生成的緩存，載入時不需要）
    incompatible_patterns = [
        'relative_position_index',  # Swin Transformer 相對位置索引
        'attn_mask',               # 注意力掩碼
        'relative_coords_table',   # 相對座標表
        'relative_position_bias_table'  # 相對位置偏置表
    ]
    
    filtered_state_dict = {}
    skipped_keys = []
    
    for key, value in state_dict.items():
        # 檢查是否包含不相容的模式
        should_skip = False
        for pattern in incompatible_patterns:
            if pattern in key:
                should_skip = True
                skipped_keys.append(key)
                break
        
        if not should_skip:
            filtered_state_dict[key] = value
    
    if skipped_keys:
        print(f"過濾掉不相容的鍵: {skipped_keys}")
    
    return filtered_state_dict

def get_num_classes_from_state_dict(state_dict):
    """
    從 state_dict 中推斷模型的類別數量
    """
    # 先清理鍵名
    cleaned_state_dict = clean_state_dict_keys(state_dict)
    
    # 尋找分類層的權重
    for key in cleaned_state_dict.keys():
        # 處理不同模型的分類器命名
        if ('head.fc.weight' in key or 'classifier.weight' in key or 'fc.weight' in key or 
            'classifier.1.weight' in key):  # EfficientNet 的分類器
            return cleaned_state_dict[key].shape[0]
        if ('head.fc.bias' in key or 'classifier.bias' in key or 'fc.bias' in key or 
            'classifier.1.bias' in key):  # EfficientNet 的分類器
            return cleaned_state_dict[key].shape[0]
    
    # 如果找不到，使用預設值
    return 183

def detect_densenet_variant(state_dict):
    """
    從 state_dict 中檢測 DenseNet 的變體
    """
    cleaned_state_dict = clean_state_dict_keys(state_dict)
    
    # 檢查分類器的輸入特徵數量
    for key in cleaned_state_dict.keys():
        if 'classifier.weight' in key:
            feature_size = cleaned_state_dict[key].shape[1]
            if feature_size == 1024:
                return 'densenet121'
            elif feature_size == 1664:
                return 'densenet169'
            elif feature_size == 1920:
                return 'densenet201'
            elif feature_size == 2208:
                return 'densenet161'
    
    # 如果找不到分類器，嘗試檢查 norm5 層
    for key in cleaned_state_dict.keys():
        if 'norm5.weight' in key or 'features.norm5.weight' in key:
            feature_size = cleaned_state_dict[key].shape[0]
            if feature_size == 1024:
                return 'densenet121'
            elif feature_size == 1664:
                return 'densenet169'
            elif feature_size == 1920:
                return 'densenet201'
            elif feature_size == 2208:
                return 'densenet161'
    
    # 預設返回 densenet121
    return 'densenet121'

def load_model(model_name: str, model_path: str = None):
    """
    載入 PyTorch 模型 (如果PyTorch可用) 或返回模擬模型
    Args:
        model_name: 模型名稱
        model_path: 模型檔案路徑，如果為 None 則使用預設路徑
    """
    if not TORCH_AVAILABLE:
        print(f"⚠️ PyTorch未安裝，{model_name} 使用模擬模式")
        return None
        
    if model_name in _loaded_models:
        return _loaded_models[model_name]
    
    # 特殊處理 EfficientNet 模型
    if 'efficientnet' in model_name.lower():
        model = load_efficientnet_model(model_name, model_path)
        if model is not None:
            _loaded_models[model_name] = model
        return model
    
    # 特殊處理 Swin Transformer 模型
    if 'swin' in model_name.lower():
        model = load_swin_model(model_name, model_path)
        if model is not None:
            _loaded_models[model_name] = model
        return model
    
    # 特殊處理 ConvNeXt 模型
    if 'convnext' in model_name.lower():
        model = load_convnext_model(model_name, model_path)
        if model is not None:
            _loaded_models[model_name] = model
        return model
    
    # 特殊處理 VGG 模型
    if 'vgg' in model_name.lower():
        model = load_vgg_model(model_name, model_path)
        if model is not None:
            _loaded_models[model_name] = model
        return model
        
    if model_path is None:
        model_path = f"./model/{model_name}.pth"
    
    if not os.path.exists(model_path):
        print(f"❌ 模型檔案不存在: {model_path}，使用模擬模式")
        return None
    
    try:
        # 載入模型
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 載入檢查點
        checkpoint = torch.load(model_path, map_location=device)
        
        # 檢查載入的是什麼類型的物件
        if isinstance(checkpoint, dict):
            # 如果是字典，可能包含 model_state_dict
            if 'model_state_dict' in checkpoint:
                # 檢查模型的類別數量
                state_dict = checkpoint['model_state_dict']
                num_classes = get_num_classes_from_state_dict(state_dict)
                
                # 創建模型架構（傳入 state_dict 用於檢測）
                model = create_model_architecture(model_name, num_classes, state_dict)
                
                # 清理 state_dict 鍵名，移除 "module." 前綴
                cleaned_state_dict = clean_state_dict_keys(state_dict)
                
                # 過濾不相容的鍵
                filtered_state_dict = filter_incompatible_keys(cleaned_state_dict, model)
                
                # 載入權重，使用 strict=False 來允許部分載入
                try:
                    model.load_state_dict(filtered_state_dict, strict=True)
                    print(f"成功載入模型架構並載入 model_state_dict (類別數: {num_classes})")
                except RuntimeError as e:
                    if "Missing key(s)" in str(e) or "Unexpected key(s)" in str(e):
                        print(f"使用 strict=False 模式載入: {e}")
                        model.load_state_dict(filtered_state_dict, strict=False)
                        print(f"成功載入模型架構並載入 model_state_dict (類別數: {num_classes}, 部分載入)")
                    else:
                        raise e
                
                model.eval()
                
            elif 'state_dict' in checkpoint:
                # 檢查模型的類別數量
                state_dict = checkpoint['state_dict']
                num_classes = get_num_classes_from_state_dict(state_dict)
                
                # 創建模型架構（傳入 state_dict 用於檢測）
                model = create_model_architecture(model_name, num_classes, state_dict)
                
                # 清理 state_dict 鍵名，移除 "module." 前綴
                cleaned_state_dict = clean_state_dict_keys(state_dict)
                
                # 過濾不相容的鍵
                filtered_state_dict = filter_incompatible_keys(cleaned_state_dict, model)
                
                # 載入權重，使用 strict=False 來允許部分載入
                try:
                    model.load_state_dict(filtered_state_dict, strict=True)
                    print(f"成功載入模型架構並載入 state_dict (類別數: {num_classes})")
                except RuntimeError as e:
                    if "Missing key(s)" in str(e) or "Unexpected key(s)" in str(e):
                        print(f"使用 strict=False 模式載入: {e}")
                        model.load_state_dict(filtered_state_dict, strict=False)
                        print(f"成功載入模型架構並載入 state_dict (類別數: {num_classes}, 部分載入)")
                    else:
                        raise e
                
                model.eval()
                
            else:
                # 直接是 state_dict (OrderedDict)
                num_classes = get_num_classes_from_state_dict(checkpoint)
                
                # 創建模型架構（傳入 state_dict 用於檢測）
                model = create_model_architecture(model_name, num_classes, checkpoint)
                
                # 清理 state_dict 鍵名，移除 "module." 前綴
                cleaned_state_dict = clean_state_dict_keys(checkpoint)
                
                # 過濾不相容的鍵
                filtered_state_dict = filter_incompatible_keys(cleaned_state_dict, model)
                
                # 載入權重，使用 strict=False 來允許部分載入
                try:
                    model.load_state_dict(filtered_state_dict, strict=True)
                    print(f"成功載入模型架構並載入純 state_dict (類別數: {num_classes})")
                except RuntimeError as e:
                    if "Missing key(s)" in str(e) or "Unexpected key(s)" in str(e):
                        print(f"使用 strict=False 模式載入: {e}")
                        model.load_state_dict(filtered_state_dict, strict=False)
                        print(f"成功載入模型架構並載入純 state_dict (類別數: {num_classes}, 部分載入)")
                    else:
                        raise e
                
                model.eval()
        else:
            # 直接是模型物件
            model = checkpoint
            model.eval()
            print(f"直接載入完整模型物件")
        
        # 確保模型在正確的設備上
        model = model.to(device)
        
        # 快取模型
        _loaded_models[model_name] = model
        
        print(f"成功載入模型: {model_name} (設備: {device})")
        return model
        
    except Exception as e:
        print(f"載入模型失敗: {e}")
        return None

def preprocess_image(image: Image.Image, model_name: str = None):
    """
    圖片預處理 (如果PyTorch可用) 或模擬預處理
    Args:
        image: 輸入圖片
        model_name: 模型名稱，用於決定輸入尺寸
    """
    if not TORCH_AVAILABLE:
        # 模擬模式，只進行基本的圖片檢查
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return np.array(image)  # 返回numpy數組作為模擬tensor
    
    # 根據模型類型決定輸入尺寸
    if model_name and 'swinv2' in model_name.lower():
        input_size = 192  # Swin Transformer V2 訓練時使用 192x192
    else:
        input_size = 224  # 其他模型使用 224x224
    
    transform = transforms.Compose([
        transforms.Resize((input_size, input_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # 確保圖片是 RGB 格式
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    return transform(image).unsqueeze(0)

def classify_food_image(image: Image.Image, model_name: str) -> Dict:
    """
    使用指定的 PyTorch 模型進行食物辨識 (或模擬辨識)
    Args:
        image: 輸入圖片
        model_name: 要使用的模型名稱
    """
    if image is None:
        return {"錯誤": "請上傳食物圖片"}
    
    if not model_name:
        return {"錯誤": "請指定模型名稱"}
    
    try:
        # 載入模型
        model = load_model(model_name)
        
        if model is None or not TORCH_AVAILABLE:
            # 如果模型載入失敗或PyTorch不可用，使用模擬模式
            print(f"🎲 模型 {model_name} 使用模擬模式進行辨識")
            food_names = list(FOOD_DATABASE.keys())
            # 基於圖片特性的簡單模擬邏輯
            np.random.seed(hash(str(image.size)) % 1000)  # 基於圖片尺寸產生種子
            recognized_food = np.random.choice(food_names)
            confidence = np.random.randint(82, 96)  # 模擬信心度
        else:
            # 使用真實模型進行預測
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            
            # 圖片預處理
            input_tensor = preprocess_image(image, model_name).to(device)
            
            # 模型推論
            with torch.no_grad():
                outputs = model(input_tensor)
                
                # 假設模型輸出是類別索引或機率分布
                if len(outputs.shape) > 1:
                    predicted_idx = torch.argmax(outputs, dim=1).item()
                    # 計算信心度
                    probabilities = torch.softmax(outputs, dim=1)
                    confidence = int(probabilities[0][predicted_idx].item() * 100)
                else:
                    predicted_idx = outputs.item()
                    confidence = random.randint(85, 98)
                
                # 將預測索引轉換為食物名稱
                # 使用訓練時的標籤列表進行映射
                if predicted_idx < len(TRAINING_LABELS):
                    recognized_food = TRAINING_LABELS[predicted_idx]
                    print(f"AI辨識結果: {recognized_food} (索引: {predicted_idx}, 信心度: {confidence}%)")
                else:
                    print(f"警告: 預測索引 {predicted_idx} 超出範圍，使用隨機選擇")
                    food_names = list(FOOD_DATABASE.keys())
                    recognized_food = random.choice(food_names)
                    confidence = random.randint(75, 90)

        # 從資料庫獲取食物資訊
        # 首先嘗試直接匹配，如果失敗則嘗試映射
        if recognized_food in FOOD_DATABASE:
            food_info = FOOD_DATABASE[recognized_food]
        else:
            # 嘗試映射到資料庫中的食物名稱
            mapped_food = map_training_label_to_database(recognized_food)
            if mapped_food and mapped_food in FOOD_DATABASE:
                food_info = FOOD_DATABASE[mapped_food]
                recognized_food = mapped_food  # 使用映射後的名稱
            else:
                return {"錯誤": f"辨識的食物 '{recognized_food}' 無法在資料庫中找到對應項目"}
        
        # 決定狀態標示
        status_prefix = "🎲" if (model is None or not TORCH_AVAILABLE) else "🤖"
        
        result = {
            "辨識食物": recognized_food,
            "英文名": food_info.get("英文名", "unknown"),
            "五性屬性": food_info["五性"],
            "使用模型": f"{status_prefix} {model_name}",
            "信心度": f"{confidence}%",
            "模式": "模擬模式" if (model is None or not TORCH_AVAILABLE) else "AI模式"
        }
        
        return result
        
    except Exception as e:
        return {"錯誤": f"辨識過程發生錯誤: {str(e)}"}

def classify_with_all_models(image: Image.Image) -> Dict:
    """
    使用所有可用模型進行食物辨識，並以隨機順序返回結果
    Args:
        image: 輸入圖片
    Returns:
        包含所有模型辨識結果的字典
    """
    if image is None:
        return {"錯誤": "請上傳食物圖片"}
    
    # 定義所有可用的模型
    available_models = [
        "convnext_90",
        "densenet_86", 
        "efficientnet_84",
        "resnet50_78",
        "swin_model_94",
        "swinv2_model_94",
        "vgg_model_78",
        "vit_model_74"
    ]
    
    # 隨機打亂模型順序
    shuffled_models = available_models.copy()
    random.shuffle(shuffled_models)
    
    results = {}
    results["🎯 綜合辨識結果"] = {}
    results["📊 各模型詳細結果"] = {}
    
    # 用於統計最終結果
    food_votes = {}
    successful_results = []
    
    for i, model_name in enumerate(shuffled_models, 1):
        try:
            print(f"正在使用模型 {model_name} 進行辨識...")
            result = classify_food_image(image, model_name)
            
            if "錯誤" not in result:
                # 成功的辨識結果
                recognized_food = result["辨識食物"]
                
                # 統計投票
                if recognized_food in food_votes:
                    food_votes[recognized_food] += 1
                else:
                    food_votes[recognized_food] = 1
                
                successful_results.append(result)
                
                # 添加到詳細結果中
                results["📊 各模型詳細結果"][f"#{i} {model_name}"] = {
                    "辨識食物": recognized_food,
                    "英文名": result.get("英文名", "unknown"),
                    "五性屬性": result.get("五性屬性", "未知"),
                    "信心度": result.get("信心度", "N/A")
                }
            else:
                # 失敗的辨識結果
                results["📊 各模型詳細結果"][f"#{i} {model_name}"] = {
                    "狀態": "載入失敗",
                    "錯誤信息": result.get("錯誤", "未知錯誤")
                }
                
        except Exception as e:
            results["📊 各模型詳細結果"][f"#{i} {model_name}"] = {
                "狀態": "辨識失敗", 
                "錯誤信息": str(e)
            }
    
    # 生成綜合結果
    if food_votes:
        # 找出得票最多的食物
        most_voted_food = max(food_votes, key=food_votes.get)
        vote_count = food_votes[most_voted_food]
        total_successful = len(successful_results)
        
        # 獲取該食物的詳細資訊
        food_info = None
        for result in successful_results:
            if result["辨識食物"] == most_voted_food:
                food_info = result
                break
        
        if food_info:
            results["🎯 綜合辨識結果"] = {
                "最終辨識": most_voted_food,
                "英文名": food_info.get("英文名", "unknown"),
                "五性屬性": food_info.get("五性屬性", "未知"),
                "模型共識度": f"{vote_count}/{total_successful} ({vote_count/total_successful*100:.1f}%)",
                "成功模型數": f"{total_successful}/{len(available_models)}",
                "投票分佈": food_votes
            }
        else:
            results["🎯 綜合辨識結果"]["錯誤"] = "無法獲取食物詳細資訊"
    else:
        results["🎯 綜合辨識結果"]["錯誤"] = "所有模型都無法成功辨識圖片"
    
    return results

def build_food_recognition_page():
    """建立食物辨識頁面"""
    # 添加食物辨識頁面專用CSS樣式
    food_page_css = """
    <style>
    /* === 食物辨識頁面專用樣式修復版 === */
    
    /* 容器基礎樣式 */
    .food-recognition-container {
        background: linear-gradient(135deg, #F0F8FF 0%, #E6F3E6 25%, #FFF8F0 75%, #F0F8FF 100%) !important;
        min-height: 100vh !important;
        padding: 20px !important;
        margin: 0 !important;
        font-family: 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', sans-serif !important;
    }
      /* 主標題區域 */
    .food-hero-section {
        text-align: center !important;
        padding: 20px 20px 30px 20px !important;
        background: linear-gradient(135deg, rgba(106, 153, 78, 0.05) 0%, rgba(212, 175, 55, 0.03) 100%) !important;
        border-radius: 25px !important;
        margin-bottom: 30px !important;
        border: 2px solid rgba(106, 153, 78, 0.1) !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.08) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* 標題區域頂部容器 */
    .food-hero-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: flex-start !important;
        width: 100% !important;
        margin-bottom: 20px !important;
    }

    /* 標題內容區域 */
    .food-hero-content {
        flex: 1 !important;
        text-align: center !important;
    }

    /* 右上角按鈕區域 */
    .food-hero-button-area {
        flex-shrink: 0 !important;
        align-self: flex-start !important;
    }
    
    .food-page-title {
        color: #2D5016 !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 15px !important;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    .food-page-subtitle {
        color: #4A6741 !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        line-height: 1.7 !important;
        max-width: 700px !important;
        margin: 0 auto !important;
    }
    
    /* 功能卡片行 */
    .food-feature-cards-row {
        margin: 20px 0 !important;
        gap: 15px !important;
    }
    
    /* 功能卡片 */
    .food-feature-card {
        background: #FEFCF8 !important;
        border-radius: 20px !important;
        padding: 20px 15px !important;
        margin: 0 !important;
        box-shadow: 0 12px 40px rgba(139, 69, 19, 0.12) !important;
        border: 2px solid rgba(212, 175, 55, 0.2) !important;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        min-height: 100px !important;
        display: flex !important;
        flex-direction: column !important;
        text-align: center !important;
    }
    
    .food-feature-card:hover {
        transform: translateY(-6px) !important;
        box-shadow: 0 20px 50px rgba(139, 69, 19, 0.18) !important;
        border-color: rgba(212, 175, 55, 0.4) !important;
    }
    
    .food-feature-icon {
        font-size: 2.5rem !important;
        margin-bottom: 8px !important;
        display: block !important;
    }
    
    .food-feature-title {
        color: #2D5016 !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin: 8px 0 5px 0 !important;
    }
    
    .food-feature-description {
        color: #4A6741 !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        margin: 0 !important;
    }
    
    /* 上傳區域樣式 */
    .food-upload-section {
        background: #F0F7F0 !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin: 20px 0 !important;
        border: 2px solid rgba(106, 153, 78, 0.3) !important;
        box-shadow: 0 8px 30px rgba(106, 153, 78, 0.1) !important;
    }
      .food-upload-section h3 {
        color: #2D5016 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 15px !important;
        text-align: center !important;
    }
    
    /* 按鈕樣式 */
    .food-recognition-btn {
        background: linear-gradient(135deg, #6A9A4E 0%, #5A8A3E 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(106, 154, 78, 0.3) !important;
        margin: 8px 0 !important;
        min-width: 200px !important;
        cursor: pointer !important;
    }
    
    .food-recognition-btn:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(106, 154, 78, 0.4) !important;
        background: linear-gradient(135deg, #5A8A3E 0%, #4A7A2E 100%) !important;
    }
    
    /* 漂浮返回按鈕樣式 - 使用 app.py 的統一樣式 */
    
    /* 結果顯示區域 */
    .food-result-section {
        background: linear-gradient(135deg, #F8FBF6 0%, #FEFEFE 100%) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin: 20px 0 !important;
        border: 2px solid rgba(106, 153, 78, 0.2) !important;
        box-shadow: 0 15px 40px rgba(106, 153, 78, 0.15) !important;
        position: relative !important;
    }
    
    /* 狀態顯示 */
    .status-display {
        background: linear-gradient(135deg, #E8F5E8 0%, #F0F8F0 100%) !important;
        border: 2px solid rgba(106, 153, 78, 0.3) !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        color: #2D5016 !important;
        font-weight: 600 !important;
        text-align: center !important;
        margin: 15px 0 !important;
        font-size: 1rem !important;
    }
    
    /* === 修復 Gradio 組件顏色問題 === */
    
    /* 全局文字顏色修復 */
    .gradio-container * {
        color: #2D5016 !important;
    }
    
    /* 標籤文字修復 */
    .gradio-container label,
    .gradio-container .gr-form label,
    .gradio-container .gr-block-label,
    .gradio-container .gr-block-title,
    .gradio-container .label-wrap,
    .gradio-container .label-wrap span {
        color: #2D5016 !important;
        font-weight: 600 !important;
        background-color: transparent !important;
        font-size: 14px !important;
    }
    
    /* 輸入框和文字區域修復 */
    .gradio-container input,
    .gradio-container textarea,
    .gradio-container select,
    .gradio-container .gr-textbox,
    .gradio-container .gr-textbox textarea,
    .gradio-container .gr-text-input {
        color: #2D5016 !important;
        background-color: #FFFFFF !important;
        border: 2px solid rgba(106, 153, 78, 0.3) !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        padding: 8px 12px !important;
    }
    
    /* 下拉選單修復 */
    .gradio-container .gr-dropdown,
    .gradio-container .gr-dropdown div,
    .gradio-container .gr-dropdown span,
    .gradio-container .gr-dropdown .wrap,
    .gradio-container .gr-dropdown .secondary-wrap {
        color: #2D5016 !important;
        background-color: #FFFFFF !important;
        border: 2px solid rgba(106, 153, 78, 0.3) !important;
    }
    
    /* 下拉選單修復 - 強化版 */
    .gradio-container select,
    .gradio-container .gr-dropdown,
    .gradio-container .dropdown,
    .gradio-container [data-testid="dropdown"],
    .gradio-container .gradio-dropdown,
    .gradio-container .gr-form .gr-dropdown,
    .gradio-container .select-wrap,
    .gradio-container .select-wrap select,
    .gradio-container .gr-form select {
        color: #2D5016 !important;
        background-color: #FFFFFF !important;
        border: 2px solid rgba(106, 153, 78, 0.3) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        height: auto !important;
        opacity: 1 !important;
        visibility: visible !important;
        pointer-events: auto !important;
    }
    
    /* 下拉選單選項修復 */
    .gradio-container .gr-dropdown option,
    .gradio-container select option,
    .gradio-container .select-wrap option,
    .gradio-container .dropdown option,
    .gradio-container [data-testid="dropdown"] option {
        color: #2D5016 !important;
        background-color: #FFFFFF !important;
        font-size: 14px !important;
        padding: 8px !important;
    }
    
    /* 下拉選單互動狀態 */
    .gradio-container .gr-dropdown:hover,
    .gradio-container .gr-dropdown:focus,
    .gradio-container .gr-dropdown:active,
    .gradio-container select:hover,
    .gradio-container select:focus,
    .gradio-container select:active {
        border-color: rgba(106, 153, 78, 0.6) !important;
        box-shadow: 0 0 0 2px rgba(106, 153, 78, 0.2) !important;
    }
    
    /* 按鈕文字確保為白色 */
    .gradio-container button,
    .gradio-container button span,
    .gradio-container .gr-button,
    .gradio-container .gr-button span {
        color: white !important;
        font-weight: 600 !important;
    }    /* Tab 標籤修復 - 使用更強的選擇器 */
    .gradio-container .tabitem button,
    .gradio-container .tab-nav button,
    .gradio-container button[role="tab"],
    .gradio-container .gr-tab-nav button,
    .gradio-container .gr-tab-nav button span,
    .gradio-container .tab-nav button span,
    .gradio-container button[role="tab"] span {
        background-color: #466235 !important; /* 深綠色背景 */
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: 2px solid rgba(106, 153, 78, 0.2) !important;
        border-radius: 8px !important;
        margin: 2px !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .gradio-container .tabitem button:hover,
    .gradio-container .tab-nav button:hover,
    .gradio-container button[role="tab"]:hover,
    .gradio-container .gr-tab-nav button:hover,
    .gradio-container .tabitem button:hover span,
    .gradio-container .tab-nav button:hover span,
    .gradio-container button[role="tab"]:hover span {
        background-color: #3A522C !important; /* 更深的綠色 */
        color: #FFFFFF !important;
        border-color: rgba(106, 153, 78, 0.4) !important;
    }
    
    .gradio-container .tabitem button.selected,
    .gradio-container .tab-nav button.selected,
    .gradio-container button[role="tab"][aria-selected="true"],
    .gradio-container .gr-tab-nav button.selected,
    .gradio-container .gr-tab-nav button[aria-selected="true"],
    .gradio-container .tabitem button.selected span,
    .gradio-container .tab-nav button.selected span,
    .gradio-container button[role="tab"][aria-selected="true"] span {
        background-color: #2D4017 !important; /* 非常深的綠色 */
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        border-color: #6A9A4E !important;
    }/* 強制覆蓋所有可能的Tab文字顏色 */
    .gradio-container [role="tablist"] button,
    .gradio-container [role="tablist"] button *,
    .gradio-container .tabs button,
    .gradio-container .tabs button *,
    .gradio-container div[role="tablist"] button,
    .gradio-container div[role="tablist"] button * {
        color: #FFFFFF !important;
    }
    
    /* 通用Tab按鈕強制白色文字 */
    .gradio-container button[role="tab"],
    .gradio-container button[role="tab"] *,
    .gradio-container [data-testid="tab"],
    .gradio-container [data-testid="tab"] *,
    .gradio-container .tab-nav button,
    .gradio-container .tab-nav button *,
    .gradio-container .gr-tab-nav button,
    .gradio-container .gr-tab-nav button * {
        color: #FFFFFF !important;
        text-shadow: none !important;
    }      /* 最強力的覆蓋 - 針對任何包含標籤emoji的按鈕 */
    .gradio-container button:contains("🎯"),
    .gradio-container button:contains("📊"), 
    .gradio-container button:contains("🔍") {
        color: #FFFFFF !important;
    }
    
    /* 終極Tab文字顏色修復 - 針對Gradio動態生成的元素 */
    .gradio-container button,
    .gradio-container button span,
    .gradio-container [role="tab"],
    .gradio-container [role="tab"] span,
    .gradio-container [data-testid*="tab"],
    .gradio-container [data-testid*="tab"] span,
    .gradio-container .tab-item,
    .gradio-container .tab-item span,
    .gradio-container .tabitem,
    .gradio-container .tabitem span {
        color: #FFFFFF !important;
    }
      /* 針對可能的深色文字覆蓋 */
    .gradio-container button:not([class*="food-recognition"]):not([class*="single-model"]) {
        color: #FFFFFF !important;
    }
    
    .gradio-container button:not([class*="food-recognition"]):not([class*="single-model"]) span {
        color: #FFFFFF !important;
    }
    
    /* 特別針對Tab按鈕的強制白色文字 */
    .gradio-container [role="tablist"] button[role="tab"],
    .gradio-container [role="tablist"] button[role="tab"] *,
    .gradio-container .tabs .tab-nav button,
    .gradio-container .tabs .tab-nav button *,
    .gradio-container .gr-tabs button,
    .gradio-container .gr-tabs button * {
        color: #FFFFFF !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    /* 結果顯示區域文字修復 */
    .gradio-container .json-holder,
    .gradio-container .json-holder *,
    .gradio-container .recognition-container,
    .gradio-container .recognition-container *,
    .gradio-container .recognition-container textarea {
        color: #2D5016 !important;
        background-color: #FFFFFF !important;
        border: 2px solid rgba(106, 153, 78, 0.2) !important;
        font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        padding: 15px !important;
    }
    
    /* Tab 內容區域修復 */
    .gradio-container .gr-tab-item,
    .gradio-container .gr-tab-item *,
    .gradio-container .gr-tab-item div,
    .gradio-container .gr-tab-item span {
        color: #2D5016 !important;
        background-color: transparent !important;
    }
    
    /* 圖片上傳區域修復 */
    .gradio-container .gr-image,
    .gradio-container .gr-image *,
    .gradio-container .gr-file-upload,
    .gradio-container .gr-file-upload * {
        color: #2D5016 !important;
        border: 2px solid rgba(106, 153, 78, 0.3) !important;
        border-radius: 12px !important;
    }
    
    /* Tab 說明區域 */
    .tab-description {
        background: rgba(106, 153, 78, 0.1) !important;
        border-radius: 10px !important;
        padding: 15px 20px !important;
        margin-bottom: 20px !important;
        border-left: 4px solid #6A9A4E !important;
        color: #2D5016 !important;
    }
    
    .tab-description strong {
        color: #2D5016 !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }
    
    /* 響應式設計 */
    @media (max-width: 768px) {
        .food-feature-cards-row {
            flex-direction: column !important;
        }
        
        .food-feature-card {
            margin: 10px 0 !important;
        }
        
        .food-page-title {
            font-size: 2.2rem !important;
        }
        
        .food-recognition-container {
            padding: 15px !important;
            margin: 5px !important;
        }
    }
    
    /* 修復下拉選單 - 最新版Gradio兼容 */
    div.gradio-dropdown {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        background-color: white !important;
        color: #2D5016 !important;
        border: 2px solid rgba(106, 153, 78, 0.3) !important;
        border-radius: 8px !important;
        position: relative !important;
        z-index: 100 !important;
        width: 100% !important;
    }
    
    /* 強制顯示下拉選單的選項 */
    div.gradio-dropdown > ul,
    div.gradio-dropdown div[role="listbox"],
    div.gradio-dropdown div[class*="list-container"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        background-color: white !important;
        color: #2D5016 !important;
        border-radius: 8px !important;
        z-index: 101 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* 下拉箭頭按鈕 */
    div.gradio-dropdown button[aria-label="Show options"],
    div.gradio-dropdown button[class*="arrow"] {
        visibility: visible !important;
        opacity: 1 !important;
        color: #2D5016 !important;
    }
    
    /* 下拉選單項目 */
    div.gradio-dropdown li,
    div.gradio-dropdown div[role="option"],
    div.gradio-dropdown div[class*="item"] {
        color: #2D5016 !important;
        background-color: white !important;
        padding: 8px 12px !important;
    }
    
    /* 下拉選單懸停效果 */
    div.gradio-dropdown li:hover,
    div.gradio-dropdown div[role="option"]:hover,
    div.gradio-dropdown div[class*="item"]:hover {
        background-color: rgba(106, 153, 78, 0.1) !important;
    }
    
    /* 下拉選單已選中項目 */
    div.gradio-dropdown li[aria-selected="true"],
    div.gradio-dropdown div[role="option"][aria-selected="true"],
    div.gradio-dropdown div[class*="item"][data-selected="true"] {
        background-color: rgba(106, 153, 78, 0.2) !important;
        font-weight: 600 !important;
    }
    
    /* 下拉選單文字顏色 */
    div.gradio-dropdown *,
    div.gradio-dropdown span,
    div.gradio-dropdown div,
    div.gradio-dropdown p {
        color: #2D5016 !important;
    }

    /* Gradio 5.x 版本下拉選單修復 */
    .block.gr-box > div[class^="wrap"] select,
    select.svelte-selector,
    .gradio-dropdown,
    [id^="component-"] select,
    div[class*="dropdown"] select {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 100 !important;
        color: #2D5016 !important;
        background-color: white !important;
        border: 2px solid rgba(106, 153, 78, 0.3) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        height: auto !important;
        min-height: 40px !important;
    }

    /* Gradio 5.x 滑鼠懸停與焦點效果 */
    .block.gr-box > div[class^="wrap"] select:hover,
    select.svelte-selector:hover,
    .gradio-dropdown:hover,
    [id^="component-"] select:hover,
    div[class*="dropdown"] select:hover,
    .block.gr-box > div[class^="wrap"] select:focus,
    select.svelte-selector:focus,
    .gradio-dropdown:focus,
    [id^="component-"] select:focus,
    div[class*="dropdown"] select:focus {
        border-color: rgba(106, 153, 78, 0.6) !important;
        box-shadow: 0 0 0 2px rgba(106, 153, 78, 0.2) !important;
        outline: none !important;
    }

    /* Gradio 5.x 選項樣式 */
    .block.gr-box > div[class^="wrap"] select option,
    select.svelte-selector option,
    .gradio-dropdown option,
    [id^="component-"] select option,
    div[class*="dropdown"] select option {
        color: #2D5016 !important;
        background-color: white !important;
        padding: 8px !important;
        font-size: 14px !important;
    }

    /* 確保下拉選單點擊事件 */
    .gradio-container {
        --dropdown-background-color: white !important;
        --dropdown-text-color: #2D5016 !important;
        --dropdown-border-color: rgba(106, 153, 78, 0.3) !important;
    }

    /* 修復下拉選單的點擊和顯示問題 */
    .gradio-container [data-testid="dropdown"],
    .gradio-container [data-testid="dropdown"] *,
    .gradio-container select,
    .gradio-container .select-wrap,
    .gradio-container .gr-dropdown {
        pointer-events: auto !important;
        user-select: auto !important;
        -webkit-user-select: auto !important;
        cursor: pointer !important;
    }

    /* 避免下拉選單被其他元素覆蓋 */
    .gradio-container [data-testid="dropdown"]:focus,
    .gradio-container [data-testid="dropdown"]:active,
    .gradio-container select:focus,
    .gradio-container select:active,
    .gradio-container .select-wrap:focus,
    .gradio-container .select-wrap:active {
        z-index: 1000 !important;
        position: relative !important;
    }
    
    /* 強制顯示下拉箭頭 */
    .gradio-container [data-testid="dropdown"] svg,
    .gradio-container [data-testid="dropdown"] [data-testid="arrow"],
    .gradio-container .select-wrap svg,
    .gradio-container .select-wrap [data-testid="arrow"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        color: #2D5016 !important;
    }

    /* 特定優化下拉選單樣式 */
    #model_selector, 
    div[id^="component-"] select,
    .gr-dropdown[id="model_selector"] {
        display: block !important;
        width: 100% !important;
        height: auto !important;
        min-height: 45px !important;
        background-color: white !important;
        color: #2D5016 !important;
        border: 2px solid #6A9A4E !important;
        border-radius: 10px !important;
        padding: 10px 15px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 10px rgba(106, 153, 78, 0.2) !important;
        margin: 8px 0 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        position: relative !important;
        z-index: 50 !important;
    }
    
    #model_selector:hover,
    div[id^="component-"] select:hover,
    .gr-dropdown[id="model_selector"]:hover {
        border-color: #5A8A3E !important;
        box-shadow: 0 6px 15px rgba(106, 153, 78, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    #model_selector:focus,
    div[id^="component-"] select:focus,
    .gr-dropdown[id="model_selector"]:focus {
        outline: none !important;
        border-color: #4A7A2E !important;
        box-shadow: 0 0 0 3px rgba(106, 153, 78, 0.3) !important;
    }

    /* 下拉選單樣式優化 */
    .gradio-container .model-dropdown,
    #model_selector,
    .gradio-container #model_selector,
    .gradio-container [data-testid="dropdown"],
    .gr-dropdown[id="model_selector"] {
        display: block !important;
        width: 100% !important;
        height: auto !important;
        min-height: 45px !important;
        background-color: white !important;
        color: #2D5016 !important;
        border: 2px solid #6A9A4E !important;
        border-radius: 10px !important;
        padding: 10px 15px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 10px rgba(106, 153, 78, 0.2) !important;
        margin: 8px 0 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        position: relative !important;
        z-index: 50 !important;
    }
    
    .gradio-container .model-dropdown:hover,
    #model_selector:hover,
    .gr-dropdown[id="model_selector"]:hover {
        border-color: #5A8A3E !important;
        box-shadow: 0 6px 15px rgba(106, 153, 78, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    .gradio-container .model-dropdown:focus,
    #model_selector:focus,
    .gr-dropdown[id="model_selector"]:focus {
        outline: none !important;
        border-color: #4A7A2E !important;
        box-shadow: 0 0 0 3px rgba(106, 153, 78, 0.3) !important;
    }

    /* 下拉選單選項樣式 */
    .gradio-container .model-dropdown .option,
    #model_selector .option,
    .gr-dropdown[id="model_selector"] .option {
        color: #2D5016 !important;
        background-color: white !important;
        padding: 10px 15px !important;
        border-bottom: 1px solid rgba(106, 153, 78, 0.1) !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    
    .gradio-container .model-dropdown .option:hover,
    #model_selector .option:hover,
    .gr-dropdown[id="model_selector"] .option:hover {
        background-color: rgba(106, 153, 78, 0.1) !important;
        color: #2D5016 !important;
    }
    
    .gradio-container .model-dropdown .option:selected,
    .gradio-container .model-dropdown .option[aria-selected="true"],
    #model_selector .option:selected,
    .gr-dropdown[id="model_selector"] .option[aria-selected="true"] {
        background-color: #6A9A4E !important;
        color: white !important;
        font-weight: 600 !important;
    }
        box-sizing: border-box !important;
    }
    </style>
    """
    
    # 不再需要額外的漂浮按鈕，使用 app.py 中的統一按鈕
    with gr.Column(elem_classes=["food-recognition-container"]):        # 添加CSS樣式
        gr.HTML(food_page_css)
        
        # 英雄區域 - 頁面標題和說明
        with gr.Column(elem_classes=["food-hero-section"]):
            gr.HTML("""
                <div style="margin-top: 40px;">
                    <h1 class="food-page-title">AI食物辨識模組</h1>
                    <p class="food-page-subtitle">
                        運用深度學習技術辨識食物，提供中醫五性屬性分析，助您了解食物的寒熱特性
                    </p>
                </div>
            """)
        
        # 功能特色說明 - 使用卡片形式
        with gr.Row(elem_classes=["food-feature-cards-row"]):
            with gr.Column(elem_classes=["food-feature-card"]):
                gr.HTML("""
                <div class="food-feature-icon">🎯</div>
                <h4 class="food-feature-title">多模型投票</h4>
                <p class="food-feature-description">8個AI模型協同判斷，提升辨識準確度</p>
                """)
            
            with gr.Column(elem_classes=["food-feature-card"]):
                gr.HTML("""
                <div class="food-feature-icon">🔬</div>
                <h4 class="food-feature-title">深度學習</h4>
                <p class="food-feature-description">最新Transformer架構，精準識別食物</p>
                """)
            
            with gr.Column(elem_classes=["food-feature-card"]):
                gr.HTML("""
                <div class="food-feature-icon">🌡️</div>
                <h4 class="food-feature-title">中醫屬性</h4>
                <p class="food-feature-description">提供食物五性寒熱分析，融合傳統智慧</p>
                """)
            
            # 上傳區域
        with gr.Column(elem_classes=["food-upload-section"]):
            gr.HTML("<h3>📸 上傳食物圖片</h3>")
            
            with gr.Row():
                with gr.Column():
                    food_image = gr.Image(
                        label="選擇或拖拽食物圖片", 
                        type="pil",
                        height=400,
                        container=True
                    )
                
                with gr.Column():
                    # 模型選擇區域
                    gr.HTML("""
                    <div style="background: rgba(106, 153, 78, 0.1); padding: 15px; border-radius: 10px; margin: 15px 0;">
                        <h4 style="color: #4A6741; margin-bottom: 10px;">🤖 AI模型說明</h4>
                        <p style="color: #6A9A4E; font-size: 0.9rem; margin: 0;">
                            系統將自動使用多個AI模型進行綜合辨識，以提高準確性。
                        </p>
                    </div>
                    """)
                    
                    # 辨識按鈕
                    recognize_all_btn = gr.Button(
                        "🎯 多模型綜合辨識",
                        elem_classes=["food-recognition-btn"],
                        variant="primary",
                        size="lg"
                    )
                    
                    # single_model_btn = gr.Button(
                    #     "🔍 單一模型辨識", 
                    #     elem_classes=["food-single-model-btn"],
                    #     variant="secondary",
                    #     size="lg"
                    # )

            # 範例圖片選擇區域
            with gr.Column(elem_classes=["food-upload-section"]):
                gr.HTML("<h3>🖼️ 或選擇範例圖片試試看</h3>")
                
                with gr.Row():
                    # 定義範例圖片信息
                    sample_images = [
                        {"name": "鮑魚", "file": "Abalone.jpg", "desc": "海鮮類"},
                        {"name": "竹筍", "file": "Bambooshoot.jpg", "desc": "蔬菜類"},
                        {"name": "玉米", "file": "Corn.jpg", "desc": "穀物類"},
                        {"name": "毛豆", "file": "GreenSoybean.jpg", "desc": "豆類"},
                        {"name": "蜂蜜", "file": "Honey.jpg", "desc": "甜品類"},
                        {"name": "馬鈴薯", "file": "Potato.jpg", "desc": "根莖類"},
                        {"name": "楊桃", "file": "Starfruit.jpg", "desc": "水果類"},
                        {"name": "鴨梨", "file": "Yapear.jpg", "desc": "水果類"}
                    ]
                    
                    # 創建範例圖片按鈕
                    sample_buttons = []
                    for i, img_info in enumerate(sample_images):
                        with gr.Column(scale=1):
                            btn = gr.Button(
                                f"🍽️ {img_info['name']}\n({img_info['desc']})",
                                elem_classes=["food-recognition-btn"],
                                variant="secondary",
                                size="sm"
                            )
                            sample_buttons.append((btn, img_info['file']))
        
        # 狀態顯示
        status_display = gr.Textbox(
            label="📊 辨識狀態",
            value="請上傳食物圖片開始辨識",
            interactive=False,
            container=True,
            elem_classes=["status-display"],
            lines=1,
            max_lines=1
        )
          # 結果顯示區域
        with gr.Column(elem_classes=["food-result-section"]):
            gr.HTML("<h3 style='color: #4A6741; text-align: center; margin-bottom: 20px;'>📋 辨識結果</h3>")
            
            with gr.Tabs():
                with gr.TabItem("🎯 綜合辨識結果", elem_id="comprehensive_tab"):
                    gr.HTML("""
                    <div class="tab-description">
                        <strong>🏆 多模型投票結果</strong><br>
                        整合8個AI模型的辨識結果，通過投票機制得出最終判斷，提供最高的準確度和可靠性。
                    </div>
                    """)
                    
                    comprehensive_result_display = gr.Textbox(
                        label="多模型綜合辨識結果",
                        container=True,
                        show_label=True,
                        lines=15,
                        max_lines=20,
                        elem_classes=["json-holder", "recognition-container"],
                        interactive=False
                    )
                
                with gr.TabItem("📊 各模型詳細結果", elem_id="detailed_tab"):
                    gr.HTML("""
                    <div class="tab-description">
                        <strong>🔍 各模型獨立分析</strong><br>
                        查看每個AI模型（Swin Transformer、Vision Transformer、ConvNeXt、EfficientNet、VGG等）的詳細辨識結果和準確度評估。
                    </div>
                    """)
                    
                    detailed_result_display = gr.Textbox(
                        label="各模型詳細辨識結果",
                        container=True,
                        show_label=True,
                        lines=15,
                        max_lines=20,
                        elem_classes=["json-holder", "recognition-container"],
                        interactive=False
                    )
                
                # with gr.TabItem("🔍 單一模型結果", elem_id="single_tab"):
                #     gr.HTML("""
                #     <div class="tab-description">
                #         <strong>🎯 指定模型辨識</strong><br>
                #         使用您在左側選擇的特定AI模型進行食物辨識，可比較不同模型的辨識能力和特點。
                #     </div>
                #     """)
                #     
                #     single_result_display = gr.Textbox(
                #         label="單一模型辨識結果",
                #         container=True,
                #         show_label=True,
                #         lines=15,                        max_lines=20,
                #         elem_classes=["json-holder", "recognition-container"],
                #         interactive=False
                #     )
        
        def format_comprehensive_result(result_dict):
            """格式化綜合辨識結果為可讀文本"""
            if not result_dict or "錯誤" in result_dict:
                return f"❌ 錯誤: {result_dict.get('錯誤', '未知錯誤')}"
            
            text = "多模型綜合辨識結果\n"
            text += "=" * 40 + "\n\n"
            
            text += f"最終辨識: {result_dict.get('最終辨識', 'N/A')}\n"
            text += f"英文名: {result_dict.get('英文名', 'N/A')}\n"
            text += f"五性屬性: {result_dict.get('五性屬性', 'N/A')}\n"
            text += f"模型共識度: {result_dict.get('模型共識度', 'N/A')}\n"
            text += f"成功模型數: {result_dict.get('成功模型數', 'N/A')}\n\n"
            
            if "投票分佈" in result_dict:
                text += "各食物得票分佈:\n"
                for food, votes in result_dict["投票分佈"].items():
                    text += f"   • {food}: {votes} 票\n"
            
            return text
        
        def format_detailed_result(result_dict):
            """格式化詳細辨識結果為可讀文本"""
            if not result_dict:
                return "❌ 無詳細結果"
            
            text = "各模型詳細辨識結果\n"
            text += "=" * 40 + "\n\n"
            
            for model_key, result in result_dict.items():
                text += f"🤖 {model_key}\n"
                text += "-" * 30 + "\n"
                
                if "錯誤信息" in result:
                    text += f"❌ 狀態: {result.get('狀態', '失敗')}\n"
                    text += f"💬 錯誤信息: {result.get('錯誤信息', '未知錯誤')}\n"
                else:
                    text += f"辨識食物: {result.get('辨識食物', 'N/A')}\n"
                    text += f"英文名: {result.get('英文名', 'N/A')}\n"
                    text += f"五性屬性: {result.get('五性屬性', 'N/A')}\n"
                    text += f"信心度: {result.get('信心度', 'N/A')}\n"
                
                text += "\n"
            
            return text
        def format_single_result(result_dict):
            """格式化單一模型結果為可讀文本"""
            if not result_dict or "錯誤" in result_dict:
                return f"❌ 錯誤: {result_dict.get('錯誤', '未知錯誤')}"
            
            text = "🔍 單一模型辨識結果\n"
            text += "=" * 40 + "\n\n"
            
            text += f"辨識食物: {result_dict.get('辨識食物', 'N/A')}\n"
            text += f"英文名: {result_dict.get('英文名', 'N/A')}\n"
            text += f"五性屬性: {result_dict.get('五性屬性', 'N/A')}\n"
            text += f"使用模型: {result_dict.get('使用模型', 'N/A')}\n"
            text += f"信心度: {result_dict.get('信心度', 'N/A')}\n"
            text += f"運行模式: {result_dict.get('模式', 'N/A')}\n"
            
            return text

        def update_quick_result_on_button(image, model_name=None, use_all_models=False):
            """按鈕點擊後的辨識函數"""
            if image is None:
                return "❌ 請先上傳圖片", "請先上傳圖片"
            
            try:
                if use_all_models:
                    # 使用多模型綜合辨識
                    all_results = classify_with_all_models(image)
                    comprehensive = all_results.get("🎯 綜合辨識結果", {})
                    
                    if "錯誤" in comprehensive:
                        return f"❌ 辨識失敗: {comprehensive.get('錯誤', '未知錯誤')}", "⚠️ 多模型辨識失敗"
                    
                    quick_text = f"食物: {comprehensive.get('最終辨識', 'N/A')}\n"
                    quick_text += f"英文名: {comprehensive.get('英文名', 'N/A')}\n"
                    quick_text += f"五性: {comprehensive.get('五性屬性', 'N/A')}\n"
                    quick_text += f"模型共識度: {comprehensive.get('模型共識度', 'N/A')}\n"
                    quick_text += f"成功模型數: {comprehensive.get('成功模型數', 'N/A')}\n"
                    quick_text += "詳細結果請查看下方分頁"
                    
                    status = "✅ 多模型綜合辨識完成！"
                else:
                    # 使用單一模型辨識
                    result = classify_food_image(image, model_name or "swin_model_94")
                    
                    if "錯誤" in result:
                        return f"❌ 辨識失敗: {result.get('錯誤', '未知錯誤')}", "⚠️ 辨識遇到問題"
                    
                    quick_text = f"食物: {result.get('辨識食物', 'N/A')}\n"
                    quick_text += f"英文名: {result.get('英文名', 'N/A')}\n"
                    quick_text += f"五性: {result.get('五性屬性', 'N/A')}\n"
                    quick_text += f"使用模型: {result.get('使用模型', 'N/A')}\n"
                    quick_text += f"信心度: {result.get('信心度', 'N/A')}\n"
                    quick_text += f"運行模式: {result.get('模式', 'N/A')}"
                    
                    status = f"✅ 使用 {model_name or 'swin_model_94'} 辨識完成！"
                
                return quick_text, status
            except Exception as e:
                error_text = f"❌ 辨識失敗: {str(e)}"
                return error_text, f"❌ 辨識失敗: {str(e)}"        
        def update_comprehensive_result(image):
            if image is None:
                return "", "", "請先上傳圖片"
            
            try:
                # 執行綜合辨識
                all_results = classify_with_all_models(image)
                
                # 分離綜合結果和詳細結果
                comprehensive = all_results.get("🎯 綜合辨識結果", {})
                detailed = all_results.get("📊 各模型詳細結果", {})
                  # 格式化結果
                comprehensive_text = format_comprehensive_result(comprehensive)
                detailed_text = format_detailed_result(detailed)
                
                status = "✅ 所有模型辨識完成！" if comprehensive and "錯誤" not in comprehensive else "⚠️ 辨識遇到問題"
                
                return comprehensive_text, detailed_text, status
            except Exception as e:
                error_text = f"❌ 辨識過程發生錯誤: {str(e)}"
                return error_text, "", f"❌ 辨識失敗: {str(e)}"
        
        def update_single_result(image, model_name):
            if image is None:
                return "❌ 請先上傳圖片", "請先上傳圖片"
            
            try:
                result = classify_food_image(image, model_name)
                formatted_result = format_single_result(result)
                status = f"✅ 使用 {model_name} 辨識完成！" if "錯誤" not in result else f"⚠️ {model_name} 辨識失敗"
                return formatted_result, status
            except Exception as e:
                error_text = f"❌ 辨識過程發生錯誤: {str(e)}"
                return error_text, f"❌ {model_name} 辨識失敗: {str(e)}"

        def load_sample_image(image_filename):
            """載入範例圖片的函數"""
            try:
                image_path = f"./assets/images/{image_filename}"
                if os.path.exists(image_path):
                    from PIL import Image
                    image = Image.open(image_path)
                    return image, f"✅ 已載入範例圖片: {image_filename}"
                else:
                    return None, f"❌ 找不到範例圖片: {image_filename}"
            except Exception as e:
                return None, f"❌ 載入範例圖片失敗: {str(e)}"

        # 使用說明部分
        with gr.Column(elem_classes=["food-result-section"]):
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h3 style="color: #4A6741; font-size: 1.8rem; margin-bottom: 20px;">📋 使用說明</h3>
            </div>
            """)
            
            with gr.Row(elem_classes=["food-feature-cards-row"]):
                with gr.Column(elem_classes=["food-feature-card"]):
                    gr.HTML("""
                    <div class="food-feature-icon">📸</div>
                    <h4 class="food-feature-title">1. 上傳圖片</h4>
                    <p class="food-feature-description">
                        選擇清晰的食物圖片，建議光線充足、主體明顯的單一食物照片
                    </p>
                    """)
                
                with gr.Column(elem_classes=["food-feature-card"]):
                    gr.HTML("""
                    <div class="food-feature-icon">🎯</div>
                    <h4 class="food-feature-title">2. 選擇辨識方式</h4>
                    <p class="food-feature-description">
                        多模型綜合辨識：6個AI模型投票結果，準確度更高<br>
                        單一模型辨識：選擇特定模型進行快速辨識
                    </p>
                    """)
                
                with gr.Column(elem_classes=["food-feature-card"]):
                    gr.HTML("""
                    <div class="food-feature-icon">📊</div>
                    <h4 class="food-feature-title">3. 查看結果</h4>
                    <p class="food-feature-description">
                        獲得食物名稱、英文對照、中醫五性屬性分析，了解食物寒熱特性
                    </p>
                    """)
        
        # 免責聲明
        with gr.Column(elem_classes=["food-result-section"]):
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3 style="color: #8B4513; font-size: 1.6rem; margin-bottom: 15px;">⚠️ 重要聲明</h3>
            </div>
            <div style="background: linear-gradient(135deg, #FFF8E1 0%, #FFFBF0 100%); 
                        border: 2px solid rgba(139, 69, 19, 0.2); 
                        border-radius: 15px; 
                        padding: 25px; 
                        color: #8B4513; 
                        line-height: 1.6;
                        font-size: 0.95rem;">
                <p style="margin: 0 0 15px 0;">
                    <strong>🔬 關於AI辨識：</strong><br>
                    本系統使用深度學習技術進行食物辨識，雖經過大量數據訓練，但仍可能存在辨識錯誤的情況。
                    辨識結果僅供參考，請以實際食物為準。
                </p>
                <p style="margin: 0 0 15px 0;">
                    <strong>🌡️ 關於中醫屬性：</strong><br>
                    食物五性（寒、涼、平、溫、熱）資訊基於傳統中醫理論整理，
                    個人體質不同，建議諮詢專業中醫師獲得個人化建議。
                </p>
                <p style="margin: 0;">
                    <strong>⚕️ 健康提醒：</strong><br>
                    本系統不能替代專業醫療建議，如有健康問題或特殊飲食需求，
                    請諮詢合格的醫療專業人員或營養師。
                </p>
            </div>            """)        
            
        food_state = gr.State()
        
        # 創建一個可見的按鈕，並應用漂浮樣式
        # 這個按鈕的 click 事件會在 app.py 中被綁定
        back_to_home_btn = gr.Button(
            "🏠 🔙",
            elem_classes=["floating-return-button"], # 應用漂浮按鈕的CSS class
            visible=True  # 設置為可見
        )
        
        # 多模型綜合辨識按鈕事件
        recognize_all_btn.click(
            fn=update_comprehensive_result,
            inputs=[food_image],
            outputs=[comprehensive_result_display, detailed_result_display, status_display],
            api_name="recognize_all_food_models",
            show_progress=True
        )
        
        # 單一模型辨識按鈕事件
        # single_model_btn.click(
        #     fn=update_single_result,
        #     inputs=[food_image, model_name_input],
        #     outputs=[single_result_display, status_display],
        #     api_name="recognize_single_food_model",
        #     show_progress=True
        # )
        
        # 範例圖片按鈕事件綁定
        for btn, filename in sample_buttons:
            btn.click(
                fn=load_sample_image,
                inputs=[gr.State(filename)],
                outputs=[food_image, status_display],
                show_progress=True
            )
        
        # 返回主頁按鈕事件已在 app.py 中統一處理
    
    return None, food_state, back_to_home_btn

def load_swin_model(model_name: str, model_path: str = None):
    """
    專門載入 Swin Transformer 模型的函數
    處理 Swin 模型特有的 relative position 參數問題
    """
    if model_path is None:
        model_path = f"./model/{model_name}.pth"
    
    if not os.path.exists(model_path):
        print(f"❌ Swin 模型檔案不存在: {model_path}，使用模擬模式")
        return None
    
    try:
        print(f"Loading Swin model from {model_path}...")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 載入檢查點
        state_dict = torch.load(model_path, map_location=device)
        
        # 處理可能的 DataParallel 或 DistributedDataParallel 包裝
        if 'module.' in list(state_dict.keys())[0]:
            # 移除 'module.' 前綴
            new_state_dict = {}
            for key, value in state_dict.items():
                new_key = key.replace('module.', '')
                new_state_dict[new_key] = value
            state_dict = new_state_dict
            print("Removed 'module.' prefix from state dict keys")
        
        # 檢測類別數量 - 從 head.fc 或 head.weight 中獲取
        num_classes = 183  # 預設值
        if 'head.fc.weight' in state_dict:
            num_classes = state_dict['head.fc.weight'].shape[0]
        elif 'head.weight' in state_dict:
            num_classes = state_dict['head.weight'].shape[0]
        
        print(f"Detected {num_classes} classes")
        
        # 建立模型架構 - 根據模型名稱選擇正確的架構
        if 'swinv2' in model_name.lower():
            # Swin Transformer V2
            model = timm.create_model('swinv2_base_window12_192', 
                                    pretrained=False, 
                                    num_classes=num_classes)
        else:
            # Swin Transformer V1 (預設)
            model = timm.create_model('swin_base_patch4_window7_224', 
                                    pretrained=False, 
                                    num_classes=num_classes)
        
        # 載入權重
        try:
            model.load_state_dict(state_dict)
            print("Successfully loaded model with all keys matching")
        except RuntimeError as e:
            # 如果有不匹配的鍵，使用 strict=False
            missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
            
            # 分析缺失和多餘的鍵
            swin_specific_keys = []
            other_missing_keys = []
            
            for key in missing_keys:
                if any(pattern in key for pattern in ['relative_position_bias_table', 'relative_position_index', 'attn_mask']):
                    swin_specific_keys.append(key)
                else:
                    other_missing_keys.append(key)
            
            if swin_specific_keys:
                print(f"✅ Swin 模型特定參數將由模型自動初始化: {len(swin_specific_keys)} 個參數")
            
            if other_missing_keys:
                print(f"⚠️ 其他缺失的鍵: {other_missing_keys}")
            
            if unexpected_keys:
                print(f"⚠️ 未預期的鍵: {unexpected_keys[:10]}...")
        
        model = model.to(device)
        model.eval()
        
        print(f"✅ 成功載入 Swin 模型: {model_name} (類別數: {num_classes})")
        return model
        
    except Exception as e:
        print(f"❌ 載入 Swin 模型失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_efficientnet_model(model_name: str, model_path: str = None):
    """
    專門載入 EfficientNet 模型的函數
    使用標準的 torchvision EfficientNet 架構
    """
    if model_path is None:
        model_path = f"./model/{model_name}.pth"
    
    if not os.path.exists(model_path):
        print(f"❌ EfficientNet 模型檔案不存在: {model_path}，使用模擬模式")
        return None
    
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 載入檢查點
        checkpoint = torch.load(model_path, map_location=device)
        
        # 提取 state_dict
        if isinstance(checkpoint, dict):
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
        else:
            state_dict = checkpoint.state_dict() if hasattr(checkpoint, 'state_dict') else checkpoint
        
        # 清理鍵名，去除可能的 module. 前綴（用於處理 DataParallel 訓練的模型）
        cleaned_state_dict = {}
        for k, v in state_dict.items():
            name = k.replace("module.", "") if k.startswith("module.") else k
            cleaned_state_dict[name] = v
        
        # 從 classifier.1 層檢測類別數量
        num_classes = 183  # 預設值
        if 'classifier.1.weight' in cleaned_state_dict:
            num_classes = cleaned_state_dict['classifier.1.weight'].shape[0]
        elif 'classifier.1.out_features' in cleaned_state_dict:
            num_classes = cleaned_state_dict['classifier.1.out_features']
        
        # 使用標準的 torchvision EfficientNet-B5 架構
        from torchvision import models
        import torch.nn as nn
        
        model = models.efficientnet_b5(weights=None)  # 不載入預訓練權重
        
        # 修改分類器的最後一層以匹配類別數
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        
        model = model.to(device)
        
        # 載入模型權重
        missing_keys, unexpected_keys = model.load_state_dict(cleaned_state_dict, strict=False)
        
        if missing_keys:
            print(f"⚠️ EfficientNet 缺失的鍵: {missing_keys[:5]}..." if len(missing_keys) > 5 else f"⚠️ EfficientNet 缺失的鍵: {missing_keys}")
        
        if unexpected_keys:
            print(f"⚠️ EfficientNet 未預期的鍵: {unexpected_keys[:5]}..." if len(unexpected_keys) > 5 else f"⚠️ EfficientNet 未預期的鍵: {unexpected_keys}")
        
        model.eval()
        print(f"✅ 成功載入 EfficientNet 模型: {model_name} (類別數: {num_classes})")
        return model
        
    except Exception as e:
        print(f"❌ 載入 EfficientNet 模型失敗: {e}")
        return None

def load_convnext_model(model_name: str, model_path: str = None):
    """專門載入 ConvNeXt 模型的函數"""
    if model_path is None:
        model_path = f"./model/{model_name}.pth"
    
    if not os.path.exists(model_path):
        print(f"❌ ConvNeXt 模型檔案不存在: {model_path}，使用模擬模式")
        return None
    
    try:
        print(f"Loading ConvNeXt model from {model_path}...")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 先載入權重檢查類別數
        checkpoint = torch.load(model_path, map_location=device)
        
        # 清理鍵名，移除 module. 前綴（DataParallel 訓練產生的）
        cleaned_state_dict = {}
        for k, v in checkpoint.items():
            name = k.replace("module.", "") if k.startswith("module.") else k
            cleaned_state_dict[name] = v
        
        # 檢測類別數（ConvNeXt 的分類器在 classifier.2）
        classifier_key = 'classifier.2.weight'
        num_classes = None
        
        if classifier_key in cleaned_state_dict:
            num_classes = cleaned_state_dict[classifier_key].shape[0]
            print(f"Found classifier layer '{classifier_key}' with {num_classes} classes")
        else:
            # 如果找不到標準的分類器鍵，搜尋其他可能的分類器層
            for key in cleaned_state_dict.keys():
                if 'classifier' in key and 'weight' in key and len(cleaned_state_dict[key].shape) == 2:
                    classifier_key = key
                    num_classes = cleaned_state_dict[key].shape[0]
                    print(f"Found classifier layer '{classifier_key}' with {num_classes} classes")
                    break
        
        if num_classes is None:
            raise ValueError("無法從模型權重中檢測到類別數")
        
        # 使用 torchvision ConvNeXt 架構
        from torchvision import models
        import torch.nn as nn
        
        model = models.convnext_base(weights=None)
        
        # 修改分類器層（ConvNeXt 的分類器在 index 2）
        model.classifier[2] = nn.Linear(model.classifier[2].in_features, num_classes)
        
        # 載入權重（使用清理後的 state_dict）
        missing_keys, unexpected_keys = model.load_state_dict(cleaned_state_dict, strict=False)
        
        if missing_keys:
            print(f"Missing keys: {missing_keys[:5]}...")  # 只顯示前5個
        if unexpected_keys:
            print(f"Unexpected keys: {unexpected_keys[:5]}...")  # 只顯示前5個
        
        model.to(device)
        model.eval()
        
        print("ConvNeXt model loaded successfully!")
        return model
        
    except Exception as e:
        print(f"Error loading ConvNeXt model: {str(e)}")
        return None

def load_vgg_model(model_name: str, model_path: str = None):
    """
    專門載入 VGG 模型的函數
    使用標準的 torchvision VGG16 架構
    """
    if model_path is None:
        model_path = f"./model/{model_name}.pth"
    
    if not os.path.exists(model_path):
        print(f"❌ VGG 模型檔案不存在: {model_path}，使用模擬模式")
        return None
    
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 載入檢查點
        checkpoint = torch.load(model_path, map_location=device)
        
        # 提取 state_dict
        if isinstance(checkpoint, dict):
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
        else:
            state_dict = checkpoint.state_dict() if hasattr(checkpoint, 'state_dict') else checkpoint
        
        # 清理鍵名，去除可能的 module. 前綴
        cleaned_state_dict = {}
        for k, v in state_dict.items():
            name = k.replace("module.", "") if k.startswith("module.") else k
            cleaned_state_dict[name] = v
        
        # 從 classifier.6 層檢測類別數量
        num_classes = 183  # 預設值
        if 'classifier.6.weight' in cleaned_state_dict:
            num_classes = cleaned_state_dict['classifier.6.weight'].shape[0]
        elif 'classifier.6.out_features' in cleaned_state_dict:
            num_classes = cleaned_state_dict['classifier.6.out_features']
        
        # 使用標準的 torchvision VGG16 架構
        from torchvision import models
        import torch.nn as nn
        
        model = models.vgg16(weights=None)  # 不載入預訓練權重
        
        # 修改最後的分類層以匹配類別數
        model.classifier[6] = nn.Linear(4096, num_classes)
        
        model = model.to(device)
        
        # 載入模型權重
        missing_keys, unexpected_keys = model.load_state_dict(cleaned_state_dict, strict=False)
        
        if missing_keys:
            print(f"⚠️ VGG 缺失的鍵: {missing_keys[:5]}..." if len(missing_keys) > 5 else f"⚠️ VGG 缺失的鍵: {missing_keys}")
        
        if unexpected_keys:
            print(f"⚠️ VGG 未預期的鍵: {unexpected_keys[:5]}..." if len(unexpected_keys) > 5 else f"⚠️ VGG 未預期的鍵: {unexpected_keys}")
        
        model.eval()
        print(f"✅ 成功載入 VGG 模型: {model_name} (類別數: {num_classes})")
        return model
        
    except Exception as e:
        print(f"❌ 載入 VGG 模型失敗: {e}")
        return None

