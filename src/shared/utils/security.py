"""
Security utilities
Password validation and security-related functions
"""

import re
import secrets
import string
from typing import Tuple


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    # Check for common patterns
    if re.search(r"(password|123|abc|qwerty)", password.lower()):
        return False, "Password contains common patterns"
    
    return True, "Password is strong"


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token
    
    Args:
        length: Token length in bytes
    
    Returns:
        Secure random token as hex string
    """
    return secrets.token_hex(length)


def generate_password(length: int = 16) -> str:
    """
    Generate a secure password
    
    Args:
        length: Password length
    
    Returns:
        Generated secure password
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if validate_password_strength(password)[0]:
            return password


def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input
    
    Args:
        input_string: Input to sanitize
    
    Returns:
        Sanitized input
    """
    if not input_string:
        return ""
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_string)
    
    # Remove potential SQL injection patterns
    sanitized = re.sub(r'[\'";\\]', '', sanitized)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data (like email or credit card)
    
    Args:
        data: Sensitive data to mask
        visible_chars: Number of characters to keep visible
    
    Returns:
        Masked data
    """
    if not data or len(data) <= visible_chars:
        return '*' * len(data) if data else ''
    
    masked_part = '*' * (len(data) - visible_chars)
    visible_part = data[-visible_chars:]
    
    return f"{masked_part}{visible_part}"


class SecurityHeaders:
    """Security headers configuration"""
    
    @staticmethod
    def get_csp_policy() -> str:
        """Get Content Security Policy"""
        return "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdnjs.cloudflare.com",
            "font-src 'self' fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "form-action 'self'"
        ])
    
    @staticmethod
    def get_hsts_policy() -> str:
        """Get HTTP Strict Transport Security policy"""
        return "max-age=31536000; includeSubDomains; preload"
    
    @staticmethod
    def get_permissions_policy() -> str:
        """Get Permissions Policy"""
        return ", ".join([
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()"
        ])