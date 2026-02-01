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
        """Generate signup confirmation email with donation page styling"""
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
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NJROTC Signup Confirmation</title>
            <style>
                /* Donation Page Theme Styling */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: #000000;
                    color: #fafaf5;
                    position: relative;
                    overflow-x: hidden;
                    min-height: 100vh;
                    line-height: 1.6;
                }}
                
                body::before {{
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: 
                        radial-gradient(circle at 20% 50%, rgb(2 60 113 / 40%) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgb(2 60 113 / 40%) 0%, transparent 50%);
                    z-index: -1;
                }}
                
                .email-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 4rem 2rem;
                }}
                
                .section-header {{
                    text-align: center;
                    margin-bottom: 3rem;
                }}
                
                .section-title {{
                    font-size: 3rem;
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
                    opacity: 0.3;
                    z-index: 1;
                }}
                
                .content-wrapper {{
                    padding: 3rem;
                    position: relative;
                    z-index: 2;
                }}
                
                .info-section {{
                    margin-bottom: 2.5rem;
                }}
                
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                    margin-top: 1.5rem;
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
                    transform: translateY(-3px);
                }}
                
                .info-icon {{
                    width: 50px;
                    height: 50px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: rgba(230, 178, 32, 0.1);
                    margin-bottom: 1rem;
                }}
                
                .info-label {{
                    color: #e6b220;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 0.5rem;
                    font-weight: 600;
                }}
                
                .info-value {{
                    color: #fafaf5;
                    font-size: 1.2rem;
                    font-weight: 600;
                }}
                
                .reason-section {{
                    margin: 2.5rem 0;
                }}
                
                .reason-box {{
                    background: rgba(230, 178, 32, 0.1);
                    border: 1px solid rgba(230, 178, 32, 0.3);
                    border-radius: 12px;
                    padding: 2rem;
                    margin-top: 1rem;
                    position: relative;
                    overflow: hidden;
                }}
                
                .reason-box::before {{
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 6px;
                    height: 100%;
                    background: #e6b220;
                }}
                
                .reason-label {{
                    color: #e6b220;
                    font-size: 1.1rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .reason-text {{
                    color: #fafaf5;
                    font-size: 1.1rem;
                    line-height: 1.8;
                    font-style: italic;
                    quotes: "\\201C" "\\201D";
                }}
                
                .reason-text::before {{
                    content: open-quote;
                    color: #e6b220;
                    font-size: 2rem;
                    line-height: 0;
                    vertical-align: -0.4em;
                    margin-right: 5px;
                }}
                
                .reason-text::after {{
                    content: close-quote;
                    color: #e6b220;
                    font-size: 2rem;
                    line-height: 0;
                    vertical-align: -0.4em;
                    margin-left: 5px;
                }}
                
                .steps-section {{
                    margin: 2.5rem 0;
                }}
                
                .steps-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1.5rem;
                    margin-top: 1.5rem;
                }}
                
                .step-card {{
                    background: rgba(10, 10, 15, 0.6);
                    border: 1px solid rgba(2, 60, 113, 0.4);
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    position: relative;
                    transition: all 0.3s ease;
                }}
                
                .step-card:hover {{
                    border-color: rgba(230, 178, 32, 0.5);
                    background: rgba(10, 10, 15, 0.8);
                }}
                
                .step-number {{
                    width: 40px;
                    height: 40px;
                    background: #e6b220;
                    color: #000;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 800;
                    font-size: 1.2rem;
                    margin: 0 auto 1rem;
                }}
                
                .step-title {{
                    color: #e6b220;
                    font-size: 1.1rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                }}
                
                .step-desc {{
                    color: rgba(250, 250, 245, 0.9);
                    font-size: 0.95rem;
                    line-height: 1.5;
                }}
                
                .thanks-section {{
                    border-top: 2px solid rgba(2, 60, 113, 0.5);
                    padding-top: 2rem;
                    margin-top: 2.5rem;
                }}
                
                .thanks-header {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 1rem;
                    margin-bottom: 1.5rem;
                }}
                
                .thanks-title {{
                    color: #e6b220;
                    font-size: 2rem;
                    font-weight: 700;
                    margin: 0;
                }}
                
                .heart-icon {{
                    animation: heartbeat 2s infinite;
                }}
                
                @keyframes heartbeat {{
                    0%, 50%, 100% {{ transform: scale(1); }}
                    25%, 75% {{ transform: scale(1.1); }}
                }}
                
                .thanks-message {{
                    color: rgba(250, 250, 245, 0.9);
                    font-size: 1.1rem;
                    line-height: 1.7;
                    text-align: center;
                    margin: 0;
                }}
                
                .footer {{
                    text-align: center;
                    padding: 2rem 0 0;
                    margin-top: 2rem;
                    border-top: 1px solid rgba(230, 178, 32, 0.2);
                }}
                
                .footer p {{
                    color: rgba(250, 250, 245, 0.7);
                    font-size: 0.9rem;
                    margin: 0.5rem 0;
                }}
                
                .footer strong {{
                    color: #e6b220;
                }}
                
                /* Responsive Design */
                @media (max-width: 768px) {{
                    .email-container {{
                        padding: 3rem 1.5rem;
                    }}
                    
                    .section-title {{
                        font-size: 2.5rem;
                    }}
                    
                    .content-wrapper {{
                        padding: 2rem 1.5rem;
                    }}
                    
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .steps-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .thanks-title {{
                        font-size: 1.8rem;
                    }}
                }}
                
                @media (max-width: 480px) {{
                    .email-container {{
                        padding: 2rem 1rem;
                    }}
                    
                    .section-title {{
                        font-size: 2rem;
                    }}
                    
                    .section-subtitle {{
                        font-size: 1.1rem;
                    }}
                    
                    .content-wrapper {{
                        padding: 1.5rem 1.25rem;
                    }}
                    
                    .reason-text {{
                        font-size: 1rem;
                    }}
                    
                    .thanks-message {{
                        font-size: 1rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="section-header">
                    <h1 class="section-title">NJROTC Signup Confirmation</h1>
                    <p class="section-subtitle">Your Journey to Excellence Begins Here</p>
                </div>
                
                <div class="content-card">
                    <div class="card-overlay"></div>
                    <div class="content-wrapper">
                        <section class="info-section">
                            <div class="info-grid">
                                <div class="info-card">
                                    <div class="info-icon">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                                        </svg>
                                    </div>
                                    <div class="info-label">Student Name</div>
                                    <div class="info-value">{full_name}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-icon">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82zM12 3L1 9l11 6 9-4.91V17h2V9L12 3z"/>
                                        </svg>
                                    </div>
                                    <div class="info-label">Grade Level</div>
                                    <div class="info-value">Grade {grade}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-icon">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8l8 5 8-5v10zm-8-7L4 6h16l-8 5z"/>
                                        </svg>
                                    </div>
                                    <div class="info-label">Student ID</div>
                                    <div class="info-value">{student_id}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-icon">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                                        </svg>
                                    </div>
                                    <div class="info-label">Submission Date</div>
                                    <div class="info-value">{self.current_time}</div>
                                </div>
                            </div>
                        </section>
                        
                        <section class="reason-section">
                            <div class="reason-label">Your Reason for Joining</div>
                            <div class="reason-box">
                                <div class="reason-text">{reason}</div>
                            </div>
                        </section>
                        
                        <section class="steps-section">
                            <h3 style="color: #e6b220; font-size: 1.4rem; margin-bottom: 1rem; text-align: center;">What Happens Next</h3>
                            <div class="steps-grid">
                                <div class="step-card">
                                    <div class="step-number">1</div>
                                    <div class="step-title">Confirmation</div>
                                    <div class="step-desc">Your application is being processed by our team</div>
                                </div>
                                
                                <div class="step-card">
                                    <div class="step-number">2</div>
                                    <div class="step-title">Documentation</div>
                                    <div class="step-desc">Prepare required forms and identification</div>
                                </div>
                                
                                <div class="step-card">
                                    <div class="step-number">3</div>
                                    <div class="step-title">Orientation</div>
                                    <div class="step-desc">Attend the scheduled orientation session</div>
                                </div>
                                
                                <div class="step-card">
                                    <div class="step-number">4</div>
                                    <div class="step-title">Welcome</div>
                                    <div class="step-desc">Begin your NJROTC journey with us</div>
                                </div>
                            </div>
                        </section>
                        
                        <section class="thanks-section">
                            <div class="thanks-header">
                                <h2 class="thanks-title">Welcome Aboard</h2>
                                <div class="heart-icon">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                                    </svg>
                                </div>
                            </div>
                            <p class="thanks-message">We're excited to welcome you to the NJROTC family at Parlier High School. Your interest in leadership, discipline, and service aligns perfectly with our mission. We look forward to helping you develop the skills and character that will serve you throughout your life.</p>
                        </section>
                        
                        <div class="footer">
                            <p><strong>Parlier High School NJROTC</strong></p>
                            <p>603 3rd St, Parlier, CA 93648</p>
                            <p>This is an automated confirmation. For questions, contact your NJROTC instructor.</p>
                            <p style="color: rgba(230, 178, 32, 0.8); font-size: 0.85rem; margin-top: 1rem;">Semper Fortis - Always Courageous</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def generate_suggestion_email(self):
        """Generate suggestion notification email with donation page styling"""
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
                /* Donation Page Theme Styling */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: #000000;
                    color: #fafaf5;
                    position: relative;
                    overflow-x: hidden;
                    min-height: 100vh;
                    line-height: 1.6;
                }}
                
                body::before {{
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: 
                        radial-gradient(circle at 20% 50%, rgb(2 60 113 / 40%) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgb(2 60 113 / 40%) 0%, transparent 50%);
                    z-index: -1;
                }}
                
                .email-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 4rem 2rem;
                }}
                
                .section-header {{
                    text-align: center;
                    margin-bottom: 3rem;
                }}
                
                .section-title {{
                    font-size: 3rem;
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
                    opacity: 0.3;
                    z-index: 1;
                }}
                
                .content-wrapper {{
                    padding: 3rem;
                    position: relative;
                    z-index: 2;
                }}
                
                .info-section {{
                    margin-bottom: 2.5rem;
                }}
                
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                    margin-top: 1.5rem;
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
                    transform: translateY(-3px);
                }}
                
                .info-icon {{
                    width: 50px;
                    height: 50px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                    background: rgba(230, 178, 32, 0.1);
                    margin-bottom: 1rem;
                }}
                
                .info-label {{
                    color: #e6b220;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 0.5rem;
                    font-weight: 600;
                }}
                
                .info-value {{
                    color: #fafaf5;
                    font-size: 1.2rem;
                    font-weight: 600;
                }}
                
                .suggestion-section {{
                    margin: 2.5rem 0;
                }}
                
                .suggestion-box {{
                    background: rgba(230, 178, 32, 0.1);
                    border: 1px solid rgba(230, 178, 32, 0.3);
                    border-radius: 12px;
                    padding: 2rem;
                    margin-top: 1rem;
                    position: relative;
                    overflow: hidden;
                }}
                
                .suggestion-box::before {{
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 6px;
                    height: 100%;
                    background: #e6b220;
                }}
                
                .suggestion-label {{
                    color: #e6b220;
                    font-size: 1.1rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .suggestion-text {{
                    color: #fafaf5;
                    font-size: 1.1rem;
                    line-height: 1.8;
                    font-style: italic;
                }}
                
                .suggestion-text::before {{
                    content: "\\201C";
                    color: #e6b220;
                    font-size: 2rem;
                    line-height: 0;
                    vertical-align: -0.4em;
                    margin-right: 5px;
                }}
                
                .suggestion-text::after {{
                    content: "\\201D";
                    color: #e6b220;
                    font-size: 2rem;
                    line-height: 0;
                    vertical-align: -0.4em;
                    margin-left: 5px;
                }}
                
                .thanks-section {{
                    border-top: 2px solid rgba(2, 60, 113, 0.5);
                    padding-top: 2rem;
                    margin-top: 2.5rem;
                }}
                
                .thanks-header {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 1rem;
                    margin-bottom: 1.5rem;
                }}
                
                .thanks-title {{
                    color: #e6b220;
                    font-size: 2rem;
                    font-weight: 700;
                    margin: 0;
                }}
                
                .heart-icon {{
                    animation: heartbeat 2s infinite;
                }}
                
                @keyframes heartbeat {{
                    0%, 50%, 100% {{ transform: scale(1); }}
                    25%, 75% {{ transform: scale(1.1); }}
                }}
                
                .thanks-message {{
                    color: rgba(250, 250, 245, 0.9);
                    font-size: 1.1rem;
                    line-height: 1.7;
                    text-align: center;
                    margin: 0;
                }}
                
                .footer {{
                    text-align: center;
                    padding: 2rem 0 0;
                    margin-top: 2rem;
                    border-top: 1px solid rgba(230, 178, 32, 0.2);
                }}
                
                .footer p {{
                    color: rgba(250, 250, 245, 0.7);
                    font-size: 0.9rem;
                    margin: 0.5rem 0;
                }}
                
                .footer strong {{
                    color: #e6b220;
                }}
                
                /* Responsive Design */
                @media (max-width: 768px) {{
                    .email-container {{
                        padding: 3rem 1.5rem;
                    }}
                    
                    .section-title {{
                        font-size: 2.5rem;
                    }}
                    
                    .content-wrapper {{
                        padding: 2rem 1.5rem;
                    }}
                    
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .thanks-title {{
                        font-size: 1.8rem;
                    }}
                }}
                
                @media (max-width: 480px) {{
                    .email-container {{
                        padding: 2rem 1rem;
                    }}
                    
                    .section-title {{
                        font-size: 2rem;
                    }}
                    
                    .section-subtitle {{
                        font-size: 1.1rem;
                    }}
                    
                    .content-wrapper {{
                        padding: 1.5rem 1.25rem;
                    }}
                    
                    .suggestion-text {{
                        font-size: 1rem;
                    }}
                    
                    .thanks-message {{
                        font-size: 1rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="section-header">
                    <h1 class="section-title">New Suggestion Received</h1>
                    <p class="section-subtitle">Your Feedback Helps Us Improve</p>
                </div>
                
                <div class="content-card">
                    <div class="card-overlay"></div>
                    <div class="content-wrapper">
                        <section class="info-section">
                            <div class="info-grid">
                                <div class="info-card">
                                    <div class="info-icon">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                                        </svg>
                                    </div>
                                    <div class="info-label">Submitted By</div>
                                    <div class="info-value">{self.user_last_name}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-icon">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
                                        </svg>
                                    </div>
                                    <div class="info-label">Suggestion Type</div>
                                    <div class="info-value">{suggestion_type}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-icon">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                                        </svg>
                                    </div>
                                    <div class="info-label">Submission Date</div>
                                    <div class="info-value">{self.current_time}</div>
                                </div>
                                
                                <div class="info-card">
                                    <div class="info-icon">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                                        </svg>
                                    </div>
                                    <div class="info-label">Status</div>
                                    <div class="info-value">Under Review</div>
                                </div>
                            </div>
                        </section>
                        
                        <section class="suggestion-section">
                            <div class="suggestion-label">Suggestion Details</div>
                            <div class="suggestion-box">
                                <div class="suggestion-text">{suggestion_text}</div>
                            </div>
                        </section>
                        
                        <section class="thanks-section">
                            <div class="thanks-header">
                                <h2 class="thanks-title">Thank You</h2>
                                <div class="heart-icon">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="#e6b220">
                                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                                    </svg>
                                </div>
                            </div>
                            <p class="thanks-message">We sincerely appreciate you taking the time to share your thoughts with us. Your feedback is valuable in helping us improve the NJROTC program and better serve our cadets. We will review your suggestion carefully and consider how we can implement improvements based on your input.</p>
                        </section>
                        
                        <div class="footer">
                            <p><strong>Parlier High School NJROTC</strong></p>
                            <p>603 3rd St, Parlier, CA 93648</p>
                            <p>This is an automated notification. The suggestion has been logged for review.</p>
                            <p style="color: rgba(230, 178, 32, 0.8); font-size: 0.85rem; margin-top: 1rem;">Feedback drives excellence - Thank you for contributing!</p>
                        </div>
                    </div>
                </div>
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