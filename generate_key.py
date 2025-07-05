# import secrets

# def generate_jwt_secret():
#     """Generate a secure JWT secret key"""
#     return secrets.token_urlsafe(32)

# if __name__ == "__main__":
#     jwt_secret = generate_jwt_secret()

import secrets
from cryptography.fernet import Fernet

def generate_all_keys():
    """Generate all required keys for the application"""
    jwt_secret = secrets.token_urlsafe(32)
    encryption_key = Fernet.generate_key()
    
    print("=== COPY THESE TO YOUR .env FILE ===")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print(f"ENCRYPTION_KEY={encryption_key.decode()}")
    print(f"REFRESH_SECRET_KEY={secrets.token_urlsafe(32)}")
    print("=" * 40)

if __name__ == "__main__":
    generate_all_keys()