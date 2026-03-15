#!/usr/bin/env python3
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

class ColorLogger:
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m',
    }
    
    @classmethod
    def log(cls, message, color='white', level='INFO'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        color_code = cls.COLORS.get(color, cls.COLORS['white'])
        reset_code = cls.COLORS['reset']
        print(f"{color_code}[{timestamp}] [{level}] {message}{reset_code}")
    
    @classmethod
    def success(cls, message):
        cls.log(message, 'green', 'SUCCESS')
    
    @classmethod
    def error(cls, message):
        cls.log(message, 'red', 'ERROR')
    
    @classmethod
    def warning(cls, message):
        cls.log(message, 'yellow', 'WARNING')
    
    @classmethod
    def info(cls, message):
        cls.log(message, 'blue', 'INFO')
    
    @classmethod
    def debug(cls, message):
        cls.log(message, 'cyan', 'DEBUG')

ColorLogger.info("=== GMAIL API BOT STARTING ===")

class GmailAPIBot:
    def __init__(self, last_name="", rank="", selected_items=None, recipient_email="", send_both_templates=False):
        ColorLogger.info(f"Initializing GmailAPIBot for: {recipient_email}")
        
        self.sender_email = os.getenv("SENDER_EMAIL", "njrotcparlier@gmail.com")
        self.recipients = [recipient_email] if recipient_email else []
        
        self.send_admin_copy = True  
        self.send_user_copy = True
        self.send_both_templates = send_both_templates
        
        self.user_last_name = last_name
        self.selected_items = selected_items or []
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.parsed_data = self.parse_selected_items()
        
        self.should_send = False
        self.email_templates = []  
        
        items_str = str(self.selected_items).lower()
        
        if "signup" in items_str:
            self.should_send = True
            self.email_templates.append({
                "subject": "NJROTC Program Signup Confirmation (Admin Copy)",
                "body_html": self.generate_admin_signup_notification(),
                "is_admin": True
            })
            
            if self.send_both_templates:
                self.email_templates.append({
                    "subject": "NJROTC Program Signup Confirmation",
                    "body_html": self.generate_signup_confirmation(),
                    "is_admin": False
                })
                ColorLogger.success(f"Will send BOTH admin and user emails to: {recipient_email}")
            else:
                ColorLogger.info(f"Will send ONLY admin copy email to: {recipient_email}")
            
        elif "suggestion" in items_str:
            self.should_send = True
            self.email_templates.append({
                "subject": "NJROTC Suggestion Received",
                "body_html": self.generate_suggestion_email(),
                "is_admin": True  
            })
            ColorLogger.success(f"Will send suggestion email to: {recipient_email}")
        else:
            ColorLogger.warning(f"Not sending email - no specific template for items")
            self.should_send = False
        
        if self.should_send:
            ColorLogger.info(f"Will send {len(self.email_templates)} email(s)")
            ColorLogger.info(f"Recipients: {self.recipients}")
        else:
            ColorLogger.error(f"Will NOT send email - no matching template")
    
    def parse_selected_items(self):
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
        
        if not data['full_name'] and self.user_last_name:
            data['full_name'] = self.user_last_name
        
        return data
    
    def generate_admin_signup_notification(self):
        data = self.parsed_data
        
        return f"""
        <html>
        <body style="margin:0; padding:20px; font-family:Segoe UI, Arial, sans-serif; color:#fafaf5;">

        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; background:#0a0a0f; border:2px solid #e6b220; border-radius:12px;">
            <tr>
                <td style="padding:30px; text-align:center;  color:white;">
                    <h1 style="margin:0; font-size:28px; font-weight:800;">NJROTC Program Signup</h1>
                    <p style="margin:10px 0 0; font-size:16px; opacity:0.9;">Parlier NJROTC Program • {self.current_time}</p>
                </td>
            </tr>

            <tr>
                <td style="padding:25px;">
                    
                    <div style="text-align:center; padding:15px; border-radius:8px; margin-bottom:25px;">
                        <h2 style="margin:0; color:white; font-size:24px;">Test</h2>
                    </div>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Student Name</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['full_name']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Grade Level</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">Grade {data['grade']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Student ID</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['student_id']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
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
        data = self.parsed_data
        
        return f"""
        <html>
        <body style="margin:0; padding:20px; font-family:Segoe UI, Arial, sans-serif; color:#fafaf5;">

        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; background:#0a0a0f; border:2px solid #e6b220; border-radius:12px;">
            <tr>
                <td style="padding:30px; text-align:center;">
                    <h1 style="margin:0; font-size:28px; font-weight:800; color:#fafaf5;">NJROTC Program Signup</h1>
                    <p style="margin:10px 0 0; font-size:16px; color:#cccccc;">Confirmation Receipt • {self.current_time}</p>
                </td>
            </tr>

            <tr>
                <td style="padding:25px;">

                    <div style="text-align:center; padding:15px; border-radius:8px; margin-bottom:25px;">
                        <h2 style="margin:0; color:white; font-size:24px;">Test</h2>
                    </div>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Full Name</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['full_name']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Grade Level</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">Grade {data['grade']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Student ID</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['student_id']}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
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

                    <div style="text-align:center; margin-top:40px; padding-top:20px; border-top:1px solid #023c71;">
                        <h2 style="color:#e6b220; font-size:24px; margin:0;">Thank You</h2>
                        <p style="max-width:500px; margin:10px auto 0; font-size:15px; color:#cccccc;">
                            We appreciate your interest in the NJROTC program. Your enthusiasm and commitment strengthen our unit. We look forward to welcoming you to our unit.
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
        data = self.parsed_data
        
        return f"""
        <html>
        <body style="margin:0; padding:20px; font-family:Segoe UI, Arial, sans-serif; color:#fafaf5;">

        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; background:#0a0a0f; border:2px solid #e6b220; border-radius:12px;">
            <tr>
                <td style="padding:30px; text-align:center;">
                    <h1 style="margin:0; font-size:28px; font-weight:800; color:#fafaf5;">Suggestion Received</h1>
                    <p style="margin:10px 0 0; font-size:16px; color:#cccccc;">NJROTC Program • {self.current_time}</p>
                </td>
            </tr>

            <tr>
                <td style="padding:25px;">

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">From</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{data['full_name'] or self.user_last_name}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
                        <tr>
                            <td style="color:#e6b220; font-size:12px; text-transform:uppercase;">Received</td>
                        </tr>
                        <tr>
                            <td style="font-size:18px; font-weight:600; color:#fafaf5;">{self.current_time}</td>
                        </tr>
                    </table>

                    <table width="100%" cellpadding="10" cellspacing="0" style="background:#000000; border:1px solid #e6b220; border-radius:12px; margin-bottom:15px;">
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
                        For inquiries, contact Your leadership directly.
                    </p>

                </td>
            </tr>
        </table>

        </body>
        </html>
        """
    
    def authenticate_gmail(self):
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None
        
        token_json = os.getenv('GMAIL_TOKEN_JSON')
        if token_json:
            try:
                token_info = json.loads(token_json)
                creds = Credentials.from_authorized_user_info(token_info, SCOPES)
                ColorLogger.success("Loaded credentials from environment variable")
            except Exception as e:
                ColorLogger.error(f"Error loading token from env: {e}")

        if not creds or not creds.valid:
            token_file = 'token.pickle'
            if os.path.exists(token_file):
                ColorLogger.info(f"Loading credentials from {token_file}")
                try:
                    with open(token_file, 'rb') as token:
                        creds = pickle.load(token)
                except Exception as e:
                    ColorLogger.error(f"Error loading token file: {e}")
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                ColorLogger.info("Refreshing expired credentials")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    ColorLogger.error(f"Error refreshing credentials: {e}")
                    return None
            else:
                ColorLogger.error("No valid credentials found")
                return None
        
        return build('gmail', 'v1', credentials=creds)
    
    def send_email(self):
        ColorLogger.info("=== ATTEMPTING TO SEND EMAIL(S) VIA GMAIL API ===")
        
        if not self.should_send:
            ColorLogger.warning("Skipping email - no matching template for items")
            return True
        
        if not self.recipients:
            ColorLogger.error("ERROR: No recipient email specified")
            return False
        
        try:
            service = self.authenticate_gmail()
            if not service:
                ColorLogger.error("ERROR: Failed to authenticate with Gmail API")
                ColorLogger.warning("Tip: You need to generate a token first")
                return False
            
            success_count = 0
            
            for template in self.email_templates:
                message = MIMEMultipart('alternative')
                message['to'] = ', '.join(self.recipients)
                message['from'] = self.sender_email
                message['subject'] = template["subject"]
                message.attach(MIMEText(template["body_html"], 'html'))
                
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                
                ColorLogger.info(f"Sending {template['subject']} to: {self.recipients}")
                
                try:
                    sent_message = service.users().messages().send(
                        userId='me', 
                        body={'raw': raw_message}
                    ).execute()
                    
                    ColorLogger.success(f"Email sent: {template['subject']}")
                    ColorLogger.info(f"Message ID: {sent_message['id']}")
                    success_count += 1
                    
                except Exception as e:
                    ColorLogger.error(f"Failed to send {template['subject']}: {e}")
            
            if success_count == len(self.email_templates):
                ColorLogger.success(f"All {success_count} email(s) sent successfully")
                return True
            elif success_count > 0:
                ColorLogger.warning(f"{success_count}/{len(self.email_templates)} email(s) sent")
                return True
            else:
                ColorLogger.error("No emails were sent successfully")
                return False
                
        except HttpError as error:
            ColorLogger.error(f"Gmail API HTTP Error: {error}")
            return False
        except Exception as e:
            ColorLogger.error(f"Error sending email: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    ColorLogger.info("=== EMAIL BOT MAIN FUNCTION ===")
    
    if len(sys.argv) >= 5:
        last_name = sys.argv[1]
        rank = sys.argv[2]
        selected_items = json.loads(sys.argv[3])
        recipient_email = sys.argv[4]
        send_both = True if len(sys.argv) < 6 else sys.argv[5].lower() == 'true'
    else:
        ColorLogger.warning("Running in test mode...")
        last_name = "Test"
        rank = ""
        selected_items = ["Student: Test User", "Grade: 10", "Student ID: 123456", "Reason for joining: Testing the system"]
        recipient_email = os.getenv("TEST_EMAIL", "test@example.com")
        send_both = True
    
    try:
        bot = GmailAPIBot(last_name, rank, selected_items, recipient_email, send_both_templates=send_both)
        success = bot.send_email()
        
        if success:
            ColorLogger.success("Email process completed successfully")
            return 0
        else:
            ColorLogger.error("Email process failed")
            return 1
    except Exception as e:
        ColorLogger.error(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())