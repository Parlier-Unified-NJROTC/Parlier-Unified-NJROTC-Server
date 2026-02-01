from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import subprocess
import threading
import sys
from datetime import datetime

# Add workers directory to path
sys.path.append('workers')

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
    
    def run_email_bot(last_name, rank, selected_items, recipient_email):
        """Run email bot directly in thread"""
        try:
            print(f"=== STARTING EMAIL BOT ===")
            print(f"Recipient: {recipient_email}")
            print(f"Name: {last_name}")
            print(f"Rank: {rank}")
            print(f"Items: {selected_items}")
            
            # Import and run email bot directly
            from workers.gmail_bot import EmailBot
            
            bot = EmailBot(last_name, rank, selected_items, recipient_email)
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
            rank = data.get('rank', 'Cadet')  # Default to 'Cadet' if not specified
            
            # Prepare selected items for email
            selected_items = [f"NJROTC Program Signup - Grade {data['grade']}"]
            
            # Start email in background thread
            email_thread = threading.Thread(
                target=run_email_bot,
                args=(last_name, rank, selected_items, data['email'])
            )
            email_thread.daemon = True
            email_thread.start()
            
            print(f"Email thread started for: {data['email']}")
            
            # Also send to admin if configured
            admin_email = os.getenv('ADMIN_EMAIL')
            if admin_email and admin_email != data['email']:
                admin_thread = threading.Thread(
                    target=run_email_bot,
                    args=(last_name, rank, [f"New Signup: {data['fullName']}"], admin_email)
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
            selected_items = [f"Suggestion Type: {data['suggestionType']}", data['suggestionText'][:100] + "..."]
            
            # Get admin email from environment or use default
            admin_email = os.getenv('ADMIN_EMAIL', 'instructor@example.com')
            
            # Trigger email to admin
            email_thread = threading.Thread(
                target=run_email_bot,
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
    
    @app.route('/test-email', methods=['GET'])
    def test_email():
        """Test endpoint to verify email sending"""
        test_email = request.args.get('email', 'saulSanchez.out@gmail.com')
        
        try:
            # Run email test directly
            from workers.gmail_bot import EmailBot
            
            bot = EmailBot(
                last_name="Test",
                rank="Cadet",
                selected_items=["Test Email from Render"],
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