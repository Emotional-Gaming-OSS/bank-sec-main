"""
User Use Cases
Domain service layer for user-related operations
"""

from typing import Optional
from datetime import datetime
from src.adapters.database.repositories.user_repository import UserRepository
from src.domain.models.user import UserRole
from src.shared.exceptions import ValidationError, AuthenticationError

class UserUseCases:
    """Use cases for user operations"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def register_user(self, username: str, email: str, password: str, role: str = 'user') -> dict:
        """Register a new user"""
        # Validate input
        if not username or len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        
        if not email or "@" not in email:
            raise ValidationError("A valid email address is required")
        
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        # Check if user already exists
        existing_user = self.user_repository.find_user_by_email(email)
        if existing_user:
            raise ValidationError("A user with this email already exists")
        
        existing_user = self.user_repository.find_user_by_username(username)
        if existing_user:
            raise ValidationError("A user with this username already exists")
        
        # Create user
        user = self.user_repository.create_user(username, email, password, role)
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'created_at': user.created_at.isoformat()
        }
    
    def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate a user with email and password"""
        user = self.user_repository.find_user_by_email(email)
        
        if user and user.check_password(password):
            # Update last login time
            self.user_repository.update_user(user.id, last_login=datetime.utcnow())
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value
            }
        
        return None
    
    def get_user_profile(self, user_id: int) -> Optional[dict]:
        """Get user profile information"""
        user = self.user_repository.find_user_by_id(user_id)
        
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        
        return None