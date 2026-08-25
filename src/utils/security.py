"""
Security - Encryption and authentication utilities.

Provides Fernet encryption for code storage and JWT-based
authentication for API access.
"""

import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False


class SecureStorage:
    """Fernet encryption for code at rest."""

    def __init__(self, password: Optional[str] = None):
        if not HAS_CRYPTO:
            raise ImportError("cryptography library required for SecureStorage")
        self.key = self._generate_key(password)
        self.cipher = Fernet(self.key)

    def _generate_key(self, password: Optional[str] = None) -> bytes:
        """Generate encryption key from password or random."""
        if not password:
            return Fernet.generate_key()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"nj-ide-copier",
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt_code(self, code: str) -> bytes:
        """Encrypt code string."""
        return self.cipher.encrypt(code.encode())

    def decrypt_code(self, encrypted_code: bytes) -> str:
        """Decrypt encrypted code."""
        return self.cipher.decrypt(encrypted_code).decode()


class AuthManager:
    """JWT token generation and verification."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def generate_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Generate a JWT token."""
        if not HAS_JWT:
            return "jwt-not-available"

        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify a JWT token."""
        if not HAS_JWT:
            return None

        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
