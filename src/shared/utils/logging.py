"""
Logging Utilities
Setup and configuration for application logging
"""

import logging
import os
from datetime import datetime
from flask import Flask

def setup_logging(app: Flask) -> None:
    """
    Setup logging for the Flask application
    
    Args:
        app: Flask application instance
    """
    if app.debug:
        # In debug mode, log to console
        app.logger.setLevel(logging.DEBUG)
        if not app.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
            handler.setFormatter(formatter)
            app.logger.addHandler(handler)
    else:
        # In production, log to file
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/banksec.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('BankSec startup')