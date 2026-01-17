from collectors.base_collector import BaseCollector

class USTechCollector(BaseCollector):
    def run(self):
        group_key = "US_MARKET_TECH"
        raw_data = self.collect_group(group_key)
        
        # Process (Clean)
        cleaned_data = self.process_and_clean(raw_data, language="ENGLISH")
        
        # Save
        filename = "Report_US_Tech.json"
        return self.save_report(filename, cleaned_data, self.stats.stats, raw_data=raw_data)
