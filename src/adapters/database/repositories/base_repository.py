"""
Base Repository Interface
Abstract base class for all repositories
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """Abstract base repository"""
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update existing entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    def list_all(self, page: int = 1, per_page: int = 20) -> List[T]:
        """List all entities with pagination"""
        pass
    
    @abstractmethod
    def count_all(self) -> int:
        """Count total entities"""
        pass
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[T]:
        """Filter entities by criteria"""
        pass