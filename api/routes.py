from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

# Add workers directory to path
import sys
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
    
    def send_signup_email(data):
        """Send signup confirmation email"""
        try:
            from workers.gmail_bot import EmailBot
            
            # Extract last name from full name
            full_name_parts = data['fullName'].strip().split()
            last_name = full_name_parts[-1] if full_name_parts else "User"
            
            # Get rank (optional)
            rank = data.get('rank', 'Cadet')
            
            # Prepare selected items for email
            selected_items = [f"NJROTC Program Signup - Grade {data['grade']}"]
            
            # Send to user
            user_bot = EmailBot(last_name, rank, selected_items, data['email'])
            user_success = user_bot.send_email()
            
            # Send to admin if configured
            admin_email = os.getenv('ADMIN_EMAIL')
            admin_success = True
            
            if admin_email and admin_email != data['email']:
                admin_items = [f"New Signup: {data['fullName']} (Grade {data['grade']})"]
                admin_bot = EmailBot(last_name, rank, admin_items, admin_email)
                admin_success = admin_bot.send_email()
            
            return user_success and admin_success
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
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
            
            # Send email synchronously
            email_sent = send_signup_email(data)
            
            if email_sent:
                email_status = "Email sent successfully"
            else:
                email_status = "Email sending failed (but signup was recorded)"
            
            return jsonify({
                "success": True,
                "message": "Signup received successfully",
                "email_sent": email_sent,
                "email_status": email_status,
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
            selected_items = [
                f"Suggestion Type: {data['suggestionType']}",
                f"Details: {data['suggestionText'][:200]}..."
            ]
            
            # Get admin email from environment
            admin_email = os.getenv('ADMIN_EMAIL', 'instructor@example.com')
            
            # Send email synchronously
            try:
                from workers.gmail_bot import EmailBot
                bot = EmailBot(last_name, "", selected_items, admin_email)
                email_sent = bot.send_email()
            except Exception as e:
                print(f"Error sending suggestion email: {str(e)}")
                email_sent = False
            
            return jsonify({
                "success": True,
                "message": "Suggestion submitted successfully",
                "email_sent": email_sent,
                "email_status": "Email sent to admin" if email_sent else "Email failed",
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
            from workers.gmail_bot import EmailBot
            
            bot = EmailBot(
                last_name="Test",
                rank="Cadet",
                selected_items=["Test Email from Render Backend"],
                recipient_email=test_email
            )
            
            success = bot.send_email()
            
            return jsonify({
                "success": success,
                "message": "Test email sent" if success else "Failed to send test email",
                "recipient": test_email,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    return app