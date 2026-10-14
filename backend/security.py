"""Security & Authentication Module for NexaData AI.

Provides password hashing via bcrypt, JWT token issuing & verification via pyjwt,
and FastAPI dependencies for both required and optional (Guest Mode) authentication.
"""
import os
import uuid
import datetime
from typing import Optional, Dict, Any
import bcrypt
import jwt
from fastapi import HTTPException, Header, status

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "nexadata-ai-super-secret-production-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "72"))  # 3 days token validity

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Create a signed JWT access token containing claims and expiry."""
    to_encode = data.copy()
    now = datetime.datetime.now(datetime.timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Helper to extract token from 'Bearer <token>' format."""
    if not authorization:
        return None
    parts = authorization.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    if len(parts) == 1:
        return parts[0]
    return None

def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency for Option B (Guest / Hybrid Mode).
    Returns authenticated user payload if valid Bearer token is provided,
    otherwise returns None without raising an exception (allowing guest access).
    """
    token = extract_token_from_header(authorization)
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    return payload

def get_current_user_required(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    FastAPI dependency for protected endpoints requiring valid login.
    Raises HTTP 401 if token is missing or invalid.
    """
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
