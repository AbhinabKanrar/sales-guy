import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailEngine:
    def __init__(self, default_from):
        """Initializes the SMTP connection once when the class is created."""
        self.default_from = default_from
        self.password = os.environ.get("MAIL_PASSWORD", "your_MAIL_PASSWORD")
        self.smtp_server = os.environ.get("MAIL_SERVER", "smtp.zoho.in")
        self.smtp_port = 587
        
        print("Connecting to server...")
        self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        
        print("Logging in...")
        self.server.login(self.default_from, self.password)
        print("Ready to send emails")

    def send_email(self, to_address, body, subject):
        """Builds and sends a single email using the open connection."""

        message = MIMEMultipart()
        message["From"] = self.default_from
        message["To"] = to_address
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        # Send the email using the active server connection
        self.server.send_message(message)

    def close_connection(self):
        """Safely closes the connection to Zoho's servers."""
        self.server.quit()
        print("SMTP connection closed.")
