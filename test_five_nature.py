#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from collections import defaultdict

def read_and_classify_by_nature(csv_file):
    """讀取 CSV 檔案並依照五性分類"""
    # 建立字典以儲存各種五性的食物
    nature_dict = defaultdict(list)
    
    # 讀取 CSV 檔案
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                english_name = row['English']
                chinese_name = row['Chinese']
                five_nature = row['FiveNature']
                
                # 將食物資訊加入對應的五性分類中
                nature_dict[five_nature].append({
                    'English': english_name,
                    'Chinese': chinese_name
                })
    
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {csv_file}")
        return None
    except Exception as e:
        print(f"讀取檔案時發生錯誤：{e}")
        return None
    
    return nature_dict

def display_classification(nature_dict):
    """依照五性分類顯示食物"""
    if not nature_dict:
        return
    
    # 定義五性的顯示順序：熱、溫、平、涼、寒
    nature_order = ['熱', '溫', '平', '涼', '寒']
    
    print("=" * 60)
    print("食物五性分類表")
    print("=" * 60)
    
    for nature in nature_order:
        if nature in nature_dict:
            print(f"\n【{nature}性食物】 (共 {len(nature_dict[nature])} 種)")
            print("-" * 40)
            
            for i, food in enumerate(nature_dict[nature], 1):
                print(f"{i:2d}. {food['Chinese']:12s} ({food['English']})")
    
    # 顯示統計資訊
    total_count = sum(len(foods) for foods in nature_dict.values())
    print("\n" + "=" * 60)
    print("統計資訊：")
    for nature in nature_order:
        if nature in nature_dict:
            count = len(nature_dict[nature])
            percentage = (count / total_count) * 100
            print(f"{nature}性食物: {count:3d} 種 ({percentage:5.1f}%)")
    print(f"總計: {total_count} 種食物")
    print("=" * 60)

def main():
    """主函式"""
    csv_file = 'merged.csv'
    
    print("正在讀取與分析食物五性資料...")
    nature_dict = read_and_classify_by_nature(csv_file)
    
    if nature_dict:
        display_classification(nature_dict)
    else:
        print("無法處理資料，請確認檔案是否存在且格式正確。")

if __name__ == "__main__":
    main()
