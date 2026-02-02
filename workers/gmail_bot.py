#!/usr/bin/env python3
"""
Email Bot for NJROTC Using Gmail API
"""
import os
import sys
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

load_dotenv()

print("=== GMAIL API BOT STARTING ===")

class GmailAPIBot:
    def __init__(self, last_name="", rank="", selected_items=None, recipient_email=""):
        print(f"Initializing GmailAPIBot for: {recipient_email}")
        
        self.sender_email = os.getenv("SENDER_EMAIL", "njrotcparlier@gmail.com")
        
        self.recipients = [recipient_email] if recipient_email else []
        
        # Admin notification email 
        admin_email = os.getenv("ADMIN_EMAIL")
        if admin_email and admin_email not in self.recipients:
            self.recipients.append(admin_email)
        
        self.user_last_name = last_name
        self.selected_items = selected_items or []
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if "Signup" in str(self.selected_items) or "SIGNUP" in str(self.selected_items):
            self.subject = "NJROTC Program Signup Confirmation"
            self.body_html = self.generate_signup_confirmation()
        elif "Suggestion" in str(self.selected_items):
            self.subject = "NJROTC Suggestion Received"
            self.body_html = self.generate_suggestion_email()
        
        print(f"Email subject: {self.subject}")
        print(f"Recipients: {self.recipients}")
    
    def generate_signup_confirmation(self):
        """Generate signup confirmation email matching website fundraising style"""
        # Extract info from selected items
        full_name = "Student"
        grade = "N/A"
        student_id = "N/A"
        reason = "Not provided"
        
        for item in self.selected_items:
            if "Student:" in item:
                full_name = item.split(":", 1)[1].strip()
            elif "Grade:" in item:
                grade = item.split(":", 1)[1].strip()
            elif "Student ID:" in item:
                student_id = item.split(":", 1)[1].strip()
            elif "Reason for joining:" in item:
                reason = item.split(":", 1)[1].strip()
        
        return f"""
        <html>
        <body style="margin:0; padding:20px; background:#000000; font-family:Segoe UI, Arial, sans-serif; color:#fafaf5;">

        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; background:#0a0a0f; border:2px solid #e6b220; border-radius:12px;">
            <tr>
                <td style="padding:30px; text-align:center;">
                    <h1 style="margin:0; font-size:28px; font-weight:800; color:#fafaf5;">NJROTC Program Signup</h1>
                    <p style="margin:10px 0 0; font-size:16px; color:#cccccc;">Confirmation Receipt • {self.current_time}</p>
                </td>
            </tr>

            <tr>
                <td style="padding:25px;">

                    <table width="100%" cellpadding="0" cellspacing="0"> <tr> <td style="text-align:center; padding-bottom:20px;"> <h2 style="margin:10px 0 0; font-size:24px; color:#2ecc71;">Test</h2> </td> </tr> </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Full Name</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{full_name}</td>
                        </tr>
                    </table>

                    <br>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Grade Level</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">Grade {grade}</td>
                        </tr>
                    </table>

                    <br>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Student ID</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{student_id}</td>
                        </tr>
                    </table>

                    <br>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Submission Date</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{self.current_time}</td>
                        </tr>
                    </table>

                    <h3 style="margin-top:30px; color:#e6b220; font-size:18px;">Your Reason for Joining</h3>
                    <div style="background:#001a33; border-left:4px solid #e6b220; padding:15px; border-radius:6px;">
                        <p style="margin:0; font-size:16px; font-style:italic; color:#fafaf5;">"{reason}"</p>
                    </div>

                    <div style="text-align:center; margin-top:40px; padding-top:20px; border-top:1px solid #023c71;">
                        <h2 style="color:#e6b220; font-size:24px; margin:0;">Thank You</h2>
                        <p style="max-width:500px; margin:10px auto 0; font-size:15px; color:#cccccc;">
                            We appreciate your interest in the NJROTC program. Your enthusiasm and commitment strengthen our unit. We look forward to welcoming you to our cadet family.
                        </p>
                    </div>

                    <p style="margin-top:30px; font-size:12px; color:#aaaaaa; text-align:center;">
                        <strong>Parlier Unified NJROTC</strong><br>
                        This is an automated confirmation message. Please do not reply.<br>
                        For inquiries, contact NJROTC instructor directly.
                    </p>

                </td>
            </tr>
        </table>

        </body>
        </html>
        """
    
    def generate_suggestion_email(self):
        """Generate suggestion notification email matching website fundraising style"""
        suggestion_type = "General"
        suggestion_text = "No suggestion provided"
        
        for item in self.selected_items:
            if "Suggestion Type:" in item:
                suggestion_type = item.split(":", 1)[1].strip()
            elif "Suggestion:" in item:
                suggestion_text = item.split(":", 1)[1].strip()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0; padding:20px; background:#000000; font-family:Segoe UI, Arial, sans-serif; color:#fafaf5;">

        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; background:#0a0a0f; border:2px solid #e6b220; border-radius:12px;">
            <tr>
                <td style="padding:30px; text-align:center;">
                    <h1 style="margin:0; font-size:28px; font-weight:800; color:#fafaf5;">Suggestion</h1>
                    <p style="margin:10px 0 0; font-size:16px; color:#cccccc;">NJROTC Program • {self.current_time}</p>
                </td>
            </tr>

            <tr>
                <td style="padding:25px;">

                    <table width="100%" cellpadding="0" cellspacing="0"> <tr> <td style="text-align:center; padding-bottom:20px;"> <h2 style="margin:10px 0 0; font-size:24px; color:#2ecc71;">Test</h2> </td> </tr> </table>


                    <!-- Received -->
                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Received</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{self.current_time}</td>
                        </tr>
                    </table>

                    <br>

                    <!-- From -->
                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">From</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{self.user_last_name}</td>
                        </tr>
                    </table>

                    <br>

                    <!-- Type -->
                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Type</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{suggestion_type}</td>
                        </tr>
                    </table>

                    <!-- Suggestion Details -->
                    <h3 style="margin-top:30px; color:#e6b220; font-size:18px;">Suggestion Details</h3>
                    <div style="background:#001a33; border-left:4px solid #e6b220; padding:15px; border-radius:6px;">
                        <p style="margin:0; font-size:16px; color:#fafaf5;">"{suggestion_text}"</p>
                    </div>

                    <!-- Footer -->
                    <div style="text-align:center; margin-top:40px; padding-top:20px; border-top:1px solid #023c71;">
                        <h2 style="color:#e6b220; font-size:24px; margin:0;">Thank You for the Feedback</h2>
                        <p style="max-width:500px; margin:10px auto 0; font-size:15px; color:#cccccc;">
                            Your input helps us improve the NJROTC program. We appreciate your perspective and will review your suggestion carefully.
                        </p>
                    </div>

                    <!-- Disclaimer -->
                    <p style="margin-top:30px; font-size:12px; color:#aaaaaa; text-align:center;">
                        <strong>Parlier Unified NJROTC</strong><br>
                        This is an automated message. Please do not reply.<br>
                        For inquiries, contact NJROTC instructor directly.
                    </p>

                </td>
            </tr>
        </table>

        </body>
        </html>

        """
    
    
    def authenticate_gmail(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None
        
        token_json = os.getenv('GMAIL_TOKEN_JSON')
        if token_json:
            try:
                token_info = json.loads(token_json)
                creds = Credentials.from_authorized_user_info(token_info, SCOPES)
                print("Loaded credentials from environment variable")
            except Exception as e:
                print(f"Error loading token from env: {e}")

        # Fallback to token.pickle file
        if not creds or not creds.valid:
            token_file = 'token.pickle'
            if os.path.exists(token_file):
                print(f"Loading credentials from {token_file}")
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                print("No valid credentials found, need to authenticate")
                return None
        
        return build('gmail', 'v1', credentials=creds)
    
    def create_message(self):
        """Create a MIME message"""
        message = MIMEMultipart('alternative')
        message['to'] = ', '.join(self.recipients)
        message['from'] = self.sender_email
        message['subject'] = self.subject
        
        message.attach(MIMEText(self.body_html, 'html'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}
    
    def send_email(self):
        """Send email using Gmail API"""
        print("=== ATTEMPTING TO SEND EMAIL VIA GMAIL API ===")
        
        if not self.recipients:
            print("ERROR: No recipient email specified")
            return False
        
        try:
            service = self.authenticate_gmail()
            if not service:
                print("ERROR: Failed to authenticate with Gmail API")
                print("Tip: You need to generate a token first (see README)")
                return False
            
            message = self.create_message()
            print(f"Sending email to: {self.recipients}")
            
            sent_message = service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            print(f"✓ Email sent successfully via Gmail API")
            print(f"  Message ID: {sent_message['id']}")
            print(f"  To: {', '.join(self.recipients)}")
            
            return True
            
        except HttpError as error:
            print(f"X Gmail API HTTP Error: {error}")
            return False
        except Exception as e:
            print(f"X Error sending email: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("=== EMAIL BOT MAIN FUNCTION ===")
    
    if len(sys.argv) >= 5:
        last_name = sys.argv[1]
        rank = sys.argv[2]
        selected_items = json.loads(sys.argv[3])
        recipient_email = sys.argv[4]
    else:
        print("Running in test mode...")
        last_name = "Test"
        rank = ""
        selected_items = ["Test Item from NJROTC Website"]
        recipient_email = os.getenv("TEST_EMAIL", "test@example.com")
    
    try:
        bot = GmailAPIBot(last_name, rank, selected_items, recipient_email)
        success = bot.send_email()
        
        if success:
            print("✓ Email process completed successfully")
            return 0
        else:
            print("X Email process failed")
            return 1
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())