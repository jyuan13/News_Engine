import logging
from formatters.email_formatter import EmailFormatter
from dispatchers.email_dispatcher import EmailDispatcher
import os

class MessageBus:
    def __init__(self):
        self.logger = logging.getLogger("MessageBus")
        self.email_formatter = EmailFormatter()
        
        # Initialize Email Dispatcher from Env/Config
        self.email_dispatcher = EmailDispatcher(
            smtp_server="smtp.qq.com",
            smtp_port=465,
            sender_email=os.getenv("SENDER_EMAIL"),
            sender_password=os.getenv("SENDER_PASSWORD"),
            receiver_email=os.getenv("RECEIVER_EMAIL")
        )

    def publish(self, topic, data, meta=None):
        """
        Publish data to a topic. For now, topic maps to "Email Subject".
        """
        self.logger.info(f"📨 Received message for topic: {topic}")
        
        # 1. Format Payload
        html_body = self.email_formatter.format_html(data, title=topic)
        
        # 2. Dispatch
        # Attach JSON file if provided as 'filename' in meta
        attachments = []
        if meta and "filename" in meta:
            # Assume filename is relative to data/ or absolute
            # Based on BaseCollector, it returns abs path.
            fpath = meta["filename"]
            if os.path.exists(fpath):
                attachments.append(fpath)
            
        success = self.email_dispatcher.send_email(
            subject=f"[News_Engine] {topic} - {meta.get('date', '')}",
            body_html=html_body,
            attachment_files=attachments
        )
        
        return success
