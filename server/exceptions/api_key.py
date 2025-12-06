class ApiKeyException(Exception):
    """Base exception for API key related errors."""
    message = "API Key Exception occurred."
    status_code = 500

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)
        self.message = message or self.message

class ApiKeyAlreadyExists(ApiKeyException):
    """Exception raised when an API key already exists."""
    message = "API key already exists."
    status_code = 409

class ApiKeyNotFound(ApiKeyException):
    """Exception raised when an API key is not found."""
    message = "API key not found."
    status_code = 404

class ApiKeyDatabaseError(ApiKeyException):
    """Exception raised for database-related errors."""
    message = "Database error occurred while processing API key."
    status_code = 500