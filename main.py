import logging
import os
from datetime import datetime
from config import CONFIG
from utils_data import StatsTracker, save_custom_json
from YFinance_Fetcher import YFinanceFetcher
from Akshare_Fetcher import AkshareFetcher
from OpenBB_NewsFetcher import OpenBBNewsFetcher

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("--- Starting News Acquisition Engine (Modular) ---")
    
    # 1. Initialize Objects
    stats_tracker = StatsTracker()
    yf_fetcher = YFinanceFetcher(stats_tracker)
    ak_fetcher = AkshareFetcher(stats_tracker)
    obb_fetcher = OpenBBNewsFetcher() # OpenBB fetcher handles its own logging/errors mostly internally or via logger

    output_data = {}

    # 2. Process English Sources (YFinance + OpenBB)
    if "ENGLISH_SOURCES" in CONFIG["GROUPS"]:
        for cat_name, cat_config in CONFIG["GROUPS"]["ENGLISH_SOURCES"].items():
            print(f"\n>>> Processing English Category: {cat_name} ({cat_config['desc']})")
            output_data[cat_name] = []
            
            for item in cat_config["items"]:
                val = item["value"]
                itype = item.get("type", "stock_us")
                
                # A. Basic YFinance Fetch
                fetched = yf_fetcher.fetch(val)
                
                # B. OpenBB Augmentation (Quantity)
                # Only distinct stocks/indices (skip keywords if any)
                if itype not in ["keyword"]:
                    try:
                        # OpenBB handles its own retries/logic internally mostly
                        obb_news = obb_fetcher.fetch_company_news([val])
                        if obb_news:
                            fetched.extend(obb_news)
                            stats_tracker.update(f"OpenBB({val})", len(obb_news))
                    except Exception as e:
                        logger.warning(f"OpenBB fetch failed for {val}: {e}")
                        stats_tracker.update(f"OpenBB({val})", 0, e)
                
                if fetched:
                    output_data[cat_name].extend(fetched)

    # 3. Process Chinese Sources (Akshare)
    if "CHINESE_SOURCES" in CONFIG["GROUPS"]:
        for cat_name, cat_config in CONFIG["GROUPS"]["CHINESE_SOURCES"].items():
            print(f"\n>>> Processing Chinese Category: {cat_name} ({cat_config['desc']})")
            output_data[cat_name] = []
            
            for item in cat_config["items"]:
                val = item["value"]
                itype = item.get("type", "stock_hk")
                
                fetched = []
                if itype in ["stock_hk", "stock_zh_a", "etf_zh"]:
                    # Note: Akshare logic for HK stocks might vary, using 'stock_news_em' generic for now
                    # or specific logic inside AkshareFetcher if distinction needed.
                    fetched = ak_fetcher.fetch_stock_news(val)
                
                elif itype == "keyword":
                    logger.info(f"Skipping Search for {val} (SerpApi Paused)")
                    stats_tracker.update(f"Search: {item['name']}", 0, "PAUSED")
                
                if fetched:
                    output_data[cat_name].extend(fetched)

    # 4. Process General/Macro (Mixed/Global)
    print("\n>>> Processing General/Macro News")
    output_data["GENERAL"] = []
    
    # A. Akshare Rolling
    output_data["GENERAL"].extend(ak_fetcher.fetch_rolling_news())
    
    # B. OpenBB World News (Proxy strategy)
    try:
        obb_world = obb_fetcher.fetch_world_news()
        if obb_world:
            output_data["GENERAL"].extend(obb_world)
            stats_tracker.update("OpenBB World", len(obb_world))
    except Exception as e:
        logger.warning(f"OpenBB World News failed: {e}")
        stats_tracker.update("OpenBB World", 0, e)

    # 5. Generate Final Report & Save
    final_output = {
        "meta": {
            "timestamp": str(datetime.now()),
            "days_back": CONFIG["DAYS_BACK"],
            "stats": stats_tracker.get_report()
        },
        "data": output_data
    }
    
    abs_path = os.path.abspath(CONFIG["OUTPUT_FILE"])
    save_custom_json(final_output, abs_path)

    print(f"\n[DONE] Execution Complete.")
    print(f"Stats & News written to: {abs_path}")

if __name__ == "__main__":
    main()
