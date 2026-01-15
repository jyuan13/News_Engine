import logging
import feedparser
from newspaper import Article, Config
from datetime import datetime, timedelta
import urllib.parse
from utils_data import StatsTracker
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

    def fetch(self, query: str, lang: str = "en-US", geo: str = "US", limit: int = 100) -> list[dict]:
        """
        Fetch news for a keyword/query using Google News RSS + Scraping.
        """
        source_name = f"GoogleRSS ({query})"
        logger.info(f"Fetching {source_name}...")
        
        # Build RSS URL
        # Params: q={query}, hl={lang}, gl={geo}, ceid={geo}:{lang}
        # optional: when:1h (realtime), but user wants quantity, let's leave default (relevance/recent)
        # or maybe 'when:24h' to ensure freshness.
        
        encoded_query = urllib.parse.quote(query)
        rss_url = f"{self.base_url}?q={encoded_query}&hl={lang}&gl={geo}&ceid={geo}:{lang.split('-')[0]}"
        
        try:
            feed = feedparser.parse(rss_url)
            entries = feed.entries[:limit]
            
            logger.info(f"Found {len(entries)} items in RSS for {query}. Starting Full-Text Scrape...")
            
            results = []
            for entry in entries:
                parsed = self._process_entry(entry, query)
                if parsed:
                    results.append(parsed)
                
                # Be polite to servers when scraping
                time.sleep(random.uniform(0.5, 1.5))
                
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
            
            # 4. Return Normalized Data
            return {
                "source": "GoogleNews (FullText)",
                "title": article.title or entry.title,
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
