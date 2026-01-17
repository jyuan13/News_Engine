from collectors.base_collector import BaseCollector

class MacroCollector(BaseCollector):
    def run(self):
        group_key = "GLOBAL_MACRO_RISKS"
        raw_data = self.collect_group(group_key)
        cleaned_data = self.process_and_clean(raw_data, language="ENGLISH")
        filename = "Report_Global_Macro.json"
        self.save_report(filename, cleaned_data, self.stats.stats)
        return cleaned_data, filename
