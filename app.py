
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import User, OTPVerification, BrandDetails
from utils import generate_otp, validate_email, validate_password, send_otp_email, validate_phone_number
from config import Config
from datetime import datetime, timedelta
from flask_cors import CORS
from bson import ObjectId
import base64
import bcrypt
import time

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)

jwt = JWTManager(app)




def sanitize_mongo_object(obj):
    if isinstance(obj, dict):
        return {k: sanitize_mongo_object(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_mongo_object(i) for i in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')  # or simply use .decode() if it’s text
    else:
        return obj

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/signup/email', methods=['POST'])
def signup_email():
    data = request.get_json()
    email = data.get('email', '').strip()
    if not email or not validate_email(email):
        return jsonify({'error': 'Invalid email'}), 400
    if User.find_by_email(email):
        return jsonify({'error': 'Email already registered'}), 409
    otp = generate_otp()
    OTPVerification.create_otp(email, otp, 'signup')
    send_otp_email(email, otp, 'signup')
    return jsonify({'message': 'OTP sent'}), 200


@app.route('/api/signup/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email', '').strip()
    otp = data.get('otp', '').strip()
    if OTPVerification.verify_otp(email, otp, 'signup'):
        return jsonify({'message': 'OTP verified'}), 200
    return jsonify({'error': 'Invalid/Expired OTP'}), 400

@app.route('/api/signup/set-password', methods=['POST'])
def set_password():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirm_password')
    if password != confirm:
        return jsonify({'error': 'Passwords do not match'}), 400
    valid, msg = validate_password(password)
    if not valid:
        return jsonify({'error': msg}), 400
    user_id = User.create_user(email, password)
    User.update_verification_status(email)
    token = create_access_token(identity=email)
    return jsonify({'message': 'Signup complete', 'access_token': token}), 201

@app.route('/api/profile/complete', methods=['POST'])
@jwt_required()
def complete_profile():
    email = get_jwt_identity()
    data = request.get_json()
    required = ['user_name', 'gender', 'company_name', 'brand_name', 'location', 'business_type', 'phone_number']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} required'}), 400
    if not validate_phone_number(data['phone_number']):
        return jsonify({'error': 'Invalid phone'}), 400
    BrandDetails.create_brand_profile(email, data)
    User.update_profile_completion(email)
    return jsonify({'message': 'Profile completed'}), 201

@app.route('/api/login/password', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.find_by_email(email)
    if not user or not user.get('is_verified') or not User.verify_password(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = create_access_token(identity=email)
    return jsonify({'message': 'Login successful', 'access_token': token}), 200

@app.route('/api/login/otp/send', methods=['POST'])
def send_login_otp():
    data = request.get_json()
    email = data.get('email')
    if not User.find_by_email(email):
        return jsonify({'error': 'User not found'}), 404
    otp = generate_otp()
    OTPVerification.create_otp(email, otp, 'login')
    send_otp_email(email, otp, 'login')
    return jsonify({'message': 'OTP sent'}), 200

@app.route('/api/login/otp/verify', methods=['POST'])
def verify_login_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    if OTPVerification.verify_otp(email, otp, 'login'):
        token = create_access_token(identity=email)
        return jsonify({'message': 'Login successful', 'access_token': token}), 200
    return jsonify({'error': 'Invalid/Expired OTP'}), 400

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    email = get_jwt_identity()
    user = User.find_by_email(email)
    profile = BrandDetails.get_brand_profile(email)

    return jsonify({
        'user': sanitize_mongo_object(user),
        'profile': sanitize_mongo_object(profile)
    }), 200

    return jsonify({'user': user, 'profile': profile}), 200

@app.route('/api/profile/update', methods=['PUT'])
@jwt_required()
def update_profile():
    email = get_jwt_identity()
    data = request.get_json()
    if data.get('phone_number') and not validate_phone_number(data['phone_number']):
        return jsonify({'error': 'Invalid phone'}), 400
    BrandDetails.update_brand_profile(email, data)
    return jsonify({'message': 'Profile updated'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)