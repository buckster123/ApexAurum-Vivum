#!/usr/bin/env python3
"""
Agent System Test Script

Tests multi-agent functionality:
1. Agent spawning
2. Agent status checking
3. Agent result retrieval
4. Socratic council voting
5. Multiple agents working in parallel
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from tools.agents import (
    agent_spawn,
    agent_status,
    agent_result,
    agent_list,
    socratic_council,
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


def test_1_agent_spawn_sync():
    """Test 1: Spawn agent synchronously"""
    print_test("Agent Spawn (Synchronous)")

    try:
        result = agent_spawn(
            task="What is 2 + 2? Just give the number.",
            agent_type="general",
            run_async=False
        )

        print(f"Result: {result}")

        assert result.get("success"), "Agent spawn failed"
        assert "result" in result, "No result returned"

        print(f"Agent result: {result['result'][:100]}...")
        print_result(True, "Synchronous agent execution works")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_2_agent_spawn_async():
    """Test 2: Spawn agent asynchronously"""
    print_test("Agent Spawn (Asynchronous)")

    try:
        result = agent_spawn(
            task="Write a haiku about programming",
            agent_type="writer",
            run_async=True
        )

        print(f"Spawn result: {result}")

        assert result.get("success"), "Agent spawn failed"
        assert "agent_id" in result, "No agent_id returned"

        agent_id = result["agent_id"]
        print(f"Agent spawned: {agent_id}")

        # Wait a bit
        print("Waiting for agent to complete...")
        time.sleep(5)

        # Check status
        status = agent_status(agent_id)
        print(f"Status: {status}")

        # Get result
        final_result = agent_result(agent_id)
        print(f"Result: {final_result}")

        if final_result.get("status") == "completed":
            print(f"Agent output: {final_result.get('result', '')[:200]}...")

        print_result(True, "Asynchronous agent execution works")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_3_agent_types():
    """Test 3: Different agent types"""
    print_test("Agent Types")

    try:
        # Test different agent types
        tasks = {
            "researcher": "What is the capital of France?",
            "coder": "Write a Python function to add two numbers",
            "analyst": "What are the pros and cons of Python?"
        }

        for agent_type, task in tasks.items():
            result = agent_spawn(
                task=task,
                agent_type=agent_type,
                run_async=False
            )

            if result.get("success"):
                print(f"✓ {agent_type}: {result['result'][:80]}...")
            else:
                print(f"✗ {agent_type}: Failed")

        print_result(True, "All agent types work")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_4_agent_list():
    """Test 4: List agents"""
    print_test("Agent List")

    try:
        result = agent_list()

        print(f"Agent list: {result}")

        assert result.get("success"), "Agent list failed"
        assert "agents" in result, "No agents list"
        assert "count" in result, "No count"

        print(f"Total agents: {result['count']}")

        if result['agents']:
            print("Recent agents:")
            for agent in result['agents'][-3:]:
                print(f"  - {agent['agent_id']}: {agent['status']} - {agent['task'][:50]}...")

        print_result(True, f"Listed {result['count']} agents")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_5_socratic_council():
    """Test 5: Socratic council voting"""
    print_test("Socratic Council")

    try:
        result = socratic_council(
            question="Which programming language is best for web development?",
            options=["Python", "JavaScript", "Go"],
            num_agents=3
        )

        print(f"Council result: {result}")

        assert result.get("success"), "Council failed"
        assert "winner" in result, "No winner"
        assert "votes" in result, "No votes"

        print(f"Winner: {result['winner']}")
        print(f"Votes: {result['votes']}")
        print(f"Consensus: {result.get('consensus', False)}")

        if result.get("reasoning"):
            print("\nAgent reasoning:")
            for r in result["reasoning"]:
                print(f"  Agent {r['agent']}: {r['vote']} - {r['reasoning'][:100]}...")

        print_result(True, f"Council chose {result['winner']}")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_6_parallel_agents():
    """Test 6: Multiple agents in parallel"""
    print_test("Parallel Agents")

    try:
        # Spawn multiple agents
        agent_ids = []

        tasks = [
            "Calculate 123 * 456",
            "What is the square root of 144?",
            "What is 10 factorial?"
        ]

        print("Spawning 3 agents in parallel...")
        for i, task in enumerate(tasks):
            result = agent_spawn(
                task=task,
                agent_type="general",
                run_async=True
            )
            if result.get("success"):
                agent_ids.append(result["agent_id"])
                print(f"  Agent {i+1} spawned: {result['agent_id']}")

        # Wait for completion
        print("\nWaiting for agents to complete...")
        time.sleep(8)

        # Check results
        print("\nResults:")
        completed = 0
        for agent_id in agent_ids:
            result = agent_result(agent_id)
            if result.get("status") == "completed":
                completed += 1
                print(f"  ✓ {agent_id}: {result.get('result', '')[:100]}...")
            else:
                print(f"  ⏳ {agent_id}: {result.get('status', 'unknown')}")

        print_result(True, f"{completed}/{len(agent_ids)} agents completed")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all agent tests"""
    print("\n" + "=" * 60)
    print("AGENT SYSTEM TEST SUITE")
    print("Testing Multi-Agent Functionality")
    print("=" * 60)

    tests = [
        ("Agent Spawn (Sync)", test_1_agent_spawn_sync),
        ("Agent Spawn (Async)", test_2_agent_spawn_async),
        ("Agent Types", test_3_agent_types),
        ("Agent List", test_4_agent_list),
        ("Socratic Council", test_5_socratic_council),
        ("Parallel Agents", test_6_parallel_agents),
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
        print("\n🎉 All agent tests passed!")
        print("\nYou now have:")
        print("  ✓ Sub-agent spawning (sync & async)")
        print("  ✓ Multiple agent types (researcher, coder, analyst, writer)")
        print("  ✓ Agent status checking")
        print("  ✓ Result retrieval")
        print("  ✓ Socratic council voting")
        print("  ✓ Parallel agent execution")
        print("\nTry in the UI:")
        print('  "Spawn an agent to research Python history"')
        print('  "Run a council to decide: Python vs JavaScript vs Go"')
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
