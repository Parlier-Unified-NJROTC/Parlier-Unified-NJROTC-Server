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
        
        # Track if this is an admin email (different template)
        self.is_admin_email = "instructor" in recipient_email.lower() or "admin" in recipient_email.lower()
        
        self.user_last_name = last_name
        self.selected_items = selected_items or []
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Parse data from selected items
        self.parsed_data = self.parse_selected_items()
        
        # Set default subject to prevent AttributeError
        self.subject = "NJROTC Notification"
        self.body_html = ""
        
        # Determine email type
        if "Signup" in str(self.selected_items) or "SIGNUP" in str(self.selected_items):
            if self.is_admin_email:
                self.subject = "🚨 NEW NJROTC Signup Notification"
                self.body_html = self.generate_admin_signup_notification()
            else:
                self.subject = "NJROTC Program Signup Confirmation"
                self.body_html = self.generate_signup_confirmation()
        elif "Suggestion" in str(self.selected_items):
            self.subject = "NJROTC Suggestion Received"
            self.body_html = self.generate_suggestion_email()
        else:
            # Fallback generic email
            self.body_html = self.generate_generic_email()
        
        print(f"Email subject: {self.subject}")
        print(f"Recipients: {self.recipients}")
        print(f"Is Admin Email: {self.is_admin_email}")
        print(f"Parsed Data: {self.parsed_data}")
    
    def parse_selected_items(self):
        """Parse data from selected items array"""
        data = {
            'full_name': '',
            'grade': '',
            'student_id': '',
            'reason': '',
            'email': '',
            'ip_address': '',
            'timestamp': self.current_time,
            'note': '',
            'suggestion_type': '',
            'suggestion_text': ''
        }
        
        for item in self.selected_items:
            item_str = str(item)
            if "Student:" in item_str:
                data['full_name'] = item_str.split(":", 1)[1].strip()
            elif "Grade:" in item_str:
                data['grade'] = item_str.split(":", 1)[1].strip()
            elif "Student ID:" in item_str:
                data['student_id'] = item_str.split(":", 1)[1].strip()
            elif "Reason for joining:" in item_str:
                data['reason'] = item_str.split(":", 1)[1].strip()
            elif "Email:" in item_str:
                data['email'] = item_str.split(":", 1)[1].strip()
            elif "IP Address:" in item_str:
                data['ip_address'] = item_str.split(":", 1)[1].strip()
            elif "NOTE:" in item_str:
                data['note'] = item_str.split(":", 1)[1].strip()
            elif "Suggestion Type:" in item_str:
                data['suggestion_type'] = item_str.split(":", 1)[1].strip()
            elif "Suggestion:" in item_str:
                data['suggestion_text'] = item_str.split(":", 1)[1].strip()
        
        # If full_name not found but we have last name, use it
        if not data['full_name'] and self.user_last_name:
            data['full_name'] = self.user_last_name
        
        return data
    
    def generate_admin_signup_notification(self):
        """Generate admin notification for new signups"""
        data = self.parsed_data
        
        return f"""
        <html>
        <body style="margin:0; padding:20px; background:#000000; font-family:Segoe UI, Arial, sans-serif; color:#fafaf5;">

        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; background:#0a0a0f; border:2px solid #e74c3c; border-radius:12px;">
            <tr>
                <td style="padding:30px; text-align:center; background:#e74c3c; color:white;">
                    <h1 style="margin:0; font-size:28px; font-weight:800;">🚨 NEW SIGNUP RECEIVED</h1>
                    <p style="margin:10px 0 0; font-size:16px; opacity:0.9;">NJROTC Program • {self.current_time}</p>
                </td>
            </tr>

            <tr>
                <td style="padding:25px;">

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Student Name</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['full_name']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Grade Level</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">Grade {data['grade']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Student ID</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['student_id']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Contact Email</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['email']}</td>
                        </tr>
                    </table>

                    <h3 style="margin-top:30px; color:#e6b220; font-size:18px;">Student's Reason for Joining</h3>
                    <div style="background:#001a33; border-left:4px solid #e6b220; padding:15px; border-radius:6px; margin-bottom:20px;">
                        <p style="margin:0; font-size:16px; font-style:italic; color:#fafaf5;">"{data['reason']}"</p>
                    </div>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #666; border-radius:12px; margin-bottom:20px;">
                        <tr>
                            <td style="color:#999; font-size:11px; text-transform:uppercase;">Technical Details</td>
                        </tr>
                        <tr>
                            <td style="font-size:12px; color:#ccc;">
                                IP Address: {data['ip_address'] or 'N/A'}<br>
                                Submitted: {data['timestamp']}<br>
                                Auto-generated by NJROTC Website
                            </td>
                        </tr>
                    </table>

                    <div style="text-align:center; margin-top:40px; padding-top:20px; border-top:1px solid #023c71;">
                        <h2 style="color:#e6b220; font-size:24px; margin:0;">Action Required</h2>
                        <p style="max-width:500px; margin:10px auto 0; font-size:15px; color:#cccccc;">
                            Please follow up with this student within 3 business days to complete their enrollment process.
                        </p>
                    </div>

                    <p style="margin-top:30px; font-size:12px; color:#aaaaaa; text-align:center;">
                        <strong>Parlier Unified NJROTC Automated Notification</strong><br>
                        This is an automated message. Please do not reply.<br>
                        System generated at {self.current_time}
                    </p>

                </td>
            </tr>
        </table>

        </body>
        </html>
        """
    
    def generate_signup_confirmation(self):
        """Generate signup confirmation email for student"""
        data = self.parsed_data
        
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

                    <div style="text-align:center; background:#2ecc71; padding:15px; border-radius:8px; margin-bottom:25px;">
                        <h2 style="margin:0; color:white; font-size:24px;">✓ Application Confirmed</h2>
                    </div>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Full Name</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['full_name']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Grade Level</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">Grade {data['grade']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Student ID</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['student_id']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Submission Date</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{self.current_time}</td>
                        </tr>
                    </table>

                    <h3 style="margin-top:30px; color:#e6b220; font-size:18px;">Your Reason for Joining</h3>
                    <div style="background:#001a33; border-left:4px solid #e6b220; padding:15px; border-radius:6px; margin-bottom:20px;">
                        <p style="margin:0; font-size:16px; font-style:italic; color:#fafaf5;">"{data['reason']}"</p>
                    </div>

                    <div style="background:#1a472a; padding:15px; border-radius:8px; margin:25px 0;">
                        <h4 style="margin:0 0 10px 0; color:#2ecc71; font-size:16px;">📋 Next Steps</h4>
                        <ul style="margin:0; padding-left:20px; color:#fafaf5; font-size:14px;">
                            <li>You will receive follow-up information within 3-5 business days</li>
                            <li>Prepare necessary documentation (ID, physical forms, etc.)</li>
                            <li>Attend the next scheduled orientation session</li>
                            <li>Contact your instructor if you have immediate questions</li>
                        </ul>
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
        """Generate suggestion notification email"""
        data = self.parsed_data
        
        return f"""
        <html>
        <body style="margin:0; padding:20px; background:#000000; font-family:Segoe UI, Arial, sans-serif; color:#fafaf5;">

        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; background:#0a0a0f; border:2px solid #3498db; border-radius:12px;">
            <tr>
                <td style="padding:30px; text-align:center;">
                    <h1 style="margin:0; font-size:28px; font-weight:800; color:#fafaf5;">New Suggestion Received</h1>
                    <p style="margin:10px 0 0; font-size:16px; color:#cccccc;">NJROTC Program • {self.current_time}</p>
                </td>
            </tr>

            <tr>
                <td style="padding:25px;">

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">From</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['full_name'] or self.user_last_name}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Received</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{self.current_time}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #023c71; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Suggestion Type</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['suggestion_type']}</td>
                        </tr>
                    </table>

                    <h3 style="margin-top:30px; color:#e6b220; font-size:18px;">Suggestion Details</h3>
                    <div style="background:#001a33; border-left:4px solid #e6b220; padding:15px; border-radius:6px;">
                        <p style="margin:0; font-size:16px; color:#fafaf5;">"{data['suggestion_text']}"</p>
                    </div>

                    <div style="text-align:center; margin-top:40px; padding-top:20px; border-top:1px solid #023c71;">
                        <h2 style="color:#e6b220; font-size:24px; margin:0;">Thank You for the Feedback</h2>
                        <p style="max-width:500px; margin:10px auto 0; font-size:15px; color:#cccccc;">
                            Your input helps us improve the NJROTC program. We appreciate your perspective and will review your suggestion carefully.
                        </p>
                    </div>

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
    
    def generate_generic_email(self):
        """Generate generic notification email"""
        items_html = "<br>".join([f"• {item}" for item in self.selected_items])
        return f"""
        <html>
        <body style="margin:0; padding:20px; background:#000000; font-family:Segoe UI, Arial, sans-serif; color:#fafaf5;">
        <div style="max-width:600px; margin:0 auto; padding:30px; background:#0a0a0f; border:2px solid #e6b220; border-radius:12px;">
            <h1 style="color:#fafaf5; text-align:center;">NJROTC Notification</h1>
            <p><strong>Date:</strong> {self.current_time}</p>
            <p><strong>Items:</strong></p>
            <p>{items_html}</p>
        </div>
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
                print("✓ Loaded credentials from environment variable")
            except Exception as e:
                print(f"✗ Error loading token from env: {e}")

        if not creds or not creds.valid:
            token_file = 'token.pickle'
            if os.path.exists(token_file):
                print(f"✓ Loading credentials from {token_file}")
                try:
                    with open(token_file, 'rb') as token:
                        creds = pickle.load(token)
                except Exception as e:
                    print(f"✗ Error loading token file: {e}")
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("✓ Refreshing expired credentials")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"✗ Error refreshing credentials: {e}")
                    return None
            else:
                print("✗ No valid credentials found")
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
            print("✗ ERROR: No recipient email specified")
            return False
        
        try:
            service = self.authenticate_gmail()
            if not service:
                print("✗ ERROR: Failed to authenticate with Gmail API")
                print("💡 Tip: You need to generate a token first (see README)")
                return False
            
            message = self.create_message()
            print(f"📧 Sending email to: {self.recipients}")
            
            sent_message = service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            print(f"✓ Email sent successfully via Gmail API")
            print(f"  📨 Message ID: {sent_message['id']}")
            print(f"  👤 To: {', '.join(self.recipients)}")
            print(f"  🏷️ Subject: {self.subject}")
            
            return True
            
        except HttpError as error:
            print(f"✗ Gmail API HTTP Error: {error}")
            return False
        except Exception as e:
            print(f"✗ Error sending email: {type(e).__name__}: {str(e)}")
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
        print("🔧 Running in test mode...")
        last_name = "Test"
        rank = ""
        selected_items = ["Student: Test User", "Grade: 10", "Student ID: 123456", "Reason for joining: Testing the system"]
        recipient_email = os.getenv("TEST_EMAIL", "test@example.com")
    
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
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())