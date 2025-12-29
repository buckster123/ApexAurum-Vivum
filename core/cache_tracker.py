"""
Cache Tracker - Phase 14

Tracks cache statistics and calculates cost savings.
Follows the same pattern as rate_limiter.py for consistency.

Statistics tracked:
- Cache hits/misses
- Token counts (creation, read, regular)
- Cost savings (actual vs without cache)
- Hit rate percentage
"""

import logging
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CacheUsageRecord:
    """Record of cache usage for a single request"""
    timestamp: datetime
    model: str
    cache_creation_tokens: int
    cache_read_tokens: int
    regular_input_tokens: int


class CacheTracker:
    """
    Track cache usage statistics and calculate savings.

    Provides session and lifetime statistics with cost calculations.
    """

    def __init__(self):
        """Initialize cache tracker"""
        # Session stats (reset when app restarts)
        self.session_total_requests = 0
        self.session_cache_writes = 0
        self.session_cache_hits = 0
        self.session_cache_misses = 0

        self.session_cache_creation_tokens = 0
        self.session_cache_read_tokens = 0
        self.session_regular_input_tokens = 0

        # History of requests (for analysis)
        self.history = []

        # Cache pricing multipliers (from cost_tracker.py)
        self.CACHE_WRITE_MULTIPLIER = 1.25  # +25%
        self.CACHE_READ_MULTIPLIER = 0.10   # -90%

        # Base model pricing (per 1M tokens)
        self.MODEL_PRICING = {
            "claude-opus-4-5-20251101": 15.00,
            "claude-sonnet-4-5-20250929": 3.00,
            "claude-3-7-sonnet-20250219": 3.00,
            "claude-3-5-haiku-20241022": 0.25,
        }

        logger.info("CacheTracker initialized")

    def record_cache_usage(
        self,
        model: str,
        cache_creation_tokens: int,
        cache_read_tokens: int,
        regular_input_tokens: int
    ):
        """
        Record cache usage for a request.

        Args:
            model: Model ID used
            cache_creation_tokens: Tokens written to cache
            cache_read_tokens: Tokens read from cache
            regular_input_tokens: Non-cached input tokens
        """
        # Update session totals
        self.session_total_requests += 1

        if cache_creation_tokens > 0:
            self.session_cache_writes += 1

        if cache_read_tokens > 0:
            self.session_cache_hits += 1
        else:
            self.session_cache_misses += 1

        self.session_cache_creation_tokens += cache_creation_tokens
        self.session_cache_read_tokens += cache_read_tokens
        self.session_regular_input_tokens += regular_input_tokens

        # Store usage record
        record = CacheUsageRecord(
            timestamp=datetime.now(),
            model=model,
            cache_creation_tokens=cache_creation_tokens,
            cache_read_tokens=cache_read_tokens,
            regular_input_tokens=regular_input_tokens
        )
        self.history.append(record)

        logger.debug(
            f"Cache usage recorded: "
            f"write={cache_creation_tokens}, "
            f"read={cache_read_tokens}, "
            f"regular={regular_input_tokens}"
        )

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.

        Returns:
            Dict with all cache statistics and savings
        """
        # Calculate hit rate
        hit_rate = 0.0
        if self.session_total_requests > 0:
            hit_rate = self.session_cache_hits / self.session_total_requests

        # Calculate costs and savings
        savings = self._calculate_savings()

        return {
            # Request counts
            "total_requests": self.session_total_requests,
            "cache_writes": self.session_cache_writes,
            "cache_hits": self.session_cache_hits,
            "cache_misses": self.session_cache_misses,

            # Token counts
            "cache_creation_tokens": self.session_cache_creation_tokens,
            "cache_read_tokens": self.session_cache_read_tokens,
            "regular_input_tokens": self.session_regular_input_tokens,

            # Performance metrics
            "cache_hit_rate": hit_rate,

            # Cost metrics
            "cost_with_cache": savings["cost_with_cache"],
            "cost_without_cache": savings["cost_without_cache"],
            "cost_savings": savings["savings"],
            "savings_percentage": savings["savings_percentage"]
        }

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session-level statistics (alias for get_cache_stats).

        Returns:
            Dict with session statistics
        """
        return self.get_cache_stats()

    def _calculate_savings(self) -> Dict[str, float]:
        """
        Calculate cost savings from caching.

        Returns:
            Dict with cost_with_cache, cost_without_cache, savings, savings_percentage
        """
        # Get average base price from history
        if not self.history:
            return {
                "cost_with_cache": 0.0,
                "cost_without_cache": 0.0,
                "savings": 0.0,
                "savings_percentage": 0.0
            }

        # Use weighted average price based on requests
        total_base_price = 0.0
        total_tokens = 0

        for record in self.history:
            base_price = self._get_base_price(record.model)
            tokens = (
                record.cache_creation_tokens +
                record.cache_read_tokens +
                record.regular_input_tokens
            )

            total_base_price += base_price * tokens
            total_tokens += tokens

        if total_tokens == 0:
            return {
                "cost_with_cache": 0.0,
                "cost_without_cache": 0.0,
                "savings": 0.0,
                "savings_percentage": 0.0
            }

        avg_base_price = total_base_price / total_tokens

        # Calculate actual cost with cache
        cost_with_cache = (
            # Cache write cost (+25%)
            (self.session_cache_creation_tokens / 1_000_000) *
            (avg_base_price * self.CACHE_WRITE_MULTIPLIER) +

            # Cache read cost (-90%)
            (self.session_cache_read_tokens / 1_000_000) *
            (avg_base_price * self.CACHE_READ_MULTIPLIER) +

            # Regular input cost
            (self.session_regular_input_tokens / 1_000_000) * avg_base_price
        )

        # Calculate what it would have cost without cache
        total_tokens_without_cache = (
            self.session_cache_creation_tokens +
            self.session_cache_read_tokens +
            self.session_regular_input_tokens
        )

        cost_without_cache = (total_tokens_without_cache / 1_000_000) * avg_base_price

        # Calculate savings
        savings = cost_without_cache - cost_with_cache
        savings_percentage = 0.0

        if cost_without_cache > 0:
            savings_percentage = (savings / cost_without_cache) * 100

        return {
            "cost_with_cache": cost_with_cache,
            "cost_without_cache": cost_without_cache,
            "savings": savings,
            "savings_percentage": savings_percentage
        }

    def _get_base_price(self, model: str) -> float:
        """
        Get base input price for model.

        Args:
            model: Model ID

        Returns:
            Base price per 1M input tokens
        """
        # Try exact match
        if model in self.MODEL_PRICING:
            return self.MODEL_PRICING[model]

        # Try partial match (for flexibility)
        for known_model, price in self.MODEL_PRICING.items():
            if known_model in model or model in known_model:
                return price

        # Default to Sonnet pricing if unknown
        logger.warning(f"Unknown model '{model}', using Sonnet pricing")
        return 3.00

    def reset_stats(self):
        """Reset all statistics (clear session data)"""
        self.session_total_requests = 0
        self.session_cache_writes = 0
        self.session_cache_hits = 0
        self.session_cache_misses = 0

        self.session_cache_creation_tokens = 0
        self.session_cache_read_tokens = 0
        self.session_regular_input_tokens = 0

        self.history.clear()

        logger.info("Cache statistics reset")

    def get_recent_usage(self, count: int = 10) -> list:
        """
        Get recent cache usage records.

        Args:
            count: Number of recent records to return

        Returns:
            List of recent CacheUsageRecord objects
        """
        return self.history[-count:] if self.history else []

    def export_stats(self) -> Dict[str, Any]:
        """
        Export all statistics for backup/analysis.

        Returns:
            Dict with all stats and history
        """
        return {
            "exported_at": datetime.now().isoformat(),
            "statistics": self.get_cache_stats(),
            "history_count": len(self.history),
            "recent_usage": [
                {
                    "timestamp": record.timestamp.isoformat(),
                    "model": record.model,
                    "cache_creation_tokens": record.cache_creation_tokens,
                    "cache_read_tokens": record.cache_read_tokens,
                    "regular_input_tokens": record.regular_input_tokens
                }
                for record in self.get_recent_usage(20)
            ]
        }
