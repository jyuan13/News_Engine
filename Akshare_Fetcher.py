import logging
import time
from datetime import datetime, timedelta
import akshare as ak
from config import CONFIG
from utils_data import StatsTracker

logger = logging.getLogger(__name__)

class AkshareFetcher:
    def __init__(self, stats_tracker: StatsTracker):
        self.stats = stats_tracker
        self.max_retries = 5
        self.retry_delay = 3

    def fetch_stock_news(self, symbol: str) -> list[dict]:
        """Fetch specific stock/ETF news from Akshare (EastMoney)."""
        source_name = f"Akshare Stock ({symbol})"
        logger.info(f"Fetching {source_name}...")
        try:
            if not hasattr(ak, 'stock_news_em'):
                self.stats.update(source_name, 0, "stock_news_em not found")
                return []

            news_df = self._retry_operation(self._fetch_stock_logic, symbol)
            
            results = []
            cutoff_date = (datetime.now() - timedelta(days=CONFIG.get("DAYS_BACK", 7))).strftime("%Y-%m-%d")
            
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
            self.stats.update(source_name, len(results))
            return results
        except Exception as e:
            logger.error(f"Error {source_name}: {e}")
            self.stats.update(source_name, 0, e)
            return []

    def fetch_rolling_news(self) -> list[dict]:
        """Fetch Cailian Press rolling news."""
        source_name = "Cailian Press (Rolling)"
        logger.info(f"Fetching {source_name}...")
        
        if not hasattr(ak, 'stock_info_global_cls'):
            self.stats.update(source_name, 0, "stock_info_global_cls not found")
            return []

        try:
            news_df = self._retry_operation(self._fetch_rolling_logic)
            
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
            self.stats.update(source_name, len(results))
            return results
        except Exception as e:
            logger.warning(f"Error {source_name}: {e}")
            self.stats.update(source_name, 0, e)
            return []

    def _fetch_stock_logic(self, symbol):
        return ak.stock_news_em(symbol=symbol)

    def _fetch_rolling_logic(self):
        return ak.stock_info_global_cls()

    def _retry_operation(self, operation, *args, **kwargs):
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"[Akshare] Attempt {attempt}/{self.max_retries} failed: {e}. Retrying...")
                time.sleep(self.retry_delay)
        raise last_exception
