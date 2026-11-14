import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ZohoMailer:
    def __init__(self, default_from):
        """Initializes the SMTP connection once when the class is created."""
        self.default_from = default_from
        self.password = os.environ.get("MAIL_PASSWORD", "your_MAIL_PASSWORD")
        self.smtp_server = "smtp.zoho.in"
        self.smtp_port = 587
        
        print("Connecting to server...")
        self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        
        print("Logging in...")
        self.server.login(self.default_from, self.password)
        print("Ready to send emails")

    def send_email(self, to_address, body, subject="Automated Notification", from_address=None):
        """Builds and sends a single email using the open connection."""
        # Use the default from_address if none is provided
        if from_address is None:
            from_address = self.default_from

        message = MIMEMultipart()
        message["From"] = from_address
        message["To"] = to_address
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        # Send the email using the active server connection
        self.server.send_message(message)
        print(f"Email sent successfully to {to_address}")

    def close_connection(self):
        """Safely closes the connection to Zoho's servers."""
        self.server.quit()
        print("SMTP connection closed.")

# ==========================================
# HOW TO USE IT IN YOUR LOOP
# ==========================================

if __name__ == "__main__":
    # 1. Open the connection ONCE before your loop begins
    mailer = ZohoMailer(default_from="abhinab.kanrar@mabsisa.com")

    # Sample data for the loop
    recipient_list = ["some.mail@gmail.com"]

    try:
        # 2. Run your loop and call the send_email function
        for email in recipient_list:
            custom_body = f"Hello {email},\n\nThis is a test email sent from a Python loop!"
            
            # Using default subject and from_address
            mailer.send_email(
                to_address=email,
                body=custom_body
            )
            
            # Example of overriding the default subject for a specific email:
            # mailer.send_email(to_address=email, body=custom_body, subject="Urgent Update!")
            
    except Exception as e:
        print(f"An error occurred during the loop: {e}")
        
    finally:
        # 3. Always close the connection when the loop is completely finished
        mailer.close_connection()

