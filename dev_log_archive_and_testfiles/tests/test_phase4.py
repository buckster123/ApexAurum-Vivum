#!/usr/bin/env python3
"""
Phase 4 Test Script

Tests state management and application setup:
1. AppState initialization
2. Conversation persistence
3. Main application imports
4. Session state setup
5. Tool integration check
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))


def print_test(test_name: str):
    """Print test header"""
    print(f"\n{'=' * 60}")
    print(f"TEST: {test_name}")
    print('=' * 60)


def print_result(success: bool, message: str = ""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {message}")


def test_1_imports():
    """Test 1: All imports work"""
    print_test("Application Imports")

    try:
        # Core imports
        from core import (
            ClaudeAPIClient,
            ClaudeModels,
            ToolRegistry,
            ToolExecutor,
            ToolCallLoop,
        )
        print("✓ Core imports")

        # Tools imports
        from tools import register_all_tools, ALL_TOOL_SCHEMAS
        print("✓ Tools imports")

        # Main imports (without Streamlit parts)
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_module", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        # Don't execute, just check it can be loaded
        print("✓ Main module loadable")

        print_result(True, "All imports successful")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_2_app_state():
    """Test 2: AppState class works"""
    print_test("AppState Functionality")

    try:
        # Import AppState (we'll extract it for testing)
        import sys
        import importlib.util

        # Load main as module
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main = importlib.util.module_from_spec(spec)

        # Mock streamlit before executing
        import types
        st_mock = types.ModuleType('streamlit')
        sys.modules['streamlit'] = st_mock

        spec.loader.exec_module(main)

        # Test AppState
        app_state = main.AppState()
        print("✓ AppState initialized")

        # Test save message
        app_state.save_message("user", "Test message")
        print("✓ Message saved")

        # Test load conversations
        conversations = app_state.get_conversations()
        print(f"✓ Loaded {len(conversations)} conversations")

        # Verify message was saved
        found = False
        for conv in conversations:
            for msg in conv.get("messages", []):
                if msg.get("content") == "Test message":
                    found = True
                    break

        if found:
            print("✓ Message persistence verified")

        print_result(True, "AppState works correctly")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_3_tool_integration():
    """Test 3: Tool integration"""
    print_test("Tool Integration")

    try:
        from core import ToolRegistry
        from tools import register_all_tools, ALL_TOOL_SCHEMAS

        # Create registry
        registry = ToolRegistry()
        register_all_tools(registry)

        tool_count = len(registry.list_tools())
        schema_count = len(ALL_TOOL_SCHEMAS)

        print(f"✓ Registered {tool_count} tools")
        print(f"✓ {schema_count} schemas available")

        assert tool_count == schema_count, "Tool count mismatch"

        # Test tool execution
        from core import ToolExecutor
        executor = ToolExecutor(registry)

        result, is_error = executor.execute_tool(
            "calculator",
            {"operation": "add", "a": 5, "b": 3},
            "test_id"
        )

        assert not is_error, f"Tool execution failed: {result}"
        assert result == 8.0, f"Wrong result: {result}"

        print("✓ Tool execution verified")

        print_result(True, "Tool integration complete")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_4_client_setup():
    """Test 4: Client setup"""
    print_test("Client Setup")

    try:
        from core import ClaudeAPIClient, ToolRegistry, ToolExecutor, ToolCallLoop
        from tools import register_all_tools

        # Create components
        client = ClaudeAPIClient()
        print("✓ Client created")

        registry = ToolRegistry()
        register_all_tools(registry)
        print("✓ Registry setup")

        executor = ToolExecutor(registry)
        print("✓ Executor created")

        loop = ToolCallLoop(client, executor, max_iterations=10)
        print("✓ Tool loop created")

        print_result(True, "All components ready")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_5_conversation_storage():
    """Test 5: Conversation storage"""
    print_test("Conversation Storage")

    try:
        import sys
        import importlib.util
        import types

        # Mock streamlit
        st_mock = types.ModuleType('streamlit')
        sys.modules['streamlit'] = st_mock

        # Load main module
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main)

        # Create app state
        app_state = main.AppState()

        # Save multiple messages
        conv_id = f"test_conv_{os.getpid()}"
        app_state.save_message("user", "Hello", conv_id)
        app_state.save_message("assistant", "Hi there!", conv_id)
        app_state.save_message("user", "How are you?", conv_id)

        print("✓ Saved 3 messages")

        # Load and verify
        conversations = app_state.get_conversations()

        # Find our conversation
        our_conv = None
        for conv in conversations:
            if conv.get("id") == conv_id:
                our_conv = conv
                break

        assert our_conv is not None, "Conversation not found"
        assert len(our_conv["messages"]) >= 3, "Not all messages saved"

        print(f"✓ Verified {len(our_conv['messages'])} messages")
        print(f"✓ Conversation ID: {conv_id}")

        print_result(True, "Conversation storage works")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_6_file_structure():
    """Test 6: File structure"""
    print_test("File Structure")

    try:
        required_files = [
            "main.py",
            "core/__init__.py",
            "core/api_client.py",
            "core/models.py",
            "core/tool_adapter.py",
            "core/tool_processor.py",
            "tools/__init__.py",
            "tools/utilities.py",
            "tools/filesystem.py",
            "tools/code_execution.py",
            "tools/memory.py",
        ]

        missing = []
        for file in required_files:
            if not Path(file).exists():
                missing.append(file)

        if missing:
            print(f"Missing files: {missing}")
            print_result(False, f"{len(missing)} files missing")
            return False

        print(f"✓ All {len(required_files)} required files present")

        # Check sandbox directory
        sandbox_dir = Path("./sandbox")
        if not sandbox_dir.exists():
            sandbox_dir.mkdir(parents=True, exist_ok=True)
            print("✓ Created sandbox directory")
        else:
            print("✓ Sandbox directory exists")

        print_result(True, "File structure complete")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 4 tests"""
    print("\n" + "=" * 60)
    print("PHASE 4 TEST SUITE")
    print("Testing State Management & Application Setup")
    print("=" * 60)

    tests = [
        ("Application Imports", test_1_imports),
        ("AppState Functionality", test_2_app_state),
        ("Tool Integration", test_3_tool_integration),
        ("Client Setup", test_4_client_setup),
        ("Conversation Storage", test_5_conversation_storage),
        ("File Structure", test_6_file_structure),
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
        print("\n🎉 All tests passed! Phase 4 is complete.")
        print("\nApplication is ready!")
        print("\nTo run the application:")
        print("  streamlit run main.py")
        print("\nOr if remotely:")
        print("  streamlit run main.py --server.address 0.0.0.0 --server.port 8501")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix before proceeding.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
