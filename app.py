
# from flask import Flask, request, jsonify
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# from models import User, OTPVerification, BrandDetails
# from utils import generate_otp, validate_email, validate_password, send_otp_email, validate_phone_number
# from config import Config
# from datetime import datetime, timedelta
# from flask_cors import CORS
# from bson import ObjectId
# import base64
# import bcrypt
# import time

# app = Flask(__name__)
# CORS(app)
# app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)

# jwt = JWTManager(app)




# def sanitize_mongo_object(obj):
#     if isinstance(obj, dict):
#         return {k: sanitize_mongo_object(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [sanitize_mongo_object(i) for i in obj]
#     elif isinstance(obj, ObjectId):
#         return str(obj)
#     elif isinstance(obj, bytes):
#         return base64.b64encode(obj).decode('utf-8')  # or simply use .decode() if it’s text
#     else:
#         return obj

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     return jsonify({'status': 'healthy'}), 200

# @app.route('/api/signup/email', methods=['POST'])
# def signup_email():
#     data = request.get_json()
#     email = data.get('email', '').strip()
#     if not email or not validate_email(email):
#         return jsonify({'error': 'Invalid email'}), 400
#     if User.find_by_email(email):
#         return jsonify({'error': 'Email already registered'}), 409
#     otp = generate_otp()
#     OTPVerification.create_otp(email, otp, 'signup')
#     send_otp_email(email, otp, 'signup')
#     return jsonify({'message': 'OTP sent'}), 200


# @app.route('/api/signup/verify-otp', methods=['POST'])
# def verify_otp():
#     data = request.get_json()
#     email = data.get('email', '').strip()
#     otp = data.get('otp', '').strip()
#     if OTPVerification.verify_otp(email, otp, 'signup'):
#         return jsonify({'message': 'OTP verified'}), 200
#     return jsonify({'error': 'Invalid/Expired OTP'}), 400

# @app.route('/api/signup/set-password', methods=['POST'])
# def set_password():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
#     confirm = data.get('confirm_password')
#     if password != confirm:
#         return jsonify({'error': 'Passwords do not match'}), 400
#     valid, msg = validate_password(password)
#     if not valid:
#         return jsonify({'error': msg}), 400
#     user_id = User.create_user(email, password)
#     User.update_verification_status(email)
#     token = create_access_token(identity=email)
#     return jsonify({'message': 'Signup complete', 'access_token': token}), 201

# @app.route('/api/profile/complete', methods=['POST'])
# @jwt_required()
# def complete_profile():
#     email = get_jwt_identity()
#     data = request.get_json()
#     required = ['user_name', 'gender', 'company_name', 'brand_name', 'location', 'business_type', 'phone_number']
#     for field in required:
#         if not data.get(field):
#             return jsonify({'error': f'{field} required'}), 400
#     if not validate_phone_number(data['phone_number']):
#         return jsonify({'error': 'Invalid phone'}), 400
#     BrandDetails.create_brand_profile(email, data)
#     User.update_profile_completion(email)
#     return jsonify({'message': 'Profile completed'}), 201

# @app.route('/api/login/password', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
#     user = User.find_by_email(email)
#     if not user or not user.get('is_verified') or not User.verify_password(user['password'], password):
#         return jsonify({'error': 'Invalid credentials'}), 401
#     token = create_access_token(identity=email)
#     return jsonify({'message': 'Login successful', 'access_token': token}), 200

# @app.route('/api/login/otp/send', methods=['POST'])
# def send_login_otp():
#     data = request.get_json()
#     email = data.get('email')
#     if not User.find_by_email(email):
#         return jsonify({'error': 'User not found'}), 404
#     otp = generate_otp()
#     OTPVerification.create_otp(email, otp, 'login')
#     send_otp_email(email, otp, 'login')
#     return jsonify({'message': 'OTP sent'}), 200

# @app.route('/api/login/otp/verify', methods=['POST'])
# def verify_login_otp():
#     data = request.get_json()
#     email = data.get('email')
#     otp = data.get('otp')
#     if OTPVerification.verify_otp(email, otp, 'login'):
#         token = create_access_token(identity=email)
#         return jsonify({'message': 'Login successful', 'access_token': token}), 200
#     return jsonify({'error': 'Invalid/Expired OTP'}), 400

# @app.route('/api/profile', methods=['GET'])
# @jwt_required()
# def get_profile():
#     email = get_jwt_identity()
#     user = User.find_by_email(email)
#     profile = BrandDetails.get_brand_profile(email)

#     return jsonify({
#         'user': sanitize_mongo_object(user),
#         'profile': sanitize_mongo_object(profile)
#     }), 200

#     return jsonify({'user': user, 'profile': profile}), 200

# @app.route('/api/profile/update', methods=['PUT'])
# @jwt_required()
# def update_profile():
#     email = get_jwt_identity()
#     data = request.get_json()
#     if data.get('phone_number') and not validate_phone_number(data['phone_number']):
#         return jsonify({'error': 'Invalid phone'}), 400
#     BrandDetails.update_brand_profile(email, data)
#     return jsonify({'message': 'Profile updated'}), 200

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)


from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import User, OTPVerification, BrandDetails, RateLimit, RefreshToken
from utils import (generate_otp, validate_email, validate_password, send_otp_email, 
                   validate_phone_number, send_password_reset_email, cache_set, cache_get, cache_delete)
from config import Config
from background_jobs import start_background_jobs
import json
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.JWT_REFRESH_TOKEN_EXPIRES

jwt = JWTManager(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Start background jobs
start_background_jobs()

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Enhanced Brand Authentication API is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    }), 200

# Step 1: Email Registration & OTP Generation with Rate Limiting
@app.route('/api/signup/email', methods=['POST'])
@limiter.limit("5 per minute")
def signup_email():
    """Step 1: Register email and send OTP with rate limiting"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({'error': 'User already exists with this email'}), 409
        
        # Check rate limiting
        can_send, wait_time = RateLimit.can_send_otp(email)
        if not can_send:
            return jsonify({
                'error': 'Too many OTP requests',
                'wait_time': wait_time,
                'message': f'Please wait {wait_time} seconds before requesting another OTP'
            }), 429
        
        # Generate and send OTP
        otp = generate_otp()
        otp_id = OTPVerification.create_otp(email, otp, 'signup')
        
        # Record OTP request for rate limiting
        RateLimit.record_otp_request(email)
        
        # For development, you can print OTP to console
        print(f"Signup OTP for {email}: {otp}")
        
        if send_otp_email(email, otp, 'signup'):
            return jsonify({
                'message': 'OTP sent successfully to your email',
                'otp_id': otp_id,
                'email': email,
                'expires_in': Config.OTP_EXPIRY_MINUTES * 60
            }), 200
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Step 2: OTP Verification with Attempt Tracking
@app.route('/api/signup/verify-otp', methods=['POST'])
@limiter.limit("10 per minute")
def verify_signup_otp():
    """Step 2: Verify OTP with attempt tracking"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '')
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        if OTPVerification.verify_otp(email, otp, 'signup'):
            # Cache verification status temporarily
            cache_set(f"verified_signup_{email}", "verified", 600)  # 10 minutes
            cache_value = cache_get(f"verified_signup_{email}")
            print(f"Cache check for {email}: {cache_value}")
            
            cache_key = f"verified_signup_{email}"
            print(f"Setting cache key: {cache_key}")
            cache_result = cache_set(cache_key, "verified", 600)
            print(f"Cache set result: {cache_result}")
            
            # Verify it was set
            check_value = cache_get(cache_key)
            print(f"Cache check immediately after setting: {check_value}")
            return jsonify({
                'message': 'OTP verified successfully',
                'email': email,
                'next_step': 'set_password'
            }), 200
        else:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Step 3: Set Password & Complete Signup
@app.route('/api/signup/set-password', methods=['POST'])
@limiter.limit("5 per minute")
def set_password():
    """Step 3: Set password and complete signup"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not email or not password or not confirm_password:
            return jsonify({'error': 'Email, password, and confirm password are required'}), 400
        
        # Check if OTP was verified
        if not cache_get(f"verified_signup_{email}"):
            return jsonify({'error': 'Email not verified. Please verify your email first.'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Create user
        user_id = User.create_user(email, password)
        User.update_verification_status(email, True)
        
        # Generate tokens
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        
        # Store refresh token
        RefreshToken.create_refresh_token(email, refresh_token)
        
        # Clean up verification cache
        cache_delete(f"verified_signup_{email}")
        
        return jsonify({
            'message': 'Signup completed successfully',
            'user_id': user_id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'email': email,
            'next_step': 'complete_profile'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Step 4: Complete Brand Profile
@app.route('/api/profile/complete', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def complete_profile():
    """Step 4: Complete brand profile"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Required fields
        required_fields = ['user_name', 'gender', 'company_name', 'brand_name', 
                          'location', 'business_type', 'phone_number', 'industry']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Validate phone number
        if not validate_phone_number(data.get('phone_number')):
            return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Validate enum values
        valid_genders = ['Male', 'Female', 'other', 'prefer_not_to_say']
        if data.get('gender') not in valid_genders:
            return jsonify({'error': 'Invalid gender value'}), 400
        
        valid_business_types = ['startup', 'small_business', 'medium_business', 'enterprise', 'agency']
        if data.get('business_type') not in valid_business_types:
            return jsonify({'error': 'Invalid business type'}), 400
        
        # Create brand profile
        brand_id = BrandDetails.create_brand_profile(current_user, data)
        
        # Update user profile completion status
        User.update_profile_completion(current_user, True)
        
        return jsonify({
            'message': 'Profile completed successfully',
            'brand_id': brand_id,
            'email': current_user
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Login with Password (Traditional Login)
@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login with password and account lockout protection"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if account is locked
        if User.is_account_locked(email):
            return jsonify({'error': 'Account is temporarily locked due to multiple failed attempts'}), 423
        
        # Find user
        user = User.find_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not User.verify_password(user['password'], password):
            User.increment_failed_attempts(email)
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is verified
        if not user.get('is_verified', False):
            return jsonify({'error': 'Please verify your email first'}), 403
        
        # Reset failed attempts on successful login
        User.reset_failed_attempts(email)
        
        # Generate tokens
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        
        # Store refresh token
        RefreshToken.create_refresh_token(email, refresh_token)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'email': email,
            'is_profile_complete': user.get('is_profile_complete', False)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Login with OTP - Request OTP
@app.route('/api/login/otp/request', methods=['POST'])
@limiter.limit("5 per minute")
def request_login_otp():
    """Request OTP for login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if account is locked
        if User.is_account_locked(email):
            return jsonify({'error': 'Account is temporarily locked due to multiple failed attempts'}), 423
        
        # Find user
        user = User.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user is verified
        if not user.get('is_verified', False):
            return jsonify({'error': 'Please verify your email first'}), 403
        
        # Check rate limiting
        can_send, wait_time = RateLimit.can_send_otp(email)
        if not can_send:
            return jsonify({
                'error': 'Too many OTP requests',
                'wait_time': wait_time,
                'message': f'Please wait {wait_time} seconds before requesting another OTP'
            }), 429
        
        # Generate and send OTP
        otp = generate_otp()
        otp_id = OTPVerification.create_otp(email, otp, 'login')
        
        # Record OTP request for rate limiting
        RateLimit.record_otp_request(email)
        
        # For development, you can print OTP to console
        print(f"Login OTP for {email}: {otp}")
        
        if send_otp_email(email, otp, 'login'):
            return jsonify({
                'message': 'Login OTP sent successfully to your email',
                'otp_id': otp_id,
                'email': email,
                'expires_in': Config.OTP_EXPIRY_MINUTES * 60
            }), 200
        else:
            return jsonify({'error': 'Failed to send login OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Login with OTP - Verify OTP and Login
@app.route('/api/login/otp/verify', methods=['POST'])
@limiter.limit("10 per minute")
def verify_login_otp():
    """Verify OTP and complete login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        # Check if account is locked
        if User.is_account_locked(email):
            return jsonify({'error': 'Account is temporarily locked due to multiple failed attempts'}), 423
        
        # Find user
        user = User.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify OTP
        if OTPVerification.verify_otp(email, otp, 'login'):
            # Reset failed attempts on successful login
            User.reset_failed_attempts(email)
            
            # Generate tokens
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)
            
            # Store refresh token
            RefreshToken.create_refresh_token(email, refresh_token)
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'email': email,
                'is_profile_complete': user.get('is_profile_complete', False)
            }), 200
        else:
            # Increment failed attempts for invalid OTP
            User.increment_failed_attempts(email)
            return jsonify({'error': 'Invalid or expired OTP'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Password Reset Request
@app.route('/api/password-reset/request', methods=['POST'])
@limiter.limit("3 per minute")
def request_password_reset():
    """Request password reset OTP"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if user exists
        user = User.find_by_email(email)
        if not user:
            # Don't reveal if user exists or not
            return jsonify({'message': 'If this email exists, a password reset OTP has been sent'}), 200
        
        # Check rate limiting
        can_send, wait_time = RateLimit.can_send_otp(email)
        if not can_send:
            return jsonify({
                'error': 'Too many password reset requests',
                'wait_time': wait_time,
                'message': f'Please wait {wait_time} seconds before requesting another OTP'
            }), 429
        
        # Generate and send OTP
        otp = generate_otp()
        otp_id = OTPVerification.create_otp(email, otp, 'password_reset')
        
        # Record OTP request for rate limiting
        RateLimit.record_otp_request(email)
        
        # For development, you can print OTP to console
        print(f"Password reset OTP for {email}: {otp}")
        
        if send_password_reset_email(email, otp):
            return jsonify({
                'message': 'Password reset OTP sent to your email',
                'otp_id': otp_id,
                'expires_in': Config.OTP_EXPIRY_MINUTES * 60
            }), 200
        else:
            return jsonify({'error': 'Failed to send password reset OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Verify Password Reset OTP
@app.route('/api/password-reset/verify-otp', methods=['POST'])
@limiter.limit("10 per minute")
def verify_password_reset_otp():
    """Verify password reset OTP"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        if OTPVerification.verify_otp(email, otp, 'password_reset'):
            # Cache verification status temporarily
            cache_set(f"verified_password_reset_{email}", "true", 600)  # 10 minutes
            
            return jsonify({
                'message': 'OTP verified successfully',
                'email': email,
                'next_step': 'reset_password'
            }), 200
        else:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Reset Password
@app.route('/api/password-reset/reset', methods=['POST'])
@limiter.limit("5 per minute")
def reset_password():
    """Reset password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        new_password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not email or not new_password or not confirm_password:
            return jsonify({'error': 'Email, new password, and confirm password are required'}), 400
        
        # Check if OTP was verified
        if not cache_get(f"verified_password_reset_{email}"):
            return jsonify({'error': 'Password reset not verified. Please verify OTP first.'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Update password
        result = User.update_password(email, new_password)
        
        if result:
            # Clean up verification cache
            cache_delete(f"verified_password_reset_{email}")
            
            # Reset failed attempts
            User.reset_failed_attempts(email)
            
            return jsonify({
                'message': 'Password reset successfully',
                'email': email
            }), 200
        else:
            return jsonify({'error': 'Failed to reset password'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get User Profile
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        current_user = get_jwt_identity()
        
        # Get user details
        user = User.find_by_email(current_user)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get brand profile
        brand_profile = BrandDetails.get_brand_profile(current_user)

        # Clean brand_profile for JSON serialization
        if brand_profile:
            brand_profile['_id'] = str(brand_profile['_id'])
            brand_profile['created_at'] = brand_profile.get('created_at').isoformat() if brand_profile.get('created_at') else None
            brand_profile['updated_at'] = brand_profile.get('updated_at').isoformat() if brand_profile.get('updated_at') else None

        profile_data = {
            'email': current_user,
            'is_verified': user.get('is_verified', False),
            'is_profile_complete': user.get('is_profile_complete', False),
            'created_at': user.get('created_at').isoformat() if user.get('created_at') else None,
            'brand_profile': brand_profile
        }

        return jsonify(profile_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Update Brand Profile
@app.route('/api/profile/update', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
def update_profile():
    """Update brand profile"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate phone number if provided
        if 'phone_number' in data and data['phone_number']:
            if not validate_phone_number(data['phone_number']):
                return jsonify({'error': 'Invalid phone number format'}), 400
        
        # Validate enum values if provided
        if 'gender' in data:
            valid_genders = ['male', 'female', 'other', 'prefer_not_to_say']
            if data['gender'] not in valid_genders:
                return jsonify({'error': 'Invalid gender value'}), 400
        
        if 'business_type' in data:
            valid_business_types = ['startup', 'small_business', 'medium_business', 'enterprise', 'agency']
            if data['business_type'] not in valid_business_types:
                return jsonify({'error': 'Invalid business type'}), 400
        
        # Update brand profile
        result = BrandDetails.update_brand_profile(current_user, data)
        
        if result:
            return jsonify({
                'message': 'Profile updated successfully',
                'email': current_user
            }), 200
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Refresh Token
@app.route('/api/auth/refresh', methods=['POST'])
@limiter.limit("20 per minute")
def refresh_token():
    """Refresh access token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        refresh_token = data.get('refresh_token', '')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400
        
        # Verify refresh token
        token_data = RefreshToken.verify_refresh_token(refresh_token)
        
        if not token_data:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
        # Get user email
        user_email = token_data['user_email']
        
        # Generate new tokens
        new_access_token = create_access_token(identity=user_email)
        new_refresh_token = create_refresh_token(identity=user_email)
        
        # Revoke old refresh token
        RefreshToken.revoke_refresh_token(refresh_token)
        
        # Store new refresh token
        RefreshToken.create_refresh_token(user_email, new_refresh_token)
        
        return jsonify({
            'access_token': new_access_token,
            'refresh_token': new_refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Logout (Revoke Refresh Token)
@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and revoke refresh token"""
    try:
        data = request.get_json()
        
        if data and data.get('refresh_token'):
            refresh_token = data['refresh_token']
            RefreshToken.revoke_refresh_token(refresh_token)
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Resend OTP
@app.route('/api/otp/resend', methods=['POST'])
@limiter.limit("3 per minute")
def resend_otp():
    """Resend OTP"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        otp_type = data.get('type', 'signup')  # signup or password_reset
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if otp_type not in ['signup', 'password_reset', 'login']:
            return jsonify({'error': 'Invalid OTP type'}), 400
        
        # Check rate limiting
        can_send, wait_time = RateLimit.can_send_otp(email)
        if not can_send:
            return jsonify({
                'error': 'Too many OTP requests',
                'wait_time': wait_time,
                'message': f'Please wait {wait_time} seconds before requesting another OTP'
            }), 429
        
        # Generate and send OTP
        otp = generate_otp()
        otp_id = OTPVerification.create_otp(email, otp, otp_type)
        
        # Record OTP request for rate limiting
        RateLimit.record_otp_request(email)
        
        # For development, you can print OTP to console
        print(f"Resend OTP for {email} ({otp_type}): {otp}")
        
        # Send appropriate email
        if otp_type == 'signup':
            email_sent = send_otp_email(email, otp, 'signup')
        elif otp_type == 'login':
            email_sent = send_otp_email(email, otp, 'login')
        else:
            email_sent = send_password_reset_email(email, otp)
        
        if email_sent:
            return jsonify({
                'message': f'OTP resent successfully',
                'otp_id': otp_id,
                'email': email,
                'expires_in': Config.OTP_EXPIRY_MINUTES * 60
            }), 200
        else:
            return jsonify({'error': 'Failed to resend OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Account Status
@app.route('/api/account/status', methods=['POST'])
@limiter.limit("10 per minute")
def get_account_status():
    """Get account status (for checking if email exists and is verified)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.find_by_email(email)
        
        if not user:
            return jsonify({
                'exists': False,
                'is_verified': False,
                'is_profile_complete': False,
                'is_locked': False
            }), 200
        
        return jsonify({
            'exists': True,
            'is_verified': user.get('is_verified', False),
            'is_profile_complete': user.get('is_profile_complete', False),
            'is_locked': User.is_account_locked(email)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token is required'}), 401

# Global Error Handler
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e.description)
    }), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)