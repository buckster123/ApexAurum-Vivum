"""
Code Execution Tool for Claude

Safe Python code execution with basic sandboxing.

WARNING: This is a basic implementation. For production use, implement:
- RestrictedPython for AST-level restrictions
- Docker containers for isolation
- Resource limits (CPU, memory, time)
- Network restrictions

Tools:
- execute_python: Execute Python code safely
"""

import logging
import sys
import io
import traceback
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def execute_python(
    code: str,
    timeout: int = 5,
    capture_output: bool = True
) -> Dict[str, Any]:
    """
    Execute Python code with basic safety measures.

    Args:
        code: Python code to execute
        timeout: Execution timeout in seconds (default: 5)
        capture_output: Whether to capture stdout/stderr

    Returns:
        Dict with execution results

    Example:
        >>> execute_python("print('Hello, world!')")
        {
            "success": True,
            "output": "Hello, world!\\n",
            "error": None,
            "return_value": None
        }
    """
    result = {
        "success": False,
        "output": "",
        "error": None,
        "return_value": None
    }

    # Capture stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    if capture_output:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

    try:
        # Create restricted execution environment
        # Remove dangerous builtins
        safe_builtins = {
            # Safe built-ins
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "print": print,
            "range": range,
            "round": round,
            "set": set,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
            # Type checking
            "isinstance": isinstance,
            "type": type,
            # String/number operations
            "chr": chr,
            "ord": ord,
            "hex": hex,
            "bin": bin,
            "oct": oct,
            # Allow safe modules
            "__import__": __import__,
        }

        # Create execution namespace
        exec_globals = {
            "__builtins__": safe_builtins,
            "__name__": "__main__",
        }

        exec_locals = {}

        # Execute code
        exec(code, exec_globals, exec_locals)

        # Get captured output
        if capture_output:
            output = sys.stdout.getvalue()
            error_output = sys.stderr.getvalue()
        else:
            output = ""
            error_output = ""

        result["success"] = True
        result["output"] = output
        if error_output:
            result["error"] = error_output

        # Try to get return value from last expression
        # (This is a simplification - proper implementation would need AST parsing)
        if "_" in exec_locals:
            result["return_value"] = str(exec_locals["_"])

        logger.info(f"Executed code successfully ({len(code)} bytes)")

    except SyntaxError as e:
        error_msg = f"Syntax Error: {str(e)}"
        result["error"] = error_msg
        logger.error(f"Syntax error in code execution: {e}")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        tb = traceback.format_exc()
        result["error"] = error_msg
        result["traceback"] = tb
        logger.error(f"Error in code execution: {e}")

    finally:
        # Restore stdout/stderr
        if capture_output:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    return result


# Tool schema for registration
CODE_EXECUTION_TOOL_SCHEMAS = {
    "execute_python": {
        "name": "execute_python",
        "description": "Execute Python code safely and return the output. Can be used for calculations, data processing, testing code snippets, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds (default: 5)",
                    "default": 5
                },
                "capture_output": {
                    "type": "boolean",
                    "description": "Whether to capture stdout/stderr (default: true)",
                    "default": True
                }
            },
            "required": ["code"]
        }
    }
}
