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

# Load environment variables from Render
load_dotenv()

print("=== GMAIL BOT STARTING ===")  # Debug print
print(f"Python path: {sys.path}")
print(f"Current dir: {os.getcwd()}")

class EmailBot:
    def __init__(self, last_name="", rank="", selected_items=None, recipient_email=""):
        print(f"Initializing EmailBot for: {recipient_email}")
        
        self.sender_email = os.getenv("SENDER_EMAIL", "njrotcparlier@gmail.com")
        self.password = os.getenv("PYTHON_EMAIL_CURSE")
        
        print(f"Sender email: {self.sender_email}")
        print(f"Password configured: {'YES' if self.password else 'NO'}")
        
        if not self.password:
            raise ValueError("Email password (PYTHON_EMAIL_CURSE) not configured")
        
        self.recipients = [recipient_email] if recipient_email else []
        
        # Add admin notification email if needed
        admin_email = os.getenv("ADMIN_EMAIL")
        if admin_email and admin_email not in self.recipients:
            self.recipients.append(admin_email)
        
        self.user_last_name = last_name
        self.rank = rank
        self.selected_items = selected_items or []
        self.full_title = f"{self.rank} {self.user_last_name}".strip()
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine email type
        if "Signup" in str(self.selected_items):
            self.subject = "NJROTC Program Signup Confirmation"
            self.body_html = self.generate_signup_confirmation()
        elif "Suggestion" in str(self.selected_items):
            self.subject = "NJROTC Suggestion Received"
            self.body_html = self.generate_suggestion_email()
        else:
            self.subject = "NJROTC Notification"
            self.body_html = self.generate_generic_email()
        
        print(f"Email subject: {self.subject}")
        print(f"Recipients: {self.recipients}")
    
    def generate_signup_confirmation(self):
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
                    <h1>NJROTC Program Signup Confirmation</h1>
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
    
    def generate_suggestion_email(self):
        items_html = "\n".join([f"<li>{item}</li>" for item in self.selected_items])
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #023c71; color: white; padding: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>NJROTC Suggestion Received</h1>
                </div>
                <div style="padding: 20px;">
                    <p><strong>From:</strong> {self.full_title}</p>
                    <p><strong>Date:</strong> {self.current_time}</p>
                    <p><strong>Suggestion Details:</strong></p>
                    <ul>{items_html}</ul>
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
        print("=== ATTEMPTING TO SEND EMAIL ===")
        
        if not self.password:
            print("ERROR: Email password not configured. Set PYTHON_EMAIL_CURSE environment variable.")
            return False
        
        if not self.recipients:
            print("ERROR: No recipient email specified")
            return False
        
        try:
            print(f"1. Creating email message...")
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = self.subject
            
            # Attach HTML body
            msg.attach(MIMEText(self.body_html, 'html'))
            
            print(f"2. Connecting to SMTP server...")
            # Setup SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            print(f"3. Starting TLS...")
            server.starttls()
            print(f"4. Logging in...")
            server.login(self.sender_email, self.password)
            
            print(f"5. Sending email...")
            # Send email
            server.send_message(msg)
            print(f"6. Closing connection...")
            server.quit()
            
            print(f"✓ Email sent successfully to {', '.join(self.recipients)}")
            print(f"  Time: {self.current_time}")
            print(f"  For: {self.full_title}")
            return True
            
        except Exception as e:
            print(f"✗ Error sending email: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("=== EMAIL BOT MAIN FUNCTION ===")
    
    # Parse command line arguments
    if len(sys.argv) >= 5:
        last_name = sys.argv[1]
        rank = sys.argv[2]
        selected_items = json.loads(sys.argv[3])
        recipient_email = sys.argv[4]
    else:
        # Test mode
        print("Running in test mode...")
        last_name = "Test"
        rank = "Cadet"
        selected_items = ["Test Item"]
        recipient_email = os.getenv("TEST_EMAIL", "test@example.com")
    
    # Create and send email
    try:
        bot = EmailBot(last_name, rank, selected_items, recipient_email)
        success = bot.send_email()
        
        if success:
            print("✓ Email process completed successfully")
            return 0
        else:
            print("✗ Email process failed")
            return 1
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())