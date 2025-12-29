"""
Memory Tools for Claude

Simple key-value memory storage using JSON files.
For Phase 3, this is a basic implementation. Phase 9 will add:
- SQLite database
- ChromaDB vector storage
- Semantic search
- Memory consolidation

Tools:
- memory_store: Store a key-value pair
- memory_retrieve: Retrieve value by key
- memory_list: List all stored keys
- memory_delete: Delete a key
- memory_search: Search memory by keyword
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# Memory storage file
MEMORY_FILE = Path("./sandbox/memory.json")


class SimpleMemory:
    """Simple JSON-based memory storage"""

    def __init__(self, storage_file: Path = MEMORY_FILE):
        """
        Initialize memory storage.

        Args:
            storage_file: Path to JSON storage file
        """
        self.storage_file = storage_file
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Create storage file and directory if needed"""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_file.exists():
            self._save_data({})

    def _load_data(self) -> Dict[str, Any]:
        """Load memory data from file"""
        try:
            with open(self.storage_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            return {}

    def _save_data(self, data: Dict[str, Any]):
        """Save memory data to file"""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")


# Global memory instance
_memory = SimpleMemory()


def memory_store(key: str, value: Any, metadata: Optional[Dict] = None) -> Dict:
    """
    Store a value in memory.

    Args:
        key: Memory key (identifier)
        value: Value to store (can be string, number, list, dict)
        metadata: Optional metadata dict

    Returns:
        Status dict

    Example:
        >>> memory_store("user_name", "Alice")
        {"success": True, "key": "user_name"}
    """
    try:
        data = _memory._load_data()

        # Create memory entry
        entry = {
            "value": value,
            "stored_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        data[key] = entry
        _memory._save_data(data)

        logger.info(f"Stored memory: {key}")

        return {
            "success": True,
            "key": key,
            "stored_at": entry["stored_at"]
        }

    except Exception as e:
        logger.error(f"Error storing memory {key}: {e}")
        return {"success": False, "error": str(e)}


def memory_retrieve(key: str) -> Union[Any, Dict]:
    """
    Retrieve a value from memory.

    Args:
        key: Memory key

    Returns:
        Stored value, or error dict if not found

    Example:
        >>> memory_retrieve("user_name")
        {"value": "Alice", "stored_at": "2024-01-01T12:00:00"}
    """
    try:
        data = _memory._load_data()

        if key not in data:
            return {"error": f"Key not found: {key}", "found": False}

        entry = data[key]

        logger.info(f"Retrieved memory: {key}")

        return {
            "found": True,
            "key": key,
            "value": entry["value"],
            "stored_at": entry["stored_at"],
            "metadata": entry.get("metadata", {})
        }

    except Exception as e:
        logger.error(f"Error retrieving memory {key}: {e}")
        return {"error": str(e), "found": False}


def memory_list(prefix: Optional[str] = None) -> Union[List[str], Dict]:
    """
    List all memory keys.

    Args:
        prefix: Optional prefix filter (e.g., "user_" to get all user keys)

    Returns:
        List of keys, or error dict

    Example:
        >>> memory_list()
        ["user_name", "user_age", "settings"]
        >>> memory_list("user_")
        ["user_name", "user_age"]
    """
    try:
        data = _memory._load_data()

        keys = list(data.keys())

        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]

        logger.info(f"Listed {len(keys)} memory keys")

        return keys

    except Exception as e:
        logger.error(f"Error listing memory: {e}")
        return {"error": str(e)}


def memory_delete(key: str) -> Dict:
    """
    Delete a key from memory.

    Args:
        key: Memory key to delete

    Returns:
        Status dict

    Example:
        >>> memory_delete("old_key")
        {"success": True, "key": "old_key"}
    """
    try:
        data = _memory._load_data()

        if key not in data:
            return {"success": False, "error": f"Key not found: {key}"}

        del data[key]
        _memory._save_data(data)

        logger.info(f"Deleted memory: {key}")

        return {
            "success": True,
            "key": key
        }

    except Exception as e:
        logger.error(f"Error deleting memory {key}: {e}")
        return {"success": False, "error": str(e)}


def memory_search(query: str, limit: int = 10) -> Union[List[Dict], Dict]:
    """
    Search memory by keyword (simple text search).

    Args:
        query: Search query
        limit: Maximum results to return

    Returns:
        List of matching entries, or error dict

    Example:
        >>> memory_search("Alice")
        [{"key": "user_name", "value": "Alice", ...}]
    """
    try:
        data = _memory._load_data()

        query_lower = query.lower()
        results = []

        for key, entry in data.items():
            # Simple keyword search in key and value
            value_str = str(entry["value"]).lower()
            if query_lower in key.lower() or query_lower in value_str:
                results.append({
                    "key": key,
                    "value": entry["value"],
                    "stored_at": entry["stored_at"],
                    "metadata": entry.get("metadata", {})
                })

                if len(results) >= limit:
                    break

        logger.info(f"Memory search for '{query}': {len(results)} results")

        return results

    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        return {"error": str(e)}


# Tool schemas for registration
MEMORY_TOOL_SCHEMAS = {
    "memory_store": {
        "name": "memory_store",
        "description": "Store a value in memory with a key for later retrieval. Use this to remember information across conversations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Unique key to identify this memory (e.g., 'user_name', 'user_preferences')"
                },
                "value": {
                    "description": "Value to store (can be string, number, array, or object)"
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional metadata about this memory",
                    "default": {}
                }
            },
            "required": ["key", "value"]
        }
    },
    "memory_retrieve": {
        "name": "memory_retrieve",
        "description": "Retrieve a previously stored value from memory by its key",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Key of the memory to retrieve"
                }
            },
            "required": ["key"]
        }
    },
    "memory_list": {
        "name": "memory_list",
        "description": "List all stored memory keys, optionally filtered by prefix",
        "input_schema": {
            "type": "object",
            "properties": {
                "prefix": {
                    "type": "string",
                    "description": "Optional prefix to filter keys (e.g., 'user_' to get all user-related keys)",
                    "default": None
                }
            },
            "required": []
        }
    },
    "memory_delete": {
        "name": "memory_delete",
        "description": "Delete a memory by its key",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Key of the memory to delete"
                }
            },
            "required": ["key"]
        }
    },
    "memory_search": {
        "name": "memory_search",
        "description": "Search memory entries by keyword (searches both keys and values)",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }
}
