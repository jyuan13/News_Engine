from collectors.base_collector import BaseCollector

class MacroCollector(BaseCollector):
    def run(self, start_date=None, end_date=None):
        group_key = "GLOBAL_MACRO_RISKS"
        raw_data = self.collect_group(group_key, start_date, end_date)
        
        # Process (Clean)
        cleaned_data = self.process_and_clean(raw_data, language="ENGLISH")
        
        # Save
        filename = "Report_Macro.json"
        return self.save_report(filename, cleaned_data, self.stats.stats, raw_data=raw_data)
