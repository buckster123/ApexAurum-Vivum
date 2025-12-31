"""
Custom Error Classes for Apex Aurum

Categorizes errors into:
- Retryable: Should be automatically retried (rate limits, server errors)
- UserFixable: User can fix (auth errors, invalid requests)
- Fatal: Cannot continue (unexpected errors)
"""

from typing import Optional


class ApexAurumError(Exception):
    """Base exception for all Apex Aurum errors"""
    pass


class RetryableError(ApexAurumError):
    """
    Error that should be automatically retried with exponential backoff.

    Examples:
    - Rate limit errors
    - Server overload (5xx errors)
    - Temporary network issues
    """

    def __init__(self, message: str, retry_after: Optional[float] = None, original_error: Optional[Exception] = None):
        """
        Initialize retryable error.

        Args:
            message: Human-readable error message
            retry_after: Seconds to wait before retry (from API headers)
            original_error: The original exception that was caught
        """
        super().__init__(message)
        self.retry_after = retry_after
        self.original_error = original_error


class UserFixableError(ApexAurumError):
    """
    Error that the user can fix by taking action.

    Examples:
    - Invalid API key
    - Insufficient permissions
    - Malformed request
    """

    def __init__(self, message: str, help_text: Optional[str] = None, original_error: Optional[Exception] = None):
        """
        Initialize user-fixable error.

        Args:
            message: Human-readable error message
            help_text: Specific guidance on how to fix the issue
            original_error: The original exception that was caught
        """
        super().__init__(message)
        self.help_text = help_text
        self.original_error = original_error


class FatalError(ApexAurumError):
    """
    Fatal error that cannot be recovered from.

    Examples:
    - Unexpected exceptions
    - System-level errors
    - Invalid configuration
    """

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Initialize fatal error.

        Args:
            message: Human-readable error message
            original_error: The original exception that was caught
        """
        super().__init__(message)
        self.original_error = original_error
