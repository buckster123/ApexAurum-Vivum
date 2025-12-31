"""
Error Message Translator

Converts technical API errors into user-friendly messages with:
- Clear titles with emojis
- Understandable explanations
- Actionable guidance
"""

from typing import Dict, Any
import anthropic

# Import specific error classes (some may be in _exceptions)
try:
    from anthropic._exceptions import OverloadedError
except ImportError:
    # Fallback if not available - use InternalServerError
    OverloadedError = anthropic.InternalServerError


# Error message templates
ERROR_MESSAGES = {
    "authentication_error": {
        "title": "🔑 Authentication Failed",
        "message": "Your API key is invalid or has expired.",
        "action": "Please check your ANTHROPIC_API_KEY in the .env file.",
        "severity": "error"
    },
    "permission_denied": {
        "title": "🚫 Permission Denied",
        "message": "Your API key doesn't have permission for this operation.",
        "action": "Please check your account permissions or contact Anthropic support.",
        "severity": "error"
    },
    "rate_limit_error": {
        "title": "⏱️ Rate Limit Reached",
        "message": "Too many requests in a short time. Please wait a moment.",
        "action": "Retrying automatically with exponential backoff...",
        "severity": "warning"
    },
    "overloaded_error": {
        "title": "🚦 Claude is Busy",
        "message": "Claude's servers are experiencing high demand right now.",
        "action": "Retrying automatically in a few seconds...",
        "severity": "warning"
    },
    "invalid_request_error": {
        "title": "❌ Invalid Request",
        "message": "There's a problem with the request format.",
        "action": "Please check your message and try again.",
        "severity": "error"
    },
    "not_found_error": {
        "title": "🔍 Not Found",
        "message": "The requested model or endpoint could not be found.",
        "action": "Please check your model selection and try again.",
        "severity": "error"
    },
    "api_connection_error": {
        "title": "🌐 Connection Error",
        "message": "Unable to connect to Claude's API servers.",
        "action": "Please check your internet connection. Retrying...",
        "severity": "warning"
    },
    "api_status_error_5xx": {
        "title": "🔧 Server Error",
        "message": "Claude's servers encountered an error (5xx).",
        "action": "This is usually temporary. Retrying automatically...",
        "severity": "warning"
    },
    "api_status_error_4xx": {
        "title": "⚠️ Request Error",
        "message": "There's an issue with the request (4xx error).",
        "action": "Please check your input and try again.",
        "severity": "error"
    },
    "timeout_error": {
        "title": "⏰ Request Timeout",
        "message": "The request took too long to complete.",
        "action": "Try a shorter message or fewer tools.",
        "severity": "error"
    },
    "unknown_error": {
        "title": "❓ Unknown Error",
        "message": "An unexpected error occurred.",
        "action": "Please try again or check the logs for details.",
        "severity": "error"
    },
    "max_retries_exceeded": {
        "title": "🔄 Max Retries Exceeded",
        "message": "Attempted multiple retries but the request still failed.",
        "action": "Please try again later or contact support if this persists.",
        "severity": "error"
    }
}


def get_user_friendly_message(error: Exception) -> Dict[str, Any]:
    """
    Convert an exception into a user-friendly message.

    Args:
        error: The exception to convert

    Returns:
        Dictionary with title, message, action, and severity
    """
    # Authentication errors
    if isinstance(error, anthropic.AuthenticationError):
        return ERROR_MESSAGES["authentication_error"]

    # Permission errors
    if isinstance(error, anthropic.PermissionDeniedError):
        return ERROR_MESSAGES["permission_denied"]

    # Rate limit errors
    if isinstance(error, anthropic.RateLimitError):
        msg = ERROR_MESSAGES["rate_limit_error"].copy()
        # Try to extract retry_after from error
        if hasattr(error, 'response') and hasattr(error.response, 'headers'):
            retry_after = error.response.headers.get('retry-after')
            if retry_after:
                msg["action"] = f"Please wait {retry_after} seconds before retrying."
        return msg

    # Overloaded errors (using imported OverloadedError)
    if isinstance(error, OverloadedError):
        return ERROR_MESSAGES["overloaded_error"]

    # Invalid request errors (BadRequestError is the actual class name)
    if isinstance(error, anthropic.BadRequestError):
        msg = ERROR_MESSAGES["invalid_request_error"].copy()
        # Add specific error details if available
        if hasattr(error, 'message'):
            msg["message"] = f"Invalid request: {error.message}"
        return msg

    # Not found errors
    if isinstance(error, anthropic.NotFoundError):
        return ERROR_MESSAGES["not_found_error"]

    # Connection errors
    if isinstance(error, anthropic.APIConnectionError):
        return ERROR_MESSAGES["api_connection_error"]

    # Unprocessable entity errors (422)
    if isinstance(error, anthropic.UnprocessableEntityError):
        msg = ERROR_MESSAGES["invalid_request_error"].copy()
        msg["message"] = "The request was well-formed but couldn't be processed."
        if hasattr(error, 'message'):
            msg["message"] = f"Validation error: {error.message}"
        return msg

    # API status errors
    if isinstance(error, anthropic.APIStatusError):
        if hasattr(error, 'status_code'):
            if 500 <= error.status_code < 600:
                msg = ERROR_MESSAGES["api_status_error_5xx"].copy()
                msg["message"] = f"Server error ({error.status_code}): {error.message}"
                return msg
            elif 400 <= error.status_code < 500:
                msg = ERROR_MESSAGES["api_status_error_4xx"].copy()
                msg["message"] = f"Client error ({error.status_code}): {error.message}"
                return msg

    # Timeout errors
    if isinstance(error, TimeoutError):
        return ERROR_MESSAGES["timeout_error"]

    # Custom errors from our retry handler
    from .errors import RetryableError, UserFixableError, FatalError

    if isinstance(error, RetryableError):
        if "max retries" in str(error).lower():
            return ERROR_MESSAGES["max_retries_exceeded"]
        return ERROR_MESSAGES["rate_limit_error"]

    if isinstance(error, UserFixableError):
        msg = ERROR_MESSAGES["invalid_request_error"].copy()
        if error.help_text:
            msg["action"] = error.help_text
        return msg

    if isinstance(error, FatalError):
        msg = ERROR_MESSAGES["unknown_error"].copy()
        msg["message"] = str(error)
        return msg

    # Default fallback
    msg = ERROR_MESSAGES["unknown_error"].copy()
    msg["message"] = f"Unexpected error: {str(error)}"
    return msg


def format_error_for_display(error: Exception, include_details: bool = False) -> str:
    """
    Format an error for display in the UI.

    Args:
        error: The exception to format
        include_details: Whether to include technical details

    Returns:
        Formatted error string with markdown
    """
    msg_dict = get_user_friendly_message(error)

    # Build formatted message
    lines = [
        f"### {msg_dict['title']}",
        "",
        msg_dict['message'],
        "",
        f"**What to do:** {msg_dict['action']}"
    ]

    # Add technical details if requested
    if include_details:
        lines.extend([
            "",
            "---",
            "",
            "**Technical details:**",
            f"```\n{type(error).__name__}: {str(error)}\n```"
        ])

    return "\n".join(lines)
