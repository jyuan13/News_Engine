import logging
import os
from datetime import datetime
from config import CONFIG
from utils.utils_data import StatsTracker, save_custom_json
from fetchers.YFinance_Fetcher import YFinanceFetcher
from fetchers.Akshare_Fetcher import AkshareFetcher
from fetchers.OpenBB_NewsFetcher import OpenBBNewsFetcher
from fetchers.GoogleNews_RSS_Fetcher import GoogleNewsRSSFetcher
from fetchers.Guardian_Fetcher import GuardianFetcher

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
    
    # Google RSS Split by Language
    data_google_rss_en = []
    data_google_rss_cn = []

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
                        data_google_rss_en.extend(g_news)
                    
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
                        data_google_rss_cn.extend(g_news_cn)

                elif itype == "keyword":
                    # Google RSS (CN)
                    g_news_cn = google_fetcher.fetch(query=val, lang="zh-CN", geo="CN")
                    if g_news_cn:
                        _tag_category(g_news_cn, cat_name)
                        data_google_rss_cn.extend(g_news_cn)

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
        data_google_rss_en.extend(w1)
    if w2:
        _tag_category(w2, "GENERAL")
        data_google_rss_en.extend(w2)

    # 5. Save Raw Reports (Combined Google RSS)
    timestamp = str(datetime.now())
    stats_report = stats_tracker.get_report()
    
    data_google_rss_combined = data_google_rss_en + data_google_rss_cn
    
    _save_report("Report_YFinance.json", data_yfinance, timestamp, stats_report)
    _save_report("Report_Akshare.json", data_akshare, timestamp, stats_report)
    _save_report("Report_OpenBB.json", data_openbb, timestamp, stats_report)
    _save_report("Report_GoogleRSS.json", data_google_rss_combined, timestamp, stats_report)
    
    
    # 6. Data Cleaning (Semantic Deduplication)
    try:
        from processing.DataCleaner import DataCleaner
        cleaner = DataCleaner()
        if cleaner.enabled:
            print("\n>>> Starting Data Cleaning (Second Stage)...")
            
            # --- English Scope ---
            map_en = {
                "YFinance": data_yfinance,
                "OpenBB": data_openbb,
                "GoogleRSS_EN": data_google_rss_en
            }
            cleaned_en = cleaner.clean_data(map_en, language="ENGLISH")
            
            # --- Chinese Scope ---
            map_cn = {
                "Akshare": data_akshare,
                "GoogleRSS_CN": data_google_rss_cn
            }
            cleaned_cn = cleaner.clean_data(map_cn, language="CHINESE")
            
            # --- Merge & Save ---
            clean_google_combined = cleaned_en["GoogleRSS_EN"] + cleaned_cn["GoogleRSS_CN"]
            
            _save_report("Cleaned_Report_YFinance.json", cleaned_en["YFinance"], timestamp, stats_report)
            _save_report("Cleaned_Report_OpenBB.json", cleaned_en["OpenBB"], timestamp, stats_report)
            _save_report("Cleaned_Report_Akshare.json", cleaned_cn["Akshare"], timestamp, stats_report)
            _save_report("Cleaned_Report_GoogleRSS.json", clean_google_combined, timestamp, stats_report)

    except Exception as e:
        logger.error(f"Data Cleaning Failed: {e}")

    print(f"\n[DONE] Execution Complete.")
    print(f"Reports saved: Report_*.json (Raw) and Cleaned_Report_*.json (Cleaned)")

def _tag_category(news_list, category):
    for n in news_list:
        n['category'] = category

def _save_report(filename, data, timestamp, stats):
    if not data:
        return # Skip empty reports
        
    # Remove 'link' field as requested by user
    # Note: If we do this in place, it affects the object.
    # Since we need to pass data to cleaner, we should be careful not to destroy potential info?
    # Actually, embedding uses 'title' and 'content'. 'link' is not used for embedding.
    # So removing 'link' from raw objects is fine, they are still passed to cleaner.
    for item in data:
        item.pop('link', None)
        
    final_output = {
        "meta": {
            "timestamp": timestamp,
            "count": len(data),
            "stats": stats 
        },
        "data": data
    }
    abs_path = os.path.abspath(os.path.join("data", filename))
    save_custom_json(final_output, abs_path)
    print(f"Saved {abs_path} ({len(data)} items)")

if __name__ == "__main__":
    main()
