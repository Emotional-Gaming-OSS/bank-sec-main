"""
Main Flask Application - REST API
Enterprise-grade Flask application with proper error handling
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import os
from datetime import timedelta

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import configuration
from config import get_config

from src.entrypoints.api.routes import register_routes
from src.shared.exceptions import (
    BankSecException,
    ValidationError,
    UnauthorizedError,
    NotFoundError
)
from src.shared.utils.logging import setup_logging

# Initialize extensions (but don't instantiate them until the app is created)
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name: str = 'development') -> Flask:
    """
    Application factory
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_instance = get_config(config_name)
    app.config.from_object(config_instance)
    
    # Initialize extensions
    _init_extensions(app)
    
    # Register routes
    register_routes(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Setup logging
    setup_logging(app)

    # Initialize database (skip in serverless environments like Vercel)
    if not os.environ.get('VERCEL'):
        with app.app_context():
            try:
                db.create_all()
            except Exception as e:
                app.logger.warning(f"Database initialization skipped: {e}")
        # _init_sample_data()  # Temporarily disabled until db is properly initialized

    return app

def _init_extensions(app: Flask) -> None:
    """Initialize Flask extensions"""
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # CORS
    CORS(app, 
         origins=app.config.get('ALLOWED_ORIGINS', ['http://localhost:3000']),
         supports_credentials=True)
    
    # Rate limiting
    limiter.init_app(app)
    
    # Logging
    if not app.debug:
        _setup_production_logging(app)

def _setup_production_logging(app: Flask) -> None:
    """Setup production logging"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = logging.RotatingFileHandler(
        'logs/banksec.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('BankSec startup')

def _register_error_handlers(app: Flask) -> None:
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors"""
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood or was missing required parameters.'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle unauthorized errors"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication credentials were missing or incorrect.'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle forbidden errors"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource could not be found.'
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limit errors"""
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle internal server errors"""
        app.logger.error(f'Internal server error: {error}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500
    
    # Custom exception handlers
    @app.errorhandler(BankSecException)
    def handle_banksec_exception(error):
        """Handle custom BankSec exceptions"""
        return jsonify({
            'error': error.__class__.__name__,
            'message': str(error)
        }), error.status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors"""
        return jsonify({
            'error': 'Validation Error',
            'message': str(error),
            'details': error.details if hasattr(error, 'details') else None
        }), 400
    
    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized_error(error):
        """Handle unauthorized errors"""
        return jsonify({
            'error': 'Unauthorized',
            'message': str(error)
        }), 401
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        """Handle not found errors"""
        return jsonify({
            'error': 'Not Found',
            'message': str(error)
        }), 404

def _init_sample_data() -> None:
    """Initialize sample data if database is empty"""
    from src.adapters.database.models import UserModel, ScenarioModel
    from src.domain.models.user import UserRole
    from src.domain.models.scenario import ScenarioDifficulty, ScenarioCategory
    
    # Create default instructor if no users exist
    if UserModel.query.count() == 0:
        from src.service.use_cases.user_use_cases import UserUseCases
        from src.adapters.database.repositories.user_repository import UserRepository
        
        user_repo = UserRepository(db.session)
        user_use_cases = UserUseCases(user_repo)
        
        try:
            user_use_cases.register_user(
                username='instructor',
                email='instructor@banksec.edu',
                password='ChangeThisPassword123!',
                role='instructor'
            )
        except Exception as e:
            print(f"Failed to create instructor: {e}")
    
    # Create sample scenarios if none exist
    if ScenarioModel.query.count() == 0:
        from src.service.use_cases.scenario_use_cases import ScenarioUseCases
        from src.adapters.database.repositories.scenario_repository import ScenarioRepository
        from src.adapters.database.repositories.attempt_repository import AttemptRepository
        
        scenario_repo = ScenarioRepository(db.session)
        attempt_repo = AttemptRepository(db.session)
        scenario_use_cases = ScenarioUseCases(scenario_repo, attempt_repo)
        
        try:
            # Get instructor ID
            instructor = UserModel.query.filter_by(role='instructor').first()
            instructor_id = instructor.id if instructor else 1
            
            # Create sample scenarios
            _create_sample_scenarios(scenario_use_cases, instructor_id)
        except Exception as e:
            print(f"Failed to create sample scenarios: {e}")

def _create_sample_scenarios(scenario_use_cases: 'ScenarioUseCases', instructor_id: int) -> None:
    """Create sample training scenarios"""
    scenarios = [
        {
            'title': 'Phishing Attempt Detection',
            'description': 'Identify and respond to a sophisticated phishing campaign targeting bank employees',
            'difficulty': 'beginner',
            'category': 'phishing',
            'estimated_time': 900,
            'max_score': 100,
            'initial_state': {
                'attack_pattern': 'credential_theft',
                'suspicious_count': 3,
                'attack_source': 'external',
                'timeframe': '48_hours'
            },
            'correct_actions': [
                {
                    'type': 'verify_email_source',
                    'points': 15,
                    'feedback': 'Correct! Always verify email sender addresses',
                    'error_feedback': 'Always check the actual email address, not just display name'
                },
                {
                    'type': 'report_phishing',
                    'points': 20,
                    'feedback': 'Good! All suspected phishing should be reported immediately',
                    'error_feedback': 'Phishing attempts must be reported to security team'
                },
                {
                    'type': 'do_not_click_links',
                    'points': 15,
                    'feedback': 'Correct! Never click links in suspicious emails',
                    'error_feedback': 'Links in suspicious emails can lead to malware'
                }
            ],
            'attack_indicators': [
                'suspicious_sender_domain',
                'urgent_language',
                'request_for_credentials',
                'mismatched_urls',
                'poor_grammar'
            ],
            'educational_content': {
                'learning_objectives': [
                    'Identify phishing email characteristics',
                    'Understand proper reporting procedures',
                    'Recognize social engineering tactics'
                ],
                'resources': [
                    'Phishing Identification Guide',
                    'Incident Response Protocol',
                    'Social Engineering Defense Handbook'
                ],
                'real_world_examples': [
                    {
                        'case': '2016 Bangladesh Bank heist',
                        'description': 'Attackers used phishing to gain credentials and attempt $1 billion transfer',
                        'lesson': 'Importance of multi-factor authentication and transaction limits'
                    }
                ]
            }
        }
    ]
    
    for scenario_data in scenarios:
        try:
            scenario_use_cases.create_scenario(
                **scenario_data,
                created_by=instructor_id
            )
        except Exception as e:
            print(f"Failed to create scenario '{scenario_data['title']}': {e}")


# Application entry point
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)