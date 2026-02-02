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
        <head>
            <style>
                /* Fundraising Page Style */
                body {{
                    background: #000000;
                    color: #fafaf5;
                    position: relative;
                    z-index: 1;
                    overflow-x: hidden;
                    min-height: 100vh;
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
                
                .email-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem 1rem;
                }}
                
                .section-header {{
                    text-align: center;
                    margin-bottom: 3rem;
                }}
                
                .section-title {{
                    font-size: 2.5rem;
                    font-weight: 800;
                    margin-bottom: 1rem;
                    color: #fafaf5;
                    opacity: 0.8;
                }}
                
                .content {{
                    padding: 30px;
                }}
                
                .content-section {{
                    margin-bottom: 25px;
                }}
                
                .section-subtitle {{
                    font-size: 1.3rem;
                    color: rgba(250, 250, 245, 0.9);
                    max-width: 600px;
                    margin: 0 auto;
                    line-height: 1.6;
                }}
                
                .content-card {{
                    background: rgba(0, 0, 0, 0.7);
                    border: 1px solid rgba(2, 60, 113, 0.7);
                    border-radius: 20px;
                    overflow: hidden;
                    position: relative;
                    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
                }}
                
                .card-overlay {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(45deg, rgba(2, 60, 113, 0.3), rgba(230, 178, 32, 0.1));
                    z-index: 1;
                }}
                
                .content-wrapper {{
                    padding: 2.5rem;
                    position: relative;
                    z-index: 2;
                }}
                
                .confirmation-section {{
                    margin-bottom: 2rem;
                }}
                
                .confirmation-header {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 1rem;
                    margin-bottom: 2rem;
                }}
                
                .confirmation-icon {{
                    width: 60px;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: rgba(46, 204, 113, 0.2);
                    flex-shrink: 0;
                }}
                
                .confirmation-icon svg {{
                    fill: #2ecc71;
                }}
                
                .confirmation-title {{
                    color: #2ecc71;
                    font-size: 2rem;
                    font-weight: 700;
                    margin: 0;
                }}
                
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1rem;
                    margin: 2rem 0;
                }}
                
                .info-card {{
                    background: rgba(2, 60, 113, 0.2);
                    border: 1px solid rgba(2, 60, 113, 0.5);
                    border-radius: 12px;
                    padding: 1.5rem;
                    transition: all 0.3s ease;
                }}
                
                .info-card:hover {{
                    border-color: rgba(230, 178, 32, 0.6);
                    transform: translateY(-2px);
                }}
                
                .info-label {{
                    color: #e6b220;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 0.5rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }}
                
                .info-value {{
                    color: #fafaf5;
                    font-size: 1.2rem;
                    font-weight: 600;
                }}
                
                .reason-section {{
                    margin: 2rem 0;
                }}
                
                .section-heading {{
                    color: #e6b220;
                    font-size: 1.4rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }}
                
                .reason-box {{
                    background: rgba(2, 60, 113, 0.1);
                    border-left: 4px solid #e6b220;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-top: 1rem;
                }}
                
                .reason-text {{
                    color: #fafaf5;
                    font-size: 1.1rem;
                    line-height: 1.7;
                    font-style: italic;
                    margin: 0;
                }}
                
                .next-steps {{
                    background: rgba(230, 178, 32, 0.1);
                    border: 1px solid rgba(230, 178, 32, 0.3);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 2rem 0;
                }}
                
                .steps-title {{
                    color: #e6b220;
                    font-size: 1.2rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }}
                
                .steps-list {{
                    color: #fafaf5;
                    padding-left: 1.5rem;
                    margin: 0;
                }}
                
                .steps-list li {{
                    margin-bottom: 0.75rem;
                    font-size: 1rem;
                }}
                
                .footer-section {{
                    border-top: 2px solid rgba(2, 60, 113, 0.5);
                    padding-top: 2rem;
                    margin-top: 2rem;
                    text-align: center;
                }}
                
                .footer-title {{
                    color: #e6b220;
                    font-size: 1.8rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 0.75rem;
                }}
                
                .footer-message {{
                    color: rgba(250, 250, 245, 0.9);
                    font-size: 1.1rem;
                    line-height: 1.7;
                    margin: 0 auto;
                    max-width: 600px;
                }}
                
                .disclaimer {{
                    color: rgba(250, 250, 245, 0.6);
                    font-size: 0.9rem;
                    margin-top: 2rem;
                    padding-top: 1rem;
                    border-top: 1px solid rgba(230, 178, 32, 0.2);
                    margin-top: 30px;
                }}
                
                /* Icon styles */
                .icon-circle {{
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: rgba(230, 178, 32, 0.1);
                    flex-shrink: 0;
                }}
                
                @keyframes heartbeat {{
                    0%, 50%, 100% {{ transform: scale(1); }}
                    25%, 75% {{ transform: scale(1.1); }}
                }}
                
                /* Responsive Design */
                @media (max-width: 768px) {{
                    .email-container {{
                        padding: 1rem;
                    }}
                    
                    .section-title {{
                        font-size: 2rem;
                    }}
                    
                    .content-wrapper {{
                        padding: 1.5rem;
                    }}
                    
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .confirmation-title {{
                        font-size: 1.6rem;
                    }}
                    
                    .footer-title {{
                        font-size: 1.5rem;
                    }}
                }}
                
                @media (max-width: 480px) {{
                    .section-title {{
                        font-size: 1.8rem;
                    }}
                    
                    .content-wrapper {{
                        padding: 1.25rem;
                    }}
                    
                    .info-card {{
                        padding: 1.25rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="section-header">
                    <h1 class="section-title">NJROTC Program Signup</h1>
                    <p class="section-subtitle">Confirmation Receipt • {self.current_time}</p>
                </div>
                
                <div class="content-card">
                    <div class="card-overlay"></div>
                    <div class="content-wrapper">
                        <section class="confirmation-section">
                            <div class="confirmation-header">
                                <div class="confirmation-icon">
                                    <svg width="32" height="32" viewBox="0 0 24 24">
                                        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                                    </svg>
                                </div>
                                <h2 class="confirmation-title">Application Confirmed</h2>
                            </div>
                            
                            <div class="info-grid">
                                <div class="info-card">
                                    <div class="info-label">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                                        </svg>
                                        Full Name
                                    </div>
                                    <div class="info-value">{full_name}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-label">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82zM12 3L1 9l11 6 9-4.91V17h2V9L12 3z"/>
                                        </svg>
                                        Grade Level
                                    </div>
                                    <div class="info-value">Grade {grade}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-label">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                                        </svg>
                                        Student ID
                                    </div>
                                    <div class="info-value">{student_id}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-label">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                                        </svg>
                                        Submission Date
                                    </div>
                                    <div class="info-value">{self.current_time}</div>
                                </div>
                            </div>
                            
                            <div class="reason-section">
                                <h3 class="section-heading">
                                    <div class="icon-circle">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                                        </svg>
                                    </div>
                                    Your Reason for Joining
                                </h3>
                                <div class="reason-box">
                                    <p class="reason-text">"{reason}"</p>
                                </div>
                            </div>
                            
                            <div class="next-steps">
                                <h3 class="steps-title">
                                    <div class="icon-circle">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                                        </svg>
                                    </div>
                                    Next Steps
                                </h3>
                                <ul class="steps-list">
                                    <li>You will receive follow-up information within 3-5 business days</li>
                                    <li>Prepare necessary documentation (ID, physical forms, etc.)</li>
                                    <li>Attend the next scheduled orientation session</li>
                                    <li>Contact your instructor if you have immediate questions</li>
                                </ul>
                            </div>
                        </section>
                        
                        <section class="footer-section">
                            <h2 class="footer-title">
                                <div style="animation: heartbeat 2s infinite;">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                                    </svg>
                                </div>
                                Thank You
                            </h2>
                            <p class="footer-message">
                                We appreciate your interest in the NJROTC program. Your enthusiasm and commitment are what make our program strong. We look forward to welcoming you to our cadet family and helping you develop leadership skills, discipline, and character.
                            </p>
                        </section>
                        
                        <div class="disclaimer">
                            <p><strong>Parlier Unified School District NJROTC</strong></p>
                            <p>This is an automated confirmation message. Please do not reply directly to this email.</p>
                            <p>For inquiries, contact your NJROTC instructor directly.</p>
                        </div>
                    </div>
                </div>
            </div>
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
        <html>
        <head>
            <style>
                /* Fundraising Page Style */
                body {{
                    background: #000000;
                    color: #fafaf5;
                    position: relative;
                    z-index: 1;
                    overflow-x: hidden;
                    min-height: 100vh;
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                }}
                
                .email-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 2rem 1rem;
                }}
                
                .section-header {{
                    text-align: center;
                    margin-bottom: 3rem;
                }}
                
                .section-title {{
                    font-size: 2.5rem;
                    font-weight: 800;
                    margin-bottom: 1rem;
                    color: #fafaf5;
                    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                    position: relative;
                    display: inline-block;
                }}
                
                .section-title::after {{
                    content: "";
                    position: absolute;
                    bottom: -10px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 100px;
                    height: 4px;
                    background: #e6b220;
                    border-radius: 2px;
                }}
                
                .section-subtitle {{
                    font-size: 1.3rem;
                    color: rgba(250, 250, 245, 0.9);
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
                    z-index: 1;
                }}
                
                .content-wrapper {{
                    padding: 2.5rem;
                    position: relative;
                    z-index: 2;
                }}
                
                .suggestion-header {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 1rem;
                    margin-bottom: 2rem;
                }}
                
                .suggestion-icon {{
                    width: 60px;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: rgba(41, 128, 185, 0.2);
                    flex-shrink: 0;
                }}
                
                .suggestion-icon svg {{
                    fill: #2980b9;
                }}
                
                .suggestion-title {{
                    color: #2980b9;
                    font-size: 2rem;
                    font-weight: 700;
                    margin: 0;
                }}
                
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1rem;
                    margin: 2rem 0;
                }}
                
                .info-card {{
                    background: rgba(2, 60, 113, 0.2);
                    border: 1px solid rgba(2, 60, 113, 0.5);
                    border-radius: 12px;
                    padding: 1.5rem;
                    transition: all 0.3s ease;
                }}
                
                .info-card:hover {{
                    border-color: rgba(230, 178, 32, 0.6);
                    transform: translateY(-2px);
                }}
                
                .info-label {{
                    color: #e6b220;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 0.5rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }}
                
                .info-value {{
                    color: #fafaf5;
                    font-size: 1.2rem;
                    font-weight: 600;
                }}
                
                .suggestion-section {{
                    margin: 2rem 0;
                }}
                
                .section-heading {{
                    color: #e6b220;
                    font-size: 1.4rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }}
                
                .suggestion-box {{
                    background: rgba(2, 60, 113, 0.1);
                    border-left: 4px solid #e6b220;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-top: 1rem;
                }}
                
                .suggestion-text {{
                    color: #fafaf5;
                    font-size: 1.1rem;
                    line-height: 1.7;
                    margin: 0;
                }}
                
                .footer-section {{
                    border-top: 2px solid rgba(2, 60, 113, 0.5);
                    padding-top: 2rem;
                    margin-top: 2rem;
                    text-align: center;
                }}
                
                .footer-title {{
                    color: #e6b220;
                    font-size: 1.8rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 0.75rem;
                }}
                
                .footer-message {{
                    color: rgba(250, 250, 245, 0.9);
                    font-size: 1.1rem;
                    line-height: 1.7;
                    margin: 0 auto;
                    max-width: 600px;
                }}
                
                /* Icon styles */
                .icon-circle {{
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: rgba(230, 178, 32, 0.1);
                    flex-shrink: 0;
                }}
                
                @keyframes heartbeat {{
                    0%, 50%, 100% {{ transform: scale(1); }}
                    25%, 75% {{ transform: scale(1.1); }}
                }}
                
                /* Responsive Design */
                @media (max-width: 768px) {{
                    .email-container {{
                        padding: 1rem;
                    }}
                    
                    .section-title {{
                        font-size: 2rem;
                    }}
                    
                    .content-wrapper {{
                        padding: 1.5rem;
                    }}
                    
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .suggestion-title {{
                        font-size: 1.6rem;
                    }}
                    
                    .footer-title {{
                        font-size: 1.5rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="section-header">
                    <h1 class="section-title">New Suggestion</h1>
                    <p class="section-subtitle">NJROTC Program • {self.current_time}</p>
                </div>
                
                <div class="content-card">
                    <div class="card-overlay"></div>
                    <div class="content-wrapper">
                        <section class="suggestion-section">
                            <div class="suggestion-header">
                                <div class="suggestion-icon">
                                    <svg width="32" height="32" viewBox="0 0 24 24">
                                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                                    </svg>
                                </div>
                                <h2 class="suggestion-title">Suggestion Received</h2>
                            </div>
                            
                            <div class="info-grid">
                                <div class="info-card">
                                    <div class="info-label">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z"/>
                                        </svg>
                                        Received
                                    </div>
                                    <div class="info-value">{self.current_time}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-label">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                                        </svg>
                                        From
                                    </div>
                                    <div class="info-value">{self.user_last_name}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-label">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/>
                                        </svg>
                                        Type
                                    </div>
                                    <div class="info-value">{suggestion_type}</div>
                                </div>
                            </div>
                            
                            <div class="suggestion-section">
                                <h3 class="section-heading">
                                    <div class="icon-circle">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                                        </svg>
                                    </div>
                                    Suggestion Details
                                </h3>
                                <div class="suggestion-box">
                                    <p class="suggestion-text">"{suggestion_text}"</p>
                                </div>
                            </div>
                        </section>
                        
                        <section class="footer-section">
                            <h2 class="footer-title">
                                <div style="animation: heartbeat 2s infinite;">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                                    </svg>
                                </div>
                                Thank You for the Feedback
                            </h2>
                            <p class="footer-message">
                                Your input helps us improve the NJROTC program for all cadets. We value your perspective and will review this suggestion carefully as we work to enhance our program and better serve our cadet community.
                            </p>
                        </section>
                    </div>
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