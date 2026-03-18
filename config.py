"""
Configuration for BankSec Enterprise Application
Different configurations for different environments
"""

import os
import secrets
from datetime import timedelta
from typing import Dict, List, Optional


class Config:
    """Base configuration class"""

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///banksec_enterprise.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # Application
    DEBUG = False
    TESTING = False

    # CORS
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or 'memory://'
    RATELIMIT_DEFAULT = "200 per day, 50 per hour, 10 per minute"

    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE')

    # Simulation
    SIMULATION_TIMEOUT = 300  # 5 minutes per simulation
    MAX_SIMULTANEOUS_SESSIONS = 3

    # Security
    MAX_LOGIN_ATTEMPTS = 5
    PASSWORD_RESET_TIMEOUT = 3600  # 1 hour

    # Training
    SCENARIO_DIFFICULTY_LEVELS = ['beginner', 'intermediate', 'advanced']
    TRAINING_MODULES = [
        'phishing_recognition',
        'transaction_verification',
        'credential_protection',
        'social_engineering_defense',
        'malware_identification'
    ]

    # Redis (for caching and sessions)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or REDIS_URL

    # Monitoring
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'false').lower() == 'true'
    METRICS_PORT = int(os.environ.get('METRICS_PORT', '9090'))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = True

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///banksec_dev.db'

    # CORS
    ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:5000', 'http://localhost:8080']

    # Session
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development

    # Rate Limiting (more lenient in development)
    RATELIMIT_DEFAULT = "1000 per day, 200 per hour, 50 per minute"

    # Logging
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Rate Limiting (disabled in tests)
    RATELIMIT_ENABLED = False

    # Logging
    LOG_LEVEL = 'ERROR'


class ProductionConfig(Config):
    """Production configuration"""

    # Security (must be set in environment)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

    # Database (PostgreSQL recommended)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable must be set in production")

    # Logging
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/var/log/banksec/app.log'

    # Monitoring
    ENABLE_METRICS = True


class StagingConfig(ProductionConfig):
    """Staging configuration (similar to production but with debug enabled)"""
    DEBUG = True
    LOG_LEVEL = 'INFO'
    ENABLE_METRICS = True


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """
    Get configuration instance

    Args:
        config_name: Configuration name (optional, defaults to FLASK_CONFIG env var)

    Returns:
        Configuration instance
    """
    config_name = config_name or os.environ.get('FLASK_CONFIG', 'default')

    if config_name not in config:
        raise ValueError(f"Invalid configuration: {config_name}")

    return config[config_name]()