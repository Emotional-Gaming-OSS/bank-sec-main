"""
Database Models
Defines all SQLAlchemy models for the BankSec application
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    USER = "user"
    GUEST = "guest"

class ScenarioDifficulty(enum.Enum):
    """Scenario difficulty enumeration"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ScenarioCategory(enum.Enum):
    """Scenario category enumeration"""
    PHISHING = "phishing"
    TRANSACTION = "transaction"
    CREDENTIALS = "credentials"
    SOCIAL_ENGINEERING = "social_engineering"
    MALWARE = "malware"

class UserModel(db.Model):
    """User model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }

class ScenarioModel(db.Model):
    """Training scenario model"""
    __tablename__ = 'scenarios'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Enum(ScenarioDifficulty), nullable=False)
    category = db.Column(db.Enum(ScenarioCategory), nullable=False)
    estimated_time = db.Column(db.Integer, nullable=False)  # in seconds
    max_score = db.Column(db.Integer, nullable=False)
    initial_state = db.Column(db.JSON, nullable=False)
    correct_actions = db.Column(db.JSON, nullable=False)
    attack_indicators = db.Column(db.JSON, nullable=False)
    educational_content = db.Column(db.JSON, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationship
    creator = db.relationship('UserModel', backref=db.backref('created_scenarios', lazy=True))

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty.value,
            'category': self.category.value,
            'estimated_time': self.estimated_time,
            'max_score': self.max_score,
            'initial_state': self.initial_state,
            'correct_actions': self.correct_actions,
            'attack_indicators': self.attack_indicators,
            'educational_content': self.educational_content,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }

class AttemptModel(db.Model):
    """Training attempt model"""
    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    final_score = db.Column(db.Integer, default=0)
    max_possible_score = db.Column(db.Integer, nullable=False)
    actions_taken = db.Column(db.JSON, default=list)
    is_completed = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship('UserModel', backref=db.backref('attempts', lazy=True))
    scenario = db.relationship('ScenarioModel', backref=db.backref('attempts', lazy=True))

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scenario_id': self.scenario_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'final_score': self.final_score,
            'max_possible_score': self.max_possible_score,
            'actions_taken': self.actions_taken,
            'is_completed': self.is_completed
        }

class TrainingResultModel(db.Model):
    """Training result model"""
    __tablename__ = 'training_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    completion_time = db.Column(db.Integer)  # in seconds
    feedback = db.Column(db.JSON)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('UserModel', backref=db.backref('training_results', lazy=True))
    scenario = db.relationship('ScenarioModel', backref=db.backref('training_results', lazy=True))
    attempt = db.relationship('AttemptModel', backref=db.backref('results', lazy=True))

    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scenario_id': self.scenario_id,
            'attempt_id': self.attempt_id,
            'score': self.score,
            'completion_time': self.completion_time,
            'feedback': self.feedback,
            'completed_at': self.completed_at.isoformat()
        }