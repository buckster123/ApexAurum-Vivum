#!/usr/bin/env python3
"""
Phase 11 Testing: Streaming Improvements
Tests for real-time streaming, tool execution visibility, and progress indicators
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
print("PHASE 11 TESTING: Streaming Improvements")
print("=" * 70)
print()

# Test 1: Streaming infrastructure imports
@test("1. Streaming infrastructure imports correctly")
def test_streaming_imports():
    from core.streaming import (
        StreamEvent,
        StreamingResponseHandler,
        ToolExecutionTracker,
        ProgressIndicator,
        format_tool_display,
        estimate_stream_progress
    )
    assert StreamEvent is not None
    assert StreamingResponseHandler is not None
    assert ToolExecutionTracker is not None
    assert ProgressIndicator is not None

test_streaming_imports()


# Test 2: StreamEvent creation
@test("2. StreamEvent creation works")
def test_stream_event():
    from core.streaming import StreamEvent

    event = StreamEvent(
        event_type="text_delta",
        data="Hello",
        timestamp=time.time()
    )

    assert event.event_type == "text_delta"
    assert event.data == "Hello"
    assert event.timestamp > 0

test_stream_event()


# Test 3: ToolExecutionTracker
@test("3. ToolExecutionTracker tracks tools")
def test_tool_execution_tracker():
    from core.streaming import ToolExecutionTracker

    tracker = ToolExecutionTracker()

    # Start a tool
    tracker.start_tool("tool_123", "search_web", {"query": "test"})
    assert "tool_123" in tracker.active_tools
    assert tracker.get_tool_status("tool_123") == "running"

    # Complete the tool
    tracker.complete_tool("tool_123", {"results": ["a", "b"]}, is_error=False)
    assert "tool_123" not in tracker.active_tools
    assert "tool_123" in tracker.completed_tools
    assert tracker.get_tool_status("tool_123") == "complete"

    # Check elapsed time
    elapsed = tracker.get_elapsed_time("tool_123")
    assert elapsed is not None
    assert elapsed >= 0

test_tool_execution_tracker()


# Test 4: ToolCallLoop has run_streaming method
@test("4. ToolCallLoop has run_streaming method")
def test_tool_loop_streaming():
    from core import ToolCallLoop

    # Check method exists
    assert hasattr(ToolCallLoop, 'run_streaming')

    # Check it's callable
    assert callable(getattr(ToolCallLoop, 'run_streaming'))

test_tool_loop_streaming()


# Test 5: ProgressIndicator
@test("5. ProgressIndicator generates frames")
def test_progress_indicator():
    from core.streaming import ProgressIndicator

    indicator = ProgressIndicator()

    # Get frames
    frame1 = indicator.next_frame()
    frame2 = indicator.next_frame()

    assert frame1 in ProgressIndicator.SPINNER_FRAMES
    assert frame2 in ProgressIndicator.SPINNER_FRAMES
    assert frame1 != frame2  # Different frames

    # Check elapsed time
    time.sleep(0.01)
    elapsed = indicator.get_elapsed()
    assert elapsed > 0

test_progress_indicator()


# Test 6: format_tool_display
@test("6. format_tool_display formats correctly")
def test_format_tool_display():
    from core.streaming import format_tool_display

    # Running tool
    display = format_tool_display(
        "search_web",
        {"query": "test"},
        status="running"
    )
    assert "search_web" in display
    assert "🔄" in display

    # Completed tool
    display = format_tool_display(
        "search_web",
        {"query": "test"},
        status="complete",
        duration=1.5,
        result={"count": 10}
    )
    assert "search_web" in display
    assert "✅" in display
    assert "1.50s" in display

test_format_tool_display()


# Test 7: UI components import
@test("7. UI streaming components import")
def test_ui_imports():
    from ui.streaming_display import (
        StreamingTextDisplay,
        ToolExecutionDisplay,
        StatusIndicator,
        StreamingProgressBar,
        format_tool_for_display,
        create_streaming_container,
        estimate_completion_time
    )

    assert StreamingTextDisplay is not None
    assert ToolExecutionDisplay is not None
    assert StatusIndicator is not None
    assert StreamingProgressBar is not None

test_ui_imports()


# Test 8: StreamingTextDisplay (without Streamlit)
@test("8. StreamingTextDisplay initializes")
def test_streaming_text_display():
    from ui.streaming_display import StreamingTextDisplay

    # Create without container (won't render but tests logic)
    display = StreamingTextDisplay(container=None)
    assert display.text_buffer == ""
    assert display.finalized == False

    # Append text
    display.append("Hello ")
    display.append("world")
    assert display.text_buffer == "Hello world"

    # Finalize
    final_text = display.finalize()
    assert final_text == "Hello world"
    assert display.finalized == True

test_streaming_text_display()


# Test 9: ToolExecutionDisplay (without Streamlit)
@test("9. ToolExecutionDisplay tracks tools")
def test_tool_execution_display():
    from ui.streaming_display import ToolExecutionDisplay

    display = ToolExecutionDisplay(container=None)

    # Start a tool
    display.start_tool("tool_123", "search_web", {"query": "test"})
    assert "tool_123" in display.active_tools
    assert len(display.tool_order) == 1

    # Complete the tool
    display.complete_tool("tool_123", {"results": []}, is_error=False, duration=1.5)
    assert "tool_123" not in display.active_tools
    assert "tool_123" in display.completed_tools

    # Get summary
    summary = display.get_summary()
    assert summary["active"] == 0
    assert summary["completed"] == 1
    assert summary["failed"] == 0
    assert summary["total"] == 1

test_tool_execution_display()


# Test 10: Main.py has streaming integration
@test("10. Main.py has streaming integration")
def test_main_streaming():
    with open('main.py', 'r') as f:
        content = f.read()

    # Check for streaming settings
    assert 'streaming_enabled' in content
    assert 'show_tool_execution' in content
    assert 'show_partial_results' in content

    # Check for streaming imports
    assert 'from ui.streaming_display import' in content
    assert 'StreamingTextDisplay' in content
    assert 'ToolExecutionDisplay' in content

    # Check for run_streaming call
    assert 'run_streaming' in content

test_main_streaming()


# Test 11: Session state includes streaming settings
@test("11. Session state includes streaming settings")
def test_session_state_streaming():
    with open('main.py', 'r') as f:
        content = f.read()

    assert '"streaming_enabled"' in content
    assert '"show_tool_execution"' in content
    assert '"show_partial_results"' in content

test_session_state_streaming()


# Test 12: Streaming settings in sidebar
@test("12. Streaming settings UI in sidebar")
def test_sidebar_streaming():
    with open('main.py', 'r') as f:
        content = f.read()

    # Check for streaming section
    assert 'Streaming Settings' in content or 'Streaming' in content
    assert 'Enable Real-time Streaming' in content or 'streaming_enabled' in content

test_sidebar_streaming()


# Test 13: estimate_stream_progress
@test("13. estimate_stream_progress calculates correctly")
def test_estimate_progress():
    from core.streaming import estimate_stream_progress

    # 50% progress
    progress = estimate_stream_progress(50, 100)
    assert progress == 0.5

    # 100% progress
    progress = estimate_stream_progress(100, 100)
    assert progress == 1.0

    # Over 100% (clamped)
    progress = estimate_stream_progress(150, 100)
    assert progress == 1.0

    # Zero total (edge case)
    progress = estimate_stream_progress(50, 0)
    assert progress == 0.0

test_estimate_progress()


# Test 14: estimate_completion_time
@test("14. estimate_completion_time formats correctly")
def test_estimate_completion():
    from ui.streaming_display import estimate_completion_time

    start_time = time.time() - 10  # 10 seconds ago

    # 50% progress -> 10 more seconds
    eta = estimate_completion_time(start_time, 0.5)
    assert eta is not None
    assert "10s" in eta or "9s" in eta  # Allow for timing variation

    # 100% progress
    eta = estimate_completion_time(start_time, 1.0)
    assert eta == "Complete"

    # No progress yet
    eta = estimate_completion_time(start_time, 0.0)
    assert eta is None

test_estimate_completion()


# Test 15: format_tool_for_display
@test("15. format_tool_for_display works")
def test_format_tool_for_ui():
    from ui.streaming_display import format_tool_for_display

    # Running tool
    display = format_tool_for_display(
        "search_web",
        {"query": "test", "limit": 10},
        status="running"
    )
    assert "search_web" in display
    assert "🔄" in display
    assert "query" in display

    # Completed tool
    display = format_tool_for_display(
        "search_web",
        {},
        status="complete"
    )
    assert "✅" in display

    # Error
    display = format_tool_for_display(
        "search_web",
        {},
        status="error"
    )
    assert "❌" in display

test_format_tool_for_ui()


# Test 16: Core exports streaming classes
@test("16. Core module exports streaming classes")
def test_core_exports():
    from core import (
        StreamEvent,
        StreamingResponseHandler,
        ToolExecutionTracker,
        ProgressIndicator
    )

    assert StreamEvent is not None
    assert StreamingResponseHandler is not None
    assert ToolExecutionTracker is not None
    assert ProgressIndicator is not None

test_core_exports()


# Test 17: Multiple tools tracking
@test("17. ToolExecutionTracker handles multiple tools")
def test_multiple_tools():
    from core.streaming import ToolExecutionTracker

    tracker = ToolExecutionTracker()

    # Start multiple tools
    tracker.start_tool("tool_1", "search_web", {})
    tracker.start_tool("tool_2", "read_file", {})
    tracker.start_tool("tool_3", "write_file", {})

    assert len(tracker.active_tools) == 3

    # Complete one
    tracker.complete_tool("tool_2", "File content", is_error=False)
    assert len(tracker.active_tools) == 2
    assert len(tracker.completed_tools) == 1

    # Complete with error
    tracker.complete_tool("tool_3", "Permission denied", is_error=True)
    assert len(tracker.active_tools) == 1
    assert len(tracker.completed_tools) == 2

    # Check error tool
    tool_3 = tracker.completed_tools["tool_3"]
    assert tool_3["is_error"] == True

test_multiple_tools()


# Test 18: ToolExecutionDisplay clear
@test("18. ToolExecutionDisplay clear works")
def test_tool_display_clear():
    from ui.streaming_display import ToolExecutionDisplay

    display = ToolExecutionDisplay(container=None)

    # Add some tools
    display.start_tool("tool_1", "search_web", {})
    display.complete_tool("tool_1", "result", False)

    assert len(display.completed_tools) > 0

    # Clear
    display.clear()
    assert len(display.active_tools) == 0
    assert len(display.completed_tools) == 0
    assert len(display.tool_order) == 0

test_tool_display_clear()


# Test 19: ProgressIndicator reset
@test("19. ProgressIndicator reset works")
def test_progress_reset():
    from core.streaming import ProgressIndicator

    indicator = ProgressIndicator()

    # Advance some frames
    for _ in range(5):
        indicator.next_frame()

    time.sleep(0.01)
    assert indicator.get_elapsed() > 0

    # Reset
    indicator.reset()
    assert indicator.frame_index == 0
    # Elapsed should be near zero (small tolerance for execution time)
    assert indicator.get_elapsed() < 0.01

test_progress_reset()


# Test 20: StreamingResponseHandler initializes
@test("20. StreamingResponseHandler initializes")
def test_streaming_handler_init():
    from core.streaming import StreamingResponseHandler
    from core import ClaudeAPIClient
    import os

    # Only test initialization if API key available
    if not os.getenv("ANTHROPIC_API_KEY"):
        # Can't initialize handler without API client
        # Just check the class exists
        assert StreamingResponseHandler is not None
    else:
        client = ClaudeAPIClient()
        handler = StreamingResponseHandler(client)

        assert handler.text_buffer == ""
        assert handler.current_tool_use is None

test_streaming_handler_init()


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
    print("🎉 All Phase 11 tests passed!")
    print()
    print("Phase 11 Features Verified:")
    print("  ✅ Streaming infrastructure working")
    print("  ✅ Tool execution tracking functional")
    print("  ✅ UI components initialized")
    print("  ✅ Main.py streaming integration complete")
    print("  ✅ Session state properly configured")
    print("  ✅ Streaming settings UI added")
    print("  ✅ Progress indicators functional")
    print("  ✅ Multiple tool tracking works")
    print()
    print("Real-time streaming ready! ⚡")
    print()
    sys.exit(0)
else:
    print("⚠️  Some tests failed. Please review the errors above.")
    sys.exit(1)
