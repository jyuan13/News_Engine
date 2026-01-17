from collectors.base_collector import BaseCollector

class VietnamCollector(BaseCollector):
    def run(self):
        group_key = "VIETNAM_EN"
        raw_data = self.collect_group(group_key)
        cleaned_data = self.process_and_clean(raw_data, language="ENGLISH") # Mixed context, mostly English keywords? Actually Vietnam keywords were mixed.
        filename = "Report_Vietnam.json"
        self.save_report(filename, cleaned_data, self.stats.stats)
        return cleaned_data, filename
