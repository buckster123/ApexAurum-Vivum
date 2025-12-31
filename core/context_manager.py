"""
Context Manager for Claude API

Orchestrates context management including tracking, summarization,
and pruning to enable unlimited conversation length.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from .context_tracker import ContextTracker
from .summarizer import ConversationSummarizer
from .message_pruner import MessagePruner
from .token_counter import estimate_message_tokens

logger = logging.getLogger(__name__)


# Strategy configurations
STRATEGY_CONFIGS = {
    "aggressive": {
        "threshold_percent": 0.5,  # Summarize at 50%
        "preserve_recent": 5,
        "summarization_style": "aggressive",
        "description": "Summarize at 50% (keeps 5 recent messages)"
    },
    "balanced": {
        "threshold_percent": 0.7,  # Summarize at 70%
        "preserve_recent": 10,
        "summarization_style": "balanced",
        "description": "Summarize at 70% (keeps 10 recent messages)"
    },
    "conservative": {
        "threshold_percent": 0.85,  # Summarize at 85%
        "preserve_recent": 20,
        "summarization_style": "conservative",
        "description": "Summarize at 85% (keeps 20 recent messages)"
    },
    "manual": {
        "threshold_percent": 1.0,  # Never auto-summarize
        "preserve_recent": 100,
        "summarization_style": "balanced",
        "description": "No auto-summarization"
    }
}


class ContextManager:
    """
    Orchestrates all context management operations.

    Coordinates tracking, summarization, and pruning to keep
    conversations within context limits while preserving important
    information.
    """

    def __init__(
        self,
        client,
        model: str,
        strategy: str = "balanced"
    ):
        """
        Initialize context manager

        Args:
            client: ClaudeAPIClient instance
            model: Model ID (e.g., 'claude-sonnet-4-5')
            strategy: Management strategy ('aggressive', 'balanced',
                     'conservative', 'manual')
        """
        self.client = client
        self.model = model
        self.strategy = strategy

        # Initialize components
        self.tracker = ContextTracker(model)
        self.summarizer = ConversationSummarizer(client)
        self.pruner = MessagePruner()

        # User bookmarks
        self.bookmarked_indices = set()

        # Rolling summary (cumulative conversation summary)
        self.rolling_summary = ""

        # Statistics
        self.total_messages_summarized = 0
        self.total_tokens_saved = 0

        logger.info(
            f"Context manager initialized: model={model}, strategy={strategy}"
        )

    def manage_context(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        preserve_recent: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Main context management method

        Analyzes context usage and applies summarization/pruning if needed.

        Args:
            messages: Current conversation messages
            system: System prompt (optional)
            tools: Tool schemas (optional)
            preserve_recent: Override preserve count (optional)

        Returns:
            Tuple of (managed_messages, summary_info)
            - managed_messages: Optimized message list
            - summary_info: Info message if summarization occurred (or None)
        """
        if not messages:
            return messages, None

        # Get strategy config
        config = STRATEGY_CONFIGS.get(self.strategy, STRATEGY_CONFIGS["balanced"])
        threshold = config["threshold_percent"]

        if preserve_recent is None:
            preserve_recent = config["preserve_recent"]

        # Calculate current context usage
        stats = self.tracker.calculate_total_context(messages, system, tools)
        current_tokens = stats["total_tokens"]
        usage_percent = stats["usage_percent"]

        logger.info(
            f"Context usage: {current_tokens:,} tokens ({usage_percent:.1f}%)"
        )

        # Check if management needed
        if not self.tracker.should_summarize(current_tokens, threshold):
            logger.debug("Context usage below threshold, no management needed")
            return messages, None

        # Context management needed
        logger.info(
            f"Context threshold reached ({threshold*100}%), "
            f"applying {self.strategy} strategy"
        )

        # Identify important messages (including bookmarked)
        important_indices = set(self.summarizer.identify_important_messages(
            messages,
            self.bookmarked_indices
        ))

        # Determine which messages to summarize
        # Keep recent messages + important messages
        keep_indices = set(range(len(messages) - preserve_recent, len(messages)))
        keep_indices.update(important_indices)

        # Messages to summarize are the ones NOT being kept
        summarize_indices = [
            i for i in range(len(messages))
            if i not in keep_indices
        ]

        if not summarize_indices:
            # Nothing to summarize (all messages are important/recent)
            logger.info("No messages eligible for summarization")
            return messages, None

        # Extract messages to summarize
        messages_to_summarize = [messages[i] for i in summarize_indices]
        messages_to_keep = [messages[i] for i in sorted(keep_indices)]

        # Generate summary
        summary_text = self.summarizer.summarize_messages(
            messages_to_summarize,
            strategy=config["summarization_style"]
        )

        # Calculate token savings
        original_tokens = sum(
            estimate_message_tokens(messages[i])
            for i in summarize_indices
        )
        summary_message = self.summarizer.create_summary_message(
            summary_text,
            len(messages_to_summarize),
            original_tokens
        )
        summary_tokens = estimate_message_tokens(summary_message)
        tokens_saved = original_tokens - summary_tokens

        # Update rolling summary
        if self.rolling_summary:
            self.rolling_summary += f"\n\n{summary_text}"
        else:
            self.rolling_summary = summary_text

        # Build new message list: [summary] + kept messages
        managed_messages = [summary_message] + messages_to_keep

        # Update statistics
        self.total_messages_summarized += len(messages_to_summarize)
        self.total_tokens_saved += tokens_saved

        # Create info message for user
        summary_info = (
            f"Summarized {len(messages_to_summarize)} older messages. "
            f"Saved ~{tokens_saved:,} tokens."
        )

        logger.info(
            f"Context management complete: {len(messages)} -> "
            f"{len(managed_messages)} messages, saved {tokens_saved:,} tokens"
        )

        return managed_messages, summary_info

    def force_summarize(
        self,
        messages: List[Dict[str, Any]],
        preserve_recent: int = 5
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Manually trigger summarization

        Args:
            messages: Current messages
            preserve_recent: Number of recent messages to keep

        Returns:
            Tuple of (managed_messages, summary_info)
        """
        logger.info(f"Manual summarization triggered (preserve {preserve_recent})")

        # Temporarily set strategy to aggressive threshold
        original_strategy = self.strategy
        self.strategy = "aggressive"

        managed_messages, summary_info = self.manage_context(
            messages,
            preserve_recent=preserve_recent
        )

        # Restore original strategy
        self.strategy = original_strategy

        if summary_info is None:
            summary_info = "No messages eligible for summarization"

        return managed_messages, summary_info

    def bookmark_message(self, index: int):
        """
        Mark message as important (never summarize)

        Args:
            index: Message index to bookmark
        """
        self.bookmarked_indices.add(index)
        logger.info(f"Bookmarked message {index}")

    def unbookmark_message(self, index: int):
        """
        Remove bookmark from message

        Args:
            index: Message index to unbookmark
        """
        self.bookmarked_indices.discard(index)
        logger.info(f"Removed bookmark from message {index}")

    def get_context_stats(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Get detailed context statistics

        Args:
            messages: Current messages
            system: System prompt (optional)
            tools: Tool schemas (optional)

        Returns:
            Dictionary with context statistics
        """
        stats = self.tracker.calculate_total_context(messages, system, tools)

        # Add management statistics
        stats.update({
            "strategy": self.strategy,
            "strategy_description": STRATEGY_CONFIGS[self.strategy]["description"],
            "threshold_percent": STRATEGY_CONFIGS[self.strategy]["threshold_percent"],
            "preserve_recent": STRATEGY_CONFIGS[self.strategy]["preserve_recent"],
            "bookmarked_count": len(self.bookmarked_indices),
            "total_summarized": self.total_messages_summarized,
            "total_saved": self.total_tokens_saved,
            "rolling_summary": self.rolling_summary
        })

        return stats

    def set_strategy(self, strategy: str):
        """
        Change context management strategy

        Args:
            strategy: New strategy ('aggressive', 'balanced',
                     'conservative', 'manual')
        """
        if strategy not in STRATEGY_CONFIGS:
            logger.warning(f"Unknown strategy '{strategy}', keeping '{self.strategy}'")
            return

        self.strategy = strategy
        logger.info(f"Context strategy changed to: {strategy}")

    def get_rolling_summary(self) -> str:
        """
        Get cumulative conversation summary

        Returns:
            Rolling summary text (empty if none)
        """
        return self.rolling_summary

    def clear_rolling_summary(self):
        """Clear rolling summary"""
        self.rolling_summary = ""
        logger.info("Rolling summary cleared")

    def reset_statistics(self):
        """Reset management statistics"""
        self.total_messages_summarized = 0
        self.total_tokens_saved = 0
        logger.info("Context management statistics reset")

    def get_bookmarked_indices(self) -> set:
        """
        Get set of bookmarked message indices

        Returns:
            Set of bookmarked indices
        """
        return self.bookmarked_indices.copy()

    def clear_bookmarks(self):
        """Clear all bookmarks"""
        count = len(self.bookmarked_indices)
        self.bookmarked_indices.clear()
        logger.info(f"Cleared {count} bookmarks")
