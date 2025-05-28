#!/usr/bin/env python3
# run.py - 啟動腳本

import sys
import os

def main():
    print("🏥 中醫食物寒熱辨識與體質分析系統")
    print("=" * 50)
    print("請選擇要運行的版本：")
    print("1. app.py - 模組化版本（推薦）")
    print("2. main.py - 導航式UI版本")
    print("3. main_old.py - 舊版備份")
    print("4. 退出")
    print("=" * 50)
    
    while True:
        choice = input("請輸入選項 (1-4): ").strip()
        
        if choice == "1":
            print("🚀 啟動模組化版本...")
            os.system("python3 app.py")
            break
        elif choice == "2":
            print("🚀 啟動導航式UI版本...")
            os.system("python3 main.py")
            break
        elif choice == "3":
            print("🚀 啟動舊版備份...")
            os.system("python3 main_old.py")
            break
        elif choice == "4":
            print("👋 再見！")
            sys.exit(0)
        else:
            print("❌ 無效選項，請重新輸入")

if __name__ == "__main__":
    main() 