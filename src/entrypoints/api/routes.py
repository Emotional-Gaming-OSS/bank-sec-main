"""
API Routes Definition
Defines all API endpoints for the BankSec application
"""

from flask import Flask, Blueprint


def register_routes(app: Flask) -> None:
    """
    Register all API routes with the Flask application
    
    Args:
        app: Flask application instance
    """
    # Create a blueprint for API routes
    api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
    
    # Import and register route modules
    from .auth_routes import auth_bp
    from .user_routes import user_bp
    from .scenario_routes import scenario_bp
    from .training_routes import training_bp
    from .admin_routes import admin_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(scenario_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(admin_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'BankSec Enterprise Simulator'}