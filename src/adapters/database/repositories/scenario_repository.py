"""
Scenario Repository
Data access layer for scenario operations
"""

from typing import Optional, List
from src.adapters.database.models import ScenarioModel, db
from src.domain.models.scenario import ScenarioDifficulty, ScenarioCategory

class ScenarioRepository:
    """Repository for scenario data operations"""
    
    def __init__(self, session):
        self.session = session
    
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
                       created_by: int) -> ScenarioModel:
        """Create a new scenario in the database"""
        scenario = ScenarioModel(
            title=title,
            description=description,
            difficulty=ScenarioDifficulty[difficulty.upper()] if difficulty.upper() in ScenarioDifficulty.__members__ else ScenarioDifficulty.INTERMEDIATE,
            category=ScenarioCategory[category.upper()] if category.upper() in ScenarioCategory.__members__ else ScenarioCategory.PHISHING,
            estimated_time=estimated_time,
            max_score=max_score,
            initial_state=initial_state,
            correct_actions=correct_actions,
            attack_indicators=attack_indicators,
            educational_content=educational_content,
            created_by=created_by
        )
        
        self.session.add(scenario)
        self.session.commit()
        
        return scenario
    
    def find_scenario_by_id(self, scenario_id: int) -> Optional[ScenarioModel]:
        """Find a scenario by its ID"""
        return self.session.query(ScenarioModel).filter(ScenarioModel.id == scenario_id).first()
    
    def find_scenarios_by_category(self, category: str) -> List[ScenarioModel]:
        """Find all scenarios by category"""
        cat_enum = ScenarioCategory[category.upper()] if category.upper() in ScenarioCategory.__members__ else ScenarioCategory.PHISHING
        return self.session.query(ScenarioModel).filter(ScenarioModel.category == cat_enum).all()
    
    def find_scenarios_by_difficulty(self, difficulty: str) -> List[ScenarioModel]:
        """Find all scenarios by difficulty"""
        diff_enum = ScenarioDifficulty[difficulty.upper()] if difficulty.upper() in ScenarioDifficulty.__members__ else ScenarioDifficulty.INTERMEDIATE
        return self.session.query(ScenarioModel).filter(ScenarioModel.difficulty == diff_enum).all()
    
    def get_all_scenarios(self) -> List[ScenarioModel]:
        """Get all active scenarios"""
        return self.session.query(ScenarioModel).filter(ScenarioModel.is_active == True).all()
    
    def update_scenario(self, scenario_id: int, **kwargs) -> Optional[ScenarioModel]:
        """Update scenario information"""
        scenario = self.find_scenario_by_id(scenario_id)
        if scenario:
            for key, value in kwargs.items():
                if hasattr(scenario, key):
                    setattr(scenario, key, value)
            
            self.session.commit()
            return scenario
        
        return None
    
    def delete_scenario(self, scenario_id: int) -> bool:
        """Delete a scenario by its ID"""
        scenario = self.find_scenario_by_id(scenario_id)
        if scenario:
            self.session.delete(scenario)
            self.session.commit()
            return True
        
        return False