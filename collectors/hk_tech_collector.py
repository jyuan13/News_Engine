from collectors.base_collector import BaseCollector

class HKTechCollector(BaseCollector):
    def run(self):
        group_key = "HK_TECH_CN"
        raw_data = self.collect_group(group_key)
        cleaned_data = self.process_and_clean(raw_data, language="CHINESE")
        filename = "Report_HK_Tech.json"
        self.save_report(filename, cleaned_data, self.stats.stats)
        return cleaned_data, filename
