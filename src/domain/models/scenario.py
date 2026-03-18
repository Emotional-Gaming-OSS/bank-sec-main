"""
Scenario Domain Model
Domain-level representation of scenario entities
"""

from enum import Enum

class ScenarioDifficulty(Enum):
    """Scenario difficulty enumeration for domain model"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ScenarioCategory(Enum):
    """Scenario category enumeration for domain model"""
    PHISHING = "phishing"
    TRANSACTION = "transaction"
    CREDENTIALS = "credentials"
    SOCIAL_ENGINEERING = "social_engineering"
    MALWARE = "malware"