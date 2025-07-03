import secrets

def generate_jwt_secret():
    """Generate a secure JWT secret key"""
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    jwt_secret = generate_jwt_secret()