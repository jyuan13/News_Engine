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
        
        # Prepare Attachments
        attachments = []
        if meta and "filename" in meta:
            fpath = meta["filename"]
            if os.path.exists(fpath):
                attachments.append(fpath)
        
        subject = f"[News_Engine] {topic} - {meta.get('date', '')}"

        # Retry Strategy: [(TruncateLength, Description)]
        # None = Full Content
        # 0 = Title Only
        retry_stages = [
            (None, "Attempt 1 (Full Content)"),
            (500,  "Attempt 2 (Truncated 500 chars)"),
            (100,  "Attempt 3 (Truncated 100 chars)"),
            (0,    "Attempt 4 (Title Only)")
        ]

        for limit, desc in retry_stages:
            self.logger.info(f"📨 {desc}...")
            
            # 1. Format Payload
            html_body = self.email_formatter.format_html(data, title=topic, cleaned_truncate_length=limit)
            
            # 2. Dispatch
            is_last_attempt = (limit == 0)
            current_subject = subject + (" [Truncated]" if limit is not None else "")
            
            success, error_msg = self.email_dispatcher.send_email(
                subject=current_subject,
                body_html=html_body,
                attachment_files=attachments
            )
            
            if success:
                self.logger.info(f"✅ Email sent successfully at {desc}.")
                return True
            
            self.logger.warning(f"⚠️ {desc} failed: {error_msg}")
        
        # If we get here, all attempts failed
        self.logger.error("❌ Action Error: Failed to send email after all retry attempts.")
        return False
