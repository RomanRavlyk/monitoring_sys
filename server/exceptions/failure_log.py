

class FailureLogException(Exception):
    """Exception raised for failures in the service layer."""
    status_code = 500
    message = "Failure log Exception occurred."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)
        self.message = message or self.message

class FailureLogNotFound(FailureLogException):
    """Exception raised when a failure log is not found."""
    status_code = 404
    message = "Failure log not found."


class FailureLogDatabaseError(FailureLogException):
    """Exception raised for database-related errors."""
    status_code = 500
    message = "Database error occurred while processing failure log."

class FailureLogRequestSendingError(FailureLogException):
    """Exception raised for invalid request sent to a monitoring system."""
    status_code = 502
    message = "Failed to send request to monitoring system."