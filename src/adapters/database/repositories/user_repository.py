"""
User Repository
Data access layer for user operations
"""

from typing import Optional, List
from src.adapters.database.models import UserModel, db
from src.domain.models.user import UserRole

class UserRepository:
    """Repository for user data operations"""
    
    def __init__(self, session):
        self.session = session
    
    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> UserModel:
        """Create a new user in the database"""
        user = UserModel(
            username=username,
            email=email,
            role=UserRole[role.upper()] if role.upper() in UserRole.__members__ else UserRole.USER
        )
        user.set_password(password)
        
        self.session.add(user)
        self.session.commit()
        
        return user
    
    def find_user_by_id(self, user_id: int) -> Optional[UserModel]:
        """Find a user by their ID"""
        return self.session.query(UserModel).filter(UserModel.id == user_id).first()
    
    def find_user_by_email(self, email: str) -> Optional[UserModel]:
        """Find a user by their email address"""
        return self.session.query(UserModel).filter(UserModel.email == email).first()
    
    def find_user_by_username(self, username: str) -> Optional[UserModel]:
        """Find a user by their username"""
        return self.session.query(UserModel).filter(UserModel.username == username).first()
    
    def get_all_users(self) -> List[UserModel]:
        """Get all users"""
        return self.session.query(UserModel).all()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[UserModel]:
        """Update user information"""
        user = self.find_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.session.commit()
            return user
        
        return None
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user by their ID"""
        user = self.find_user_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        
        return False