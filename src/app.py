"""Flask application entrypoint"""
from src.entrypoints.api.app import create_app

app = create_app()
