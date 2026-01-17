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

def run_collector(key, bus):
    """
    Executes a single collector and publishes results via MessageBus.
    """
    cfg = COLLECTOR_MAP.get(key)
    if not cfg:
        logger.error(f"Unknown collector key: {key}")
        return

    logger.info(f"🟢 Starting Collector: {key} ({cfg['name']})")
    try:
        collector = cfg["class"]()
        # Run Collection -> Returns (CleanedData, Filename)
        # Note: BaseCollector.run() in subclasses returns (data, filename)
        
        # We need to make sure subclasses actually return this. 
        # I implemented them to return (cleaned_data, filename). 
        # Let's double check... Yes I did.
        
        data_json, filename = collector.run()
        
        if not data_json or "data" not in data_json or not data_json["data"]:
            logger.warning(f"⚠️ No data collected for {key}. Skipping email.")
            return

        # Prepare Metadata for MessageBus
        meta = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "filename": os.path.abspath(os.path.join("data", filename))
        }

        # Publish to MessageBus (trigger Email)
        logger.info(f"📨 Publishing to MessageBus: {cfg['name']}")
        bus.publish(topic=cfg['name'], data=data_json, meta=meta)
        
    except Exception as e:
        logger.error(f"❌ Error running {key}: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="News Engine CLI")
    parser.add_argument("--collector", type=str, default="ALL", help="Specific collector to run (e.g., US_TECH) or ALL")
    args = parser.parse_args()

    # Initialize MessageBus
    bus = MessageBus()

    target = args.collector.upper()
    
    if target == "ALL":
        for key in COLLECTOR_MAP.keys():
            run_collector(key, bus)
    else:
        if target in COLLECTOR_MAP:
            run_collector(target, bus)
        else:
            logger.error(f"Invalid collector: {target}. Available: {list(COLLECTOR_MAP.keys())}")

if __name__ == "__main__":
    main()
