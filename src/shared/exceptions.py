"""
Shared Exceptions
Custom exception classes for the BankSec application
"""

class BankSecException(Exception):
    """Base exception for BankSec application"""
    status_code = 500

    def __init__(self, message, status_code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message

class ValidationError(BankSecException):
    """Exception raised for validation errors"""
    status_code = 400

    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}

class UnauthorizedError(BankSecException):
    """Exception raised for unauthorized access attempts"""
    status_code = 401

class NotFoundError(BankSecException):
    """Exception raised when a requested resource is not found"""
    status_code = 404

class DatabaseError(BankSecException):
    """Exception raised for database-related errors"""
    status_code = 500

class AuthenticationError(BankSecException):
    """Exception raised for authentication-related errors"""
    status_code = 401

class AuthorizationError(BankSecException):
    """Exception raised for authorization-related errors"""
    status_code = 403