"""
Filesystem Tools for Claude

Safe filesystem operations within a sandboxed directory.
All operations are restricted to the sandbox directory for security.

Tools:
- fs_read_file: Read file contents
- fs_write_file: Write to file
- fs_list_files: List directory contents
- fs_mkdir: Create directory
- fs_delete: Delete file or directory
- fs_exists: Check if path exists
- fs_get_info: Get file/directory info
"""

import os
import logging
from pathlib import Path
from typing import Union, List, Dict, Any
import json

logger = logging.getLogger(__name__)

# Default sandbox directory (relative to project root)
DEFAULT_SANDBOX_DIR = "./sandbox"


class FilesystemSandbox:
    """Manages sandboxed filesystem operations"""

    def __init__(self, sandbox_dir: str = DEFAULT_SANDBOX_DIR):
        """
        Initialize filesystem sandbox.

        Args:
            sandbox_dir: Path to sandbox directory
        """
        self.sandbox_dir = Path(sandbox_dir).resolve()
        self._ensure_sandbox_exists()

    def _ensure_sandbox_exists(self):
        """Create sandbox directory if it doesn't exist"""
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, path: str) -> Path:
        """
        Resolve and validate a path within the sandbox.

        Args:
            path: Relative or absolute path

        Returns:
            Absolute path within sandbox

        Raises:
            ValueError: If path escapes sandbox
        """
        # Convert to Path and resolve
        target = (self.sandbox_dir / path).resolve()

        # Security check: ensure path is within sandbox
        try:
            target.relative_to(self.sandbox_dir)
        except ValueError:
            raise ValueError(f"Path '{path}' escapes sandbox directory")

        return target


# Global sandbox instance
_sandbox = FilesystemSandbox()


def fs_read_file(path: str, encoding: str = "utf-8") -> Union[str, dict]:
    """
    Read contents of a file.

    Args:
        path: Path to file (relative to sandbox)
        encoding: File encoding (default: utf-8)

    Returns:
        File contents as string, or error dict

    Example:
        >>> fs_read_file("test.txt")
        "Hello, world!"
    """
    try:
        target = _sandbox._resolve_path(path)

        if not target.exists():
            return {"error": f"File not found: {path}"}

        if not target.is_file():
            return {"error": f"Not a file: {path}"}

        with open(target, "r", encoding=encoding) as f:
            content = f.read()

        logger.info(f"Read file: {path} ({len(content)} bytes)")
        return content

    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return {"error": str(e)}


def fs_write_file(
    path: str,
    content: str,
    encoding: str = "utf-8",
    mode: str = "overwrite"
) -> dict:
    """
    Write content to a file.

    Args:
        path: Path to file (relative to sandbox)
        content: Content to write
        encoding: File encoding (default: utf-8)
        mode: Write mode - "overwrite" or "append"

    Returns:
        Status dict with success/error

    Example:
        >>> fs_write_file("test.txt", "Hello, world!")
        {"success": True, "path": "test.txt", "bytes_written": 13}
    """
    try:
        target = _sandbox._resolve_path(path)

        # Create parent directories if needed
        target.parent.mkdir(parents=True, exist_ok=True)

        # Determine write mode
        write_mode = "a" if mode == "append" else "w"

        with open(target, write_mode, encoding=encoding) as f:
            bytes_written = f.write(content)

        logger.info(f"Wrote file: {path} ({bytes_written} bytes, mode={mode})")

        return {
            "success": True,
            "path": path,
            "bytes_written": bytes_written,
            "mode": mode
        }

    except Exception as e:
        logger.error(f"Error writing file {path}: {e}")
        return {"error": str(e), "success": False}


def fs_list_files(
    path: str = ".",
    recursive: bool = False,
    pattern: str = "*"
) -> Union[List[str], dict]:
    """
    List files and directories.

    Args:
        path: Directory path (relative to sandbox)
        recursive: Whether to list recursively
        pattern: Glob pattern to match (e.g., "*.txt")

    Returns:
        List of file/directory paths, or error dict

    Example:
        >>> fs_list_files(".", pattern="*.txt")
        ["test.txt", "notes.txt"]
    """
    try:
        target = _sandbox._resolve_path(path)

        if not target.exists():
            return {"error": f"Path not found: {path}"}

        if not target.is_dir():
            return {"error": f"Not a directory: {path}"}

        # List files
        if recursive:
            matches = target.rglob(pattern)
        else:
            matches = target.glob(pattern)

        # Convert to relative paths
        results = []
        for match in sorted(matches):
            try:
                rel_path = match.relative_to(_sandbox.sandbox_dir)
                results.append(str(rel_path))
            except ValueError:
                continue

        logger.info(f"Listed {len(results)} items in {path}")
        return results

    except Exception as e:
        logger.error(f"Error listing files in {path}: {e}")
        return {"error": str(e)}


def fs_mkdir(path: str) -> dict:
    """
    Create a directory.

    Args:
        path: Directory path (relative to sandbox)

    Returns:
        Status dict

    Example:
        >>> fs_mkdir("new_folder")
        {"success": True, "path": "new_folder"}
    """
    try:
        target = _sandbox._resolve_path(path)
        target.mkdir(parents=True, exist_ok=True)

        logger.info(f"Created directory: {path}")

        return {
            "success": True,
            "path": path
        }

    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return {"error": str(e), "success": False}


def fs_delete(path: str, recursive: bool = False) -> dict:
    """
    Delete a file or directory.

    Args:
        path: Path to delete (relative to sandbox)
        recursive: Whether to delete directories recursively

    Returns:
        Status dict

    Example:
        >>> fs_delete("old_file.txt")
        {"success": True, "path": "old_file.txt"}
    """
    try:
        target = _sandbox._resolve_path(path)

        if not target.exists():
            return {"error": f"Path not found: {path}"}

        if target.is_file():
            target.unlink()
            logger.info(f"Deleted file: {path}")
        elif target.is_dir():
            if recursive:
                import shutil
                shutil.rmtree(target)
                logger.info(f"Deleted directory recursively: {path}")
            else:
                target.rmdir()
                logger.info(f"Deleted empty directory: {path}")
        else:
            return {"error": f"Unknown file type: {path}"}

        return {
            "success": True,
            "path": path
        }

    except Exception as e:
        logger.error(f"Error deleting {path}: {e}")
        return {"error": str(e), "success": False}


def fs_exists(path: str) -> dict:
    """
    Check if a path exists.

    Args:
        path: Path to check (relative to sandbox)

    Returns:
        Dict with exists status and type

    Example:
        >>> fs_exists("test.txt")
        {"exists": True, "type": "file"}
    """
    try:
        target = _sandbox._resolve_path(path)

        exists = target.exists()
        file_type = None

        if exists:
            if target.is_file():
                file_type = "file"
            elif target.is_dir():
                file_type = "directory"
            else:
                file_type = "other"

        return {
            "exists": exists,
            "type": file_type,
            "path": path
        }

    except Exception as e:
        logger.error(f"Error checking existence of {path}: {e}")
        return {"error": str(e)}


def fs_get_info(path: str) -> dict:
    """
    Get information about a file or directory.

    Args:
        path: Path (relative to sandbox)

    Returns:
        Dict with file info (size, modified time, etc.)

    Example:
        >>> fs_get_info("test.txt")
        {"size": 1024, "modified": "2024-01-01T12:00:00", ...}
    """
    try:
        target = _sandbox._resolve_path(path)

        if not target.exists():
            return {"error": f"Path not found: {path}"}

        stat = target.stat()

        info = {
            "path": path,
            "exists": True,
            "type": "file" if target.is_file() else "directory",
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
        }

        if target.is_file():
            info["extension"] = target.suffix

        logger.info(f"Got info for: {path}")
        return info

    except Exception as e:
        logger.error(f"Error getting info for {path}: {e}")
        return {"error": str(e)}


# Tool schemas for registration
FILESYSTEM_TOOL_SCHEMAS = {
    "fs_read_file": {
        "name": "fs_read_file",
        "description": "Read the contents of a file from the sandbox directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file (relative to sandbox directory)"
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8"
                }
            },
            "required": ["path"]
        }
    },
    "fs_write_file": {
        "name": "fs_write_file",
        "description": "Write content to a file in the sandbox directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file (relative to sandbox directory)"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8"
                },
                "mode": {
                    "type": "string",
                    "enum": ["overwrite", "append"],
                    "description": "Write mode: 'overwrite' replaces file, 'append' adds to end",
                    "default": "overwrite"
                }
            },
            "required": ["path", "content"]
        }
    },
    "fs_list_files": {
        "name": "fs_list_files",
        "description": "List files and directories in the sandbox",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path (relative to sandbox, default: '.')",
                    "default": "."
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to list recursively (default: false)",
                    "default": False
                },
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to filter results (default: '*')",
                    "default": "*"
                }
            },
            "required": []
        }
    },
    "fs_mkdir": {
        "name": "fs_mkdir",
        "description": "Create a directory in the sandbox",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to create (relative to sandbox)"
                }
            },
            "required": ["path"]
        }
    },
    "fs_delete": {
        "name": "fs_delete",
        "description": "Delete a file or directory from the sandbox",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to delete (relative to sandbox)"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to delete directories recursively (default: false)",
                    "default": False
                }
            },
            "required": ["path"]
        }
    },
    "fs_exists": {
        "name": "fs_exists",
        "description": "Check if a file or directory exists in the sandbox",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to check (relative to sandbox)"
                }
            },
            "required": ["path"]
        }
    },
    "fs_get_info": {
        "name": "fs_get_info",
        "description": "Get detailed information about a file or directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path (relative to sandbox)"
                }
            },
            "required": ["path"]
        }
    }
}
