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

    # Separate Data Containers
    data_yfinance = []
    data_openbb = []
    data_akshare = []
    data_google_rss = []
    data_guardian = [] # If enabled later

    # 2. Process English Sources
    if "ENGLISH_SOURCES" in CONFIG["GROUPS"]:
        for cat_name, cat_config in CONFIG["GROUPS"]["ENGLISH_SOURCES"].items():
            print(f"\n>>> Processing English Category: {cat_name}")
            
            for item in cat_config["items"]:
                val = item["value"]
                itype = item.get("type", "stock_us")
                
                # CASE A: Stocks/Indices (YFinance, OpenBB)
                if itype in ["stock_us", "index_us", "stock_vn", "future_us"]:
                    # 1. YFinance
                    yf_res = yf_fetcher.fetch(val)
                    if yf_res:
                        _tag_category(yf_res, cat_name)
                        data_yfinance.extend(yf_res)
                    
                    # 2. OpenBB
                    try:
                        obb_news = obb_fetcher.fetch_company_news([val])
                        if obb_news:
                            _tag_category(obb_news, cat_name)
                            data_openbb.extend(obb_news)
                            stats_tracker.update(f"OpenBB({val})", len(obb_news))
                    except Exception as e:
                        stats_tracker.update(f"OpenBB({val})", 0, e)
                        
                # CASE B: Keywords/Topics (Google RSS, Gaurdian)
                if itype == "keyword" or "desc" in item:
                    # 1. Google RSS
                    g_news = google_fetcher.fetch(query=val, lang="en-US", geo="US")
                    if g_news:
                        _tag_category(g_news, cat_name)
                        data_google_rss.extend(g_news)
                    
                    # 2. Guardian (Disabled)
                    # guard_news = guardian_fetcher.fetch(query=val)
                    # if guard_news: data_guardian.extend(guard_news)

    # 3. Process Chinese Sources
    if "CHINESE_SOURCES" in CONFIG["GROUPS"]:
        for cat_name, cat_config in CONFIG["GROUPS"]["CHINESE_SOURCES"].items():
            print(f"\n>>> Processing Chinese Category: {cat_name}")
            
            for item in cat_config["items"]:
                val = item["value"]
                itype = item.get("type", "stock_hk")
                
                if itype in ["stock_hk", "stock_zh_a", "etf_zh"]:
                    # Akshare
                    ak_news = ak_fetcher.fetch_stock_news(val)
                    if ak_news:
                        _tag_category(ak_news, cat_name)
                        data_akshare.extend(ak_news)
                    
                    # Google RSS (CN)
                    name_query = item.get("name", val)
                    g_news_cn = google_fetcher.fetch(query=name_query, lang="zh-CN", geo="CN", limit=30)
                    if g_news_cn:
                        _tag_category(g_news_cn, cat_name)
                        data_google_rss.extend(g_news_cn)

                elif itype == "keyword":
                    # Google RSS (CN)
                    g_news_cn = google_fetcher.fetch(query=val, lang="zh-CN", geo="CN")
                    if g_news_cn:
                        _tag_category(g_news_cn, cat_name)
                        data_google_rss.extend(g_news_cn)

    # 4. General/Macro
    print("\n>>> Processing General/Macro News")
    
    # Akshare Rolling
    rolling = ak_fetcher.fetch_rolling_news()
    if rolling:
        _tag_category(rolling, "GENERAL")
        data_akshare.extend(rolling)
    
    # OpenBB World
    try:
        obb_world = obb_fetcher.fetch_world_news()
        if obb_world:
            _tag_category(obb_world, "GENERAL")
            data_openbb.extend(obb_world)
    except Exception as e:
        logger.warning(f"OpenBB World News failed: {e}")
        
    # Google RSS World
    w1 = google_fetcher.fetch("World Economy", limit=50)
    w2 = google_fetcher.fetch("Artificial Intelligence", limit=50)
    if w1: 
        _tag_category(w1, "GENERAL")
        data_google_rss.extend(w1)
    if w2:
        _tag_category(w2, "GENERAL")
        data_google_rss.extend(w2)

    # 5. Save Reports Separately
    timestamp = str(datetime.now())
    stats_report = stats_tracker.get_report()
    
    _save_report("Report_YFinance.json", data_yfinance, timestamp, stats_report)
    _save_report("Report_Akshare.json", data_akshare, timestamp, stats_report)
    _save_report("Report_OpenBB.json", data_openbb, timestamp, stats_report)
    _save_report("Report_GoogleRSS.json", data_google_rss, timestamp, stats_report)
    
    # Optional: Save Combined for backward compatibility or easier viewing
    # combined = data_yfinance + data_akshare + data_openbb + data_google_rss
    # _save_report("Report_All.json", combined, timestamp, stats_report)

    print(f"\n[DONE] Execution Complete.")
    print(f"Reports saved: Report_YFinance.json, Report_Akshare.json, Report_OpenBB.json, Report_GoogleRSS.json")

def _tag_category(news_list, category):
    for n in news_list:
        n['category'] = category

def _save_report(filename, data, timestamp, stats):
    if not data:
        return # Skip empty reports
        
    final_output = {
        "meta": {
            "timestamp": timestamp,
            "count": len(data),
            "stats": stats # Include full stats in each for context, or filter? Keeping full for now.
        },
        "data": data
    }
    abs_path = os.path.abspath(filename)
    save_custom_json(final_output, abs_path)
    print(f"Saved {abs_path} ({len(data)} items)")

if __name__ == "__main__":
    main()
