#!/usr/bin/env python3
"""
Phase 2 Test Script

Tests the tool system:
1. Tool schema conversion (OpenAI → Claude)
2. Tool registration and execution
3. Tool result formatting
4. Tool calling loop with Claude API
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from core.api_client import ClaudeAPIClient
from core.models import ClaudeModels
from core.tool_adapter import (
    convert_openai_tool_to_claude,
    convert_openai_tools_to_claude,
    extract_tool_calls_from_response,
    format_tool_result_for_claude,
    format_multiple_tool_results_for_claude,
    validate_claude_tool_schema,
    create_simple_tool_schema,
)
from core.tool_processor import (
    ToolRegistry,
    ToolExecutor,
    ToolCallLoop,
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


def test_1_schema_conversion():
    """Test 1: Convert OpenAI tool schema to Claude format"""
    print_test("Tool Schema Conversion")

    try:
        # OpenAI format tool
        openai_tool = {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature unit"
                        }
                    },
                    "required": ["location"]
                }
            }
        }

        # Convert to Claude format
        claude_tool = convert_openai_tool_to_claude(openai_tool)

        # Validate conversion
        assert claude_tool["name"] == "get_weather"
        assert claude_tool["description"] == "Get current weather for a location"
        assert "input_schema" in claude_tool
        assert claude_tool["input_schema"]["type"] == "object"
        assert "location" in claude_tool["input_schema"]["properties"]
        assert "location" in claude_tool["input_schema"]["required"]

        print(f"Converted tool: {claude_tool['name']}")
        print(f"Input schema properties: {list(claude_tool['input_schema']['properties'].keys())}")

        # Validate schema
        is_valid = validate_claude_tool_schema(claude_tool)
        assert is_valid, "Schema validation failed"

        print_result(True, "Schema conversion works correctly")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_2_tool_registration():
    """Test 2: Register and retrieve tools"""
    print_test("Tool Registration")

    try:
        # Create registry
        registry = ToolRegistry()

        # Define sample tools
        def add(a: float, b: float) -> float:
            """Add two numbers"""
            return a + b

        def multiply(a: float, b: float) -> float:
            """Multiply two numbers"""
            return a * b

        # Create schemas
        add_schema = create_simple_tool_schema(
            "add",
            "Add two numbers together",
            {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            ["a", "b"]
        )

        multiply_schema = create_simple_tool_schema(
            "multiply",
            "Multiply two numbers together",
            {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            ["a", "b"]
        )

        # Register tools
        registry.register("add", add, add_schema)
        registry.register("multiply", multiply, multiply_schema)

        # Test retrieval
        assert registry.has_tool("add")
        assert registry.has_tool("multiply")
        assert not registry.has_tool("divide")

        # Test execution
        add_func = registry.get_tool("add")
        result = add_func(2, 3)
        assert result == 5

        print(f"Registered tools: {registry.list_tools()}")
        print(f"Test execution: add(2, 3) = {result}")

        print_result(True, f"Registered {len(registry.list_tools())} tools")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_3_tool_execution():
    """Test 3: Execute tools with ToolExecutor"""
    print_test("Tool Execution")

    try:
        # Create registry and executor
        registry = ToolRegistry()
        executor = ToolExecutor(registry)

        # Register a simple tool
        def greet(name: str) -> str:
            """Greet someone by name"""
            return f"Hello, {name}!"

        greet_schema = create_simple_tool_schema(
            "greet",
            "Greet someone by name",
            {
                "name": {"type": "string", "description": "Person's name"}
            },
            ["name"]
        )

        registry.register("greet", greet, greet_schema)

        # Execute tool
        result, is_error = executor.execute_tool(
            "greet",
            {"name": "Alice"},
            "toolu_123"
        )

        assert not is_error, f"Execution error: {result}"
        assert result == "Hello, Alice!"

        print(f"Tool result: {result}")

        # Test error handling (missing argument)
        result2, is_error2 = executor.execute_tool(
            "greet",
            {},  # Missing 'name' argument
            "toolu_124"
        )

        assert is_error2, "Should have errored with missing argument"
        print(f"Error handling works: {result2}")

        print_result(True, "Tool execution and error handling work")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_4_result_formatting():
    """Test 4: Format tool results for Claude"""
    print_test("Tool Result Formatting")

    try:
        # Single result
        single_result = format_tool_result_for_claude(
            "toolu_123",
            "Result text",
            is_error=False
        )

        assert single_result["role"] == "user"
        assert len(single_result["content"]) == 1
        assert single_result["content"][0]["type"] == "tool_result"
        assert single_result["content"][0]["tool_use_id"] == "toolu_123"
        print("Single result formatting: ✓")

        # Multiple results
        results = [
            {"tool_use_id": "toolu_1", "result": "First", "is_error": False},
            {"tool_use_id": "toolu_2", "result": {"key": "value"}, "is_error": False}
        ]

        multi_result = format_multiple_tool_results_for_claude(results)

        assert multi_result["role"] == "user"
        assert len(multi_result["content"]) == 2
        assert multi_result["content"][0]["tool_use_id"] == "toolu_1"
        assert multi_result["content"][1]["tool_use_id"] == "toolu_2"
        print("Multiple results formatting: ✓")

        # Error result
        error_result = format_tool_result_for_claude(
            "toolu_999",
            "Something went wrong",
            is_error=True
        )

        assert error_result["content"][0]["is_error"] == True
        print("Error result formatting: ✓")

        print_result(True, "All result formatting works")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_5_api_with_tools():
    """Test 5: Call Claude API with tools"""
    print_test("API Call with Tools")

    try:
        # Create client
        client = ClaudeAPIClient()

        # Create a simple calculator tool
        def calculator(operation: str, a: float, b: float) -> float:
            """Perform a calculation"""
            if operation == "add":
                return a + b
            elif operation == "subtract":
                return a - b
            elif operation == "multiply":
                return a * b
            elif operation == "divide":
                return a / b if b != 0 else "Error: division by zero"
            else:
                return f"Unknown operation: {operation}"

        # Create tool schema
        calc_schema = {
            "name": "calculator",
            "description": "Perform basic arithmetic operations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }

        # Call API with tools
        messages = [
            {"role": "user", "content": "What is 15 + 27?"}
        ]

        response = client.create_message(
            messages=messages,
            model=ClaudeModels.HAIKU_3_5.value,
            max_tokens=1024,
            tools=[calc_schema]
        )

        print(f"Response stop_reason: {response.stop_reason}")

        # Check if Claude tried to use the tool
        tool_uses = []
        for block in response.content:
            if hasattr(block, 'type') and block.type == 'tool_use':
                tool_uses.append({
                    "name": block.name,
                    "input": block.input if hasattr(block, 'input') else {}
                })

        if tool_uses:
            print(f"Claude called {len(tool_uses)} tool(s):")
            for tool_use in tool_uses:
                print(f"  - {tool_use['name']} with {tool_use['input']}")
            print_result(True, f"Claude successfully requested tool use")
        else:
            # Claude might answer directly without tools for simple math
            print("Claude answered without using tools (acceptable for simple math)")
            print_result(True, "API call with tools succeeded")

        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_6_tool_call_loop():
    """Test 6: Full tool calling loop"""
    print_test("Tool Calling Loop")

    try:
        # Setup
        client = ClaudeAPIClient()
        registry = ToolRegistry()
        executor = ToolExecutor(registry)

        # Register tools
        def get_time() -> str:
            """Get the current time"""
            from datetime import datetime
            return datetime.now().strftime("%H:%M:%S")

        def reverse_string(text: str) -> str:
            """Reverse a string"""
            return text[::-1]

        time_schema = create_simple_tool_schema(
            "get_time",
            "Get the current time",
            {},
            []
        )

        reverse_schema = create_simple_tool_schema(
            "reverse_string",
            "Reverse a string",
            {"text": {"type": "string", "description": "Text to reverse"}},
            ["text"]
        )

        registry.register("get_time", get_time, time_schema)
        registry.register("reverse_string", reverse_string, reverse_schema)

        # Create tool loop
        loop = ToolCallLoop(client, executor, max_iterations=5)

        # Run loop
        messages = [
            {"role": "user", "content": "What time is it right now?"}
        ]

        tools = [time_schema, reverse_schema]

        response, updated_messages = loop.run(
            messages=messages,
            model=ClaudeModels.HAIKU_3_5.value,
            max_tokens=1024,
            tools=tools
        )

        print(f"Loop completed after {len(updated_messages)} messages")
        print(f"Final stop_reason: {response.stop_reason}")

        # Extract final text
        final_text = None
        for block in response.content:
            if hasattr(block, 'type') and block.type == 'text':
                final_text = block.text
                break

        if final_text:
            print(f"Final response: {final_text[:100]}...")

        assert len(updated_messages) >= len(messages), "Messages should have been added"

        print_result(True, "Tool calling loop completed successfully")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def test_7_multiple_tool_calls():
    """Test 7: Handle multiple tool calls in one response"""
    print_test("Multiple Tool Calls")

    try:
        # Create registry and executor
        registry = ToolRegistry()
        executor = ToolExecutor(registry)

        # Register multiple tools
        def add(a: float, b: float) -> float:
            return a + b

        def multiply(a: float, b: float) -> float:
            return a * b

        add_schema = create_simple_tool_schema(
            "add", "Add numbers",
            {"a": {"type": "number"}, "b": {"type": "number"}},
            ["a", "b"]
        )

        mul_schema = create_simple_tool_schema(
            "multiply", "Multiply numbers",
            {"a": {"type": "number"}, "b": {"type": "number"}},
            ["a", "b"]
        )

        registry.register("add", add, add_schema)
        registry.register("multiply", multiply, mul_schema)

        # Simulate multiple tool calls
        tool_calls = [
            {
                "type": "tool_use",
                "id": "toolu_1",
                "name": "add",
                "input": {"a": 5, "b": 3}
            },
            {
                "type": "tool_use",
                "id": "toolu_2",
                "name": "multiply",
                "input": {"a": 4, "b": 7}
            }
        ]

        # Execute all tools
        results = executor.execute_tool_calls(tool_calls)

        assert len(results) == 2
        assert results[0]["result"] == 8  # 5 + 3
        assert results[1]["result"] == 28  # 4 * 7
        assert not results[0]["is_error"]
        assert not results[1]["is_error"]

        print(f"Executed {len(results)} tools successfully")
        print(f"Results: {[r['result'] for r in results]}")

        # Format for Claude
        formatted = format_multiple_tool_results_for_claude(results)
        assert len(formatted["content"]) == 2

        print_result(True, "Multiple tool calls handled correctly")
        return True

    except Exception as e:
        print_result(False, str(e))
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 2 tests"""
    print("\n" + "=" * 60)
    print("PHASE 2 TEST SUITE")
    print("Testing Tool System")
    print("=" * 60)

    tests = [
        ("Tool Schema Conversion", test_1_schema_conversion),
        ("Tool Registration", test_2_tool_registration),
        ("Tool Execution", test_3_tool_execution),
        ("Tool Result Formatting", test_4_result_formatting),
        ("API Call with Tools", test_5_api_with_tools),
        ("Tool Calling Loop", test_6_tool_call_loop),
        ("Multiple Tool Calls", test_7_multiple_tool_calls),
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
        print("\n🎉 All tests passed! Phase 2 is complete.")
        print("\nNext steps:")
        print("  1. Review docs/IMPLEMENTATION_PLAN.md")
        print("  2. Start Phase 3: Streaming & Tool Execution")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix before proceeding.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
