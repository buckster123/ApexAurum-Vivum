#!/usr/bin/env python3
"""
Phase 9 Testing: Context Management
Tests for context tracking, summarization, pruning, and management orchestration
"""

import sys
import os

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
print("PHASE 9 TESTING: Context Management")
print("=" * 70)
print()

# Test 1: Context tracker calculates correctly
@test("1. Context tracker calculates total tokens")
def test_context_tracker():
    from core.context_tracker import ContextTracker

    tracker = ContextTracker("claude-sonnet-4-5")
    assert tracker.max_tokens == 200000, "Should have 200K token limit"

    messages = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"}
    ]

    stats = tracker.calculate_total_context(messages, "System prompt", [])
    assert stats["total_tokens"] > 0, "Should calculate tokens"
    assert stats["max_tokens"] == 200000
    assert stats["usage_percent"] < 1.0, "Should be less than 1% for short conversation"
    assert stats["remaining_tokens"] > 0

test_context_tracker()


# Test 2: Message token breakdown
@test("2. Context tracker provides per-message breakdown")
def test_message_token_breakdown():
    from core.context_tracker import ContextTracker

    tracker = ContextTracker("claude-sonnet-4-5")
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I help you today?"}
    ]

    breakdown = tracker.get_message_token_breakdown(messages)
    assert len(breakdown) == 2, "Should have 2 entries"
    assert breakdown[0]["role"] == "user"
    assert breakdown[0]["tokens"] > 0
    assert breakdown[1]["role"] == "assistant"
    assert breakdown[1]["tokens"] > 0

test_message_token_breakdown()


# Test 3: Should summarize threshold check
@test("3. Context tracker detects when to summarize")
def test_should_summarize():
    from core.context_tracker import ContextTracker

    tracker = ContextTracker("claude-sonnet-4-5")

    # 60% usage, threshold 50% = should summarize
    assert tracker.should_summarize(120000, threshold_percent=0.5)

    # 60% usage, threshold 70% = should not summarize
    assert not tracker.should_summarize(120000, threshold_percent=0.7)

    # 90% usage, threshold 85% = should summarize
    assert tracker.should_summarize(180000, threshold_percent=0.85)

test_should_summarize()


# Test 4: Summarizer creates summaries
@test("4. Summarizer creates summaries (fallback mode)")
def test_summarizer():
    from core.summarizer import ConversationSummarizer

    # Test without API client (fallback mode)
    summarizer = ConversationSummarizer(client=None)

    messages = [
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "2+2 equals 4."},
        {"role": "user", "content": "What about 3+3?"},
        {"role": "assistant", "content": "3+3 equals 6."}
    ]

    summary = summarizer.summarize_messages(messages, strategy="balanced")
    assert len(summary) > 0, "Should create summary"
    assert "messages" in summary.lower() or "discussion" in summary.lower()

test_summarizer()


# Test 5: Identify important messages
@test("5. Summarizer identifies important messages")
def test_identify_important():
    from core.summarizer import ConversationSummarizer

    summarizer = ConversationSummarizer(client=None)

    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "```python\nprint('hello')\n```"},
        {"role": "user", "content": "Error: File not found"},
        {"role": "assistant", "content": "OK"}
    ]

    # Test with bookmarks
    bookmarked = {0}  # Bookmark first message
    important = summarizer.identify_important_messages(messages, bookmarked)

    assert 0 in important, "Bookmarked message should be important"
    assert 1 in important, "Code block should be important"
    assert 2 in important, "Error message should be important"
    # Message 3 ("OK") is likely not in important

test_identify_important()


# Test 6: Message pruner scores correctly
@test("6. Message pruner calculates importance scores")
def test_message_pruner():
    from core.message_pruner import MessagePruner

    pruner = MessagePruner()

    # User question (high importance)
    user_msg = {"role": "user", "content": "Can you help me with this problem?"}
    score = pruner.calculate_message_importance(user_msg)
    assert score >= 0.7, f"User messages should be important (got {score})"

    # Code block (high importance)
    code_msg = {"role": "assistant", "content": "```python\nprint('test')\n```"}
    score = pruner.calculate_message_importance(code_msg)
    assert score >= 0.7, f"Code blocks should be important (got {score})"

    # Acknowledgment (low importance)
    ack_msg = {"role": "assistant", "content": "OK"}
    score = pruner.calculate_message_importance(ack_msg)
    assert score <= 0.3, f"Acknowledgments should be low priority (got {score})"

test_message_pruner()


# Test 7: Message pruner removes low-priority messages
@test("7. Message pruner removes low-priority messages")
def test_prune_messages():
    from core.message_pruner import MessagePruner

    pruner = MessagePruner()

    messages = [
        {"role": "user", "content": "Question 1"},
        {"role": "assistant", "content": "OK"},  # Low importance
        {"role": "user", "content": "Question 2"},
        {"role": "assistant", "content": "```python\ncode\n```"},  # High importance
        {"role": "user", "content": "Question 3"},
        {"role": "assistant", "content": "Sure"},  # Low importance
    ]

    # Prune to target (will remove low-importance messages)
    pruned = pruner.prune_messages(
        messages,
        target_token_count=50,  # Very low target to force aggressive pruning
        preserve_recent=1,  # Keep only last message
        bookmarked_indices=set()
    )

    # Should keep at least recent + important messages (code block + recent)
    assert len(pruned) < len(messages), "Should have removed some messages"
    # Recent message should be preserved
    assert any("Sure" in str(msg.get("content", "")) for msg in pruned), "Should preserve recent message"

test_prune_messages()


# Test 8: Context manager initialization
@test("8. Context manager initializes correctly")
def test_context_manager_init():
    from core.context_manager import ContextManager

    # Mock client (None is OK for initialization)
    manager = ContextManager(None, "claude-sonnet-4-5", "balanced")

    assert manager.strategy == "balanced"
    assert manager.model == "claude-sonnet-4-5"
    assert len(manager.bookmarked_indices) == 0

test_context_manager_init()


# Test 9: Context manager bookmarking
@test("9. Context manager bookmarking works")
def test_context_manager_bookmarks():
    from core.context_manager import ContextManager

    manager = ContextManager(None, "claude-sonnet-4-5", "balanced")

    # Bookmark messages
    manager.bookmark_message(5)
    manager.bookmark_message(10)

    assert 5 in manager.bookmarked_indices
    assert 10 in manager.bookmarked_indices

    # Unbookmark
    manager.unbookmark_message(5)
    assert 5 not in manager.bookmarked_indices
    assert 10 in manager.bookmarked_indices

test_context_manager_bookmarks()


# Test 10: Context manager stats
@test("10. Context manager provides statistics")
def test_context_manager_stats():
    from core.context_manager import ContextManager

    manager = ContextManager(None, "claude-sonnet-4-5", "balanced")

    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

    stats = manager.get_context_stats(messages, "System prompt", None)

    assert "total_tokens" in stats
    assert "usage_percent" in stats
    assert "strategy" in stats
    assert stats["strategy"] == "balanced"
    assert "bookmarked_count" in stats
    assert stats["bookmarked_count"] == 0

test_context_manager_stats()


# Test 11: Context manager strategy change
@test("11. Context manager changes strategy")
def test_context_manager_strategy():
    from core.context_manager import ContextManager

    manager = ContextManager(None, "claude-sonnet-4-5", "balanced")
    assert manager.strategy == "balanced"

    manager.set_strategy("aggressive")
    assert manager.strategy == "aggressive"

    manager.set_strategy("conservative")
    assert manager.strategy == "conservative"

test_context_manager_strategy()


# Test 12: Context tracker handles images
@test("12. Context tracker counts image tokens")
def test_context_tracker_images():
    from core.context_tracker import ContextTracker

    tracker = ContextTracker("claude-sonnet-4-5")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image", "source": {"type": "base64", "data": "..."}}
            ]
        }
    ]

    stats = tracker.calculate_total_context(messages, None, None)
    # Should include image tokens (~170 per image)
    assert stats["total_tokens"] > 170, "Should count image tokens"

test_context_tracker_images()


# Test 13: Pruner detects redundancy
@test("13. Message pruner detects redundant messages")
def test_redundancy_detection():
    from core.message_pruner import MessagePruner

    pruner = MessagePruner()

    # Test with previous acknowledgment
    previous_with_ack = [
        {"role": "assistant", "content": "Sure"}
    ]

    # Another acknowledgment after recent one (redundant)
    redundant = {"role": "assistant", "content": "OK"}
    assert pruner.is_redundant(redundant, previous_with_ack), "Multiple acknowledgments should be redundant"

    # Unique content after acknowledgment (not redundant)
    unique = {"role": "assistant", "content": "Here's the implementation: ..."}
    assert not pruner.is_redundant(unique, previous_with_ack), "Substantive content should not be redundant"

    # Test exact duplicate
    previous_with_content = [
        {"role": "assistant", "content": "test message"}
    ]
    duplicate = {"role": "assistant", "content": "test message"}
    assert pruner.is_redundant(duplicate, previous_with_content), "Exact duplicates should be redundant"

test_redundancy_detection()


# Test 14: Summarizer creates proper message format
@test("14. Summarizer creates valid summary message")
def test_summary_message_format():
    from core.summarizer import ConversationSummarizer

    summarizer = ConversationSummarizer(client=None)

    summary_msg = summarizer.create_summary_message(
        summary_text="User discussed topics A, B, and C.",
        original_count=10,
        token_savings=5000
    )

    assert summary_msg["role"] == "assistant"
    assert "📝 Summary" in summary_msg["content"]
    assert "10" in summary_msg["content"]
    assert "5,000" in summary_msg["content"]

test_summary_message_format()


# Test 15: Integration test - Main.py imports
@test("15. Main.py imports context management")
def test_main_imports():
    with open('main.py', 'r') as f:
        content = f.read()

    assert 'from core.context_manager import ContextManager' in content
    assert 'context_manager' in content
    assert 'Context Management' in content

test_main_imports()


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
    print("🎉 All Phase 9 tests passed!")
    print()
    print("Phase 9 Features Verified:")
    print("  ✅ Context tracker (token counting)")
    print("  ✅ Conversation summarizer")
    print("  ✅ Message pruner (importance scoring)")
    print("  ✅ Context manager (orchestration)")
    print("  ✅ Bookmarking support")
    print("  ✅ Strategy management")
    print("  ✅ Image token counting")
    print("  ✅ Redundancy detection")
    print("  ✅ Main.py integration")
    print()
    print("Ready for unlimited conversations! 🚀")
    print()
    sys.exit(0)
else:
    print("⚠️  Some tests failed. Please review the errors above.")
    sys.exit(1)
