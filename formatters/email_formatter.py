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

    def format_html(self, data, title="News Report", cleaned_truncate_length=None):
        """
        Converts the standardized JSON report OR Unified Multi-Group payload into an HTML email body.
        Only displays Cleaned Data. Raw data is attached as a file.
        cleaned_truncate_length: 
            - None: Full content
            - Int (e.g. 500, 100): Truncate content
            - 0: Title Only (Hide Summary)
        """
        if not data:
            return "<html><body><p>No data available.</p></body></html>"

        # helper
        def generate_section_html(group_key, group_data, group_meta):
            news_items = group_data.get("data", [])
            raw_items = group_data.get("raw_data", []) # Used for counting only
            group_name = group_meta.get("group_name", group_key)
            
            # Helper to generate table rows
            def generate_rows(items, truncate_length):
                rows = ""
                for item in items:
                    item_title = item.get('title', 'No Title')
                    source = item.get('source', 'Unknown')
                    # Handle varying date keys
                    pdate = item.get('published_date') or item.get('publish_time') or 'N/A'
                    link = item.get('link') or item.get('url') or '#'
                    content = item.get('content', '') or item.get('summary', '') or ''
                    
                    # Logic for Title Only vs Truncation
                    summary_html = ""
                    if truncate_length != 0:
                        # Truncate content
                        if truncate_length is not None and len(content) > truncate_length:
                            content = content[:truncate_length] + "..."
                        summary_html = f'<div class="summary">{content}</div>'
                    
                    rows += f"""
                    <tr>
                        <td class="meta-col">
                            <div class="source">{source}</div>
                            <div class="date">{pdate}</div>
                        </td>
                        <td class="content-col">
                            <div class="title"><a href="{link}">{item_title}</a></div>
                            {summary_html}
                        </td>
                    </tr>
                    """
                return rows

            cleaned_rows = generate_rows(news_items, truncate_length=cleaned_truncate_length)
            
            # Note: Raw Data is NOT included in the HTML body anymore, only in Attachment.
            
            html_part = f"""
            <div class="group-container" style="margin-top: 30px; border-top: 3px solid #3498db; padding-top: 10px;">
                <h2 style="color: #2c3e50;">📌 {group_name}</h2>
                <div class="meta">
                    Cleaned: {len(news_items)} | Raw: {len(raw_items)} (See Attachment)
                </div>
                
                <h3>✅ Cleaned Highlights</h3>
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
            </div>
            """
            return html_part

        # Main Logic ----------------------------------------------------------
        content_body = ""
        meta_info = ""
        
        # Determine if it's a Unified payload or Legacy single payload
        if data.get("is_unified"):
            # Unified Multi-Group
            results_map = data.get("results", {})
            title = data.get("subject", title)
            
            # Summarize Stats
            total_groups = len(results_map)
            meta_info = f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Total Groups: {total_groups}"
            
            # Iterate groups
            for key, res in results_map.items():
                g_data = res["data"]
                g_meta = res["meta"]
                content_body += generate_section_html(key, g_data, g_meta)
                
        else:
            # Legacy Single Payload (fallback if called directly)
            # Wrap it to reuse logic
            content_body += generate_section_html("News Report", data, data.get("meta", {}))
            meta_info = f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        final_html = f"""
        <html>
        <head>{self.css}</head>
        <body>
            <h1 style="color: #2c3e50; text-align: center;">{title}</h1>
            <div class="meta" style="text-align: center;">
                {meta_info}
            </div>
            
            {content_body}
            
            <div class="footer" style="margin-top: 50px; text-align: center; color: #95a5a6; border-top: 1px solid #eee; padding-top: 20px;">
                Powered by News Engine 7-Layer Architecture
            </div>
        </body>
        </html>
        """
        return final_html


