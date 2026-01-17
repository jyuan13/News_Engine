import argparse
import logging
import os
from datetime import datetime

# Import Collectors
from collectors import (
    USTechCollector,
    CommoditiesCollector,
    VietnamCollector,
    MacroCollector,
    HKTechCollector,
    HKPharmaCollector,
    Star50Collector
)

# Import Core
from core.message_bus import MessageBus

# Setup Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NewsEngine_CLI")

COLLECTOR_MAP = {
    "US_TECH": {"class": USTechCollector, "name": "美股科技与AI"},
    "COMMODITIES": {"class": CommoditiesCollector, "name": "全球大宗商品"},
    "VIETNAM": {"class": VietnamCollector, "name": "越南市场动态"},
    "MACRO": {"class": MacroCollector, "name": "全球宏观风险"},
    "HK_TECH": {"class": HKTechCollector, "name": "港股科技板块"},
    "HK_PHARMA": {"class": HKPharmaCollector, "name": "港股创新药"},
    "STAR50": {"class": Star50Collector, "name": "科创50与芯片"}
}

def run_collector(key):
    """
    Executes a single collector and returns the data and metadata.
    Does NOT publish to MessageBus directly.
    """
    cfg = COLLECTOR_MAP.get(key)
    if not cfg:
        logger.error(f"Unknown collector key: {key}")
        return None, None

    logger.info(f"🟢 Starting Collector: {key} ({cfg['name']})")
    try:
        collector = cfg["class"]()
        # Run Collection -> Returns (data_json, filename)
        data_json, filename = collector.run()
        
        if not data_json or "data" not in data_json or not data_json["data"]:
            logger.warning(f"⚠️ No data collected for {key}.")
            return None, None

        # Prepare Metadata
        meta = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "filename": os.path.abspath(os.path.join("data", filename)),
            "group_name": cfg['name'],
            "key": key
        }
        
        return data_json, meta
        
    except Exception as e:
        logger.error(f"❌ Error running {key}: {e}", exc_info=True)
        return None, None

def main():
    parser = argparse.ArgumentParser(description="News Engine CLI")
    parser.add_argument("--collector", type=str, default="ALL", help="Specific collector to run (e.g., US_TECH) or ALL")
    args = parser.parse_args()

    # Initialize MessageBus
    bus = MessageBus()

    target = args.collector.upper()
    collector_keys = []
    
    if target == "ALL":
        collector_keys = list(COLLECTOR_MAP.keys())
    else:
        if target in COLLECTOR_MAP:
            collector_keys = [target]
        else:
            logger.error(f"Invalid collector: {target}. Available: {list(COLLECTOR_MAP.keys())}")
            return

    # 1. Collection Phase
    collected_results = {} # { key: {data: ..., meta: ...} }
    
    for key in collector_keys:
        data, meta = run_collector(key)
        if data and meta:
            collected_results[key] = {"data": data, "meta": meta}

    if not collected_results:
        logger.warning("No data collected from any source. Exiting.")
        return

    # 2. Dispatch/Notification Phase
    logger.info("📨 Starting Dispatch Phase...")
    
    # Determine Subject Line dynamically
    active_names = [res["meta"]["group_name"] for res in collected_results.values()]
    unique_names = list(set(active_names))
    
    if len(unique_names) == 1:
        subject = f"{unique_names[0]}日报"
    elif len(unique_names) == 2:
        subject = f"{unique_names[0]} & {unique_names[1]}日报"
    else:
        subject = f"News Engine 此刻采集报告 ({len(unique_names)}板块)" # Default for many

    # Publish Once
    # We pass the entire dictionary of results to the MessageBus
    # The topic here is mainly for the Email Subject if not overridden, but we'll modify the message payload structure
    
    # Construct a Unified Payload
    unified_payload = {
        "is_unified": True,
        "subject": subject,
        "results": collected_results, # Keyed by collector key (US_TECH, etc)
        "meta": {
            "timestamp": datetime.now().isoformat(),
            "collector_count": len(collected_results)
        }
    }
    
    # We use a special topic "UNIFIED_REPORT" or just rely on the bus to handle it.
    # Since MessageBus might expect (topic, data, meta), let's adapt.
    
    logger.info(f"🚀 Dispatching Unified Report: {subject}")
    bus.publish(topic=subject, data=unified_payload, meta={})

if __name__ == "__main__":
    main()
