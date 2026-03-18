"""Flask application entrypoint for Vercel serverless"""
import os

# Set VERCEL flag for serverless environment
os.environ.setdefault('VERCEL', '1')

from src.entrypoints.api.app import create_app

# Lazy initialization for serverless
app = create_app()
