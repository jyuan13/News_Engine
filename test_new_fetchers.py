import logging
import time
from utils_data import StatsTracker
from GoogleNews_RSS_Fetcher import GoogleNewsRSSFetcher
from Guardian_Fetcher import GuardianFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_rss():
    print("\n--- Testing Google News RSS (Quantity + Full Text Scrape) ---")
    stats = StatsTracker()
    fetcher = GoogleNewsRSSFetcher(stats)
    
    # Test Keyword
    query = "Artificial Intelligence"
    print(f"Query: {query}")
    
    results = fetcher.fetch(query, limit=5)
    
    print(f"Fetched {len(results)} items.")
    for idx, item in enumerate(results):
        content_preview = item['content'][:100].replace('\n', ' ') + "..."
        print(f"[{idx+1}] {item['title']}")
        print(f"    Source: {item['source']}")
        print(f"    Date: {item['published_date']}")
        print(f"    Content (Preview): {content_preview}")
        print("-" * 50)

def test_guardian():
    print("\n--- Testing The Guardian API (High Quality Full Text) ---")
    stats = StatsTracker()
    fetcher = GuardianFetcher(stats)
    
    # Test Keyword
    query = "China Economy"
    print(f"Query: {query}")
    
    results = fetcher.fetch(query, limit=5)
    
    if not results:
        print("No results (API Key missing or no news).")
    
    print(f"Fetched {len(results)} items.")
    for idx, item in enumerate(results):
        content_preview = item['content'][:100].replace('\n', ' ') + "..."
        print(f"[{idx+1}] {item['title']}")
        print(f"    Source: {item['source']}")
        print(f"    Date: {item['published_date']}")
        print(f"    Content (Preview): {content_preview}")
        print("-" * 50)

if __name__ == "__main__":
    try:
        import feedparser
        import newspaper
    except ImportError:
        print("CRITICAL: Missing dependencies.")
        print("Please run: pip install feedparser newspaper3k lxml[html_clean]")
        exit(1)
        
    test_google_rss()
    test_guardian()
