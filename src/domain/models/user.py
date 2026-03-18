"""
User Domain Model
Domain-level representation of user entities
"""

from enum import Enum

class UserRole(Enum):
    """User role enumeration for domain model"""
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    USER = "user"
    GUEST = "guest"