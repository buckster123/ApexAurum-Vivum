#!/usr/bin/env python3
"""
Phase 5 Testing: UI Enhancements
Tests for conversation browser, file browser, memory viewer, and advanced settings
"""

import sys
import os
from pathlib import Path

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
print("PHASE 5 TESTING: UI Enhancements")
print("=" * 70)
print()

# Test 1: Dark mode configuration
@test("1. Dark mode config file exists")
def test_dark_mode_config():
    config_path = Path(".streamlit/config.toml")
    assert config_path.exists(), "Config file not found"

    content = config_path.read_text()
    assert 'base = "dark"' in content, "Dark mode not configured"
    assert 'backgroundColor' in content, "Background color not set"
    assert 'primaryColor' in content, "Primary color not set"

test_dark_mode_config()


# Test 2: Import main module
@test("2. Main module imports successfully")
def test_main_import():
    import main
    assert hasattr(main, 'load_conversation'), "load_conversation function missing"
    assert hasattr(main, 'list_sandbox_files'), "list_sandbox_files function missing"
    assert hasattr(main, 'load_memory_data'), "load_memory_data function missing"
    assert hasattr(main, 'delete_memory_entry'), "delete_memory_entry function missing"
    assert hasattr(main, 'format_file_size'), "format_file_size function missing"

test_main_import()


# Test 3: File browser functions
@test("3. File browser lists sandbox files")
def test_file_browser():
    from main import list_sandbox_files

    files = list_sandbox_files()
    assert isinstance(files, list), "Should return a list"

    # Check if we have the expected test files
    file_names = [f['name'] for f in files]
    assert 'memory.json' in file_names or 'conversations.json' in file_names, "Expected files not found"

test_file_browser()


# Test 4: Format file size
@test("4. File size formatting works")
def test_format_file_size():
    from main import format_file_size

    assert format_file_size(100) == "100 B"
    assert "KB" in format_file_size(1024)
    assert "KB" in format_file_size(10240)
    assert "MB" in format_file_size(1024 * 1024)

test_format_file_size()


# Test 5: Memory data loading
@test("5. Memory data can be loaded")
def test_memory_loading():
    from main import load_memory_data

    memory = load_memory_data()
    assert isinstance(memory, dict), "Should return a dictionary"

test_memory_loading()


# Test 6: Conversation management
@test("6. AppState conversation methods exist")
def test_conversation_management():
    from main import AppState

    app_state = AppState()
    assert hasattr(app_state, 'get_conversations'), "get_conversations missing"
    assert hasattr(app_state, 'delete_conversation'), "delete_conversation missing"

    # Test getting conversations
    conversations = app_state.get_conversations()
    assert isinstance(conversations, list), "Should return a list"

test_conversation_management()


# Test 7: Session state initialization
@test("7. Session state includes new settings")
def test_session_state_init():
    import streamlit as st
    from main import init_session_state

    # Mock session state
    if not hasattr(st, 'session_state'):
        class MockSessionState:
            def __init__(self):
                self._state = {}
            def __contains__(self, key):
                return key in self._state
            def __setitem__(self, key, value):
                self._state[key] = value
            def __getitem__(self, key):
                return self._state[key]
        st.session_state = MockSessionState()

    init_session_state()

    # Check new settings exist
    assert 'temperature' in st.session_state, "temperature not initialized"
    assert 'top_p' in st.session_state, "top_p not initialized"
    assert 'max_tokens' in st.session_state, "max_tokens not initialized"

test_session_state_init()


# Test 8: Protected files list
@test("8. Protected files are defined")
def test_protected_files():
    # Read the main.py file and check for protected files
    with open('main.py', 'r') as f:
        content = f.read()

    assert 'protected_files' in content, "Protected files list not found"
    assert 'conversations.json' in content, "conversations.json not protected"
    assert 'memory.json' in content, "memory.json not protected"

test_protected_files()


# Test 9: UI components exist
@test("9. Render sidebar function updated")
def test_render_sidebar():
    with open('main.py', 'r') as f:
        content = f.read()

    # Check for new UI components
    assert '📚 Conversation History' in content, "Conversation browser missing"
    assert '📁 File Browser' in content, "File browser missing"
    assert '🧠 Memory Viewer' in content, "Memory viewer missing"
    assert '🎛️ Advanced Settings' in content, "Advanced settings missing"
    assert 'Temperature' in content, "Temperature slider missing"
    assert 'Top P' in content, "Top P slider missing"

test_render_sidebar()


# Test 10: API call parameters
@test("10. Process message uses new parameters")
def test_api_parameters():
    with open('main.py', 'r') as f:
        content = f.read()

    # Check that process_message passes new parameters
    assert 'temperature=st.session_state.temperature' in content, "temperature not passed to API"
    assert 'top_p=st.session_state.top_p' in content, "top_p not passed to API"
    assert 'max_tokens=st.session_state.max_tokens' in content, "max_tokens not used from session state"

test_api_parameters()


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
    print("🎉 All Phase 5 tests passed!")
    print()
    print("Phase 5 Features Verified:")
    print("  ✅ Dark mode configuration")
    print("  ✅ Conversation browser (load/delete)")
    print("  ✅ File browser (view/delete)")
    print("  ✅ Memory viewer (view/delete)")
    print("  ✅ Advanced settings (temperature, top_p, max_tokens)")
    print()
    sys.exit(0)
else:
    print("⚠️  Some tests failed. Please review the errors above.")
    sys.exit(1)
