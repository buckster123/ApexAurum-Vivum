#!/usr/bin/env python3
"""
Phase 10 Testing: Agent Tools UI & Management
Tests for agent management UI, spawn dialogs, and Socratic council integration
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
print("PHASE 10 TESTING: Agent Tools UI & Management")
print("=" * 70)
print()

# Test 1: Agent tools are registered
@test("1. Agent tools are registered")
def test_agent_tools_registered():
    from tools import ALL_TOOL_SCHEMAS
    assert "agent_spawn" in ALL_TOOL_SCHEMAS, "agent_spawn should be registered"
    assert "agent_status" in ALL_TOOL_SCHEMAS, "agent_status should be registered"
    assert "agent_result" in ALL_TOOL_SCHEMAS, "agent_result should be registered"
    assert "agent_list" in ALL_TOOL_SCHEMAS, "agent_list should be registered"
    assert "socratic_council" in ALL_TOOL_SCHEMAS, "socratic_council should be registered"

test_agent_tools_registered()


# Test 2: Agent manager initializes
@test("2. Agent manager initializes correctly")
def test_agent_manager():
    from tools.agents import _agent_manager
    assert _agent_manager is not None, "Agent manager should exist"
    agents = _agent_manager.list_agents()
    assert isinstance(agents, list), "Should return list of agents"

test_agent_manager()


# Test 3: Agent spawn works (sync mode for testing)
@test("3. Agent spawn returns proper structure")
def test_agent_spawn():
    from tools.agents import agent_spawn
    import os

    # Skip if no API key (can't actually run agent)
    if not os.getenv("ANTHROPIC_API_KEY"):
        # Just test that it returns proper error structure
        result = agent_spawn(
            task="Test task",
            agent_type="general",
            run_async=False
        )
        # Should return a result dict
        assert isinstance(result, dict), "Should return dict"
        assert "success" in result or "error" in result, "Should have success or error key"
    else:
        # With API key, test actual spawn
        result = agent_spawn(
            task="Say hello in one word",
            agent_type="general",
            run_async=False
        )
        assert result.get("success") == True, "Agent spawn should succeed"
        assert "agent_id" in result, "Should return agent_id"

test_agent_spawn()


# Test 4: Agent status works
@test("4. Agent status retrieval works")
def test_agent_status():
    from tools.agents import agent_spawn, agent_status

    # Spawn agent
    result = agent_spawn("Test task", agent_type="general", run_async=False)
    agent_id = result["agent_id"]

    # Check status
    status = agent_status(agent_id)
    assert status.get("found") == True, "Agent should be found"
    assert status.get("status") in ["completed", "failed", "running"], "Should have valid status"

test_agent_status()


# Test 5: Agent result retrieval
@test("5. Agent result retrieval works")
def test_agent_result():
    from tools.agents import agent_spawn, agent_result

    # Spawn agent
    result = agent_spawn("Say hello", agent_type="general", run_async=False)
    agent_id = result["agent_id"]

    # Get result
    result_data = agent_result(agent_id)
    assert result_data.get("found") == True, "Agent should be found"
    assert "status" in result_data, "Should have status"

test_agent_result()


# Test 6: Agent list works
@test("6. Agent list functionality works")
def test_agent_list():
    from tools.agents import agent_list

    result = agent_list()
    assert result.get("success") == True, "Agent list should succeed"
    assert "agents" in result, "Should return agents list"
    assert "count" in result, "Should return count"
    assert isinstance(result["agents"], list), "Agents should be a list"

test_agent_list()


# Test 7: Socratic council (simple test)
@test("7. Socratic council returns proper structure")
def test_socratic_council():
    from tools.agents import socratic_council
    import os

    # Skip actual execution if no API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        # Just test that it returns proper error structure
        result = socratic_council(
            question="Which is simpler?",
            options=["A", "B"],
            num_agents=1
        )
        # Should return a result dict
        assert isinstance(result, dict), "Should return dict"
        assert "success" in result or "error" in result, "Should have success or error key"
    else:
        # With API key, test actual council
        result = socratic_council(
            question="Which is simpler?",
            options=["A", "B"],
            num_agents=1  # Minimal for testing
        )
        assert result.get("success") == True, "Council should succeed"
        assert "winner" in result, "Should have a winner"
        assert "votes" in result, "Should have votes"
        assert result["winner"] in ["A", "B"], "Winner should be one of the options"

test_socratic_council()


# Test 8: UI imports in main.py
@test("8. Main.py has agent UI components")
def test_ui_imports():
    with open('main.py', 'r') as f:
        content = f.read()

    assert 'Agent Management' in content, "Should have Agent Management section"
    assert 'agent_spawn' in content, "Should use agent_spawn"
    assert 'show_spawn_agent' in content, "Should have spawn dialog state"
    assert 'view_agent_result' in content, "Should have result viewer state"
    assert 'show_council' in content, "Should have council dialog state"

test_ui_imports()


# Test 9: Session state initialization
@test("9. Session state includes agent UI state")
def test_session_state():
    with open('main.py', 'r') as f:
        content = f.read()

    assert 'show_spawn_agent' in content, "Should init show_spawn_agent"
    assert 'show_council' in content, "Should init show_council"
    assert 'council_options' in content, "Should init council_options"
    assert 'view_agent_result' in content, "Should init view_agent_result"

test_session_state()


# Test 10: Agent manager storage
@test("10. Agent manager has storage")
def test_agent_storage():
    from tools.agents import _agent_manager
    from pathlib import Path

    assert _agent_manager.storage_file is not None, "Should have storage file"
    assert isinstance(_agent_manager.storage_file, Path), "Storage should be a Path"

    # Storage directory should exist
    assert _agent_manager.storage_file.parent.exists(), "Storage directory should exist"

test_agent_storage()


# Test 11: Agent types are valid
@test("11. Agent types are properly defined")
def test_agent_types():
    from tools.agents import Agent

    # Test creating agents of each type
    types = ["general", "researcher", "coder", "analyst", "writer"]

    for agent_type in types:
        agent = Agent(
            agent_id=f"test_{agent_type}",
            task="Test task",
            agent_type=agent_type
        )
        assert agent.agent_type == agent_type, f"Agent type should be {agent_type}"

test_agent_types()


# Test 12: Tool schemas have required fields
@test("12. Agent tool schemas are valid")
def test_tool_schemas():
    from tools.agents import AGENT_TOOL_SCHEMAS

    required_fields = ["name", "description", "input_schema"]

    for tool_name, schema in AGENT_TOOL_SCHEMAS.items():
        for field in required_fields:
            assert field in schema, f"{tool_name} missing {field}"

        # Check input schema structure
        assert "type" in schema["input_schema"], f"{tool_name} input_schema missing type"
        assert "properties" in schema["input_schema"], f"{tool_name} input_schema missing properties"

test_tool_schemas()


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
    print("🎉 All Phase 10 tests passed!")
    print()
    print("Phase 10 Features Verified:")
    print("  ✅ Agent tools registered and working")
    print("  ✅ Agent manager initialized")
    print("  ✅ Agent spawn/status/result")
    print("  ✅ Agent list functionality")
    print("  ✅ Socratic council voting")
    print("  ✅ UI components in main.py")
    print("  ✅ Session state properly initialized")
    print("  ✅ Agent storage configured")
    print("  ✅ Agent types validated")
    print("  ✅ Tool schemas valid")
    print()
    print("Multi-agent system ready! 🚀")
    print()
    sys.exit(0)
else:
    print("⚠️  Some tests failed. Please review the errors above.")
    sys.exit(1)
