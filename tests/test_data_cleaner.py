import logging
import sys
# Make sure project root is in path if running directly
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.DataCleaner import DataCleaner

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_cleaning():
    print("\n--- Testing DataCleaner ---")
    
    cleaner = DataCleaner()
    if not cleaner.enabled:
        print("SKIP: Cleaning not enabled (missing dependencies?)")
        return

    # Mock Data - English
    en_data = {
        "SourceA": [
            {"title": "Apple releases new iPhone 16", "content": "The new phone features AI integration and better battery."},
            {"title": "iPhone 16 launched by Apple today", "content": "It comes with artificial intelligence and improved power efficiency."}, # Should be dup
            {"title": "Microsoft updates Windows", "content": "Windows 12 is coming soon."}
        ],
        "SourceB": [
            {"title": "Apple's iPhone 16 is here", "content": "AI features are the highlight of the new device."} # Should be dup of Item 1
        ]
    }
    
    # Mock Data - Chinese
    cn_data = {
        "SourceCN": [
            {"title": "腾讯发布新游戏", "content": "这款游戏名为王者荣耀世界。"},
            {"title": "王者荣耀世界由腾讯发布", "content": "腾讯推出了新的开放世界游戏。"} # Should be dup
        ]
    }

    print("\n1. Testing ENGLISH Cleaning...")
    cleaned_en = cleaner.clean_data(en_data, language="ENGLISH")
    
    count_en = sum(len(v) for v in cleaned_en.values())
    print(f"Original EN: 4 -> Cleaned EN: {count_en}")
    
    if count_en == 2:
        print("PASS: English Deduplication successful.")
    else:
        print(f"FAIL: Expected 2 items, got {count_en}.")

    print("\n2. Testing CHINESE Cleaning...")
    cleaned_cn = cleaner.clean_data(cn_data, language="CHINESE")
    
    count_cn = sum(len(v) for v in cleaned_cn.values())
    print(f"Original CN: 2 -> Cleaned CN: {count_cn}")
    
    if count_cn == 1:
        print("PASS: Chinese Deduplication successful.")
    else:
        print(f"FAIL: Expected 1 item, got {count_cn}.")

if __name__ == "__main__":
    test_cleaning()
