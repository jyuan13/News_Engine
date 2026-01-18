import logging
import feedparser
from newspaper import Article, Config
from datetime import datetime, timedelta
import urllib.parse
from utils.utils_data import StatsTracker
import time
import random

logger = logging.getLogger(__name__)

class GoogleNewsRSSFetcher:
    """
    Fetches news from Google News RSS feeds and scrapes full content using Newspaper3k.
    Focus: "Quantity" and "Full Text".
    """
    def __init__(self, stats_tracker: StatsTracker):
        self.stats = stats_tracker
        self.base_url = "https://news.google.com/rss/search"
        
        # Newspaper3k Config
        self.scrape_config = Config()
        self.scrape_config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.scrape_config.request_timeout = 10

    def fetch(self, query: str, lang: str = "en-US", geo: str = "US", limit: int = 100, start_date: str = None, end_date: str = None) -> list[dict]:
        """
        Fetch news for a keyword/query using Google News RSS + Scraping (Optimized).
        Supports date range via search operators (after:YYYY-MM-DD before:YYYY-MM-DD).
        """
        source_name = f"GoogleRSS ({query})"
        logger.info(f"Fetching {source_name}...")
        
        # Date Logic
        # If start/end provided, append to query
        final_query = query
        if start_date and end_date:
            # Google Search Operators: "term after:2025-01-01 before:2025-01-07"
            final_query = f"{query} after:{start_date} before:{end_date}"
            logger.info(f"📅 Using Date Range: {start_date} to {end_date}")

        encoded_query = urllib.parse.quote(final_query)
        rss_url = f"{self.base_url}?q={encoded_query}&hl={lang}&gl={geo}&ceid={geo}:{lang.split('-')[0]}"
        
        try:
            feed = feedparser.parse(rss_url)
            all_entries = feed.entries
            
            # 1. Date Filtering (Pre-filtering)
            valid_entries = []
            
            if start_date and end_date:
                # Targeted Range Mode: strict filter based on provided dates
                s_dt = datetime.strptime(start_date, "%Y-%m-%d")
                e_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) # Inclusive end? allow some buffer
                
                for entry in all_entries:
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        # Basic buffer check (sometimes RSS returns out of range items)
                        if s_dt <= pub_dt <= e_dt + timedelta(days=1): 
                           valid_entries.append(entry)
            else:
                # Default "Recent" Mode
                days_back = 7 
                cutoff_date = datetime.now() - timedelta(days=days_back)
                for entry in all_entries:
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        if pub_dt >= cutoff_date:
                            valid_entries.append(entry)
            
            # Apply limit after date filtering
            valid_entries = valid_entries[:limit]
            
            logger.info(f"RSS: Found {len(all_entries)} total, {len(valid_entries)} relevant. Scraping...")
            
            results = []
            
            # 2. Concurrent Scraping
            # Use ThreadPoolExecutor to download articles in parallel
            import concurrent.futures
            
            # Helper wrapper for thread mapping
            def scrape_wrapper(entry):
                return self._process_entry(entry, final_query) # Use final_query for related_ticker

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Map entries to threads
                future_to_entry = {executor.submit(scrape_wrapper, entry): entry for entry in valid_entries}
                
                for future in concurrent.futures.as_completed(future_to_entry):
                    try:
                        data = future.result()
                        if data:
                            results.append(data)
                    except Exception as exc:
                        logger.debug(f"Thread generated an exception: {exc}")
                
            self.stats.update(source_name, len(results))
            return results
            
        except Exception as e:
            logger.error(f"Error {source_name}: {e}")
            self.stats.update(source_name, 0, e)
            return []

    def _process_entry(self, entry, query) -> dict:
        try:
            url = entry.link
            
            # 1. Init Article
            article = Article(url, config=self.scrape_config)
            
            # 2. Download & Parse
            try:
                article.download()
                article.parse()
            except Exception as e:
                # Fallback to snippet if download fails
                logger.debug(f"Scrape failed for {url}: {e}")
                return {
                    "source": "GoogleNews (Snippet)",
                    "title": entry.title,
                    "published_date": self._parse_date(entry),
                    "content": entry.get('summary', 'No content'),
                    "link": url,
                    "related_ticker": query
                }

            # 3. Extract Full Text
            full_text = article.text
            if not full_text or len(full_text) < 50:
                 # If full text is too short or empty, fallback to summary
                 full_text = entry.get('summary', '') or article.text
            
            # Title Fallback Logic
            title = article.title
            if not title or title.strip().lower() in ["google news", "google", "news"]:
                title = entry.title

            # Final Quality Check
            if not title or not full_text or len(full_text) < 20:
                logger.debug(f"Skipping low quality item: {url}")
                return None

            # 4. Return Normalized Data
            return {
                "source": "GoogleNews (FullText)",
                "title": title,
                "published_date": self._parse_date(entry),
                "author": article.authors,
                "content": full_text, # PRIORITY: Full Text
                "link": url,
                "related_ticker": query,
                "images": list(article.images) if article.images else []
            }
            
        except Exception as e:
            logger.error(f"Failed to process entry: {e}")
            return None

    def _parse_date(self, entry):
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime.fromtimestamp(time.mktime(entry.published_parsed)).isoformat()
        return datetime.now().isoformat()
