#!/usr/bin/env python3
"""
Email bot for NJROTC - Render compatible
"""
import os
import sys
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class EmailBot:
    def __init__(self, last_name="", rank="", selected_items=None, recipient_email=""):
        self.sender_email = os.getenv("SENDER_EMAIL", "njrotcparlier@gmail.com")
        self.password = os.getenv("PYTHON_EMAIL_CURSE")
        self.recipients = [recipient_email] if recipient_email else []
        admin_email = os.getenv("ADMIN_EMAIL")
        if admin_email:
            self.recipients.append(admin_email)
        
        self.user_last_name = last_name
        self.rank = rank
        self.selected_items = selected_items or []
        self.full_title = f"{self.rank} {self.user_last_name}".strip()
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine email type
        if "Signup" in str(self.selected_items):
            self.subject = "NJROTC Program Signup Request - test"
            self.body_html = self.generate_signup_request()
        else:
            self.subject = "NJROTC Notification - test"
            self.body_html = self.generate_generic_email()
    
    def generate_signup_request(self):
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #023c71; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .highlight {{ color: #e6b220; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>NJROTC Program Signup Request</h1>
                </div>
                <div class="content">
                    <p>Dear {self.full_title},</p>
                    <p>Thank you for signing up for the NJROTC program!</p>
                    <p>Your signup has been received on <span class="highlight">{self.current_time}</span>.</p>
                    <p>We will contact you soon with further information about the program.</p>
                    <p><strong>Semper Fortis!</strong></p>
                </div>
                <div class="footer">
                    <p>Parlier Unified NJROTC<br>
                    This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def generate_generic_email(self):
        items_html = "\n".join([f"<li>{item}</li>" for item in self.selected_items])
        return f"""
        <html>
        <body>
            <h2>NJROTC Notification</h2>
            <p><strong>Date:</strong> {self.current_time}</p>
            <p><strong>Recipient:</strong> {self.full_title}</p>
            <p><strong>Items:</strong></p>
            <ul>{items_html}</ul>
        </body>
        </html>
        """
    
    def send_email(self):
        if not self.password:
            print("ERROR: Email password not configured. Set PYTHON_EMAIL_CURSE environment variable.")
            return False
        
        if not self.recipients:
            print("ERROR: No recipient email specified")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = self.subject
            
            msg.attach(MIMEText(self.body_html, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.password)
            
            server.send_message(msg)
            server.quit()
            
            print(f"✓ Email sent successfully to {', '.join(self.recipients)}")
            print(f"  Time: {self.current_time}")
            print(f"  For: {self.full_title}")
            return True
            
        except Exception as e:
            print(f"✗ Error sending email: {str(e)}")
            return False

def main():
    if len(sys.argv) >= 5:
        last_name = sys.argv[1]
        rank = sys.argv[2]
        selected_items = json.loads(sys.argv[3])
        recipient_email = sys.argv[4]
    else:
        last_name = "Test"
        rank = "Cadet"
        selected_items = ["Test Item"]
        recipient_email = "test@example.com"
    
    bot = EmailBot(last_name, rank, selected_items, recipient_email)
    success = bot.send_email()
    
    if success:
        print("Email process completed successfully")
    else:
        print("Email process failed")
        sys.exit(1)

if __name__ == "__main__":
    main()