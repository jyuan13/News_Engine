import logging
import os
from datetime import datetime
from config import CONFIG
from utils_data import StatsTracker, save_custom_json
from YFinance_Fetcher import YFinanceFetcher
from Akshare_Fetcher import AkshareFetcher
from OpenBB_NewsFetcher import OpenBBNewsFetcher
from GoogleNews_RSS_Fetcher import GoogleNewsRSSFetcher
from Guardian_Fetcher import GuardianFetcher

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("--- Starting News Acquisition Engine (Modular + Mass Quantity) ---")
    
    # 1. Initialize Objects
    stats_tracker = StatsTracker()
    yf_fetcher = YFinanceFetcher(stats_tracker)
    ak_fetcher = AkshareFetcher(stats_tracker)
    obb_fetcher = OpenBBNewsFetcher()
    google_fetcher = GoogleNewsRSSFetcher(stats_tracker)
    guardian_fetcher = GuardianFetcher(stats_tracker)

    output_data = {}

    # 2. Process English Sources (YFinance + OpenBB + Google + Guardian)
    if "ENGLISH_SOURCES" in CONFIG["GROUPS"]:
        for cat_name, cat_config in CONFIG["GROUPS"]["ENGLISH_SOURCES"].items():
            print(f"\n>>> Processing English Category: {cat_name}")
            output_data[cat_name] = []
            
            for item in cat_config["items"]:
                val = item["value"]
                name = item["name"]
                itype = item.get("type", "stock_us")
                
                fetched = []
                
                # CASE A: Stocks/Indices (YFinance, OpenBB)
                if itype in ["stock_us", "index_us", "stock_vn", "future_us"]:
                    # 1. YFinance
                    fetched.extend(yf_fetcher.fetch(val))
                    
                    # 2. OpenBB
                    try:
                        obb_news = obb_fetcher.fetch_company_news([val])
                        if obb_news:
                            fetched.extend(obb_news)
                            stats_tracker.update(f"OpenBB({val})", len(obb_news))
                    except Exception as e:
                        stats_tracker.update(f"OpenBB({val})", 0, e)
                        
                # CASE B: Keywords/Topics (Google RSS, Guardian)
                # Note: We also add Google RSS for stocks to boost quantity if user wants
                # But primarily for keywords.
                
                if itype == "keyword" or "desc" in item: # "desc" usually implies complex topic
                    # 1. Google RSS (Mass Quantity + Full Text Scrape)
                    g_news = google_fetcher.fetch(query=val, lang="en-US", geo="US")
                    fetched.extend(g_news)
                    
                    # 2. Guardian (High Quality Full Text)
                    # Use 'val' or 'name' as query
                    guard_news = guardian_fetcher.fetch(query=val)
                    fetched.extend(guard_news)
                
                if fetched:
                    output_data[cat_name].extend(fetched)

    # 3. Process Chinese Sources (Akshare + Google RSS CN)
    if "CHINESE_SOURCES" in CONFIG["GROUPS"]:
        for cat_name, cat_config in CONFIG["GROUPS"]["CHINESE_SOURCES"].items():
            print(f"\n>>> Processing Chinese Category: {cat_name}")
            output_data[cat_name] = []
            
            for item in cat_config["items"]:
                val = item["value"]
                itype = item.get("type", "stock_hk")
                
                fetched = []
                
                # CASE A: HK/CN Stocks (Akshare)
                if itype in ["stock_hk", "stock_zh_a", "etf_zh"]:
                    fetched.extend(ak_fetcher.fetch_stock_news(val))
                    
                    # Augment with Google RSS (CN) for specific tickers (using Name often better than Code in RSS)
                    # e.g. "腾讯" instead of "0700.HK"
                    name_query = item.get("name", val)
                    g_news = google_fetcher.fetch(query=name_query, lang="zh-CN", geo="CN", limit=30) # Moderate limit for specific stocks
                    fetched.extend(g_news)

                # CASE B: Keywords (Google RSS CN)
                elif itype == "keyword":
                    logger.info(f"Searching Keyword (CN): {val}")
                    g_news = google_fetcher.fetch(query=val, lang="zh-CN", geo="CN")
                    fetched.extend(g_news)
                
                if fetched:
                    output_data[cat_name].extend(fetched)

    # 4. Process General/Macro (Mixed/Global)
    print("\n>>> Processing General/Macro News")
    output_data["GENERAL"] = []
    
    # A. Akshare Rolling
    output_data["GENERAL"].extend(ak_fetcher.fetch_rolling_news())
    
    # B. OpenBB World News (Proxy)
    try:
        obb_world = obb_fetcher.fetch_world_news()
        if obb_world:
            output_data["GENERAL"].extend(obb_world)
    except Exception as e:
        logger.warning(f"OpenBB World News failed: {e}")
        
    # C. Google RSS "World News"
    output_data["GENERAL"].extend(google_fetcher.fetch("World Economy", limit=50))
    output_data["GENERAL"].extend(google_fetcher.fetch("Artificial Intelligence", limit=50))

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
