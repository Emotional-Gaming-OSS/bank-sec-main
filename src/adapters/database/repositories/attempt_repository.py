"""
Attempt Repository
Data access layer for attempt operations
"""

from typing import Optional, List
from src.adapters.database.models import AttemptModel, db

class AttemptRepository:
    """Repository for attempt data operations"""
    
    def __init__(self, session):
        self.session = session
    
    def create_attempt(self, 
                      user_id: int, 
                      scenario_id: int,
                      max_possible_score: int) -> AttemptModel:
        """Create a new attempt in the database"""
        attempt = AttemptModel(
            user_id=user_id,
            scenario_id=scenario_id,
            max_possible_score=max_possible_score
        )
        
        self.session.add(attempt)
        self.session.commit()
        
        return attempt
    
    def find_attempt_by_id(self, attempt_id: int) -> Optional[AttemptModel]:
        """Find an attempt by its ID"""
        return self.session.query(AttemptModel).filter(AttemptModel.id == attempt_id).first()
    
    def find_attempts_by_user(self, user_id: int) -> List[AttemptModel]:
        """Find all attempts by a specific user"""
        return self.session.query(AttemptModel).filter(AttemptModel.user_id == user_id).all()
    
    def find_attempts_by_scenario(self, scenario_id: int) -> List[AttemptModel]:
        """Find all attempts for a specific scenario"""
        return self.session.query(AttemptModel).filter(AttemptModel.scenario_id == scenario_id).all()
    
    def update_attempt(self, attempt_id: int, **kwargs) -> Optional[AttemptModel]:
        """Update attempt information"""
        attempt = self.find_attempt_by_id(attempt_id)
        if attempt:
            for key, value in kwargs.items():
                if hasattr(attempt, key):
                    setattr(attempt, key, value)
            
            self.session.commit()
            return attempt
        
        return None
    
    def delete_attempt(self, attempt_id: int) -> bool:
        """Delete an attempt by its ID"""
        attempt = self.find_attempt_by_id(attempt_id)
        if attempt:
            self.session.delete(attempt)
            self.session.commit()
            return True
        
        return False