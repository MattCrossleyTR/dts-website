import hashlib
import os
import secrets


# injected from env file
SECRET_KEY = os.environ['DB_SECRET_KEY'].encode()
# assert on length, this guards against the key being missing if the injection fails, etc
assert len(SECRET_KEY) > 25, 'secret key either missing or too short'
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 60
# generated with openssl
PEPPER = '9aa8fc47a0fe5fbdb4b089fe4a15006fc75ee36e0de2bb5f40cd29820d8823cd'


def hash_password(password: str, salt: bytes | None = None):
    if salt is None:
        salt = secrets.token_bytes(32)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode() + PEPPER.encode(), salt, 600_000)
    return salt + hashed


def verify_password(user: User, password: str):
    salt = user.password[:32]
    return hash_password(password, salt) == user.password
