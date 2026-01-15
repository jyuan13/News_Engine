import os
import logging
from datetime import datetime, timedelta
try:
    from openbb import obb
except ImportError:
    # Fallback to prevent crash if openbb is not installed in the environment yet, 
    # though it is expected to be available.
    obb = None

class OpenBBNewsFetcher:
    def __init__(self):
        self.logger = logging.getLogger("OpenBBNewsFetcher")
        self._check_api_keys()

    def _check_api_keys(self):
        """
        Log status of available API keys for debugging.
        """
        keys = {
            "FMP": os.getenv("FMP_API_KEY"),
            "Tiingo": os.getenv("TIINGO_API_KEY"), # User might have this or not
            "Polygon": os.getenv("POLYGON_API_KEY"),
            "Intrinio": os.getenv("INTRINIO_API_KEY"),
        }
        for name, key in keys.items():
            if key:
                self.logger.info(f"{name} API Key found.")
            else:
                self.logger.debug(f"{name} API Key not found.")

    def fetch_company_news(self, symbols: list[str], limit: int = 50, days_back: int = 7) -> list[dict]:
        """
        Fetch company news from multiple providers to maximize quantity.
        Prioritizes YFinance (Free/Working) over FMP (Restricted).
        """
        if not obb:
            self.logger.error("OpenBB SDK not installed.")
            return []

        all_news = []
        # Adjusted priorities based on user feedback/logs:
        # 1. YFinance: Confirmed working and free.
        # 2. FMP: API key exists but user reported 402 Restricted. usage might be limited.
        providers = ['yfinance', 'fmp']
        
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # YFinance works best with single symbols or small batches.
        # OpenBB 'company' endpoint often handles lists, but let's be safe with YFinance
        # by passing the list if supported, or looping if needed. 
        # OpenBB SDK usually joins them.
        symbols_str = ",".join(symbols)

        for provider in providers:
            try:
                self.logger.info(f"Fetching company news for {symbols} from {provider}...")
                result = obb.news.company(
                    symbol=symbols_str,
                    provider=provider,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit
                )
                
                if result and result.results:
                    news_items = result.results
                    self.logger.info(f"Fetched {len(news_items)} items from {provider}.")
                    for item in news_items:
                        normalized = self._normalize_news_data(item, provider)
                        if normalized:
                            all_news.append(normalized)
            except Exception as e:
                # Handle specific FMP 402 error cleanly
                error_msg = str(e)
                if "402" in error_msg and provider == 'fmp':
                    self.logger.warning(f"FMP Plan Limit: Company news endpoint restricted (402). Skipping FMP.")
                else:
                    self.logger.warning(f"Failed to fetch from {provider}: {e}")

        return self._deduplicate_news(all_news)

    def fetch_world_news(self, limit: int = 50) -> list[dict]:
        """
        Fetch general world/market news.
        STRATEGY CHANGE:
        - Direct `obb.news.world` does NOT support yfinance.
        - FMP `world` endpoint is restricted (402).
        - User has no Benzinga/Tiingo/Intrinio keys.
        - SOLUTION: Fetch `company_news` via YFinance for MAJOR INDICES to proxy 'World News'.
        """
        self.logger.info("Fetching World News via Index Proxy (YFinance)...")
        
        # Major indices to represent "The Market"
        world_proxies = ["^GSPC", "^DJI", "^IXIC", "SPY", "QQQ", "GC=F", "BTC-USD"]
        
        # We invoke fetch_company_news using these proxies
        # This reuses the logic that definitely works (YFinance).
        proxy_news = self.fetch_company_news(world_proxies, limit=limit)
        
        # Label them as "World/Macro" for clarity in the source if desired, 
        # or just let them retain "OpenBB-YFINANCE"
        for news in proxy_news:
            news["source"] = "OpenBB-YFINANCE (Macro)"
            
        return proxy_news

    def _normalize_news_data(self, item, source_provider: str) -> dict:
        """
        Convert OpenBB data model to project's standard dictionary format.
        Standard fields: 'title', 'published_date', 'content', 'link', 'source', 'symbols'
        """
        try:
            # item is usually a Pydantic model or object, access via attributes
            # Fields found in doc: date, title, author, excerpt, body, images, url, symbols
            
            # Handle date parsing if needed
            pub_date = getattr(item, 'date', None)
            if pub_date:
                if isinstance(pub_date, datetime):
                    pub_date_str = pub_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # Try to parse string if convenient, or just keep as str
                    pub_date_str = str(pub_date)
            else:
                pub_date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Extract symbols (could be list or string)
            syms = getattr(item, 'symbols', [])
            if isinstance(syms, str):
                syms = syms.split(',') if syms else []
            
            # Normalize content
            content = getattr(item, 'excerpt', '') or getattr(item, 'body', '') or getattr(item, 'text', '')
            if not content:
                content = getattr(item, 'title', '') # Fallback

            return {
                "title": getattr(item, 'title', 'No Title'),
                "published_date": pub_date_str,
                "content": content,
                "link": getattr(item, 'url', ''),
                "source": f"OpenBB-{source_provider.upper()}",
                "symbols": syms
            }
        except Exception as e:
            self.logger.warning(f"Error normalizing item: {e}")
            return None

    def _deduplicate_news(self, news_list: list[dict]) -> list[dict]:
        """
        Remove duplicates based on URL or Title.
        """
        unique_news = []
        seen_urls = set()
        seen_titles = set()

        for news in news_list:
            url = news.get("link")
            title = news.get("title")
            
            # Simplify title for dedup (ignore case, spaces)
            clean_title = title.lower().strip() if title else ""
            
            if url and url in seen_urls:
                continue
            if clean_title and clean_title in seen_titles:
                continue
            
            if url: seen_urls.add(url)
            if clean_title: seen_titles.add(clean_title)
            
            unique_news.append(news)
        
        return unique_news

if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    fetcher = OpenBBNewsFetcher()
    
    print("\n--- Testing Company News (AAPL) ---")
    company_news = fetcher.fetch_company_news(["AAPL"], limit=5)
    for n in company_news:
        print(f"[{n['source']}] {n['published_date']} - {n['title']}")
    
    print("\n--- Testing World News ---")
    world_news = fetcher.fetch_world_news(limit=5)
    for n in world_news:
        print(f"[{n['source']}] {n['published_date']} - {n['title']}")
