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

        # Stats Summary
        stats_data = meta.get('stats', {})
        stats_html = ""
        if stats_data:
            unique_sources = set()
            total_fetched = 0
            stats_html = "<div style='margin-bottom: 20px; font-size: 11px; color: #555;'><strong>Source Summary:</strong><br>"
            for src, info in stats_data.items():
                count = info.get('count', 0)
                if count > 0:
                     stats_html += f"{src}: {count} | "
            stats_html += "</div>"

        html = f"""
        <html>
        <head>{self.css}</head>
        <body>
            <h2>{title}</h2>
            <div class="meta">
                Generated at: {meta.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}<br>
                Total Items (Cleaned): {meta.get('count', len(news_items))}<br>
                Raw Items Fetched: {meta.get('raw_count', 'N/A')}<br>
                {stats_html}
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 15%">Meta</th>
                        <th style="width: 85%">News Content</th>
                    </tr>
                </thead>
                <tbody>
        """

        for item in news_items:
            source = item.get("source", "Unknown")
            pub_date = item.get("pubDate", "")
            title_text = item.get("title", "No Title")
            content = item.get("content", "")
            if not content: content = item.get("description", "")
            
            # Semantic Info
            semantic_info = ""
            if item.get("semantic_dedup"):
               semantic_info = f"<br><span class='tag tag-dup'>Merged: {item.get('semantic_count', 1)}</span>"

            # Check if URL exists (we removed link field in previous step but maybe we want it back for clickable titles?)
            # The previous step removed 'link' BUT specific fetchers might still have 'link' in raw data before saving?
            # Actually main.py _save_report removed it.
            # Ideally collectors should keep it until saving.
            
            html += f"""
                <tr>
                    <td>
                        <div class="source">{source}</div>
                        <div class="date">{pub_date}</div>
                        {semantic_info}
                    </td>
                    <td>
                        <strong>{title_text}</strong>
                        <p>{content}</p>
                    </td>
                </tr>
            """

        html += """
                </tbody>
            </table>
            <p style="font-size: 10px; color: #bdc3c7;">Powered by News Engine 7-Layer Architecture</p>
        </body>
        </html>
        """
        return html
