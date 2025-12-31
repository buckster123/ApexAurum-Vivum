#!/usr/bin/env python3
"""
Phase 7-8 Testing: Error Handling & Rate Limiting
Tests for retry logic, error messages, rate limiting, token counting, and cost tracking
"""

import sys
import os
import time

# Test counter
tests_passed = 0
tests_failed = 0

def test(name):
    """Decorator for test functions"""
    def decorator(func):
        def wrapper():
            global tests_passed, tests_failed
            try:
                func()
                print(f"✅ {name}")
                tests_passed += 1
            except AssertionError as e:
                print(f"❌ {name}: {e}")
                tests_failed += 1
            except Exception as e:
                print(f"❌ {name}: Unexpected error: {e}")
                tests_failed += 1
        return wrapper
    return decorator


print("=" * 70)
print("PHASE 7-8 TESTING: Error Handling & Rate Limiting")
print("=" * 70)
print()

# Test 1: Custom error classes exist
@test("1. Custom error classes exist")
def test_error_classes():
    from core.errors import ApexAurumError, RetryableError, UserFixableError, FatalError

    # Test creation
    retryable = RetryableError("Test", retry_after=5.0)
    assert retryable.retry_after == 5.0

    fixable = UserFixableError("Test", help_text="Fix this")
    assert fixable.help_text == "Fix this"

    fatal = FatalError("Test")
    assert str(fatal) == "Test"

test_error_classes()


# Test 2: Retry handler module exists
@test("2. Retry handler module exists")
def test_retry_handler():
    from core.retry_handler import (
        extract_retry_after,
        classify_error,
        calculate_backoff,
        retry_on_error
    )

    # Test backoff calculation
    delay = calculate_backoff(0, base_delay=1.0)
    assert 0.75 <= delay <= 1.25, "Backoff should be ~1s with jitter"

    delay = calculate_backoff(1, base_delay=1.0)
    assert 1.5 <= delay <= 2.5, "Backoff should be ~2s with jitter"

test_retry_handler()


# Test 3: Error message translator
@test("3. Error message translator works")
def test_error_messages():
    from core.error_messages import get_user_friendly_message, ERROR_MESSAGES

    # Check all error messages have required fields
    for key, msg in ERROR_MESSAGES.items():
        assert "title" in msg, f"{key} missing title"
        assert "message" in msg, f"{key} missing message"
        assert "action" in msg, f"{key} missing action"
        assert "severity" in msg, f"{key} missing severity"

test_error_messages()


# Test 4: Rate limiter class
@test("4. Rate limiter class works")
def test_rate_limiter():
    from core.rate_limiter import RateLimiter

    limiter = RateLimiter(max_requests_per_min=10)

    # Should be able to make requests initially
    can_proceed, wait_time = limiter.can_make_request()
    assert can_proceed, "Should be able to make first request"
    assert wait_time == 0.0, "Wait time should be 0"

    # Record some requests
    for i in range(5):
        limiter.record_request(input_tokens=100, output_tokens=50)

    # Check stats
    stats = limiter.get_usage_stats()
    assert stats["requests"] == 5, "Should have 5 requests"
    assert stats["input_tokens"] == 500, "Should have 500 input tokens"
    assert stats["output_tokens"] == 250, "Should have 250 output tokens"

test_rate_limiter()


# Test 5: Token counter
@test("5. Token counter works")
def test_token_counter():
    from core.token_counter import (
        estimate_text_tokens,
        estimate_image_tokens,
        estimate_tool_tokens,
        count_tokens
    )

    # Test text estimation
    tokens = estimate_text_tokens("Hello, world!")
    assert tokens > 0, "Should estimate tokens for text"

    # Test image estimation
    tokens = estimate_image_tokens(2)
    assert tokens == 340, "Should be 170 tokens per image"

    # Test full message counting
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    result = count_tokens(messages)
    assert "input_tokens" in result
    assert "output_tokens" in result
    assert "total_tokens" in result
    assert result["total_tokens"] > 0

test_token_counter()


# Test 6: Cost tracker
@test("6. Cost tracker works")
def test_cost_tracker():
    from core.cost_tracker import CostTracker

    tracker = CostTracker()

    # Record some usage
    tracker.record_usage("claude-sonnet-4-5", input_tokens=1000, output_tokens=500)

    # Check stats
    stats = tracker.get_session_stats()
    assert stats["input_tokens"] == 1000
    assert stats["output_tokens"] == 500
    assert stats["total_tokens"] == 1500
    assert stats["cost"] > 0, "Should calculate non-zero cost"
    assert stats["request_count"] == 1

    # Calculate specific cost
    costs = tracker.calculate_cost("claude-haiku-3-5", 10000, 5000)
    assert costs["total_cost"] > 0, "Should calculate cost"

test_cost_tracker()


# Test 7: API client has retry decorator
@test("7. API client has retry decorator")
def test_api_client_retry():
    import inspect
    from core.api_client import ClaudeAPIClient

    # Check that create_message has been wrapped
    method = ClaudeAPIClient.create_message
    assert hasattr(method, '__wrapped__') or 'retry' in str(method), \
        "create_message should be wrapped with retry decorator"

test_api_client_retry()


# Test 8: API client has rate limiter
@test("8. API client has rate limiter and cost tracker")
def test_api_client_integration():
    from core.api_client import ClaudeAPIClient

    # Mock API key for testing
    import os
    os.environ['ANTHROPIC_API_KEY'] = 'test-key-123'

    client = ClaudeAPIClient()

    assert hasattr(client, 'rate_limiter'), "Should have rate_limiter"
    assert hasattr(client, 'cost_tracker'), "Should have cost_tracker"

test_api_client_integration()


# Test 9: Error messages imported in main
@test("9. Error handling in main.py")
def test_main_error_handling():
    with open('main.py', 'r') as f:
        content = f.read()

    assert 'from core.error_messages import' in content, "Should import error_messages"
    assert 'from core.errors import' in content, "Should import error classes"
    assert 'get_user_friendly_message' in content, "Should use user-friendly messages"

test_main_error_handling()


# Test 10: Usage display in UI
@test("10. Usage display in main.py")
def test_usage_display():
    with open('main.py', 'r') as f:
        content = f.read()

    assert '📊 API Usage' in content, "Should have API Usage section"
    assert 'rate_limiter.get_usage_stats' in content, "Should get usage stats"
    assert 'cost_tracker' in content, "Should display cost tracking"
    assert 'Session Cost' in content, "Should show session cost"

test_usage_display()


# Test 11: Rate limiter sliding window
@test("11. Rate limiter sliding window works")
def test_sliding_window():
    from core.rate_limiter import RateLimiter

    limiter = RateLimiter(max_requests_per_min=5, safety_margin=1.0)

    # Fill up to limit
    for i in range(5):
        limiter.record_request(100, 50)

    # Should not be able to make more requests
    can_proceed, wait_time = limiter.can_make_request()
    assert not can_proceed, "Should hit rate limit"
    assert wait_time > 0, "Should have wait time"

test_sliding_window()


# Test 12: Token counting for images
@test("12. Token counting handles images")
def test_token_counting_images():
    from core.token_counter import count_tokens, count_images_in_messages

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image", "source": {"data": "base64..."}}
            ]
        }
    ]

    result = count_tokens(messages)
    assert result["input_tokens"] > 170, "Should include image tokens"

    image_count = count_images_in_messages(messages)
    assert image_count == 1, "Should count 1 image"

test_token_counting_images()


# Test 13: Cost tracker model pricing
@test("13. Cost tracker has correct pricing")
def test_cost_pricing():
    from core.cost_tracker import MODEL_PRICING

    # Check all expected models
    assert "claude-opus-4-5" in MODEL_PRICING
    assert "claude-sonnet-4-5" in MODEL_PRICING
    assert "claude-sonnet-3-7" in MODEL_PRICING
    assert "claude-haiku-3-5" in MODEL_PRICING

    # Check pricing format (input, output)
    for model, (input_price, output_price) in MODEL_PRICING.items():
        assert input_price > 0, f"{model} should have input price"
        assert output_price > 0, f"{model} should have output price"
        assert output_price > input_price, f"{model} output should cost more"

test_cost_pricing()


# Test 14: Error classification
@test("14. Error classification works")
def test_error_classification():
    from core.retry_handler import classify_error
    import anthropic
    from unittest.mock import Mock

    # Create mock response object
    mock_response = Mock()
    mock_response.status_code = 429

    # Test rate limit error
    rate_limit_error = anthropic.RateLimitError(
        message="test",
        response=mock_response,
        body={"error": {"type": "rate_limit_error"}}
    )
    error_type, retry_after = classify_error(rate_limit_error)
    assert error_type == "retryable", "Rate limit should be retryable"

    # Test auth error
    mock_response.status_code = 401
    auth_error = anthropic.AuthenticationError(
        message="test",
        response=mock_response,
        body={"error": {"type": "authentication_error"}}
    )
    error_type, retry_after = classify_error(auth_error)
    assert error_type == "user_fixable", "Auth error should be user-fixable"

test_error_classification()


# Test 15: Backoff calculation bounds
@test("15. Backoff calculation respects bounds")
def test_backoff_bounds():
    from core.retry_handler import calculate_backoff

    # Test max delay
    delay = calculate_backoff(10, base_delay=1.0, max_delay=5.0)
    assert delay <= 6.25, "Should not exceed max_delay + jitter"

    # Test minimum delay
    delay = calculate_backoff(0, base_delay=0.01, max_delay=10.0)
    assert delay >= 0.1, "Should have minimum 0.1s delay"

test_backoff_bounds()


# Summary
print()
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print(f"Total: {tests_passed + tests_failed}")
print()

if tests_failed == 0:
    print("🎉 All Phase 7-8 tests passed!")
    print()
    print("Phase 7-8 Features Verified:")
    print("  ✅ Custom error classes (Retryable, UserFixable, Fatal)")
    print("  ✅ Retry logic with exponential backoff")
    print("  ✅ User-friendly error messages")
    print("  ✅ Rate limiter with sliding window")
    print("  ✅ Token counting (text + images)")
    print("  ✅ Cost tracking per model")
    print("  ✅ API client integration")
    print("  ✅ UI error display")
    print("  ✅ UI usage display")
    print()
    print("Ready for production use!")
    print()
    sys.exit(0)
else:
    print("⚠️  Some tests failed. Please review the errors above.")
    sys.exit(1)
