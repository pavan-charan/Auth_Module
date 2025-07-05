# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/influencer_marketing')
#     JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-here')
#     JWT_ACCESS_TOKEN_EXPIRES = 3600  # in seconds
#     SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
#     SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
#     EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
#     EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Database
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/influencer_marketing')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-here')
    REFRESH_SECRET_KEY = os.getenv('REFRESH_SECRET_KEY', 'your-refresh-secret-key-here')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your-encryption-key-here')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Rate Limiting
    OTP_RATE_LIMIT = 60  # seconds between OTP requests
    MAX_OTP_ATTEMPTS = 5  # max failed attempts before lockout
    LOCKOUT_DURATION = 300  # 5 minutes lockout in seconds
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES = 10
    OTP_LENGTH = 6