"""
Scenario Use Cases
Domain service layer for scenario-related operations
"""

from typing import Optional, List
from src.adapters.database.repositories.scenario_repository import ScenarioRepository
from src.adapters.database.repositories.attempt_repository import AttemptRepository
from src.shared.exceptions import ValidationError, NotFoundError

class ScenarioUseCases:
    """Use cases for scenario operations"""
    
    def __init__(self, scenario_repository: ScenarioRepository, attempt_repository: AttemptRepository):
        self.scenario_repository = scenario_repository
        self.attempt_repository = attempt_repository
    
    def create_scenario(self, 
                       title: str, 
                       description: str, 
                       difficulty: str, 
                       category: str,
                       estimated_time: int,
                       max_score: int,
                       initial_state: dict,
                       correct_actions: list,
                       attack_indicators: list,
                       educational_content: dict,
                       created_by: int) -> dict:
        """Create a new training scenario"""
        # Validate input
        if not title or len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long")
        
        if not description or len(description) < 10:
            raise ValidationError("Description must be at least 10 characters long")
        
        if estimated_time <= 0:
            raise ValidationError("Estimated time must be greater than 0")
        
        if max_score <= 0:
            raise ValidationError("Max score must be greater than 0")
        
        # Create scenario
        scenario = self.scenario_repository.create_scenario(
            title=title,
            description=description,
            difficulty=difficulty,
            category=category,
            estimated_time=estimated_time,
            max_score=max_score,
            initial_state=initial_state,
            correct_actions=correct_actions,
            attack_indicators=attack_indicators,
            educational_content=educational_content,
            created_by=created_by
        )
        
        return scenario.to_dict()
    
    def get_scenario_by_id(self, scenario_id: int) -> Optional[dict]:
        """Get a specific scenario by ID"""
        scenario = self.scenario_repository.find_scenario_by_id(scenario_id)
        
        if scenario:
            return scenario.to_dict()
        
        return None
    
    def get_scenarios_by_category(self, category: str) -> List[dict]:
        """Get all scenarios by category"""
        scenarios = self.scenario_repository.find_scenarios_by_category(category)
        return [s.to_dict() for s in scenarios]
    
    def get_scenarios_by_difficulty(self, difficulty: str) -> List[dict]:
        """Get all scenarios by difficulty"""
        scenarios = self.scenario_repository.find_scenarios_by_difficulty(difficulty)
        return [s.to_dict() for s in scenarios]
    
    def get_all_scenarios(self) -> List[dict]:
        """Get all active scenarios"""
        scenarios = self.scenario_repository.get_all_scenarios()
        return [s.to_dict() for s in scenarios]
    
    def update_scenario(self, scenario_id: int, **kwargs) -> Optional[dict]:
        """Update a scenario"""
        scenario = self.scenario_repository.update_scenario(scenario_id, **kwargs)
        
        if scenario:
            return scenario.to_dict()
        
        return None
    
    def delete_scenario(self, scenario_id: int) -> bool:
        """Delete a scenario"""
        return self.scenario_repository.delete_scenario(scenario_id)