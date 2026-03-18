"""
Session Manager
Redis-based session management with database fallback
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from src.adapters.cache.redis_cache import get_cache_manager
from src.adapters.database.repositories.session_repository import SessionRepository
from src.domain.models.user import User
from src.shared.utils.logging import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages user sessions with Redis primary storage and PostgreSQL fallback"""
    
    def __init__(self, 
                 cache_manager=None,
                 session_repository: Optional[SessionRepository] = None):
        """
        Initialize session manager
        
        Args:
            cache_manager: Redis cache manager instance
            session_repository: Session repository for database fallback
        """
        self.cache_manager = cache_manager or get_cache_manager()
        self.session_repository = session_repository
    
    def create_session(self, 
                      user: User,
                      ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None,
                      ttl: int = 3600) -> str:
        """
        Create new user session
        
        Args:
            user: User instance
            ip_address: Client IP address
            user_agent: Client user agent
            ttl: Session TTL in seconds
        
        Returns:
            Session token
        """
        session_token = str(uuid.uuid4())
        refresh_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        # Session data
        session_data = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'expires_at': expires_at.isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store in Redis (primary)
        redis_key = f"session:{session_token}"
        self.cache_manager.redis.set(redis_key, session_data, ex=ttl)
        
        # Store in database (fallback)
        if self.session_repository:
            try:
                from src.adapters.database.models import UserSession
                
                db_session = UserSession(
                    user_id=user.id,
                    session_token=session_token,
                    refresh_token=refresh_token,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    expires_at=expires_at,
                    is_active=True
                )
                self.session_repository.create(db_session)
            except Exception as e:
                logger.error(f"Failed to store session in database: {e}")
        
        logger.info(f"Session created for user {user.username}")
        return session_token
    
    def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        
        Args:
            session_token: Session token
        
        Returns:
            Session data or None if not found/expired
        """
        # Try Redis first (primary storage)
        redis_key = f"session:{session_token}"
        session_data = self.cache_manager.redis.get(redis_key)
        
        if session_data:
            # Check expiration
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.utcnow() > expires_at:
                # Session expired
                self.delete_session(session_token)
                return None
            
            return session_data
        
        # Fallback to database
        if self.session_repository:
            try:
                db_session = self.session_repository.get_by_token(session_token)
                if db_session and db_session.is_active:
                    # Check expiration
                    if datetime.utcnow() > db_session.expires_at:
                        self.delete_session(session_token)
                        return None
                    
                    # Convert to session data format
                    session_data = {
                        'user_id': db_session.user_id,
                        'ip_address': db_session.ip_address,
                        'user_agent': db_session.user_agent,
                        'expires_at': db_session.expires_at.isoformat(),
                        'created_at': db_session.created_at.isoformat()
                    }
                    
                    # Cache in Redis for future requests
                    ttl = int((db_session.expires_at - datetime.utcnow()).total_seconds())
                    if ttl > 0:
                        self.cache_manager.redis.set(redis_key, session_data, ex=ttl)
                    
                    return session_data
            except Exception as e:
                logger.error(f"Failed to get session from database: {e}")
        
        return None
    
    def delete_session(self, session_token: str) -> bool:
        """
        Delete session
        
        Args:
            session_token: Session token
        
        Returns:
            True if deleted, False otherwise
        """
        # Delete from Redis
        redis_key = f"session:{session_token}"
        redis_deleted = self.cache_manager.redis.delete(redis_key)
        
        # Delete from database
        db_deleted = True
        if self.session_repository:
            try:
                db_session = self.session_repository.get_by_token(session_token)
                if db_session:
                    db_session.is_active = False
                    self.session_repository.update(db_session)
            except Exception as e:
                logger.error(f"Failed to delete session from database: {e}")
                db_deleted = False
        
        logger.info(f"Session deleted: {session_token}")
        return redis_deleted and db_deleted
    
    def refresh_session(self, session_token: str, ttl: int = 3600) -> bool:
        """
        Refresh session TTL
        
        Args:
            session_token: Session token
            ttl: New TTL in seconds
        
        Returns:
            True if refreshed, False otherwise
        """
        session_data = self.get_session(session_token)
        if not session_data:
            return False
        
        # Update expiration
        new_expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        session_data['expires_at'] = new_expires_at.isoformat()
        
        # Update in Redis
        redis_key = f"session:{session_token}"
        redis_updated = self.cache_manager.redis.set(redis_key, session_data, ex=ttl)
        
        # Update in database
        db_updated = True
        if self.session_repository:
            try:
                db_session = self.session_repository.get_by_token(session_token)
                if db_session:
                    db_session.expires_at = new_expires_at
                    self.session_repository.update(db_session)
            except Exception as e:
                logger.error(f"Failed to refresh session in database: {e}")
                db_updated = False
        
        return redis_updated and db_updated
    
    def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all active sessions for user
        
        Args:
            user_id: User ID
        
        Returns:
            List of session data
        """
        sessions = []
        
        # Get from database (more reliable for listing)
        if self.session_repository:
            try:
                db_sessions = self.session_repository.get_by_user_id(user_id, active_only=True)
                for db_session in db_sessions:
                    # Check if still active
                    if datetime.utcnow() <= db_session.expires_at:
                        session_data = {
                            'session_token': db_session.session_token,
                            'user_id': db_session.user_id,
                            'ip_address': db_session.ip_address,
                            'user_agent': db_session.user_agent,
                            'expires_at': db_session.expires_at.isoformat(),
                            'created_at': db_session.created_at.isoformat()
                        }
                        sessions.append(session_data)
            except Exception as e:
                logger.error(f"Failed to get user sessions from database: {e}")
        
        return sessions
    
    def delete_all_user_sessions(self, user_id: int) -> int:
        """
        Delete all sessions for user
        
        Args:
            user_id: User ID
        
        Returns:
            Number of sessions deleted
        """
        deleted_count = 0
        
        # Get user's sessions
        sessions = self.get_user_sessions(user_id)
        
        # Delete each session
        for session in sessions:
            if self.delete_session(session['session_token']):
                deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} sessions for user {user_id}")
        return deleted_count
    
    def cleanup_expired_sessions(self) -> int:
        """
        Cleanup expired sessions
        
        Returns:
            Number of sessions cleaned up
        """
        cleaned_count = 0
        
        # Cleanup database sessions
        if self.session_repository:
            try:
                expired_sessions = self.session_repository.get_expired_sessions()
                for session in expired_sessions:
                    session.is_active = False
                    self.session_repository.update(session)
                    cleaned_count += 1
            except Exception as e:
                logger.error(f"Failed to cleanup expired sessions: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} expired sessions")
        return cleaned_count
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate secure session token"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_refresh_token() -> str:
        """Generate secure refresh token"""
        return str(uuid.uuid4())


# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    global _session_manager
    if _session_manager is None:
        from src.adapters.database.repositories.session_repository import SessionRepository
        from src.adapters.database.database import get_db_session
        
        db_session = get_db_session()
        session_repo = SessionRepository(db_session)
        cache_mgr = get_cache_manager()
        
        _session_manager = SessionManager(cache_mgr, session_repo)
    
    return _session_manager