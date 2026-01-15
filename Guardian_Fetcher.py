import logging
import requests
import os
from datetime import datetime, timedelta
from utils_data import StatsTracker
import time

logger = logging.getLogger(__name__)

class GuardianFetcher:
    """
    Fetches news from The Guardian Open Platform.
    Key Feature: "Full Text" via show-fields=body.
    Limit: 500 requests/day, 1/sec.
    """
    def __init__(self, stats_tracker: StatsTracker):
        self.stats = stats_tracker
        self.api_key = os.getenv("GUARDIAN_API_KEY") # User needs to set this
        self.base_url = "https://content.guardianapis.com/search"

    def fetch(self, query: str, limit: int = 20) -> list[dict]:
        """
        Fetch full-text news from The Guardian.
        """
        source_name = f"Guardian ({query})"
        
        if not self.api_key:
            logger.debug(f"Skipping {source_name}: GUARDIAN_API_KEY not found.")
            # self.stats.update(source_name, 0, "No API Key") # Don't clutter stats if not configured
            return []

        logger.info(f"Fetching {source_name}...")
        
        # Params for Full Text
        params = {
            'q': query,
            'api-key': self.api_key,
            'page-size': limit,
            'show-fields': 'bodyText,headline,byline,shortUrl,thumbnail', # Request bodyText for plain text
            'order-by': 'newest',
            'lang': 'en'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 429:
                 logger.warning(f"Guardian API Limit Reached (429).")
                 self.stats.update(source_name, 0, "Rate Limit")
                 return []
            
            if response.status_code != 200:
                logger.error(f"Guardian API Error: {response.status_code} - {response.text}")
                self.stats.update(source_name, 0, f"HTTP {response.status_code}")
                return []

            data = response.json()
            results = data.get('response', {}).get('results', [])
            
            parsed_results = []
            for item in results:
                parsed = self._parse_item(item, query)
                if parsed:
                    parsed_results.append(parsed)
            
            self.stats.update(source_name, len(parsed_results))
            return parsed_results

        except Exception as e:
            logger.error(f"Error {source_name}: {e}")
            self.stats.update(source_name, 0, e)
            return []

    def _parse_item(self, item, query) -> dict:
        fields = item.get('fields', {})
        
        # Full Text (HTML) - Might need cleaning if user wants plain text, 
        # but storing HTML is often better for preserving structure until final processing.
        # However, for consistency with other fetchers, let's try to strip basic HTML or keep it.
        # Report says "NewsData.io provides Full Content".
        # Let's keep it as is or basic clean. For now, raw body (HTML) is safest to ensure no data loss.
        # Note: 'body' field is HTML. 'bodyText' might be available if requested?
        # Checking docs: show-fields=bodyText is an option for plain text!
        # Let's optimize: fetch bodyText.
        
        # WAIT: I used 'body' in params. Let me correct params in next step if needed.
        # Actually, let's check if 'bodyText' is in fields if I requested 'body'.
        # Usually 'body' is HTML, 'bodyText' is plain.
        # I will change the request to 'show-fields': 'bodyText,headline,...' to be safer for NLP later.
        
        content = fields.get('bodyText') or fields.get('body', '')
        
        return {
            "source": "The Guardian (FullText)",
            "title": item.get('webTitle'),
            "published_date": item.get('webPublicationDate'),
            "author": fields.get('byline'),
            "content": content,
            "link": item.get('webUrl'),
            "related_ticker": query,
            "images": [fields.get('thumbnail')] if fields.get('thumbnail') else []
        }
