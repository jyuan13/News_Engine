from collectors.base_collector import BaseCollector

class CommoditiesCollector(BaseCollector):
    def run(self, start_date=None, end_date=None):
        group_key = "COMMODITIES_EN"
        raw_data = self.collect_group(group_key, start_date, end_date)
        
        # Process (Clean)
        cleaned_data = self.process_and_clean(raw_data, language="ENGLISH")
        
        # Save
        filename = "Report_Commodities.json"
        return self.save_report(filename, cleaned_data, self.stats.stats, raw_data=raw_data)
