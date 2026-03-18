"""
Database Configuration
PostgreSQL with connection pooling and PgBouncer compatibility
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator, Optional
import os

from src.config import get_config
from src.shared.exceptions import DatabaseError
from src.shared.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Database connection manager with pooling and session management"""
    
    def __init__(self):
        self.config = get_config()
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database engine with connection pooling"""
        database_url = self.config.SQLALCHEMY_DATABASE_URI
        
        # Connection pool configuration
        pool_config = {
            'poolclass': QueuePool,
            'pool_size': self.config.SQLALCHEMY_ENGINE_OPTIONS.get('pool_size', 10),
            'pool_recycle': self.config.SQLALCHEMY_ENGINE_OPTIONS.get('pool_recycle', 3600),
            'pool_pre_ping': self.config.SQLALCHEMY_ENGINE_OPTIONS.get('pool_pre_ping', True),
            'max_overflow': 20,
            'pool_timeout': 30,
        }
        
        # Additional PostgreSQL-specific options
        if database_url.startswith('postgresql'):
            pool_config.update({
                'executemany_mode': 'values_plus_batch',
                'executemany_values_page_size': 1000,
                'executemany_batch_page_size': 500,
            })
        
        # Create engine
        self.engine = create_engine(
            database_url,
            **pool_config
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database engine created for {database_url.split('@')[-1]}")
    
    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """
        Get database session context manager
        
        Yields:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            session.close()
    
    def get_session(self) -> Session:
        """
        Get database session (manual management required)
        
        Returns:
            Database session
        """
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close database session"""
        try:
            session.close()
        except Exception as e:
            logger.error(f"Error closing session: {e}")
    
    def execute_raw_sql(self, sql: str, params: Optional[dict] = None) -> None:
        """
        Execute raw SQL query
        
        Args:
            sql: SQL query string
            params: Query parameters
        """
        with self.get_db_session() as session:
            session.execute(sql, params or {})
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_db_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get database connection information"""
        return {
            'url': self.config.SQLALCHEMY_DATABASE_URI,
            'pool_size': self.config.SQLALCHEMY_ENGINE_OPTIONS.get('pool_size', 10),
            'pool_recycle': self.config.SQLALCHEMY_ENGINE_OPTIONS.get('pool_recycle', 3600),
            'engine': str(self.engine.url) if self.engine else None
        }
    
    def get_pool_status(self) -> dict:
        """Get connection pool status"""
        if not self.engine:
            return {}
        
        pool = self.engine.pool
        return {
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'timeout': pool.timeout()
        }
    
    def create_tables(self):
        """Create all database tables"""
        from src.adapters.database.models import Base
        
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise DatabaseError(f"Failed to create tables: {e}")
    
    def drop_tables(self):
        """Drop all database tables (use with caution)"""
        from src.adapters.database.models import Base
        
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise DatabaseError(f"Failed to drop tables: {e}")


# Global database manager instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db_session() -> Session:
    """Get database session (convenience function)"""
    return get_db_manager().get_session()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    db_manager = get_db_manager()
    with db_manager.get_db_session() as session:
        yield session


def init_database():
    """Initialize database (create tables if they don't exist)"""
    db_manager = get_db_manager()
    
    # Test connection
    if not db_manager.test_connection():
        raise DatabaseError("Failed to connect to database")
    
    # Create tables
    db_manager.create_tables()
    
    logger.info("Database initialized successfully")


def reset_database():
    """Reset database (drop and recreate tables - use with caution)"""
    db_manager = get_db_manager()
    
    # Confirm in production
    config = get_config()
    if config.FLASK_ENV == 'production':
        confirm = input("Are you sure you want to reset the database? (yes/no): ")
        if confirm.lower() != 'yes':
            logger.info("Database reset cancelled")
            return
    
    db_manager.drop_tables()
    db_manager.create_tables()
    
    logger.info("Database reset successfully")


def get_database_health() -> dict:
    """Get database health status"""
    db_manager = get_db_manager()
    
    health = {
        'connected': False,
        'pool_status': {},
        'connection_info': {}
    }
    
    try:
        health['connected'] = db_manager.test_connection()
        health['pool_status'] = db_manager.get_pool_status()
        health['connection_info'] = db_manager.get_connection_info()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health['error'] = str(e)
    
    return health