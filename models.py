# from pymongo import MongoClient
# from datetime import datetime, timedelta
# import bcrypt
# from config import Config

# client = MongoClient(Config.MONGODB_URI)
# db = client.influencer_marketing

# # Collections
# users_collection = db.users
# otp_collection = db.otp_verification
# brand_details_collection = db.brand_details

# class User:
#     @staticmethod
#     def create_user(email, password):
#         """Create a new user with hashed password"""
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
#         user_data = {
#             'email': email.lower(),
#             'password': hashed_password,
#             'is_verified': False,
#             'is_profile_complete': False,
#             'created_at': datetime.utcnow(),
#             'updated_at': datetime.utcnow()
#         }
        
#         result = users_collection.insert_one(user_data)
#         return str(result.inserted_id)
    
#     @staticmethod
#     def find_by_email(email):
#         """Find user by email"""
#         return users_collection.find_one({'email': email.lower()})
    
#     @staticmethod
#     def find_by_id(user_id):
#         """Find user by ID"""
#         from bson import ObjectId
#         return users_collection.find_one({'_id': ObjectId(user_id)})
    
#     @staticmethod
#     def verify_password(stored_password, provided_password):
#         """Verify password"""
#         return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
    
#     @staticmethod
#     def update_verification_status(email, status=True):
#         """Update user verification status"""
#         return users_collection.update_one(
#             {'email': email.lower()},
#             {'$set': {'is_verified': status, 'updated_at': datetime.utcnow()}}
#         )
    
#     @staticmethod
#     def update_profile_completion(email, status=True):
#         """Update profile completion status"""
#         return users_collection.update_one(
#             {'email': email.lower()},
#             {'$set': {'is_profile_complete': status, 'updated_at': datetime.utcnow()}}
#         )

# class OTPVerification:
#     @staticmethod
#     def create_otp(email, otp, otp_type='signup'):
#         """Create OTP entry"""
#         otp_data = {
#             'email': email.lower(),
#             'otp': otp,
#             'type': otp_type,  # 'signup' or 'login'
#             'created_at': datetime.utcnow(),
#             'expires_at': datetime.utcnow() + timedelta(minutes=10),
#             'is_used': False
#         }
        
#         # Remove any existing OTP for this email and type
#         otp_collection.delete_many({'email': email.lower(), 'type': otp_type})
        
#         result = otp_collection.insert_one(otp_data)
#         return str(result.inserted_id)
    
#     @staticmethod
#     def verify_otp(email, otp, otp_type='signup'):
#         """Verify OTP"""
#         otp_record = otp_collection.find_one({
#             'email': email.lower(),
#             'otp': otp,
#             'type': otp_type,
#             'is_used': False,
#             'expires_at': {'$gt': datetime.utcnow()}
#         })
        
#         if otp_record:
#             # Mark OTP as used
#             otp_collection.update_one(
#                 {'_id': otp_record['_id']},
#                 {'$set': {'is_used': True}}
#             )
#             return True
#         return False

# class BrandDetails:
#     @staticmethod
#     def create_brand_profile(user_email, brand_data):
#         """Create brand profile"""
#         brand_profile = {
#             'user_email': user_email.lower(),
#             'user_name': brand_data.get('user_name'),
#             'gender': brand_data.get('gender'),
#             'company_name': brand_data.get('company_name'),
#             'brand_name': brand_data.get('brand_name'),
#             'location': brand_data.get('location'),
#             'business_type': brand_data.get('business_type'),
#             'phone_number': brand_data.get('phone_number'),
#             'website': brand_data.get('website'),
#             'industry': brand_data.get('industry'),
#             'company_size': brand_data.get('company_size'),
#             'description': brand_data.get('description'),
#             'created_at': datetime.utcnow(),
#             'updated_at': datetime.utcnow()
#         }
        
#         result = brand_details_collection.insert_one(brand_profile)
#         return str(result.inserted_id)
    
#     @staticmethod
#     def get_brand_profile(user_email):
#         """Get brand profile by user email"""
#         return brand_details_collection.find_one({'user_email': user_email.lower()})
    
#     @staticmethod
#     def update_brand_profile(user_email, brand_data):
#         """Update brand profile"""
#         brand_data['updated_at'] = datetime.utcnow()
#         return brand_details_collection.update_one(
#             {'user_email': user_email.lower()},
#             {'$set': brand_data}
#         )
# print("✅ User class found")

# if __name__ == "__main__":
#     print("✅ models.py is running directly")


from pymongo import MongoClient
from datetime import datetime, timedelta
import bcrypt
from config import Config
from utils import encrypt_data, decrypt_data

client = MongoClient(Config.MONGODB_URI)
db = client.influencer_marketing

# Collections
users_collection = db.users
otp_collection = db.otp_verification
brand_details_collection = db.brand_details
rate_limit_collection = db.rate_limits
refresh_tokens_collection = db.refresh_tokens

class User:
    @staticmethod
    def create_user(email, password):
        """Create a new user with hashed password"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        encrypted_email = encrypt_data(email.lower())
        
        user_data = {
            'email': encrypted_email,
            'email_hash': bcrypt.hashpw(email.lower().encode('utf-8'), bcrypt.gensalt()),
            'password': hashed_password,
            'is_verified': False,
            'is_profile_complete': False,
            'is_locked': False,
            'failed_attempts': 0,
            'locked_until': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        email_hash = bcrypt.hashpw(email.lower().encode('utf-8'), bcrypt.gensalt())
        # Find by comparing hashed emails
        users = users_collection.find()
        for user in users:
            try:
                decrypted_email = decrypt_data(user['email'])
                if decrypted_email == email.lower():
                    return user
            except:
                continue
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        from bson import ObjectId
        return users_collection.find_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify password"""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
    
    @staticmethod
    def update_verification_status(email, status=True):
        """Update user verification status"""
        user = User.find_by_email(email)
        if user:
            return users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'is_verified': status, 'updated_at': datetime.utcnow()}}
            )
        return None
    
    @staticmethod
    def update_profile_completion(email, status=True):
        """Update profile completion status"""
        user = User.find_by_email(email)
        if user:
            return users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'is_profile_complete': status, 'updated_at': datetime.utcnow()}}
            )
        return None
    
    @staticmethod
    def increment_failed_attempts(email):
        """Increment failed login attempts"""
        user = User.find_by_email(email)
        if user:
            failed_attempts = user.get('failed_attempts', 0) + 1
            update_data = {'failed_attempts': failed_attempts, 'updated_at': datetime.utcnow()}
            
            if failed_attempts >= Config.MAX_OTP_ATTEMPTS:
                update_data['is_locked'] = True
                update_data['locked_until'] = datetime.utcnow() + timedelta(seconds=Config.LOCKOUT_DURATION)
            
            return users_collection.update_one(
                {'_id': user['_id']},
                {'$set': update_data}
            )
        return None
    
    @staticmethod
    def reset_failed_attempts(email):
        """Reset failed login attempts"""
        user = User.find_by_email(email)
        if user:
            return users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {
                    'failed_attempts': 0,
                    'is_locked': False,
                    'locked_until': None,
                    'updated_at': datetime.utcnow()
                }}
            )
        return None
    
    @staticmethod
    def is_account_locked(email):
        """Check if account is locked"""
        user = User.find_by_email(email)
        if user:
            if user.get('is_locked') and user.get('locked_until'):
                if datetime.utcnow() < user['locked_until']:
                    return True
                else:
                    # Auto-unlock if lockout period has passed
                    User.reset_failed_attempts(email)
                    return False
            return user.get('is_locked', False)
        return False
    
    @staticmethod
    def update_password(email, new_password):
        """Update user password"""
        user = User.find_by_email(email)
        if user:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            return users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'password': hashed_password, 'updated_at': datetime.utcnow()}}
            )
        return None

class OTPVerification:
    @staticmethod
    def create_otp(email, otp, otp_type='signup'):
        """Create OTP entry with encryption"""
        encrypted_otp = encrypt_data(otp)
        encrypted_email = encrypt_data(email.lower())
        
        otp_data = {
            'email': encrypted_email,
            'otp': encrypted_otp,
            'type': otp_type,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=Config.OTP_EXPIRY_MINUTES),
            'is_used': False,
            'attempts': 0
        }
        
        # Remove any existing OTP for this email and type
        OTPVerification.delete_user_otps(email, otp_type)
        
        result = otp_collection.insert_one(otp_data)
        return str(result.inserted_id)
    
    @staticmethod
    def verify_otp(email, otp, otp_type='signup'):
        """Verify OTP with attempt tracking"""
        otps = otp_collection.find({
            'type': otp_type,
            'is_used': False,
            'expires_at': {'$gt': datetime.utcnow()}
        })
        
        for otp_record in otps:
            try:
                decrypted_email = decrypt_data(otp_record['email'])
                decrypted_otp = decrypt_data(otp_record['otp'])
                
                if decrypted_email == email.lower():
                    if decrypted_otp == otp:
                        # Mark OTP as used
                        otp_collection.update_one(
                            {'_id': otp_record['_id']},
                            {'$set': {'is_used': True}}
                        )
                        return True
                    else:
                        # Increment attempts
                        otp_collection.update_one(
                            {'_id': otp_record['_id']},
                            {'$inc': {'attempts': 1}}
                        )
                        return False
            except:
                continue
        
        return False
    
    @staticmethod
    def delete_user_otps(email, otp_type):
        """Delete all OTPs for a user and type"""
        otps = otp_collection.find({'type': otp_type})
        for otp_record in otps:
            try:
                decrypted_email = decrypt_data(otp_record['email'])
                if decrypted_email == email.lower():
                    otp_collection.delete_one({'_id': otp_record['_id']})
            except:
                continue
    
    @staticmethod
    def cleanup_expired_otps():
        """Delete expired OTPs"""
        result = otp_collection.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })
        return result.deleted_count

class BrandDetails:
    @staticmethod
    def create_brand_profile(user_email, brand_data):
        """Create brand profile with encryption"""
        encrypted_email = encrypt_data(user_email.lower())
        encrypted_phone = encrypt_data(brand_data.get('phone_number', ''))
        
        brand_profile = {
            'user_email': encrypted_email,
            'user_name': brand_data.get('user_name'),
            'gender': brand_data.get('gender'),
            'company_name': brand_data.get('company_name'),
            'brand_name': brand_data.get('brand_name'),
            'location': brand_data.get('location'),
            'business_type': brand_data.get('business_type'),
            'phone_number': encrypted_phone,
            'website': brand_data.get('website'),
            'industry': brand_data.get('industry'),
            'company_size': brand_data.get('company_size'),
            'description': brand_data.get('description'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = brand_details_collection.insert_one(brand_profile)
        return str(result.inserted_id)
    
    @staticmethod
    def get_brand_profile(user_email):
        """Get brand profile by user email"""
        profiles = brand_details_collection.find()
        for profile in profiles:
            try:
                decrypted_email = decrypt_data(profile['user_email'])
                if decrypted_email == user_email.lower():
                    # Decrypt sensitive data before returning
                    if profile.get('phone_number'):
                        profile['phone_number'] = decrypt_data(profile['phone_number'])
                    return profile
            except:
                continue
        return None
    
    @staticmethod
    def update_brand_profile(user_email, brand_data):
        """Update brand profile"""
        profile = BrandDetails.get_brand_profile(user_email)
        if profile:
            update_data = brand_data.copy()
            update_data['updated_at'] = datetime.utcnow()
            
            # Encrypt sensitive data
            if 'phone_number' in update_data:
                update_data['phone_number'] = encrypt_data(update_data['phone_number'])
            
            return brand_details_collection.update_one(
                {'_id': profile['_id']},
                {'$set': update_data}
            )
        return None

class RateLimit:
    @staticmethod
    def can_send_otp(email):
        """Check if user can send OTP (rate limiting)"""
        rate_limit = rate_limit_collection.find_one({
            'email': email.lower(),
            'type': 'otp_request'
        })
        
        if rate_limit:
            time_diff = (datetime.utcnow() - rate_limit['last_request']).total_seconds()
            if time_diff < Config.OTP_RATE_LIMIT:
                return False, Config.OTP_RATE_LIMIT - int(time_diff)
        
        return True, 0
    
    @staticmethod
    def record_otp_request(email):
        """Record OTP request for rate limiting"""
        rate_limit_collection.update_one(
            {'email': email.lower(), 'type': 'otp_request'},
            {
                '$set': {
                    'last_request': datetime.utcnow(),
                    'email': email.lower(),
                    'type': 'otp_request'
                }
            },
            upsert=True
        )

class RefreshToken:
    @staticmethod
    def create_refresh_token(user_email, token):
        """Create refresh token"""
        token_data = {
            'user_email': user_email.lower(),
            'token': token,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + Config.JWT_REFRESH_TOKEN_EXPIRES,
            'is_used': False
        }
        
        result = refresh_tokens_collection.insert_one(token_data)
        return str(result.inserted_id)
    
    @staticmethod
    def verify_refresh_token(token):
        """Verify refresh token"""
        return refresh_tokens_collection.find_one({
            'token': token,
            'is_used': False,
            'expires_at': {'$gt': datetime.utcnow()}
        })
    
    @staticmethod
    def revoke_refresh_token(token):
        """Revoke refresh token"""
        return refresh_tokens_collection.update_one(
            {'token': token},
            {'$set': {'is_used': True}}
        )
    
    @staticmethod
    def cleanup_expired_tokens():
        """Delete expired refresh tokens"""
        result = refresh_tokens_collection.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })
        return result.deleted_count