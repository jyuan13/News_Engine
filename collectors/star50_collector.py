from collectors.base_collector import BaseCollector

class Star50Collector(BaseCollector):
    def run(self):
        group_key = "A_SHARES_STAR50"
        raw_data = self.collect_group(group_key)
        cleaned_data = self.process_and_clean(raw_data, language="CHINESE")
        filename = "Report_Star50.json"
        return self.save_report(filename, cleaned_data, self.stats.stats, raw_data=raw_data)
