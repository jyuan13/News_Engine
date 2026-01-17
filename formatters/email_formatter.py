import json
from datetime import datetime

class EmailFormatter:
    def __init__(self):
        self.css = """
        <style>
            body { font-family: Arial, sans-serif; font-size: 14px; color: #333; }
            h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .meta { font-size: 12px; color: #7f8c8d; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; vertical-align: top; }
            th { background-color: #f2f2f2; color: #2c3e50; font-weight: bold; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f1f1f1; }
            .source { font-weight: bold; color: #2980b9; font-size: 12px; }
            .date { color: #95a5a6; font-size: 11px; white-space: nowrap; }
            .tag { display: inline-block; padding: 2px 6px; font-size: 10px; border-radius: 4px; color: white; margin-right: 5px; }
            .tag-cat { background-color: #e67e22; }
            .tag-dup { background-color: #9b59b6; }
        </style>
        """

    def format_html(self, data, title="News Report"):
        """
        Converts the standardized JSON report into an HTML email body.
        """
        if not data or "data" not in data:
            return "<html><body><p>No data available.</p></body></html>"

        news_items = data["data"]
        meta = data.get("meta", {})
        
        # Sort by date (descending)
        # news_items.sort(key=lambda x: x.get('pubDate', ''), reverse=True)

        # Helper to generate table rows
        def generate_rows(items):
            rows = ""
            for item in items:
                title = item.get('title', 'No Title')
                source = item.get('source', 'Unknown')
                # Handle varying date keys
                pdate = item.get('published_date') or item.get('publish_time') or 'N/A'
                link = item.get('link') or item.get('url') or '#'
                content = item.get('content', '') or item.get('summary', '') or ''
                
                # Truncate content for display
                if len(content) > 300:
                    content = content[:300] + "..."
                
                rows += f"""
                <tr>
                    <td class="meta-col">
                        <div class="source">{source}</div>
                        <div class="date">{pdate}</div>
                    </td>
                    <td class="content-col">
                        <div class="title"><a href="{link}">{title}</a></div>
                        <div class="summary">{content}</div>
                    </td>
                </tr>
                """
            return rows

        cleaned_rows = generate_rows(news_items)
        
        # Raw Data Handling
        raw_items = data.get('raw_data', [])
        raw_section = ""
        if raw_items:
            # Sort raw items if possible? Keeping original order for now.
            raw_rows = generate_rows(raw_items)
            raw_section = f"""
            <h3>Part 2: Raw Data (Pre-Cleaning) - {len(raw_items)} Items</h3>
            <table>
                <thead>
                    <tr>
                        <th style="width: 15%">Meta</th>
                        <th style="width: 85%">News Content</th>
                    </tr>
                </thead>
                <tbody>
                    {raw_rows}
                </tbody>
            </table>
            """

        html = f"""
        <html>
        <head>{self.css}</head>
        <body>
            <h2>{title}</h2>
            <div class="meta">
                Generated at: {meta.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}<br>
                Total Cleaned: {meta.get('count', len(news_items))}<br>
                Total Raw: {len(raw_items)}
            </div>
            
            <h3>Part 1: Cleaned Data - {len(news_items)} Items</h3>
            <table>
                <thead>
                    <tr>
                        <th style="width: 15%">Meta</th>
                        <th style="width: 85%">News Content</th>
                    </tr>
                </thead>
                <tbody>
                    {cleaned_rows}
                </tbody>
            </table>
            
            {raw_section}
            
            <div class="footer">
                Powered by News Engine 7-Layer Architecture
            </div>
        </body>
        </html>
        """
        return html


