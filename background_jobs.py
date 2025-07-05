from apscheduler.schedulers.background import BackgroundScheduler
from models import OTPVerification, RefreshToken
from datetime import datetime
import atexit

def cleanup_expired_data():
    """Clean up expired OTPs and refresh tokens"""
    try:
        # Clean up expired OTPs
        deleted_otps = OTPVerification.cleanup_expired_otps()
        print(f"Cleaned up {deleted_otps} expired OTPs at {datetime.utcnow()}")
        
        # Clean up expired refresh tokens
        deleted_tokens = RefreshToken.cleanup_expired_tokens()
        print(f"Cleaned up {deleted_tokens} expired refresh tokens at {datetime.utcnow()}")
        
    except Exception as e:
        print(f"Error in cleanup job: {str(e)}")

def start_background_jobs():
    """Start background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Run cleanup every 30 minutes
    scheduler.add_job(
        func=cleanup_expired_data,
        trigger="interval",
        minutes=30,
        id='cleanup_expired_data'
    )
    
    scheduler.start()
    print("Background jobs started")
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler