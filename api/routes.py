from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import json
import threading
import sys
import time
import hashlib
from datetime import datetime, timedelta
from collections import deque
from queue import Queue, Empty
from threading import Lock
import redis  # Optional for distributed rate limiting

sys.path.append('workers')

class RequestQueue:
    """Thread-safe request queue with rate limiting"""
    def __init__(self, max_queue_size=100, max_workers=5, processing_delay=0.1):
        self.queue = Queue(maxsize=max_queue_size)
        self.max_workers = max_workers
        self.processing_delay = processing_delay
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
        
        self._clean_old_timestamps(current_time)
        
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
        """Clean old timestamps to prevent memory leak"""
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
                time.sleep(self.processing_delay)
                self.queue.task_done()
            except Empty:
                continue

class SecurityMiddleware:
    """Security middleware for additional protection"""
    
    def __init__(self, app):
        self.app = app
        self.suspicious_ips = {}
        self.blocked_ips = set()
        self.request_counts = {}
        self.lock = Lock()
    
    def check_request(self, ip, path):
        """Check if request should be blocked"""
        current_time = time.time()
        
        if ip in self.blocked_ips:
            return False, "IP blocked"
        
        if self._is_suspicious(ip, path, current_time):
            return False, "Suspicious activity detected"
        
        return True, "OK"
    
    def _is_suspicious(self, ip, path, current_time):
        """Detect suspicious request patterns"""
        with self.lock:
            if ip not in self.request_counts:
                self.request_counts[ip] = {'count': 0, 'last_reset': current_time}
            
            if current_time - self.request_counts[ip]['last_reset'] > 60:
                self.request_counts[ip] = {'count': 0, 'last_reset': current_time}
            
            self.request_counts[ip]['count'] += 1
            
            if self.request_counts[ip]['count'] > 100:
                self.blocked_ips.add(ip)
                return True
            
            if ip not in self.suspicious_ips:
                self.suspicious_ips[ip] = deque(maxlen=10)
            
            self.suspicious_ips[ip].append(current_time)
            
            if len(self.suspicious_ips[ip]) == 10:
                time_diff = self.suspicious_ips[ip][-1] - self.suspicious_ips[ip][0]
                if time_diff < 2: 
                    self.blocked_ips.add(ip)
                    return True
        
        return False

def create_app():
    app = Flask(__name__)
    
    app.config.update(
        MAX_CONTENT_LENGTH=1024 * 1024,
        JSON_SORT_KEYS=False,
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)
    )
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    request_queue = RequestQueue(
        max_queue_size=200,
        max_workers=10,
        processing_delay=0.05
    )
    
    security_middleware = SecurityMiddleware(app)
    
    allowed_origins = os.getenv('ALLOWED_ORIGINS').split(',')
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
        
        ip = get_remote_address()
        path = request.path
        
        allowed, reason = security_middleware.check_request(ip, path)
        if not allowed:
            return jsonify({
                "error": "Access denied",
                "reason": reason
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
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    @app.route('/health', methods=['GET'])
    @limiter.limit("10 per minute")
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
    @limiter.limit("10 per minute", "20 per hour")
    def handle_signup():
        if request.method == 'OPTIONS':
            return '', 200
        
        ip_address = get_remote_address()
        
        try:
            data = request.json
            
            is_valid, message = validate_signup_data(data)
            if not is_valid:
                return jsonify({"error": message}), 400
            
            print(f"Received signup data from {ip_address}")
            
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
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'ip_address': ip_address
            }
            
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
                    f"Reason: {data['reason'][:150]}...",
                    f"IP Address: {ip_address}"
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
    @limiter.limit("5 per minute", "10 per hour")
    def handle_suggestion():
        if request.method == 'OPTIONS':
            return '', 200
        
        ip_address = get_remote_address()
        
        try:
            data = request.json
            print(f"Received suggestion data from {ip_address}")
            
            required_fields = ['fullName', 'suggestionType', 'suggestionText']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        "error": f"Missing required field: {field}"
                    }), 400
            
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
    @limiter.limit("5 per minute")
    def queue_status():
        """Endpoint to check queue status (for monitoring)"""
        return jsonify({
            "queue_size": request_queue.queue.qsize(),
            "active_workers": request_queue.active_workers,
            "max_queue_size": request_queue.queue.maxsize,
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/test-email', methods=['GET'])
    @limiter.limit("2 per minute")
    def test_email():
        """Test endpoint to verify email sending"""
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