#!/usr/bin/env python3
"""
Gmail API Email Bot for NJROTC - Render compatible
"""
import os
import sys
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Gmail API imports
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# Load environment variables from Render
load_dotenv()

print("=== GMAIL API BOT STARTING ===")
print(f"Python path: {sys.path}")
print(f"Current dir: {os.getcwd()}")

class GmailAPIBot:
    def __init__(self, last_name="", rank="", selected_items=None, recipient_email=""):
        print(f"Initializing GmailAPIBot for: {recipient_email}")
        
        # Sender email (must be the same as authenticated account)
        self.sender_email = os.getenv("SENDER_EMAIL", "njrotcparlier@gmail.com")
        
        # Recipients
        self.recipients = [recipient_email] if recipient_email else []
        
        # Add admin notification email if needed
        admin_email = os.getenv("ADMIN_EMAIL")
        if admin_email and admin_email not in self.recipients:
            self.recipients.append(admin_email)
        
        # User info
        self.user_last_name = last_name
        self.rank = rank
        self.selected_items = selected_items or []
        self.full_title = f"{self.rank} {self.user_last_name}".strip()
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine email type and content
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
    
    def authenticate_gmail(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None
        
        # Try to get token from environment variable first (for Render)
        token_json = os.getenv('GMAIL_TOKEN_JSON')
        if token_json:
            try:
                token_info = json.loads(token_json)
                creds = Credentials.from_authorized_user_info(token_info, SCOPES)
                print("Loaded credentials from environment variable")
            except Exception as e:
                print(f"Error loading token from env: {e}")
        
        # If no token in env, try token.pickle file
        if not creds or not creds.valid:
            token_file = 'token.pickle'
            if os.path.exists(token_file):
                print(f"Loading credentials from {token_file}")
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
        
        # If credentials are invalid or don't exist
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                print("No valid credentials found, need to authenticate")
                # For Render, we need pre-authenticated token
                return None
        
        return build('gmail', 'v1', credentials=creds)
    
    def create_message(self):
        """Create a MIME message"""
        message = MIMEMultipart('alternative')
        message['to'] = ', '.join(self.recipients)
        message['from'] = self.sender_email
        message['subject'] = self.subject
        
        # Attach HTML body
        message.attach(MIMEText(self.body_html, 'html'))
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
    
    def send_email(self):
        """Send email using Gmail API"""
        print("=== ATTEMPTING TO SEND EMAIL VIA GMAIL API ===")
        
        if not self.recipients:
            print("ERROR: No recipient email specified")
            return False
        
        try:
            # Authenticate with Gmail API
            service = self.authenticate_gmail()
            if not service:
                print("ERROR: Failed to authenticate with Gmail API")
                print("Tip: You need to generate a token first (see README)")
                return False
            
            # Create and send message
            message = self.create_message()
            print(f"Sending email to: {self.recipients}")
            
            sent_message = service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            print(f"✓ Email sent successfully via Gmail API")
            print(f"  Message ID: {sent_message['id']}")
            print(f"  To: {', '.join(self.recipients)}")
            print(f"  Time: {self.current_time}")
            
            return True
            
        except HttpError as error:
            print(f"✗ Gmail API HTTP Error: {error}")
            if error.resp.status == 403:
                print("  This usually means:")
                print("  1. Gmail API not enabled in Google Cloud Console")
                print("  2. OAuth consent screen not configured")
                print("  3. Token doesn't have gmail.send permission")
            return False
        except Exception as e:
            print(f"✗ Error sending email: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("=== GMAIL API BOT MAIN FUNCTION ===")
    
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
        selected_items = ["Test Item from Gmail API"]
        recipient_email = os.getenv("TEST_EMAIL", "test@example.com")
    
    # Create and send email
    try:
        bot = GmailAPIBot(last_name, rank, selected_items, recipient_email)
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