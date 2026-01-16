import logging
import main
from config import CONFIG
import main as main_module # Alias for clarity if needed

# Mock the CONFIG to be very small for quick testing
# Must match the new "GROUPS" structure keys: US_MARKET_TECH, HK_TECH_CN
MINI_CONFIG = {
    "DAYS_BACK": 2,
    "OUTPUT_FILE": "test_news_result.json",
    "GROUPS": {
        "ENGLISH_SOURCES": {
            "US_MARKET_TECH": {
                "desc": "Test US Tech",
                "items": [{"value": "NVDA", "name": "Nvidia", "type": "stock_us"}]
            }
        },
        "CHINESE_SOURCES": {
            "HK_TECH_CN": {
                "desc": "Test HK Tech",
                "items": [{"value": "0700.HK", "name": "Tencent", "type": "stock_hk"}]
            }
        }
    }
}

def test_run():
    # Patch the config in the imported module
    main.CONFIG = MINI_CONFIG
    
    print(">>> Running Mini Integration Test (Modular)...")
    main.main()
    print(">>> Test Complete. Check test_news_result.json")

if __name__ == "__main__":
    test_run()
