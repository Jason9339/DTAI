# config.py - 配置文件
import csv
import os
from datetime import datetime

def load_food_database_from_csv(csv_file="food_database.csv"):
    """從CSV文件載入食物資料庫"""
    food_database = {}
    
    try:
        if os.path.exists(csv_file):
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    chinese_name = row['Chinese']
                    five_nature = row['FiveNature']
                    
                    food_database[chinese_name] = {
                        "英文名": row['English'],
                        "五性": five_nature,
                    }
        else:
            # 如果CSV文件不存在，使用預設資料庫
            print(f"警告：找不到 {csv_file}，使用預設食物資料庫")
            food_database = {
                "蘋果": {"英文名": "apple", "五性": "平性"},
                "香蕉": {"英文名": "banana", "五性": "寒性"},
                "橘子": {"英文名": "orange", "五性": "溫性"},
                "西瓜": {"英文名": "watermelon", "五性": "寒性"},
                "龍眼": {"英文名": "longan", "五性": "溫性"},
            }
    except Exception as e:
        print(f"載入CSV文件時發生錯誤: {e}")
        # 使用預設資料庫作為備案
        food_database = {
            "蘋果": {"英文名": "apple", "五性": "平性"},
            "香蕉": {"英文名": "banana", "五性": "寒性"},
            "橘子": {"英文名": "orange", "五性": "溫性"},
            "西瓜": {"英文名": "watermelon", "五性": "寒性"},
            "龍眼": {"英文名": "longan", "五性": "溫性"},
        }
    
    return food_database

# 載入食物資料庫
FOOD_DATABASE = load_food_database_from_csv()

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

# 體質別名和圖片路徑映射
CONSTITUTION_INFO = {
    "平和體質": {
        "alias": "曦光導者",
        "nickname": "健康派",
        "image_path": "assets/images/平和體質.png",
        "description": "陰陽氣血調和，體質平和"
    },
    "氣虛體質": {
        "alias": "虛風使者",
        "nickname": "氣短派",
        "image_path": "assets/images/氣虛體質.png",
        "description": "元氣不足，易疲勞乏力"
    },
    "陽虛體質": {
        "alias": "寒光守望者",
        "nickname": "怕冷派",
        "image_path": "assets/images/陽虛體質.png",
        "description": "陽氣不足，畏寒怕冷"
    },
    "陰虛體質": {
        "alias": "燄泉行者",
        "nickname": "缺水派",
        "image_path": "assets/images/陰虛體質.png",
        "description": "陰液虧少，虛熱內擾"
    },
    "痰濕體質": {
        "alias": "濁澤漫步者",
        "nickname": "痰多派",
        "image_path": "assets/images/痰濕體質.png",
        "description": "痰濕凝聚，形體肥胖"
    },
    "濕熱體質": {
        "alias": "焰痕旅客",
        "nickname": "長痘派",
        "image_path": "assets/images/濕熱體質.png",
        "description": "濕熱內蘊，面垢油膩"
    },
    "血瘀體質": {
        "alias": "夜凝旅人",
        "nickname": "長斑派",
        "image_path": "assets/images/瘀滯體質.png",
        "description": "血行不暢，膚色晦暗"
    },
    "氣鬱體質": {
        "alias": "思霧使徒",
        "nickname": "鬱悶派",
        "image_path": "assets/images/氣鬱體質.png",
        "description": "氣機鬱滯，神情抑鬱"
    },
    "特稟體質": {
        "alias": "異感覺醒者",
        "nickname": "過敏派",
        "image_path": "assets/images/特稟體質.png",
        "description": "先天稟賦不足，過敏體質"
    }
}

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