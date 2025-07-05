# import random
# import string
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from config import Config
# import re

# def generate_otp(length=6):
#     """Generate random OTP"""
#     return ''.join(random.choices(string.digits, k=length))

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None

# def validate_password(password):
#     """Validate password strength"""
#     if len(password) < 8:
#         return False, "Password must be at least 8 characters long"
    
#     if not re.search(r'[A-Z]', password):
#         return False, "Password must contain at least one uppercase letter"
    
#     if not re.search(r'[a-z]', password):
#         return False, "Password must contain at least one lowercase letter"
    
#     if not re.search(r'[0-9]', password):
#         return False, "Password must contain at least one digit"
    
#     if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
#         return False, "Password must contain at least one special character"
    
#     return True, "Password is valid"

# def send_otp_email(email, otp, purpose='signup'):
#     """Send OTP via email"""
#     try:
#         msg = MIMEMultipart()
#         msg['From'] = Config.EMAIL_USERNAME
#         msg['To'] = email
#         msg['Subject'] = f"OTP for {purpose.title()} - Influencer Marketing Platform"
        
#         body = f"""
#         Dear User,
        
#         Your OTP for {purpose} is: {otp}
        
#         This OTP is valid for 10 minutes only.
        
#         If you didn't request this OTP, please ignore this email.
        
#         Best regards,
#         Influencer Marketing Platform Team
#         """
        
#         msg.attach(MIMEText(body, 'plain'))
        
#         server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
#         server.starttls()
#         server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
#         text = msg.as_string()
#         server.sendmail(Config.EMAIL_USERNAME, email, text)
#         server.quit()
        
#         return True
#     except Exception as e:
#         print(f"Error sending email: {str(e)}")
#         return False

# def validate_phone_number(phone):
#     """Validate phone number format"""
#     pattern = r'^\+?1?\d{9,15}$'
#     return re.match(pattern, phone) is not None

import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from cryptography.fernet import Fernet
import re
import redis

# Initialize encryption
cipher_suite = Fernet(Config.ENCRYPTION_KEY.encode())

# Initialize Redis
redis_client = redis.from_url(Config.REDIS_URL)

def encrypt_data(data):
    """Encrypt sensitive data"""
    if not data:
        return data
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    """Decrypt sensitive data"""
    if not encrypted_data:
        return encrypted_data
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

def generate_otp(length=None):
    """Generate random OTP"""
    if length is None:
        length = Config.OTP_LENGTH
    return ''.join(random.choices(string.digits, k=length))

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

def send_otp_email(email, otp, purpose='signup'):
    """Send OTP via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_USERNAME
        msg['To'] = email
        msg['Subject'] = f"OTP for {purpose.title()} - Influencer Marketing Platform"
        
        body = f"""
        <html>
        <body>
        <h2>OTP Verification</h2>
        <p>Dear User,</p>
        <p>Your OTP for <strong>{purpose}</strong> is:</p>
        <h1 style="color: #007bff; font-size: 36px; letter-spacing: 5px;">{otp}</h1>
        <p>This OTP is valid for {Config.OTP_EXPIRY_MINUTES} minutes only.</p>
        <p>If you didn't request this OTP, please ignore this email.</p>
        <br>
        <p>Best regards,<br>Influencer Marketing Platform Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(Config.EMAIL_USERNAME, email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_password_reset_email(email, otp):
    """Send password reset OTP via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_USERNAME
        msg['To'] = email
        msg['Subject'] = "Password Reset OTP - Influencer Marketing Platform"
        
        body = f"""
        <html>
        <body>
        <h2>Password Reset Request</h2>
        <p>Dear User,</p>
        <p>You have requested to reset your password. Your OTP is:</p>
        <h1 style="color: #dc3545; font-size: 36px; letter-spacing: 5px;">{otp}</h1>
        <p>This OTP is valid for {Config.OTP_EXPIRY_MINUTES} minutes only.</p>
        <p>If you didn't request this password reset, please ignore this email and ensure your account is secure.</p>
        <br>
        <p>Best regards,<br>Influencer Marketing Platform Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(Config.EMAIL_USERNAME, email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False

def validate_phone_number(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

temp_cache = {}

def cache_set(key, value, expiry=3600):
    """Temporary in-memory cache for testing"""
    temp_cache[key] = value
    print(f"✓ Cache set: {key} = {value}")
    return True

def cache_get(key):
    """Get from temporary cache"""
    value = temp_cache.get(key)
    print(f"✓ Cache get: {key} = {value}")
    return value

def cache_delete(key):
    """Delete from temporary cache"""
    temp_cache.pop(key, None)
    print(f"✓ Cache delete: {key}")
    return True

# Optional: Add this to see what's in cache
def cache_debug():
    """Debug function to see all cache contents"""
    print("Current cache contents:")
    for key, value in temp_cache.items():
        print(f"  {key}: {value}")
    return temp_cache