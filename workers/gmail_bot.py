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
        else:
            self.subject = "NJROTC Notification"
            self.body_html = self.generate_generic_email()
        
        print(f"Email subject: {self.subject}")
        print(f"Recipients: {self.recipients}")
    
    def generate_signup_confirmation(self):
        """Generate signup confirmation email with website styling"""
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
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NJROTC Signup Confirmation</title>
            <style>
                /* Website Theme Styling */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: #000000;
                    color: #fafaf5;
                    line-height: 1.6;
                    padding: 20px;
                }}
                
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: linear-gradient(135deg, rgba(10, 10, 15, 0.95), rgba(2, 60, 113, 0.2));
                    border: 2px solid #e6b220;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
                    position: relative;
                }}
                
                .email-container::before {{
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(45deg, rgba(2, 60, 113, 0.3), rgba(230, 178, 32, 0.1));
                    opacity: 0.3;
                    z-index: -1;
                }}
                
                .header {{
                    text-align: center;
                    padding: 30px 20px;
                    background: rgba(2, 60, 113, 0.1);
                    border-bottom: 1px solid rgba(230, 178, 32, 0.3);
                }}
                
                .header h1 {{
                    color: #e6b220;
                    font-size: 2rem;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                
                .header p {{
                    color: #fafaf5;
                    opacity: 0.8;
                }}
                
                .content {{
                    padding: 30px;
                }}
                
                .content-section {{
                    margin-bottom: 25px;
                }}
                
                .section-title {{
                    color: #e6b220;
                    font-size: 1.2rem;
                    margin-bottom: 15px;
                    padding-bottom: 8px;
                    border-bottom: 2px solid rgba(230, 178, 32, 0.3);
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                    margin-top: 15px;
                }}
                
                .info-item {{
                    background: rgba(255, 255, 255, 0.05);
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid rgba(230, 178, 32, 0.2);
                }}
                
                .info-label {{
                    color: #e6b220;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 5px;
                }}
                
                .info-value {{
                    color: #fafaf5;
                    font-size: 1.1rem;
                }}
                
                .reason-box {{
                    background: rgba(2, 60, 113, 0.1);
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #e6b220;
                    margin-top: 10px;
                }}
                
                .reason-text {{
                    color: #fafaf5;
                    font-style: italic;
                    line-height: 1.8;
                }}
                
                .footer {{
                    text-align: center;
                    padding: 20px;
                    background: rgba(0, 0, 0, 0.3);
                    border-top: 1px solid rgba(230, 178, 32, 0.2);
                    margin-top: 30px;
                }}
                
                .footer p {{
                    color: rgba(250, 250, 245, 0.7);
                    font-size: 0.9rem;
                }}
                
                .highlight {{
                    color: #e6b220;
                    font-weight: bold;
                }}
                
                .thank-you {{
                    text-align: center;
                    padding: 20px;
                    margin: 20px 0;
                    background: rgba(46, 204, 113, 0.1);
                    border: 1px solid #2ecc71;
                    border-radius: 8px;
                }}
                
                @media (max-width: 600px) {{
                    .content {{
                        padding: 20px;
                    }}
                    
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .header h1 {{
                        font-size: 1.5rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>NJROTC Program Signup</h1>
                    <p>Confirmation Receipt • {self.current_time}</p>
                </div>
                
                <div class="content">
                    <div class="thank-you">
                        <h2 style="color: #2ecc71;">Thank You for Signing Up!</h2>
                        <p>Your application has been received and is being processed.</p>
                    </div>
                    
                    <div class="content-section">
                        <h3 class="section-title">Application Details</h3>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Full Name</div>
                                <div class="info-value">{full_name}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Grade Level</div>
                                <div class="info-value">Grade {grade}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Student ID</div>
                                <div class="info-value">{student_id}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Submission Date</div>
                                <div class="info-value">{self.current_time}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="content-section">
                        <h3 class="section-title">Reason for Joining</h3>
                        <div class="reason-box">
                            <div class="reason-text">"{reason}"</div>
                        </div>
                    </div>
                    
                    <div class="content-section">
                        <h3 class="section-title">Next Steps</h3>
                        <div class="info-item">
                            <ul style="color: #fafaf5; padding-left: 20px;">
                                <li>You will receive follow-up information within 3-5 business days</li>
                                <li>Prepare necessary documentation (ID, physical forms, etc.)</li>
                                <li>Attend the next scheduled orientation session</li>
                                <li>Contact your instructor if you have immediate questions</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>Parlier Unified School District NJROTC</strong></p>
                    <p>This is an automated confirmation message. Please do not reply directly to this email.</p>
                    <p>For inquiries, contact your NJROTC instructor directly.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def generate_suggestion_email(self):
        """Generate suggestion notification email with website styling"""
        suggestion_type = "General"
        suggestion_text = "No suggestion provided"
        
        for item in self.selected_items:
            if "Suggestion Type:" in item:
                suggestion_type = item.split(":", 1)[1].strip()
            elif "Suggestion:" in item:
                suggestion_text = item.split(":", 1)[1].strip()
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NJROTC Suggestion Received</title>
            <style>
                /* Same website theme styling as above */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: #000000;
                    color: #fafaf5;
                    line-height: 1.6;
                    padding: 20px;
                }}
                
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: linear-gradient(135deg, rgba(10, 10, 15, 0.95), rgba(2, 60, 113, 0.2));
                    border: 2px solid #e6b220;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
                    position: relative;
                }}
                
                .email-container::before {{
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(45deg, rgba(2, 60, 113, 0.3), rgba(230, 178, 32, 0.1));
                    opacity: 0.3;
                    z-index: -1;
                }}
                
                .header {{
                    text-align: center;
                    padding: 30px 20px;
                    background: rgba(2, 60, 113, 0.1);
                    border-bottom: 1px solid rgba(230, 178, 32, 0.3);
                }}
                
                .header h1 {{
                    color: #e6b220;
                    font-size: 2rem;
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                
                .content {{
                    padding: 30px;
                }}
                
                .content-section {{
                    margin-bottom: 25px;
                }}
                
                .section-title {{
                    color: #e6b220;
                    font-size: 1.2rem;
                    margin-bottom: 15px;
                    padding-bottom: 8px;
                    border-bottom: 2px solid rgba(230, 178, 32, 0.3);
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .info-item {{
                    background: rgba(255, 255, 255, 0.05);
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid rgba(230, 178, 32, 0.2);
                    margin-bottom: 15px;
                }}
                
                .info-label {{
                    color: #e6b220;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 5px;
                }}
                
                .info-value {{
                    color: #fafaf5;
                    font-size: 1.1rem;
                }}
                
                .suggestion-box {{
                    background: rgba(2, 60, 113, 0.1);
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #e6b220;
                    margin-top: 10px;
                }}
                
                .suggestion-text {{
                    color: #fafaf5;
                    line-height: 1.8;
                }}
                
                .footer {{
                    text-align: center;
                    padding: 20px;
                    background: rgba(0, 0, 0, 0.3);
                    border-top: 1px solid rgba(230, 178, 32, 0.2);
                    margin-top: 30px;
                }}
                
                .footer p {{
                    color: rgba(250, 250, 245, 0.7);
                    font-size: 0.9rem;
                }}
                
                @media (max-width: 600px) {{
                    .content {{
                        padding: 20px;
                    }}
                    
                    .header h1 {{
                        font-size: 1.5rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>New Suggestion Received</h1>
                    <p>NJROTC Program • {self.current_time}</p>
                </div>
                
                <div class="content">
                    <div class="content-section">
                        <h3 class="section-title">Suggestion Details</h3>
                        
                        <div class="info-item">
                            <div class="info-label">Type</div>
                            <div class="info-value">{suggestion_type}</div>
                        </div>
                        
                        <div class="info-item">
                            <div class="info-label">Submitted By</div>
                            <div class="info-value">{self.user_last_name}</div>
                        </div>
                        
                        <div class="info-item">
                            <div class="info-label">Submission Time</div>
                            <div class="info-value">{self.current_time}</div>
                        </div>
                    </div>
                    
                    <div class="content-section">
                        <h3 class="section-title">Suggestion Content</h3>
                        <div class="suggestion-box">
                            <div class="suggestion-text">{suggestion_text}</div>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>NJROTC Suggestion Box</strong></p>
                    <p>This is an automated notification. Review this suggestion when convenient.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def generate_generic_email(self):
        """Generate generic notification email"""
        items_html = "\n".join([f"<li>{item}</li>" for item in self.selected_items])
        return f"""
        <html>
        <body>
            <h2>NJROTC Notification</h2>
            <p><strong>Date:</strong> {self.current_time}</p>
            <p><strong>Items:</strong></p>
            <ul>{items_html}</ul>
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