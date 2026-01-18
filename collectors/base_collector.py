import logging
import os
import concurrent.futures
from datetime import datetime
import config
from utils.utils_data import StatsTracker, save_custom_json
from data_sources.YFinance_Fetcher import YFinanceFetcher
from data_sources.Akshare_Fetcher import AkshareFetcher
from data_sources.GoogleNews_RSS_Fetcher import GoogleNewsRSSFetcher
from data_sources.Guardian_Fetcher import GuardianFetcher
from data_sources.OpenBB_NewsFetcher import OpenBBNewsFetcher
from processors.DataCleaner import DataCleaner

class BaseCollector:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.stats = StatsTracker()
        # Initialize Cleaner (language agnostic mostly, or pass specific)
        self.cleaner = DataCleaner()
        
        # Initialize Data Sources
        self.yf_fetcher = YFinanceFetcher(self.stats)
        self.ak_fetcher = AkshareFetcher(self.stats)
        self.google_fetcher = GoogleNewsRSSFetcher(self.stats)
        self.guardian_fetcher = GuardianFetcher(self.stats)
        self.obb_fetcher = OpenBBNewsFetcher(self.stats)
        
        self.config = config.CONFIG
        self.results = []
    
    def fetch_item(self, item, cat_name, start_date=None, end_date=None):
        """
        Generic fetch logic refactored from main.py
        """
        name = item.get("name")
        val = item.get("value")
        itype = item.get("type", "keyword")
        
        fetched_data = []

        # --- Sub-Strategy A: Stock Tickers (YFinance/Akshare/OpenBB) ---
        if "stock" in itype or "index" in itype or "etf" in itype or "future" in itype:
            # 1. YFinance
            if itype in ["stock_us", "index_us", "index_hk", "etf_zh", "future_foreign", "stock_hk", "stock_vn"]:
                # PROPER METHOD NAME: fetch
                # Note: YFetcher likely does not support historical yet. 
                # We prioritize GoogleRSS for history anyway as per plan.
                yf_news = self.yf_fetcher.fetch(val)
                if yf_news:
                    self._tag(yf_news, cat_name)
                    fetched_data.extend(yf_news)

            # 2. AkShare
            if itype in ["stock_zh_a", "etf_zh", "index_hk", "stock_hk"]:
                # PROPER METHOD NAME: fetch_stock_news
                # Akshare typically returns latest.
                ak_news = self.ak_fetcher.fetch_stock_news(val)
                if ak_news:
                    self._tag(ak_news, cat_name)
                    fetched_data.extend(ak_news)

            # 3. OpenBB (Supplement)
            if itype in ["stock_us"]:
                obb_news = self.obb_fetcher.fetch_company_news(val)
                if obb_news:
                    self._tag(obb_news, cat_name)
                    fetched_data.extend(obb_news)

        # --- Sub-Strategy B: Keywords (Google RSS, Guardian) ---
        if itype == "keyword" or "desc" in item:
            # 1. Google RSS (Massive)
            if self.config.get("ENABLE_GOOGLE_RSS"):
                # Determine Lang/Geo...
                limit = 1000 
                
                # Try English Fetch
                # PASS DATES HERE
                g_news = self.google_fetcher.fetch(query=val, lang="en-US", geo="US", limit=limit, start_date=start_date, end_date=end_date)
                if g_news:
                    self._tag(g_news, cat_name)
                    fetched_data.extend(g_news)

                # 2. Guardian (High Quality)
                if self.config.get("GUARD_API_KEY") or os.getenv("GUARDIAN_API_KEY"):
                     guardian_news = self.guardian_fetcher.fetch(query=val)
                     if guardian_news:
                         self._tag(guardian_news, cat_name)
                         fetched_data.extend(guardian_news)
        
        return fetched_data

    def _tag(self, news_list, category):
        for n in news_list:
            n['category'] = category

    def collect_group(self, group_key, start_date=None, end_date=None):
        """
        Main orchestration for a config group.
        """
        target_group = self.config["GROUPS"].get("ENGLISH_SOURCES", {}).get(group_key) or \
                       self.config["GROUPS"].get("CHINESE_SOURCES", {}).get(group_key)
        
        if not target_group:
            self.logger.error(f"Group {group_key} not found in Config!")
            return []

        items = target_group.get("items", [])
        desc = target_group.get("desc", group_key)
        self.logger.info(f"🚀 Collecting {group_key} ({len(items)} items)...")

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # PASS DATES HERE
            future_to_item = {executor.submit(self.fetch_item, item, group_key, start_date, end_date): item for item in items}
            for future in concurrent.futures.as_completed(future_to_item):
                try:
                    data = future.result()
                    if data:
                        results.extend(data)
                except Exception as e:
                    self.logger.error(f"Error fetching item: {e}", exc_info=True)
        
        return results

    def process_and_clean(self, raw_data, language="ENGLISH"):
        """
        Deduplication and Cleaning Steps.
        """
        # Group by Source for Cleaner
        # Cleaner expects { "Source": [items] }
        # But here we have flat list.
        # Let's just pass { "Combined": raw_data }
        
        if not raw_data:
            return []

        mapped_data = { "RawData": raw_data }
        cleaned_map = self.cleaner.clean_data(mapped_data, language=language)
        return cleaned_map.get("RawData", [])

    def save_report(self, filename, cleaned_data, stats_report, raw_data=None):
        
        # Token Saving: Remove 'link', 'images', 'url' fields as requested
        keys_to_remove = ["link", "url", "image", "images", "thumbnail"]
        
        def optimize_item(item):
            # Create a copy or modify in place? modifying in place is fine here.
            for k in keys_to_remove:
                if k in item:
                    del item[k]
            return item

        # Optimize Cleaned Data
        if cleaned_data:
            cleaned_data = [optimize_item(x) for x in cleaned_data]
            
        # Optimize Raw Data
        if raw_data:
            raw_data = [optimize_item(x) for x in raw_data]

        final_output = {
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "count": len(cleaned_data),
                "raw_count": len(raw_data) if raw_data else 0,
                "stats": stats_report
            },
            "cleaned_data": cleaned_data, # Renamed from 'data' for clarity
            "raw_data": raw_data or []
        }
        abs_path = os.path.abspath(os.path.join("data", filename))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        save_custom_json(final_output, abs_path)
        self.logger.info(f"Saved {abs_path}")
        return final_output, abs_path
