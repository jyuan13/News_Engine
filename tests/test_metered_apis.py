import logging
import os
from utils_data import StatsTracker
from central_api_manager import CentralAPIManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_metered_apis():
    print("\n==================================================")
    print("   TESTING METERED APIs (1 Call Each) ")
    print("==================================================")
    
    stats = StatsTracker()
    manager = CentralAPIManager(stats)
    
    # 1. Test NewsAPI
    print("\n>>> Testing NewsAPI (Limit 1)...")
    if os.getenv("News_API_KEY"):
        results = manager.newsapi.fetch("Artificial Intelligence", limit=1)
        _print_result(results)
    else:
        print("SKIP: News_API_KEY not found.")

    # 2. Test Guardian
    print("\n>>> Testing Guardian (Limit 1)...")
    if os.getenv("GUARDIAN_API_KEY"):
        results = manager.guardian.fetch("China Economy", limit=1)
        _print_result(results)
    else:
        print("SKIP: GUARDIAN_API_KEY not found.")

    # 3. Test SerpApi
    print("\n>>> Testing SerpApi (Limit 1)...")
    if os.getenv("Serp_API_KEY"):
        results = manager.serpapi.fetch("FDA Approval", limit=1)
        _print_result(results)
    else:
        print("SKIP: Serp_API_KEY not found.")
        
    # 4. Test OpenBB (via Manager Wrapper)
    print("\n>>> Testing OpenBB (via Manager)...")
    try:
        # Just a dummy call if implemented, or check import
        print("OpenBB logic is currently pass-through or wrapper. Skipping direct call here.")
    except:
        pass

    print("\n[DONE] API Verification Complete.")

def _print_result(results):
    if results:
        print(f"SUCCESS: Fetched {len(results)} items.")
        print(f"Title: {results[0]['title']}")
        print(f"Source: {results[0]['source']}")
    else:
        print("FAILED or EMPTY.")

if __name__ == "__main__":
    test_metered_apis()
