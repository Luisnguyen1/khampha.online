"""
Authentication utilities for khappha.online
"""
import hashlib
import secrets
import re
from typing import Optional, Dict


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash password with salt
    
    Args:
        password: Plain text password
        salt: Optional salt (will be generated if not provided)
        
    Returns:
        (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Combine password and salt, then hash
    password_salt = f"{password}{salt}".encode('utf-8')
    hashed = hashlib.sha256(password_salt).hexdigest()
    
    return hashed, salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password
        hashed_password: Hashed password from database
        salt: Salt used for hashing
        
    Returns:
        True if password matches, False otherwise
    """
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == hashed_password


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """
    Validate username format
    - Length: 3-20 characters
    - Only alphanumeric and underscore
    
    Args:
        username: Username
        
    Returns:
        True if valid, False otherwise
    """
    if not username or len(username) < 3 or len(username) > 20:
        return False
    
    pattern = r'^[a-zA-Z0-9_]+$'
    return re.match(pattern, username) is not None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    - Minimum 6 characters
    - At least one letter and one number (recommended)
    
    Args:
        password: Password
        
    Returns:
        (is_valid, error_message)
    """
    if not password or len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự"
    
    if len(password) > 100:
        return False, "Mật khẩu quá dài (tối đa 100 ký tự)"
    
    # Check for at least one letter and one number (recommended but not required)
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not (has_letter and has_number):
        return True, "Khuyến nghị: Mật khẩu nên có cả chữ và số"
    
    return True, None


def generate_session_token() -> str:
    """
    Generate secure session token
    
    Returns:
        Random session token
    """
    return secrets.token_urlsafe(32)


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input
    
    Args:
        text: User input
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Trim whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text
