"""
Retry Handler with Exponential Backoff

Provides decorator for automatic retry logic with:
- Exponential backoff (1s, 2s, 4s, 8s, 16s)
- Jitter to prevent thundering herd
- Respect for Retry-After headers
- Configurable max retries
- Detailed logging
"""

import time
import random
import logging
from functools import wraps
from typing import Callable, Optional, Tuple, Type
import anthropic

from .errors import RetryableError, UserFixableError, FatalError

logger = logging.getLogger(__name__)


def extract_retry_after(error: Exception) -> Optional[float]:
    """
    Extract retry_after value from API error headers.

    Args:
        error: The API error exception

    Returns:
        Seconds to wait, or None if not available
    """
    # Check if it's an Anthropic RateLimitError with headers
    if isinstance(error, anthropic.RateLimitError):
        # Try to extract from response headers
        if hasattr(error, 'response') and hasattr(error.response, 'headers'):
            retry_after = error.response.headers.get('retry-after')
            if retry_after:
                try:
                    return float(retry_after)
                except (ValueError, TypeError):
                    pass

    return None


def classify_error(error: Exception) -> Tuple[str, Optional[float]]:
    """
    Classify an error and determine if it should be retried.

    Args:
        error: The exception to classify

    Returns:
        Tuple of (error_type, retry_after)
        error_type: 'retryable', 'user_fixable', or 'fatal'
        retry_after: Seconds to wait (for retryable errors)
    """
    # Retryable errors
    if isinstance(error, anthropic.RateLimitError):
        retry_after = extract_retry_after(error)
        return ('retryable', retry_after)

    if isinstance(error, anthropic.APIStatusError):
        # 529 (overloaded) and 5xx errors are retryable (server errors)
        if hasattr(error, 'status_code'):
            if error.status_code == 529 or (500 <= error.status_code < 600):
                return ('retryable', None)
        # 4xx errors are usually user-fixable
        return ('user_fixable', None)

    if isinstance(error, anthropic.APIConnectionError):
        # Network issues are retryable
        return ('retryable', None)

    # User-fixable errors
    if isinstance(error, anthropic.AuthenticationError):
        return ('user_fixable', None)

    if isinstance(error, anthropic.PermissionDeniedError):
        return ('user_fixable', None)

    if isinstance(error, anthropic.BadRequestError):
        return ('user_fixable', None)

    if isinstance(error, anthropic.NotFoundError):
        return ('user_fixable', None)

    # Everything else is fatal
    return ('fatal', None)


def calculate_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 32.0) -> float:
    """
    Calculate exponential backoff with jitter.

    Args:
        attempt: Retry attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds with jitter applied
    """
    # Exponential: 1s, 2s, 4s, 8s, 16s, 32s
    delay = min(base_delay * (2 ** attempt), max_delay)

    # Add jitter (±25% randomness to prevent thundering herd)
    jitter = delay * 0.25 * (random.random() * 2 - 1)
    delay_with_jitter = delay + jitter

    return max(0.1, delay_with_jitter)  # Minimum 0.1s


def retry_on_error(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 32.0,
    retry_callback: Optional[Callable[[int, float], None]] = None
):
    """
    Decorator for automatic retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay for exponential backoff (seconds)
        max_delay: Maximum delay between retries (seconds)
        retry_callback: Optional callback(attempt, delay) called before each retry

    Example:
        @retry_on_error(max_retries=3, base_delay=1.0)
        def call_api():
            return client.messages.create(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    # Try the function
                    return func(*args, **kwargs)

                except Exception as e:
                    last_error = e

                    # Classify the error
                    error_type, retry_after = classify_error(e)

                    # If it's the last attempt, always raise
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                        if error_type == 'retryable':
                            raise RetryableError(
                                f"Max retries exceeded: {str(e)}",
                                original_error=e
                            )
                        elif error_type == 'user_fixable':
                            raise UserFixableError(
                                str(e),
                                help_text="Please check your request and try again.",
                                original_error=e
                            )
                        else:
                            raise FatalError(
                                f"Fatal error: {str(e)}",
                                original_error=e
                            )

                    # If not retryable, raise immediately
                    if error_type == 'user_fixable':
                        logger.warning(f"User-fixable error in {func.__name__}: {e}")
                        raise UserFixableError(
                            str(e),
                            help_text="Please check your request and try again.",
                            original_error=e
                        )

                    if error_type == 'fatal':
                        logger.error(f"Fatal error in {func.__name__}: {e}")
                        raise FatalError(
                            f"Fatal error: {str(e)}",
                            original_error=e
                        )

                    # Calculate delay for retryable errors
                    if retry_after:
                        # Use API-specified retry_after
                        delay = retry_after
                        logger.info(f"API requested retry after {delay}s")
                    else:
                        # Use exponential backoff
                        delay = calculate_backoff(attempt, base_delay, max_delay)

                    logger.warning(
                        f"Retryable error in {func.__name__}: {e}. "
                        f"Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})"
                    )

                    # Call retry callback if provided
                    if retry_callback:
                        retry_callback(attempt + 1, delay)

                    # Wait before retry
                    time.sleep(delay)

            # Should never reach here, but just in case
            if last_error:
                raise FatalError(
                    f"Unexpected error after retries: {str(last_error)}",
                    original_error=last_error
                )

        return wrapper
    return decorator
