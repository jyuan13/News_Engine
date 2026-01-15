import json
import re
import logging

logger = logging.getLogger(__name__)

class StatsTracker:
    def __init__(self):
        self.stats = {} 

    def update(self, source, count, error=None):
        if source not in self.stats:
            self.stats[source] = {'count': 0, 'status': 'OK', 'error': None}
        
        self.stats[source]['count'] += count
        if error:
            self.stats[source]['status'] = 'FAILED'
            self.stats[source]['error'] = str(error)
    
    def get_report(self):
        return self.stats

def save_custom_json(data, filepath):
    """
    Save JSON with 'stats' inner objects formatted on a single line.
    """
    json_str = json.dumps(data, ensure_ascii=False, indent=4)
    
    # Regex to collapse stats values to single lines
    def collapse_match(match):
        block = match.group(0)
        collapsed = re.sub(r'\s*\n\s*', ' ', block)
        collapsed = re.sub(r'\{ "', '{ "', collapsed)
        collapsed = re.sub(r', "', ', "', collapsed)
        collapsed = re.sub(r' \} ', ' }', collapsed) 
        return collapsed

    # Pattern matches the specific structure of stats objects
    pattern = r'\{\s+"count": \d+,\s+"status": "[^"]+",\s+"error": (?:null|"[^"]*")\s+\}'
    json_str_custom = re.sub(pattern, collapse_match, json_str)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_str_custom)
