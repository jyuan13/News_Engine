import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

class EmailDispatcher:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password, receiver_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email
        self.logger = logging.getLogger("EmailDispatcher")

    def send_email(self, subject, body_html, attachment_files=None):
        if not self.sender_email or not self.sender_password:
            self.logger.warning("❌ Missing SENDER_EMAIL or PW. Skipping email.")
            return False

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        msg['Subject'] = subject

        # Attach HTML Body
        msg.attach(MIMEText(body_html, 'html'))

        if attachment_files:
            for file_path in attachment_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        filename = os.path.basename(file_path)
                        part.add_header('Content-Disposition', 'attachment', filename=filename)
                        msg.attach(part)
                    except Exception as e:
                        self.logger.error(f"Failed to attach {file_path}: {e}")

        try:
            self.logger.info(f"Connecting to SMTP {self.smtp_server}...")
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.receiver_email, msg.as_string())
            server.quit()
            self.logger.info("✅ Email sent successfully.")
            return True
        except Exception as e:
            self.logger.error(f"❌ Email sending failed: {e}")
            return False
