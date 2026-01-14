import os
import json
import logging
import re
import time
from datetime import datetime, timedelta
import yfinance as yf
import akshare as ak
from config import CONFIG

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 1. Retry Helpers
# ==========================================
MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds

def retry_operation(func_name, operation, *args, **kwargs):
    """
    Helper to retry a function call up to MAX_RETRIES times.
    """
    last_exception = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logger.warning(f"[{func_name}] Attempt {attempt}/{MAX_RETRIES} failed: {e}. Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    
    # If we get here, all retries failed
    raise last_exception

# ==========================================
# 2. Statistics Tracker
# ==========================================
class StatsTracker:
    def __init__(self):
        self.stats = {} 

    def update(self, source, count, error=None):
        if source not in self.stats:
            self.stats[source] = {'count': 0, 'status': 'OK', 'error': None}
        
        self.stats[source]['count'] += count
        if error:
            self.stats[source]['status'] = 'FAILED'
            self.stats[source]['error'] = str(error)
    
    def get_report(self):
        return self.stats

STATS = StatsTracker()

# ==========================================
# 3. Fetcher Layers
# ==========================================

def fetch_yfinance_news_logic(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    # Ticker.news is a property that calls API
    return ticker.news

def fetch_yfinance_news(ticker_symbol):
    """Fetch news from YFinance with Retries."""
    source_name = f"YFinance ({ticker_symbol})"
    logger.info(f"Fetching {source_name}...")
    try:
        # Retry the actual network call
        news = retry_operation("YFinance", fetch_yfinance_news_logic, ticker_symbol)
        
        results = []
        for item in news:
            content_data = item.get('content', item) if 'content' in item else item
            
            title = content_data.get('title')
            if not title: continue

            pub_date_str = content_data.get('pubDate') or content_data.get('displayTime')
            pub_time = None
            
            if pub_date_str:
                try:
                    pub_time = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                except:
                    pass
            
            if not pub_time and 'providerPublishTime' in item:
                 pub_time = datetime.fromtimestamp(item['providerPublishTime'])
            
            if not pub_time:
                pub_time = datetime.now()

            # Ensure TZ-naive comparison
            pub_time_naive = pub_time.replace(tzinfo=None)
            if (datetime.now() - pub_time_naive).days <= CONFIG["DAYS_BACK"]:
                results.append({
                    "source": "YFinance",
                    "title": title,
                    "publish_time": pub_time.isoformat(),
                    "publisher": (content_data.get('provider') or {}).get('displayName'),
                    "related_ticker": ticker_symbol,
                    "content": content_data.get('summary', 'N/A')
                })
        STATS.update(source_name, len(results))
        return results
    except Exception as e:
        logger.error(f"Error {source_name}: {e}")
        STATS.update(source_name, 0, e)
        return []

def fetch_akshare_stock_logic(symbol):
    return ak.stock_news_em(symbol=symbol)

def fetch_akshare_stock(symbol):
    """Fetch specific stock/ETF news from Akshare (EastMoney) with Retries."""
    source_name = f"Akshare Stock ({symbol})"
    logger.info(f"Fetching {source_name}...")
    try:
        if hasattr(ak, 'stock_news_em'):
            # Retry the network call
            news_df = retry_operation(f"Akshare({symbol})", fetch_akshare_stock_logic, symbol)
            
            results = []
            cutoff_date = (datetime.now() - timedelta(days=CONFIG["DAYS_BACK"])).strftime("%Y-%m-%d")
            
            for _, row in news_df.iterrows():
                pub_time = row.get('发布时间')
                if pub_time >= cutoff_date:
                    results.append({
                        "source": "Akshare/EastMoney",
                        "title": row.get('新闻标题'),
                        "publish_time": pub_time,
                        "content": row.get('新闻内容'),
                        "related_ticker": symbol
                    })
            STATS.update(source_name, len(results))
            return results
        else:
            STATS.update(source_name, 0, "stock_news_em not found")
            return []
            
    except Exception as e:
        logger.error(f"Error {source_name}: {e}")
        STATS.update(source_name, 0, e)
        return []

def try_fetch_cls_rolling_logic():
    func = getattr(ak, 'stock_info_global_cls')
    return func()

def try_fetch_cls_rolling():
    """Fetch Cailian Press rolling news with Retries."""
    source_name = "Cailian Press (Rolling)"
    logger.info(f"Fetching {source_name}...")
    
    if not hasattr(ak, 'stock_info_global_cls'):
        STATS.update(source_name, 0, "stock_info_global_cls not found")
        return []

    try:
        # Retry logic
        news_df = retry_operation("Akshare(CLS)", try_fetch_cls_rolling_logic)
        
        results = []
        for _, row in news_df.head(100).iterrows():
            title = row.get('标题', 'No Title')
            content = row.get('内容', '')
            d = row.get('发布日期')
            t = row.get('发布时间')
            pub_time = f"{d} {t}" if d and t else str(datetime.now())
            
            results.append({
                "source": "Akshare/CLS",
                "title": title,
                "publish_time": str(pub_time),
                "content": content,
                "related_ticker": "MARKET"
            })
        STATS.update(source_name, len(results))
        return results
    except Exception as e:
        STATS.update(source_name, 0, e)
        return []

# ==========================================
# 4. JSON Formatter (Single Line Stats)
# ==========================================

def save_custom_json(data, filepath):
    """
    Save JSON with 'stats' inner objects formatted on a single line.
    """
    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    
    # Regex to collapse stats values to single lines
    def collapse_match(match):
        block = match.group(0)
        collapsed = re.sub(r'\s*\n\s*', ' ', block)
        collapsed = re.sub(r'\{ "', '{ "', collapsed)
        collapsed = re.sub(r', "', ', "', collapsed)
        collapsed = re.sub(r' \} ', ' }', collapsed) 
        return collapsed

    pattern = r'\{\s+"count": \d+,\s+"status": "[^"]+",\s+"error": (?:null|"[^"]*")\s+\}'
    json_str_custom = re.sub(pattern, collapse_match, json_str)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_str_custom)

# ==========================================
# 5. Main Execution
# ==========================================

def main():
    print("--- Starting News Acquisition Engine (Robust) ---")
    
    output_data = {}
    
    # 1. Process Categories
    for cat_name, cat_config in CONFIG["CATEGORIES"].items():
        print(f"\n>>> Processing Category: {cat_name} ({cat_config['desc']})")
        output_data[cat_name] = []
        
        for item in cat_config["items"]:
            itype = item.get("type", "stock_us")
            val = item["value"]
            
            fetched = []
            
            # MAPPING LOGIC
            if itype in ["stock_us", "index_us", "stock_hk", "index_hk", "stock_vn", "future_foreign"]:
                fetched = fetch_yfinance_news(val)
                
            elif itype in ["stock_zh_a", "etf_zh"]:
                fetched = fetch_akshare_stock(val)
                
            elif itype == "future_zh_sina":
                 # Fallback attempt for 'au0' or Shanghai Gold if standard function exists
                 # Currently Akshare 'stock_news_em' might not support 'au0' prefix directly
                 logger.warning(f"Future {val} news fetching not fully supported yet.")
                 STATS.update(f"Akshare Future ({val})", 0, "Not Implemented")
                 
            elif itype == "keyword":
                logger.info(f"Skipping Search for {val} (SerpApi Paused)")
                STATS.update(f"Search: {item['name']}", 0, "PAUSED")
            
            if fetched:
                output_data[cat_name].extend(fetched)

    # 2. Process General Market
    print("\n>>> Processing General/Macro News")
    output_data["GENERAL"] = []
    output_data["GENERAL"].extend(try_fetch_cls_rolling())

    # 3. Generate Final Report & Save
    final_output = {
        "meta": {
            "timestamp": str(datetime.now()),
            "days_back": CONFIG["DAYS_BACK"],
            "stats": STATS.get_report()
        },
        "data": output_data
    }
    
    abs_path = os.path.abspath(CONFIG["OUTPUT_FILE"])
    save_custom_json(final_output, abs_path)

    print(f"\n[DONE] Execution Complete.")
    print(f"Stats & News written to: {abs_path}")
    
if __name__ == "__main__":
    main()
