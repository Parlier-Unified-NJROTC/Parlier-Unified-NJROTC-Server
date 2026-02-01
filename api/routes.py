from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import threading
import sys
from datetime import datetime

sys.path.append('workers')

def create_app():
    app = Flask(__name__)
    
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://parlier-unified-njrotc.github.io').split(',')
    CORS(app, origins=allowed_origins, supports_credentials=True)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "njrotc-backend",
            "email_enabled": bool(os.getenv('GMAIL_TOKEN_JSON'))
        })
    
    def run_email_bot(last_name, selected_items, recipient_email, extra_data=None):
        """Run email bot using Gmail API"""
        try:
            print(f"=== STARTING EMAIL BOT ===")
            print(f"Recipient: {recipient_email}")
            
            from workers.gmail_bot import GmailAPIBot
            
            bot = GmailAPIBot(last_name, "", selected_items, recipient_email)
            
            if extra_data:
                bot.extra_data = extra_data
            
            success = bot.send_email()
            
            if success:
                print(f"✓ Email sent successfully to {recipient_email}")
            else:
                print(f"✗ Failed to send email to {recipient_email}")
                
            print(f"=== EMAIL BOT COMPLETE ===")
            
        except Exception as e:
            print(f"ERROR in email bot: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @app.route('/api/signup', methods=['POST', 'OPTIONS'])
    def handle_signup():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            data = request.json
            print(f"Received signup data: {data}")
            
            required_fields = ['fullName', 'schoolId', 'grade', 'email', 'reason']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        "error": f"Missing required field: {field}"
                    }), 400
            
            full_name_parts = data['fullName'].strip().split()
            last_name = full_name_parts[-1] if full_name_parts else "Student"
            
            selected_items = [
                f"NJROTC Program Signup",
                f"Grade: {data['grade']}",
                f"Student ID: {data['schoolId']}",
                f"Reason for joining: {data['reason'][:200]}..."
            ]
            
            extra_data = {
                'full_name': data['fullName'],
                'school_id': data['schoolId'],
                'grade': data['grade'],
                'email': data['email'],
                'reason': data['reason'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Start email to student in background thread
            student_thread = threading.Thread(
                target=run_email_bot,
                args=(last_name, selected_items, data['email'], extra_data)
            )
            student_thread.daemon = True
            student_thread.start()
            
            print(f"Student confirmation email thread started for: {data['email']}")
            
            admin_email = os.getenv('ADMIN_EMAIL')
            if admin_email and admin_email != data['email']:
                admin_items = [
                    f"NEW SIGNUP RECEIVED",
                    f"Student: {data['fullName']}",
                    f"Grade: {data['grade']}",
                    f"Student ID: {data['schoolId']}",
                    f"Email: {data['email']}",
                    f"Reason: {data['reason'][:150]}..."
                ]
                
                admin_thread = threading.Thread(
                    target=run_email_bot,
                    args=(last_name, admin_items, admin_email, extra_data)
                )
                admin_thread.daemon = True
                admin_thread.start()
                print(f"Admin notification email triggered to: {admin_email}")
            
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
            
            required_fields = ['fullName', 'suggestionType', 'suggestionText']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        "error": f"Missing required field: {field}"
                    }), 400
            
            full_name_parts = data['fullName'].strip().split()
            last_name = full_name_parts[-1] if full_name_parts else "User"
            
            selected_items = [
                f"Suggestion Type: {data['suggestionType']}",
                f"Suggestion: {data['suggestionText'][:500]}..."
            ]
            
            extra_data = {
                'full_name': data['fullName'],
                'suggestion_type': data['suggestionType'],
                'suggestion_text': data['suggestionText'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            admin_email = os.getenv('ADMIN_EMAIL')
            
            email_thread = threading.Thread(
                target=run_email_bot,
                args=(last_name, selected_items, admin_email, extra_data)
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
        
    # don't use this in production
    @app.route('/test-email', methods=['GET'])
    def test_email():
        """Test endpoint to verify email sending"""
        test_email = request.args.get('email', 'saulSanchez.out@gmail.com')
        
        try:
            from workers.gmail_bot import GmailAPIBot
            
            bot = GmailAPIBot(
                last_name="Test",
                rank="",
                selected_items=["Test Email from NJROTC Website"],
                recipient_email=test_email
            )
            
            success = bot.send_email()
            
            return jsonify({
                "success": success,
                "message": "Test email sent" if success else "Failed to send test email",
                "recipient": test_email
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return app