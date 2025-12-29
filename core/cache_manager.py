"""
Cache Manager - Phase 14

Orchestrates prompt caching with 4 strategies:
- Disabled: No caching (default, backward compatible)
- Conservative: Cache only system + tools
- Balanced: Cache system + tools + older history (5+ turns back)
- Aggressive: Cache system + tools + most history (3+ turns back)

Implements Anthropic's prompt caching with cache_control breakpoints.
"""

import hashlib
import json
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategies with increasing aggressiveness"""
    DISABLED = "disabled"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class CacheManager:
    """
    Manages prompt caching for Anthropic API requests.

    Places cache_control breakpoints strategically to maximize savings
    while maintaining performance.
    """

    MIN_CACHEABLE_TOKENS = 1024  # Anthropic's minimum for caching

    def __init__(self, strategy: CacheStrategy = CacheStrategy.DISABLED):
        """
        Initialize cache manager with strategy.

        Args:
            strategy: Caching strategy to use
        """
        self.strategy = strategy

        # Track content hashes for change detection
        self.previous_system_hash = None
        self.previous_tools_hash = None

        # Cache status tracking
        self.system_cached = False
        self.tools_cached = False
        self.history_cached = False
        self.history_cached_count = 0

        logger.info(f"CacheManager initialized with strategy: {strategy.value}")

    def apply_cache_controls(
        self,
        system: Optional[Any],
        tools: Optional[List[Dict]],
        messages: List[Dict]
    ) -> Tuple[Any, Optional[List[Dict]], List[Dict]]:
        """
        Apply cache control breakpoints based on strategy.

        Args:
            system: System prompt (string or list of content blocks)
            tools: Tool definitions
            messages: Conversation messages

        Returns:
            Tuple of (modified_system, modified_tools, modified_messages)
        """
        if self.strategy == CacheStrategy.DISABLED:
            # No caching
            return system, tools, messages

        # Reset cache status
        self.system_cached = False
        self.tools_cached = False
        self.history_cached = False
        self.history_cached_count = 0

        # Apply caching based on strategy
        if self.strategy == CacheStrategy.CONSERVATIVE:
            system = self._cache_system(system)
            tools = self._cache_tools(tools)

        elif self.strategy == CacheStrategy.BALANCED:
            system = self._cache_system(system)
            tools = self._cache_tools(tools)
            messages = self._cache_history(messages, turns_back=5)

        elif self.strategy == CacheStrategy.AGGRESSIVE:
            system = self._cache_system(system)
            tools = self._cache_tools(tools)
            messages = self._cache_history(messages, turns_back=3)

        return system, tools, messages

    def _cache_system(self, system: Optional[Any]) -> Optional[Any]:
        """
        Add cache control to system prompt.

        Args:
            system: System prompt (string or list)

        Returns:
            System prompt with cache control
        """
        if not system:
            return system

        # Estimate tokens (rough: ~4 chars per token)
        if isinstance(system, str):
            estimated_tokens = len(system) / 4
        elif isinstance(system, list):
            total_chars = sum(len(str(block.get("text", ""))) for block in system)
            estimated_tokens = total_chars / 4
        else:
            return system

        # Only cache if meets minimum size
        if estimated_tokens < self.MIN_CACHEABLE_TOKENS:
            logger.debug(f"System prompt too small for caching ({estimated_tokens:.0f} tokens < {self.MIN_CACHEABLE_TOKENS})")
            return system

        # Convert string to content block format with cache control
        if isinstance(system, str):
            system = [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"}
                }
            ]
            self.system_cached = True
            logger.debug("Applied cache control to system prompt (string → content block)")

        elif isinstance(system, list):
            # Add cache control to last block
            if system:
                system[-1]["cache_control"] = {"type": "ephemeral"}
                self.system_cached = True
                logger.debug("Applied cache control to system prompt (last content block)")

        # Update hash for change detection
        system_str = json.dumps(system) if isinstance(system, list) else system
        self.previous_system_hash = self._hash_content(system_str)

        return system

    def _cache_tools(self, tools: Optional[List[Dict]]) -> Optional[List[Dict]]:
        """
        Add cache control to tool definitions.

        Args:
            tools: Tool definitions list

        Returns:
            Tools with cache control on last tool
        """
        if not tools or len(tools) == 0:
            return tools

        # Estimate total tokens in tool schemas
        tools_json = json.dumps(tools)
        estimated_tokens = len(tools_json) / 4

        # Only cache if meets minimum size
        if estimated_tokens < self.MIN_CACHEABLE_TOKENS:
            logger.debug(f"Tools too small for caching ({estimated_tokens:.0f} tokens < {self.MIN_CACHEABLE_TOKENS})")
            return tools

        # Add cache control to last tool
        tools[-1]["cache_control"] = {"type": "ephemeral"}
        self.tools_cached = True

        # Update hash for change detection
        self.previous_tools_hash = self._hash_content(tools_json)

        logger.debug(f"Applied cache control to tools (last of {len(tools)} tools)")

        return tools

    def _cache_history(
        self,
        messages: List[Dict],
        turns_back: int
    ) -> List[Dict]:
        """
        Add cache control to older conversation history.

        Args:
            messages: Conversation messages
            turns_back: How many turns back to start caching (3 or 5)

        Returns:
            Messages with cache control applied
        """
        if not messages or len(messages) < turns_back * 2:
            # Not enough history to cache
            return messages

        # Find the message to cache (turns_back from end)
        # Each turn = user + assistant message (2 messages)
        cache_index = len(messages) - (turns_back * 2)

        if cache_index < 0:
            return messages

        # Get the message at cache point
        cache_message = messages[cache_index]

        # Convert content to content block format if needed
        if isinstance(cache_message.get("content"), str):
            # String content → convert to content blocks
            messages[cache_index] = {
                "role": cache_message["role"],
                "content": [
                    {
                        "type": "text",
                        "text": cache_message["content"]
                    },
                    {
                        "type": "text",
                        "text": "",  # Empty block for cache control
                        "cache_control": {"type": "ephemeral"}
                    }
                ]
            }
            self.history_cached = True
            self.history_cached_count = cache_index + 1
            logger.debug(f"Applied cache control to history at message {cache_index} ({turns_back} turns back)")

        elif isinstance(cache_message.get("content"), list):
            # Already content blocks → add cache control to last block
            cache_message["content"].append({
                "type": "text",
                "text": "",  # Empty marker
                "cache_control": {"type": "ephemeral"}
            })
            self.history_cached = True
            self.history_cached_count = cache_index + 1
            logger.debug(f"Applied cache control to history at message {cache_index} (content blocks)")

        return messages

    def _hash_content(self, content: str) -> str:
        """
        Generate hash for content change detection.

        Args:
            content: Content to hash

        Returns:
            Short hash string (16 chars)
        """
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def detect_content_change(
        self,
        system: Optional[str],
        tools: Optional[List[Dict]]
    ) -> Dict[str, bool]:
        """
        Detect if system or tools have changed since last request.

        Args:
            system: Current system prompt
            tools: Current tool definitions

        Returns:
            Dict with change flags: {"system_changed": bool, "tools_changed": bool}
        """
        changes = {
            "system_changed": False,
            "tools_changed": False
        }

        # Check system change
        if system:
            current_hash = self._hash_content(system)
            if self.previous_system_hash and current_hash != self.previous_system_hash:
                changes["system_changed"] = True
                logger.info("System prompt changed - cache will be invalidated")

        # Check tools change
        if tools:
            tools_json = json.dumps(tools)
            current_hash = self._hash_content(tools_json)
            if self.previous_tools_hash and current_hash != self.previous_tools_hash:
                changes["tools_changed"] = True
                logger.info("Tools changed - cache will be invalidated")

        return changes

    def get_cache_status(self) -> Dict[str, Any]:
        """
        Get current cache status.

        Returns:
            Dict with cache state information
        """
        return {
            "strategy": self.strategy.value,
            "system_cached": self.system_cached,
            "tools_cached": self.tools_cached,
            "history_cached": self.history_cached,
            "history_cached_count": self.history_cached_count,
            "system_hash": self.previous_system_hash or "N/A",
            "tools_hash": self.previous_tools_hash or "N/A"
        }

    def invalidate_cache(self):
        """
        Force cache invalidation by resetting hashes.

        This will cause cache misses on next request, forcing rebuild.
        """
        self.previous_system_hash = None
        self.previous_tools_hash = None

        self.system_cached = False
        self.tools_cached = False
        self.history_cached = False
        self.history_cached_count = 0

        logger.info("Cache invalidated - will rebuild on next request")

    def get_strategy_info(self) -> Dict[str, str]:
        """
        Get information about current strategy.

        Returns:
            Dict with strategy details
        """
        strategy_descriptions = {
            CacheStrategy.DISABLED: {
                "name": "Disabled",
                "description": "No caching (backward compatible)",
                "caches": "Nothing",
                "savings": "0%"
            },
            CacheStrategy.CONSERVATIVE: {
                "name": "Conservative",
                "description": "Cache only stable content",
                "caches": "System prompt + Tool definitions",
                "savings": "20-40%"
            },
            CacheStrategy.BALANCED: {
                "name": "Balanced",
                "description": "Cache stable content + older history",
                "caches": "System + Tools + History (5+ turns back)",
                "savings": "50-70%"
            },
            CacheStrategy.AGGRESSIVE: {
                "name": "Aggressive",
                "description": "Maximum caching for maximum savings",
                "caches": "System + Tools + Most History (3+ turns back)",
                "savings": "70-90%"
            }
        }

        return strategy_descriptions.get(self.strategy, {
            "name": "Unknown",
            "description": "Unknown strategy",
            "caches": "Unknown",
            "savings": "Unknown"
        })
