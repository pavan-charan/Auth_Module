import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import re

def generate_otp(length=6):
    """Generate random OTP"""
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
        Dear User,
        
        Your OTP for {purpose} is: {otp}
        
        This OTP is valid for 10 minutes only.
        
        If you didn't request this OTP, please ignore this email.
        
        Best regards,
        Influencer Marketing Platform Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
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

def validate_phone_number(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None