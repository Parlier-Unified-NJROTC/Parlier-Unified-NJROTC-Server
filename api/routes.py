from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import subprocess
import threading
from datetime import datetime

def create_app():
    app = Flask(__name__)
    
    # Configure CORS for your GitHub Pages domain
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://parlier-unified-njrotc.github.io').split(',')
    CORS(app, origins=allowed_origins, supports_credentials=True)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "njrotc-backend",
            "email_enabled": bool(os.getenv('PYTHON_EMAIL_CURSE'))
        })
    
    def trigger_email_bot(last_name, rank, selected_items, recipient_email):
        """Background function to trigger email bot"""
        try:
            # Build command to run your email bot
            cmd = [
                'python', '-c',
                f'''
import sys
sys.path.append(".")
from workers.gmail_bot import EmailBot
bot = EmailBot("{last_name}", "{rank}", {json.dumps(selected_items)}, "{recipient_email}")
success = bot.send_email()
print("Email send result:", success)
                '''
            ]
            
            # Run in background thread
            print(f"Attempting to send email to: {recipient_email}")
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Email process started in background")
            
        except Exception as e:
            print(f"Error triggering email bot: {str(e)}")
    
    @app.route('/api/signup', methods=['POST', 'OPTIONS'])
    def handle_signup():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            data = request.json
            print(f"Received signup data: {data}")
            
            # Validate required fields
            required_fields = ['fullName', 'schoolId', 'grade', 'email']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Extract last name from full name
            full_name_parts = data['fullName'].strip().split()
            last_name = full_name_parts[-1] if full_name_parts else "User"
            
            # Get rank (optional)
            rank = data.get('rank', '')
            
            # Prepare selected items for email
            selected_items = ["NJROTC Program Signup Confirmation"]
            
            # Trigger email in background thread
            email_thread = threading.Thread(
                target=trigger_email_bot,
                args=(last_name, rank, selected_items, data['email'])
            )
            email_thread.daemon = True
            email_thread.start()
            
            print(f"Email thread started for: {data['email']}")
            
            return jsonify({
                "success": True,
                "message": "Signup received successfully",
                "email_triggered": True,
                "data": {
                    "name": data['fullName'],
                    "email": data['email'],
                    "timestamp": datetime.now().isoformat()
                }
            }), 200
            
        except Exception as e:
            print(f"Error processing signup: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "details": str(e)
            }), 500
    
    @app.route('/api/suggestion', methods=['POST', 'OPTIONS'])
    def handle_suggestion():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            data = request.json
            print(f"Received suggestion data: {data}")
            
            # Validate required fields
            required_fields = ['fullName', 'suggestionType', 'suggestionText']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Extract last name
            full_name_parts = data['fullName'].strip().split()
            last_name = full_name_parts[-1] if full_name_parts else "User"
            
            # Prepare email data
            selected_items = [f"Suggestion: {data['suggestionType']}"]
            
            # Get admin email from environment or use default
            admin_email = os.getenv('ADMIN_EMAIL', 'instructor@example.com')
            
            # Trigger email to admin
            email_thread = threading.Thread(
                target=trigger_email_bot,
                args=(last_name, "", selected_items, admin_email)
            )
            email_thread.daemon = True
            email_thread.start()
            
            print(f"Suggestion notification email triggered to: {admin_email}")
            
            return jsonify({
                "success": True,
                "message": "Suggestion submitted successfully",
                "email_triggered": True,
                "data": {
                    "name": data['fullName'],
                    "type": data['suggestionType'],
                    "timestamp": datetime.now().isoformat()
                }
            }), 200
            
        except Exception as e:
            print(f"Error processing suggestion: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "details": str(e)
            }), 500
    
    return app