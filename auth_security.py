import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
from cryptography.fernet import Fernet
import hashlib
import hmac
from config import (
    SECRET_KEY, 
    ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    BCRYPT_LOG_ROUNDS
)

class PasswordManager:
    """Handle password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt
        Args:
            password: Plain text password
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt(rounds=BCRYPT_LOG_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        Args:
            password: Plain text password
            hashed_password: Hashed password from database
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def hash_email(email: str) -> str:
        """Hash email for privacy"""
        return hashlib.sha256(email.lower().encode()).hexdigest()


class JWTManager:
    """Handle JWT token creation and validation"""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        Args:
            data: Payload data
            expires_delta: Token expiration time
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        Create JWT refresh token
        Args:
            user_id: User ID
        Returns:
            JWT refresh token string
        """
        to_encode = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode JWT token
        Args:
            token: JWT token string
        Returns:
            Token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def create_password_reset_token(user_id: int, email: str) -> str:
        """
        Create password reset token
        Args:
            user_id: User ID
            email: User email
        Returns:
            Password reset token
        """
        to_encode = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "type": "password_reset"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify password reset token
        Args:
            token: Password reset token
        Returns:
            Token payload or None if invalid
        """
        payload = JWTManager.decode_token(token)
        if payload and payload.get("type") == "password_reset":
            return payload
        return None


class EncryptionManager:
    """Handle encryption and decryption of sensitive data"""
    
    def __init__(self, key: Optional[str] = None):
        """
        Initialize encryption manager
        Args:
            key: Encryption key (generated if not provided)
        """
        if key:
            self.key = key.encode() if isinstance(key, str) else key
        else:
            # Generate key from SECRET_KEY
            self.key = Fernet(
                base64.urlsafe_b64encode(
                    hashlib.sha256(SECRET_KEY.encode()).digest()
                )
            )
        
        self.cipher_suite = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt data
        Args:
            data: Plain text data
        Returns:
            Encrypted data
        """
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data
        Args:
            encrypted_data: Encrypted data
        Returns:
            Decrypted data
        """
        try:
            return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return None


class CSRFManager:
    """Handle CSRF token generation and validation"""
    
    @staticmethod
    def generate_csrf_token(session_id: str) -> str:
        """
        Generate CSRF token
        Args:
            session_id: Session ID
        Returns:
            CSRF token
        """
        return hmac.new(
            SECRET_KEY.encode(),
            session_id.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_csrf_token(session_id: str, token: str) -> bool:
        """
        Verify CSRF token
        Args:
            session_id: Session ID
            token: CSRF token to verify
        Returns:
            True if token is valid
        """
        expected_token = CSRFManager.generate_csrf_token(session_id)
        return hmac.compare_digest(expected_token, token)


class SecureSessionManager:
    """Handle secure session management"""
    
    def __init__(self):
        """Initialize session manager"""
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, user_id: int, user_data: Dict[str, Any]) -> str:
        """
        Create new session
        Args:
            user_id: User ID
            user_data: User data to store
        Returns:
            Session ID
        """
        import secrets
        session_id = secrets.token_urlsafe(32)
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow()
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        Args:
            session_id: Session ID
        Returns:
            Session data or None if expired
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is expired (1 hour)
        if (datetime.utcnow() - session["last_accessed"]).seconds > 3600:
            del self.sessions[session_id]
            return None
        
        session["last_accessed"] = datetime.utcnow()
        return session
    
    def destroy_session(self, session_id: str) -> bool:
        """
        Destroy session
        Args:
            session_id: Session ID
        Returns:
            True if session was destroyed
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# Global session manager instance
session_manager = SecureSessionManager()

import base64
