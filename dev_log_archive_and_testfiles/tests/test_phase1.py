#!/usr/bin/env python3
"""
Phase 1 Test Script

Tests basic Claude API functionality:
1. Client initialization
2. Simple message
3. Message with system prompt
4. Streaming response
5. Message format conversion
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.api_client import ClaudeAPIClient, ClaudeAPIClientWithRetry
from core.models import ClaudeModels, ModelSelector, resolve_model
from core.message_converter import (
    extract_system_prompt,
    prepare_messages_for_claude,
    validate_claude_messages,
)


def print_test(test_name: str):
    """Print test header"""
    print(f"\n{'=' * 60}")
    print(f"TEST: {test_name}")
    print('=' * 60)


def print_result(success: bool, message: str = ""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {message}")


def test_1_environment():
    """Test 1: Check environment setup"""
    print_test("Environment Setup")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print_result(True, f"API key found: {api_key[:20]}...")
        return True
    else:
        print_result(False, "ANTHROPIC_API_KEY not set in environment")
        print("\nPlease set your API key:")
        print("  1. Copy .env.example to .env")
        print("  2. Add: ANTHROPIC_API_KEY=your_key_here")
        return False


def test_2_models():
    """Test 2: Model configuration"""
    print_test("Model Configuration")

    try:
        # Test model enum
        default_model = ModelSelector.get_default()
        print(f"Default model: {default_model.value}")

        # Test model resolution
        resolved = resolve_model("sonnet")
        print(f"Resolved 'sonnet': {resolved}")

        # Test model info
        from core.models import ModelCapabilities
        info = ModelCapabilities.get_info(ClaudeModels.SONNET_4_5)
        print(f"Sonnet 4.5 info: {info['name']} - {info['best_for']}")

        print_result(True)
        return True
    except Exception as e:
        print_result(False, str(e))
        return False


def test_3_message_converter():
    """Test 3: Message format conversion"""
    print_test("Message Format Conversion")

    try:
        # Test system prompt extraction
        openai_messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        system, messages = extract_system_prompt(openai_messages)
        print(f"Extracted system: '{system}'")
        print(f"Remaining messages: {len(messages)}")

        # Test full conversion
        system2, claude_msgs = prepare_messages_for_claude(openai_messages)
        print(f"Claude messages: {len(claude_msgs)}")

        # Test validation
        is_valid = validate_claude_messages(claude_msgs)
        print(f"Messages valid: {is_valid}")

        print_result(True)
        return True
    except Exception as e:
        print_result(False, str(e))
        return False


def test_4_simple_message():
    """Test 4: Simple non-streaming message"""
    print_test("Simple Message (Non-Streaming)")

    try:
        client = ClaudeAPIClient()
        print("Client initialized")

        # Use cheapest model for testing
        response = client.simple_message(
            prompt="Say 'hello' in exactly one word.",
            model=ClaudeModels.HAIKU_3_5.value,
            system="You are a concise assistant.",
            max_tokens=10,
        )

        print(f"Response: '{response}'")

        if response and len(response) > 0:
            print_result(True)
            return True
        else:
            print_result(False, "Empty response")
            return False

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_5_streaming():
    """Test 5: Streaming response"""
    print_test("Streaming Response")

    try:
        client = ClaudeAPIClient()

        print("Streaming response: ", end="", flush=True)
        chunks_received = 0

        for chunk in client.create_message_stream(
            messages=[{"role": "user", "content": "Count from 1 to 5, one number per line."}],
            model=ClaudeModels.HAIKU_3_5.value,
            system="You are a helpful assistant.",
            max_tokens=100,
        ):
            print(chunk, end="", flush=True)
            chunks_received += 1

        print()  # New line

        if chunks_received > 0:
            print_result(True, f"Received {chunks_received} chunks")
            return True
        else:
            print_result(False, "No chunks received")
            return False

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_6_conversation():
    """Test 6: Multi-turn conversation"""
    print_test("Multi-Turn Conversation")

    try:
        client = ClaudeAPIClient()

        # Simulate a conversation
        messages = [
            {"role": "user", "content": "My name is Alice."},
        ]

        # First response
        response1 = client.create_message(
            messages=messages,
            model=ClaudeModels.HAIKU_3_5.value,
            system="You are a friendly assistant.",
            max_tokens=50,
        )

        # Extract text
        text1 = response1.content[0].text if response1.content else ""
        print(f"Claude: {text1[:100]}...")

        # Add to conversation
        messages.append({"role": "assistant", "content": text1})
        messages.append({"role": "user", "content": "What is my name?"})

        # Second response
        response2 = client.create_message(
            messages=messages,
            model=ClaudeModels.HAIKU_3_5.value,
            system="You are a friendly assistant.",
            max_tokens=50,
        )

        text2 = response2.content[0].text if response2.content else ""
        print(f"Claude: {text2}")

        # Check if it remembered the name
        if "alice" in text2.lower():
            print_result(True, "Claude remembered the name!")
            return True
        else:
            print_result(False, "Claude didn't remember the name")
            return False

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_7_retry_client():
    """Test 7: Retry client initialization"""
    print_test("Retry Client")

    try:
        client = ClaudeAPIClientWithRetry(max_retries=3, initial_backoff=1.0)
        print("Retry client initialized")

        # Make a simple call
        response = client.simple_message(
            prompt="Say 'test' in one word.",
            model=ClaudeModels.HAIKU_3_5.value,
            max_tokens=10,
        )

        print(f"Response: '{response}'")

        if response:
            print_result(True)
            return True
        else:
            print_result(False, "Empty response")
            return False

    except Exception as e:
        print_result(False, str(e))
        return False


def run_all_tests():
    """Run all Phase 1 tests"""
    print("\n" + "=" * 60)
    print("PHASE 1 TEST SUITE")
    print("Testing Core API Functionality")
    print("=" * 60)

    tests = [
        ("Environment Setup", test_1_environment),
        ("Model Configuration", test_2_models),
        ("Message Conversion", test_3_message_converter),
        ("Simple Message", test_4_simple_message),
        ("Streaming", test_5_streaming),
        ("Multi-Turn Conversation", test_6_conversation),
        ("Retry Client", test_7_retry_client),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Phase 1 is complete.")
        print("\nNext steps:")
        print("  1. Review docs/IMPLEMENTATION_PLAN.md")
        print("  2. Start Phase 2: Tool System Adapter")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix before proceeding.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
