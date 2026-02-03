from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import threading
import sys
import time
from datetime import datetime
from collections import deque
from queue import Queue, Empty
from threading import Lock

sys.path.append('workers')

class SimpleRateLimiter:
    """Simple rate limiter without external dependencies"""
    
    def __init__(self):
        self.requests = {}
        self.lock = Lock()
    
    def check_limit(self, ip, limit=100, window=3600):
        """Check if IP has exceeded rate limit"""
        with self.lock:
            current_time = time.time()
            
            self._clean_old_entries(current_time, window)
            
            if ip not in self.requests:
                self.requests[ip] = []
            
            window_start = current_time - window
            request_count = sum(1 for ts in self.requests[ip] if ts > window_start)
            
            if request_count >= limit:
                return False
            
            self.requests[ip].append(current_time)
            return True
    
    def _clean_old_entries(self, current_time, window):
        """Remove old entries to prevent memory leaks"""
        cutoff = current_time - (window * 2) 
        for ip in list(self.requests.keys()):
            self.requests[ip] = [ts for ts in self.requests[ip] if ts > cutoff]
            if not self.requests[ip]:
                del self.requests[ip]

class RequestQueue:
    """Thread-safe request queue"""
    def __init__(self, max_queue_size=100, max_workers=5):
        self.queue = Queue(maxsize=max_queue_size)
        self.max_workers = max_workers
        self.active_workers = 0
        self.lock = Lock()
        self.request_timestamps = {}
        self.start_workers()
    
    def start_workers(self):
        """Start worker threads to process the queue"""
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._process_queue, daemon=True)
            worker.start()
    
    def add_request(self, endpoint, data, ip_address):
        """Add request to queue with timestamp tracking"""
        current_time = time.time()
        
        if self._check_rate_limit(ip_address, current_time):
            return False, "Rate limit exceeded"
        
        try:
            self.queue.put_nowait({
                'endpoint': endpoint,
                'data': data,
                'ip': ip_address,
                'timestamp': current_time
            })
            
            if ip_address not in self.request_timestamps:
                self.request_timestamps[ip_address] = deque(maxlen=100)
            self.request_timestamps[ip_address].append(current_time)
            
            return True, "Request queued"
        except:
            return False, "Queue full"
    
    def _check_rate_limit(self, ip_address, current_time, window_seconds=60, max_requests=30):
        """Check if IP has exceeded rate limit"""
        if ip_address not in self.request_timestamps:
            return False
        
        window_start = current_time - window_seconds
        request_count = sum(1 for ts in self.request_timestamps[ip_address] 
                          if ts > window_start)
        
        return request_count >= max_requests
    
    def _clean_old_timestamps(self, current_time, max_age=300):
        """Clean old timestamps"""
        cutoff = current_time - max_age
        for ip in list(self.request_timestamps.keys()):
            self.request_timestamps[ip] = deque(
                [ts for ts in self.request_timestamps[ip] if ts > cutoff],
                maxlen=100
            )
            if not self.request_timestamps[ip]:
                del self.request_timestamps[ip]
    
    def _process_queue(self):
        """Worker thread to process queued requests"""
        while True:
            try:
                task = self.queue.get(timeout=1)
                time.sleep(0.05)
                self.queue.task_done()
            except Empty:
                continue

def create_app():
    app = Flask(__name__)

    app.config.update(
        MAX_CONTENT_LENGTH=1024 * 1024, 
        JSON_SORT_KEYS=False
    )

    rate_limiter = SimpleRateLimiter()
    request_queue = RequestQueue(max_queue_size=200, max_workers=10)

    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://parlier-unified-njrotc.github.io').split(',')
    CORS(app, 
         origins=allowed_origins, 
         supports_credentials=True,
         methods=['GET', 'POST', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])

    @app.before_request
    def before_request():
        """Security checks before processing any request"""
        if request.method == 'OPTIONS':
            return

        ip = request.remote_addr
        if not rate_limiter.check_limit(ip, limit=200, window=86400):  # 200/day
            return jsonify({
                "error": "Daily rate limit exceeded"
            }), 429
        
        if request.path.startswith('/api/'):
            if not rate_limiter.check_limit(ip, limit=50, window=3600):  # 50/hour
                return jsonify({
                    "error": "Hourly rate limit exceeded"
                }), 429

        if request.method == 'POST':
            if not request.is_json:
                return jsonify({
                    "error": "Content-Type must be application/json"
                }), 400
    
    @app.after_request
    def after_request(response):
        """Add security headers"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "njrotc-backend",
            "email_enabled": bool(os.getenv('GMAIL_TOKEN_JSON')),
            "queue_size": request_queue.queue.qsize()
        })
    
    def validate_signup_data(data):
        """Validate signup form data"""
        required_fields = ['fullName', 'schoolId', 'grade', 'email', 'reason']
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        if '@' not in data['email'] or '.' not in data['email']:
            return False, "Invalid email format"
        
        try:
            grade = int(data['grade'])
            if grade < 9 or grade > 12:
                return False, "Grade must be between 9 and 12"
        except:
            return False, "Invalid grade format"

        if len(data['reason']) > 1000:
            return False, "Reason is too long (max 1000 characters)"
        
        return True, "Valid"
    
    def run_email_bot(last_name, selected_items, recipient_email, extra_data=None):
        """Run email bot using Gmail API - sends BOTH templates to user"""
        try:
            print(f"=== STARTING EMAIL BOT (USER - BOTH TEMPLATES) ===")
            print(f"Recipient: {recipient_email}")
            
            from workers.gmail_bot import GmailAPIBot
            
            bot = GmailAPIBot(last_name, "", selected_items, recipient_email)
            
            # Ensure it has both templates (should already be set in __init__)
            if extra_data:
                bot.extra_data = extra_data
            
            success = bot.send_email()
            
            if success:
                print(f"✓ Email with both templates sent successfully to {recipient_email}")
            else:
                print(f"✗ Failed to send email to {recipient_email}")
                
            print(f"=== EMAIL BOT COMPLETE ===")
            
        except Exception as e:
            print(f"ERROR in email bot: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def run_admin_email_only(last_name, selected_items, recipient_email, extra_data=None):
        """Run email bot for admin only (sends only admin copy)"""
        try:
            print(f"=== STARTING ADMIN-ONLY EMAIL BOT ===")
            print(f"Admin Recipient: {recipient_email}")
            
            from workers.gmail_bot import GmailAPIBot
            
            # Create bot but we'll modify it to send only admin copy
            bot = GmailAPIBot(last_name, "", selected_items, recipient_email)
            
            # Override the email_templates to only include admin template
            bot.email_templates = [{
                "subject": "NJROTC Program Signup Confirmation (Admin Copy)",
                "body_html": bot.generate_admin_signup_notification(),
                "is_admin": True
            }]
            
            if extra_data:
                bot.extra_data = extra_data
            
            success = bot.send_email()
            
            if success:
                print(f"✓ Admin-only email sent successfully to {recipient_email}")
            else:
                print(f"✗ Failed to send admin-only email to {recipient_email}")
                
            print(f"=== ADMIN-ONLY EMAIL BOT COMPLETE ===")
            
        except Exception as e:
            print(f"ERROR in admin-only email bot: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @app.route('/api/signup', methods=['POST', 'OPTIONS'])
    def handle_signup():
        if request.method == 'OPTIONS':
            return '', 200
        
        ip_address = request.remote_addr
        
        try:
            data = request.json
            
            is_valid, message = validate_signup_data(data)
            if not is_valid:
                return jsonify({"error": message}), 400
            
            if not rate_limiter.check_limit(ip_address, limit=10, window=3600):
                return jsonify({
                    "error": "Too many signup requests. Please try again later."
                }), 429
            
            queued, queue_message = request_queue.add_request(
                '/api/signup', 
                data, 
                ip_address
            )
            
            if not queued:
                return jsonify({
                    "error": "System busy. Please try again later.",
                    "details": queue_message
                }), 429
            
            # Extract last name from full name
            full_name_parts = data['fullName'].strip().split()
            last_name = full_name_parts[-1] if full_name_parts else "Student"
            
            # Create selected_items with student info for USER
            user_selected_items = [
                f"Student: {data['fullName']}",
                f"Grade: {data['grade']}",
                f"Student ID: {data['schoolId']}",
                f"Reason for joining: {data['reason']}",
                f"Email: {data['email']}",
                f"IP Address: {ip_address}",
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"NOTE: Student signup - sending both user and admin copies"
            ]
            
            # Create selected_items for ADMIN (actual teacher/admin)
            admin_selected_items = [
                f"Student: {data['fullName']}",
                f"Grade: {data['grade']}",
                f"Student ID: {data['schoolId']}",
                f"Reason for joining: {data['reason']}",
                f"Email: {data['email']}",
                f"IP Address: {ip_address}",
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"NOTE: New student signup notification for admin"
            ]
            
            extra_data = {
                'full_name': data['fullName'],
                'school_id': data['schoolId'],
                'grade': data['grade'],
                'email': data['email'],
                'reason': data['reason'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'ip_address': ip_address
            }
            
            # Send email to USER - they will get BOTH user confirmation AND admin copy
            user_email_thread = threading.Thread(
                target=run_email_bot,
                args=(last_name, user_selected_items, data['email'], extra_data)
            )
            user_email_thread.daemon = True
            user_email_thread.start()
            
            print(f"✓ User email with BOTH templates queued for: {data['email']}")
            
            # Send separate email to ACTUAL ADMIN/TEACHER (only admin copy)
            admin_email = os.getenv('ADMIN_EMAIL')
            if admin_email and admin_email.strip():
                # For actual admin, send only admin copy
                admin_email_thread = threading.Thread(
                    target=run_admin_email_only,
                    args=(last_name, admin_selected_items, admin_email, extra_data)
                )
                admin_email_thread.daemon = True
                admin_email_thread.start()
                print(f"✓ Admin notification email queued for actual admin: {admin_email}")
            
            return jsonify({
                "success": True,
                "message": "Signup received successfully",
                "email_triggered": True,
                "queue_position": request_queue.queue.qsize(),
                "data": {
                    "name": data['fullName'],
                    "email": data['email'],
                    "timestamp": datetime.now().isoformat()
                }
            }), 200
            
        except Exception as e:
            print(f"Error processing signup from {ip_address}: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "details": "Please try again later"
            }), 500
    
    @app.route('/api/suggestion', methods=['POST', 'OPTIONS'])
    def handle_suggestion():
        if request.method == 'OPTIONS':
            return '', 200
        
        ip_address = request.remote_addr
        
        try:
            data = request.json
            
            required_fields = ['fullName', 'suggestionType', 'suggestionText']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        "error": f"Missing required field: {field}"
                    }), 400
            
            if not rate_limiter.check_limit(ip_address, limit=400, window=600):
                return jsonify({
                    "error": "Too many suggestion requests. Please try again later."
                }), 429
            
            if len(data['suggestionText']) > 2000:
                return jsonify({
                    "error": "Suggestion text too long (max 2000 characters)"
                }), 400
            
            queued, queue_message = request_queue.add_request(
                '/api/suggestion', 
                data, 
                ip_address
            )
            
            if not queued:
                return jsonify({
                    "error": "System busy. Please try again later.",
                    "details": queue_message
                }), 429
            
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
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'ip_address': ip_address
            }
            
            admin_email = os.getenv('ADMIN_EMAIL')
            
            if admin_email and admin_email.strip():
                email_thread = threading.Thread(
                    target=run_email_bot,
                    args=(last_name, selected_items, admin_email, extra_data)
                )
                email_thread.daemon = True
                email_thread.start()
                print(f"✓ Suggestion email queued for admin: {admin_email}")
            
            return jsonify({
                "success": True,
                "message": "Suggestion submitted successfully",
                "email_triggered": True,
                "queue_position": request_queue.queue.qsize(),
                "data": {
                    "name": data['fullName'],
                    "type": data['suggestionType'],
                    "timestamp": datetime.now().isoformat()
                }
            }), 200
            
        except Exception as e:
            print(f"Error processing suggestion from {ip_address}: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "details": "Please try again later"
            }), 500
    
    @app.route('/api/queue-status', methods=['GET'])
    def queue_status():
        """Endpoint to check queue status (for monitoring)"""
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return jsonify({"error": "Unauthorized"}), 401
        
        return jsonify({
            "queue_size": request_queue.queue.qsize(),
            "max_queue_size": request_queue.queue.maxsize,
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/test-email', methods=['GET'])
    def test_email():
        """Test endpoint to verify email sending"""
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return jsonify({"error": "Unauthorized"}), 401
        
        test_email = request.args.get('email', 'saulSanchez.out@gmail.com')

        if '@' not in test_email or '.' not in test_email:
            return jsonify({
                "success": False,
                "error": "Invalid email format"
            }), 400
        
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