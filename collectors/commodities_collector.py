from collectors.base_collector import BaseCollector

class CommoditiesCollector(BaseCollector):
    def run(self):
        group_key = "COMMODITIES_EN"
        raw_data = self.collect_group(group_key)
        cleaned_data = self.process_and_clean(raw_data, language="ENGLISH")
        filename = "Report_Commodities.json"
        self.save_report(filename, cleaned_data, self.stats.stats)
        return cleaned_data, filename
