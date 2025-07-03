from pymongo import MongoClient
from datetime import datetime, timedelta
import bcrypt
from config import Config

client = MongoClient(Config.MONGODB_URI)
db = client.influencer_marketing

# Collections
users_collection = db.users
otp_collection = db.otp_verification
brand_details_collection = db.brand_details

class User:
    @staticmethod
    def create_user(email, password):
        """Create a new user with hashed password"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'email': email.lower(),
            'password': hashed_password,
            'is_verified': False,
            'is_profile_complete': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return users_collection.find_one({'email': email.lower()})
    
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
        return users_collection.update_one(
            {'email': email.lower()},
            {'$set': {'is_verified': status, 'updated_at': datetime.utcnow()}}
        )
    
    @staticmethod
    def update_profile_completion(email, status=True):
        """Update profile completion status"""
        return users_collection.update_one(
            {'email': email.lower()},
            {'$set': {'is_profile_complete': status, 'updated_at': datetime.utcnow()}}
        )

class OTPVerification:
    @staticmethod
    def create_otp(email, otp, otp_type='signup'):
        """Create OTP entry"""
        otp_data = {
            'email': email.lower(),
            'otp': otp,
            'type': otp_type,  # 'signup' or 'login'
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=10),
            'is_used': False
        }
        
        # Remove any existing OTP for this email and type
        otp_collection.delete_many({'email': email.lower(), 'type': otp_type})
        
        result = otp_collection.insert_one(otp_data)
        return str(result.inserted_id)
    
    @staticmethod
    def verify_otp(email, otp, otp_type='signup'):
        """Verify OTP"""
        otp_record = otp_collection.find_one({
            'email': email.lower(),
            'otp': otp,
            'type': otp_type,
            'is_used': False,
            'expires_at': {'$gt': datetime.utcnow()}
        })
        
        if otp_record:
            # Mark OTP as used
            otp_collection.update_one(
                {'_id': otp_record['_id']},
                {'$set': {'is_used': True}}
            )
            return True
        return False

class BrandDetails:
    @staticmethod
    def create_brand_profile(user_email, brand_data):
        """Create brand profile"""
        brand_profile = {
            'user_email': user_email.lower(),
            'user_name': brand_data.get('user_name'),
            'gender': brand_data.get('gender'),
            'company_name': brand_data.get('company_name'),
            'brand_name': brand_data.get('brand_name'),
            'location': brand_data.get('location'),
            'business_type': brand_data.get('business_type'),
            'phone_number': brand_data.get('phone_number'),
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
        return brand_details_collection.find_one({'user_email': user_email.lower()})
    
    @staticmethod
    def update_brand_profile(user_email, brand_data):
        """Update brand profile"""
        brand_data['updated_at'] = datetime.utcnow()
        return brand_details_collection.update_one(
            {'user_email': user_email.lower()},
            {'$set': brand_data}
        )
print("✅ User class found")

if __name__ == "__main__":
    print("✅ models.py is running directly")