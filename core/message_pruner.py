"""
Message Pruner for Context Management

Intelligently removes or compresses less important messages to reduce
context size while preserving critical information.
"""

import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MessagePruner:
    """
    Intelligently prunes low-importance messages from context.

    Uses heuristic scoring to identify which messages can be safely
    removed or compressed without losing important information.
    """

    def __init__(self):
        """Initialize message pruner"""
        # Simple acknowledgment patterns (low importance)
        self.acknowledgment_patterns = [
            r"^(ok|okay|sure|got it|understood|yes|no|alright|sounds good)\.?$",
            r"^(thanks|thank you|great|perfect|excellent)\.?$",
        ]

        logger.info("Message pruner initialized")

    def calculate_message_importance(
        self,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Score message importance (0.0 - 1.0)

        Scoring guidelines:
        - 1.0: Bookmarked (user-marked important)
        - 0.9: User questions/requests
        - 0.8: Code blocks, error messages
        - 0.7: Important tool results
        - 0.6: Assistant explanations
        - 0.4: Simple tool calls
        - 0.2: Acknowledgments
        - 0.1: "Thinking..." / transient messages

        Args:
            message: Message dict to score
            context: Optional context (bookmarks, etc.)

        Returns:
            Importance score (0.0 - 1.0)
        """
        if context is None:
            context = {}

        role = message.get("role", "")
        content = message.get("content", "")

        # Handle array content
        if isinstance(content, list):
            # Extract text content
            text_parts = []
            has_image = False
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif item.get("type") == "image":
                        has_image = True
            content = " ".join(text_parts)

            # Images are important (vision analysis)
            if has_image:
                return 0.85

        # Convert to string for analysis
        content_str = str(content).lower()

        # Check if bookmarked
        message_index = context.get("index", -1)
        bookmarked_indices = context.get("bookmarked_indices", set())
        if message_index in bookmarked_indices:
            return 1.0

        # User messages
        if role == "user":
            # Long user messages (detailed requests)
            if len(content_str) > 200:
                return 0.9

            # Medium user messages (questions)
            if len(content_str) > 50:
                return 0.85

            # Short user messages
            return 0.75

        # Assistant messages
        if role == "assistant":
            # Code blocks (very important)
            if "```" in content_str:
                return 0.8

            # Error messages (important for debugging)
            if "error" in content_str or "failed" in content_str:
                return 0.8

            # Simple acknowledgments (low importance)
            if self._is_acknowledgment(content_str):
                return 0.2

            # "Thinking..." or similar transient messages
            if len(content_str) < 20 and any(
                word in content_str
                for word in ["thinking", "processing", "working", "wait"]
            ):
                return 0.1

            # Tool call results
            if "tool" in content_str or "calling" in content_str:
                # Check if it's a simple status message
                if len(content_str) < 100:
                    return 0.4
                # Detailed tool results
                return 0.7

            # Regular assistant explanations
            if len(content_str) > 100:
                return 0.6

            # Short assistant responses
            return 0.5

        # System messages (summaries)
        if role == "system":
            # Summaries are important
            if "summary" in content_str:
                return 0.75
            return 0.5

        # Default
        return 0.5

    def prune_messages(
        self,
        messages: List[Dict[str, Any]],
        target_token_count: int,
        preserve_recent: int = 5,
        bookmarked_indices: Optional[set] = None
    ) -> List[Dict[str, Any]]:
        """
        Remove low-importance messages to reach target token count

        Strategy:
        1. Score all messages by importance
        2. Keep recent N messages untouched
        3. Remove lowest-scoring messages first
        4. Stop when target token count reached

        Args:
            messages: List of messages
            target_token_count: Target number of tokens
            preserve_recent: Number of recent messages to always keep
            bookmarked_indices: Set of bookmarked message indices

        Returns:
            Pruned list of messages
        """
        if not messages:
            return []

        if bookmarked_indices is None:
            bookmarked_indices = set()

        # Calculate current token count
        from .token_counter import estimate_message_tokens
        current_tokens = sum(estimate_message_tokens(m) for m in messages)

        logger.info(
            f"Pruning messages: current={current_tokens:,}, "
            f"target={target_token_count:,}"
        )

        # If already under target, return as-is
        if current_tokens <= target_token_count:
            return messages

        # Score all messages
        scored_messages = []
        for index, message in enumerate(messages):
            # Recent messages get boosted score
            is_recent = index >= len(messages) - preserve_recent

            context = {
                "index": index,
                "bookmarked_indices": bookmarked_indices,
                "is_recent": is_recent
            }

            score = self.calculate_message_importance(message, context)

            # Boost score for recent messages
            if is_recent:
                score = min(1.0, score + 0.3)

            tokens = estimate_message_tokens(message)

            scored_messages.append({
                "index": index,
                "message": message,
                "score": score,
                "tokens": tokens,
                "keep": is_recent or index in bookmarked_indices
            })

        # Sort by score (ascending) - lowest scores first
        sorted_messages = sorted(scored_messages, key=lambda x: x["score"])

        # Remove messages until we reach target
        tokens_removed = 0
        for item in sorted_messages:
            if item["keep"]:
                continue  # Never remove recent or bookmarked

            if current_tokens - tokens_removed <= target_token_count:
                break  # Reached target

            # Mark for removal
            item["keep"] = False
            tokens_removed += item["tokens"]

            logger.debug(
                f"Removing message {item['index']} (score={item['score']:.2f}, "
                f"tokens={item['tokens']})"
            )

        # Build final message list (preserve order)
        pruned_messages = [
            item["message"]
            for item in sorted(scored_messages, key=lambda x: x["index"])
            if item["keep"]
        ]

        final_tokens = sum(estimate_message_tokens(m) for m in pruned_messages)
        logger.info(
            f"Pruning complete: {len(messages)} -> {len(pruned_messages)} messages, "
            f"{current_tokens:,} -> {final_tokens:,} tokens"
        )

        return pruned_messages

    def compress_tool_calls(
        self,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compress verbose tool call messages

        Replaces long tool outputs with concise summaries.

        Args:
            message: Message dict

        Returns:
            Compressed message dict
        """
        content = message.get("content", "")

        if not isinstance(content, str):
            return message  # Can't compress array content

        # Check if it's a tool result
        if "tool" not in content.lower():
            return message

        # Compress verbose results
        if len(content) > 300:
            # Try to extract tool name
            tool_match = re.search(r"tool[:\s]+['\"]?(\w+)['\"]?", content, re.IGNORECASE)
            tool_name = tool_match.group(1) if tool_match else "unknown"

            # Create compressed version
            compressed_content = f"Tool '{tool_name}' completed successfully"

            logger.debug(
                f"Compressed tool call: {len(content)} -> "
                f"{len(compressed_content)} characters"
            )

            return {
                **message,
                "content": compressed_content
            }

        return message

    def is_redundant(
        self,
        message: Dict[str, Any],
        previous_messages: List[Dict[str, Any]],
        lookback: int = 3
    ) -> bool:
        """
        Check if message is redundant

        Detects repeated information, acknowledgments, etc.

        Args:
            message: Message to check
            previous_messages: Previous messages to compare against
            lookback: How many recent messages to check

        Returns:
            True if message appears redundant
        """
        content = str(message.get("content", "")).lower().strip()

        # Check if it's a simple acknowledgment
        if self._is_acknowledgment(content):
            # Check if there was a recent acknowledgment
            recent = previous_messages[-lookback:] if previous_messages else []
            for prev in recent:
                prev_content = str(prev.get("content", "")).lower().strip()
                if self._is_acknowledgment(prev_content):
                    return True  # Multiple acknowledgments are redundant

        # Very short messages that are similar to recent ones
        if len(content) < 50:
            recent = previous_messages[-lookback:] if previous_messages else []
            for prev in recent:
                prev_content = str(prev.get("content", "")).lower().strip()
                if content == prev_content:
                    return True  # Exact duplicate

        return False

    def _is_acknowledgment(self, content: str) -> bool:
        """
        Check if content is a simple acknowledgment

        Args:
            content: Message content (lowercase)

        Returns:
            True if content matches acknowledgment pattern
        """
        content = content.strip()

        for pattern in self.acknowledgment_patterns:
            if re.match(pattern, content, re.IGNORECASE):
                return True

        return False
