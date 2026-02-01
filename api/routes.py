from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import subprocess
from datetime import datetime

def create_app():
    app = Flask(__name__)
    
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://parlier-unified-njrotc.github.io').split(',')
    CORS(app, origins=allowed_origins, supports_credentials=True)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "njrotc-backend"
        })
    
    @app.route('/api/signup', methods=['POST', 'OPTIONS'])
    def handle_signup():
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            data = request.json
            print(f"Received signup data: {data}")
            
            required_fields = ['fullName', 'schoolId', 'grade', 'email']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        "error": f"Missing required field: {field}"
                    }), 400
            
            full_name_parts = data['fullName'].strip().split()
            last_name = full_name_parts[-1] if full_name_parts else "User"
            
            rank = ""
            
            selected_items = ["Signup Confirmation"]
            
            # Prepare email data
            email_data = {
                "last_name": last_name,
                "rank": rank,
                "selected_items": selected_items,
                "recipient_email": data['email'],
                "user_data": data
            }
            
            
            try:
                 subprocess.Popen([
                     'python', '-m', 'workers.gmail_bot',
                     last_name,
                     rank,
                     json.dumps(selected_items),
                     data['email']
                 ])
            except Exception as e:
                print(f"Error triggering email: {e}")
            
            return jsonify({
                "success": True,
                "message": "Signup received successfully",
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
            
            required_fields = ['fullName', 'schoolId', 'grade', 'suggestionType', 'suggestionText']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        "error": f"Missing required field: {field}"
                    }), 400
            
            # Process suggestion
            print(f"Suggestion from {data['fullName']}: {data['suggestionText']}")
            
            subprocess.Popen([
                 'python', '-m', 'workers.gmail_bot',
                 data['fullName'].split()[-1],
                 "",
                 json.dumps([f"Suggestion: {data['suggestionType']}"]),
                 "instructor@example.com"  # Change to actual instructor email
             ])
            
            return jsonify({
                "success": True,
                "message": "Suggestion submitted successfully",
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