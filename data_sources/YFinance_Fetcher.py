import logging
import time
from datetime import datetime
import yfinance as yf
from config import CONFIG
from utils.utils_data import StatsTracker

logger = logging.getLogger(__name__)

class YFinanceFetcher:
    def __init__(self, stats_tracker: StatsTracker):
        self.stats = stats_tracker
        self.max_retries = 5
        self.retry_delay = 3

    def fetch(self, ticker_symbol: str) -> list[dict]:
        """Fetch news from YFinance with Retries."""
        source_name = f"YFinance ({ticker_symbol})"
        logger.info(f"Fetching {source_name}...")
        try:
            news = self._retry_operation(self._fetch_logic, ticker_symbol)
            
            results = []
            for item in news:
                parsed = self._parse_item(item, ticker_symbol)
                if parsed:
                    results.append(parsed)
            
            self.stats.update(source_name, len(results))
            return results
        except Exception as e:
            logger.error(f"Error {source_name}: {e}")
            self.stats.update(source_name, 0, e)
            return []

    def _fetch_logic(self, ticker_symbol):
        ticker = yf.Ticker(ticker_symbol)
        return ticker.news

    def _retry_operation(self, operation, *args, **kwargs):
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"[YFinance] Attempt {attempt}/{self.max_retries} failed: {e}. Retrying...")
                time.sleep(self.retry_delay)
        raise last_exception

    def _parse_item(self, item, ticker_symbol):
        content_data = item.get('content', item) if 'content' in item else item
        
        title = content_data.get('title')
        if not title: return None

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

        # Ensure TZ-naive comparison for simplicity with CONFIG["DAYS_BACK"]
        pub_time_naive = pub_time.replace(tzinfo=None)
        if (datetime.now() - pub_time_naive).days <= CONFIG.get("DAYS_BACK", 7):
            return {
                "source": "YFinance",
                "title": title,
                "publish_time": pub_time.isoformat(),
                "publisher": (content_data.get('provider') or {}).get('displayName'),
                "related_ticker": ticker_symbol,
                "content": content_data.get('summary', 'N/A')
            }
        return None
