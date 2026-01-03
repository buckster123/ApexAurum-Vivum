"""
Analytics Store Module

Provides persistent storage for usage analytics:
- Tool usage tracking (calls, success rates, timing)
- Cost tracking (by model, daily totals)
- Cache performance (hit rates, savings)

Data is stored in sandbox/analytics.json with daily summaries.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading


class AnalyticsStore:
    """
    Persistent analytics storage with daily aggregation.

    Thread-safe for concurrent recording from multiple sources.
    """

    MAX_RECENT_TOOL_CALLS = 100  # Keep last N tool calls for detail view

    def __init__(self, storage_path: str = "sandbox/analytics.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.data = self._load()

    def _load(self) -> Dict:
        """Load analytics data from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Initialize empty structure
        return {
            "version": 1,
            "daily_summaries": {},
            "recent_tool_calls": [],
            "metadata": {
                "first_record": None,
                "last_updated": None
            }
        }

    def _save(self):
        """Save analytics data to disk."""
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            # Don't crash on write failures, just log
            print(f"Analytics save failed: {e}")

    def _get_today(self) -> str:
        """Get today's date as string key."""
        return datetime.now().strftime("%Y-%m-%d")

    def _ensure_today_exists(self) -> Dict:
        """Ensure today's summary exists, return it."""
        today = self._get_today()

        if today not in self.data["daily_summaries"]:
            self.data["daily_summaries"][today] = {
                "cost": {"total": 0.0, "by_model": {}},
                "tokens": {"input": 0, "output": 0, "cached": 0},
                "cache": {"hits": 0, "misses": 0, "hit_rate": 0.0, "savings": 0.0},
                "tools": {
                    "calls": {},
                    "success": {},
                    "errors": {},
                    "total_calls": 0,
                    "unique_tools": 0,
                    "total_duration_ms": 0
                },
                "sessions": 0,
                "api_calls": 0
            }

            # Update first record if needed
            if self.data["metadata"]["first_record"] is None:
                self.data["metadata"]["first_record"] = today

        return self.data["daily_summaries"][today]

    # =========================================================================
    # Recording Methods
    # =========================================================================

    def record_tool_call(self, tool_name: str, success: bool, duration_ms: float = 0):
        """
        Record a tool execution.

        Args:
            tool_name: Name of the tool called
            success: Whether the call succeeded
            duration_ms: Execution time in milliseconds
        """
        with self._lock:
            today = self._ensure_today_exists()

            # Update call counts
            today["tools"]["calls"][tool_name] = today["tools"]["calls"].get(tool_name, 0) + 1
            today["tools"]["total_calls"] += 1
            today["tools"]["total_duration_ms"] += duration_ms

            if success:
                today["tools"]["success"][tool_name] = today["tools"]["success"].get(tool_name, 0) + 1
            else:
                today["tools"]["errors"][tool_name] = today["tools"]["errors"].get(tool_name, 0) + 1

            # Update unique tool count
            today["tools"]["unique_tools"] = len(today["tools"]["calls"])

            # Add to recent calls (with limit)
            self.data["recent_tool_calls"].append({
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "success": success,
                "duration_ms": round(duration_ms, 2)
            })

            # Trim recent calls if over limit
            if len(self.data["recent_tool_calls"]) > self.MAX_RECENT_TOOL_CALLS:
                self.data["recent_tool_calls"] = self.data["recent_tool_calls"][-self.MAX_RECENT_TOOL_CALLS:]

            self._save()

    def record_api_call(self, model: str, input_tokens: int, output_tokens: int,
                        cached_tokens: int, cost: float):
        """
        Record an API call with token/cost data.

        Args:
            model: Model ID used
            input_tokens: Input tokens consumed
            output_tokens: Output tokens generated
            cached_tokens: Tokens read from cache
            cost: Cost in dollars
        """
        with self._lock:
            today = self._ensure_today_exists()

            # Update cost
            today["cost"]["total"] += cost
            today["cost"]["by_model"][model] = today["cost"]["by_model"].get(model, 0) + cost

            # Update tokens
            today["tokens"]["input"] += input_tokens
            today["tokens"]["output"] += output_tokens
            today["tokens"]["cached"] += cached_tokens

            # Update API call count
            today["api_calls"] += 1

            self._save()

    def record_cache_event(self, hit: bool, tokens_cached: int = 0, savings: float = 0):
        """
        Record a cache hit or miss.

        Args:
            hit: Whether cache was hit
            tokens_cached: Tokens served from cache (if hit)
            savings: Dollar savings from cache hit
        """
        with self._lock:
            today = self._ensure_today_exists()

            if hit:
                today["cache"]["hits"] += 1
                today["cache"]["savings"] += savings
            else:
                today["cache"]["misses"] += 1

            # Update hit rate
            total = today["cache"]["hits"] + today["cache"]["misses"]
            if total > 0:
                today["cache"]["hit_rate"] = today["cache"]["hits"] / total

            self._save()

    def record_session_start(self):
        """Record that a new session started today."""
        with self._lock:
            today = self._ensure_today_exists()
            today["sessions"] += 1
            self._save()

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_daily_summary(self, date: str = None) -> Optional[Dict]:
        """
        Get summary for a specific date.

        Args:
            date: Date string (YYYY-MM-DD), defaults to today

        Returns:
            Summary dict or None if no data
        """
        if date is None:
            date = self._get_today()
        return self.data["daily_summaries"].get(date)

    def get_date_range(self, days: int = 7) -> List[Dict]:
        """
        Get summaries for last N days.

        Args:
            days: Number of days to include

        Returns:
            List of (date, summary) tuples, oldest first
        """
        results = []
        today = datetime.now()

        for i in range(days - 1, -1, -1):  # Oldest first
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            summary = self.data["daily_summaries"].get(date)
            if summary:
                results.append({"date": date, **summary})
            else:
                # Include empty day for continuity
                results.append({
                    "date": date,
                    "cost": {"total": 0, "by_model": {}},
                    "tokens": {"input": 0, "output": 0, "cached": 0},
                    "cache": {"hits": 0, "misses": 0, "hit_rate": 0, "savings": 0},
                    "tools": {"calls": {}, "total_calls": 0, "unique_tools": 0},
                    "api_calls": 0
                })

        return results

    def get_tool_stats(self, days: int = 30) -> Dict:
        """
        Get aggregated tool usage statistics.

        Args:
            days: Number of days to aggregate

        Returns:
            Dict with tool usage data
        """
        summaries = self.get_date_range(days)

        # Aggregate across days
        tool_calls = {}
        tool_success = {}
        tool_errors = {}
        total_calls = 0

        for day in summaries:
            tools = day.get("tools", {})
            for tool, count in tools.get("calls", {}).items():
                tool_calls[tool] = tool_calls.get(tool, 0) + count
                total_calls += count
            for tool, count in tools.get("success", {}).items():
                tool_success[tool] = tool_success.get(tool, 0) + count
            for tool, count in tools.get("errors", {}).items():
                tool_errors[tool] = tool_errors.get(tool, 0) + count

        # Calculate success rates
        tool_rates = {}
        for tool in tool_calls:
            calls = tool_calls[tool]
            successes = tool_success.get(tool, 0)
            tool_rates[tool] = successes / calls if calls > 0 else 0

        # Sort by usage
        sorted_tools = sorted(tool_calls.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_calls": total_calls,
            "unique_tools": len(tool_calls),
            "by_tool": dict(sorted_tools),
            "success_rates": tool_rates,
            "errors": tool_errors,
            "top_10": sorted_tools[:10]
        }

    def get_cost_stats(self, days: int = 30) -> Dict:
        """
        Get aggregated cost statistics.

        Args:
            days: Number of days to aggregate

        Returns:
            Dict with cost data
        """
        summaries = self.get_date_range(days)

        total_cost = 0
        by_model = {}
        daily_costs = []

        for day in summaries:
            cost_data = day.get("cost", {})
            day_total = cost_data.get("total", 0)
            total_cost += day_total
            daily_costs.append({"date": day["date"], "cost": day_total})

            for model, cost in cost_data.get("by_model", {}).items():
                by_model[model] = by_model.get(model, 0) + cost

        days_with_data = len([d for d in daily_costs if d["cost"] > 0])
        avg_daily = total_cost / days_with_data if days_with_data > 0 else 0

        return {
            "total": round(total_cost, 4),
            "average_daily": round(avg_daily, 4),
            "by_model": {k: round(v, 4) for k, v in by_model.items()},
            "daily": daily_costs,
            "projected_monthly": round(avg_daily * 30, 2)
        }

    def get_cache_stats(self, days: int = 30) -> Dict:
        """
        Get aggregated cache performance statistics.

        Args:
            days: Number of days to aggregate

        Returns:
            Dict with cache data
        """
        summaries = self.get_date_range(days)

        total_hits = 0
        total_misses = 0
        total_savings = 0
        daily_rates = []

        for day in summaries:
            cache_data = day.get("cache", {})
            hits = cache_data.get("hits", 0)
            misses = cache_data.get("misses", 0)
            total_hits += hits
            total_misses += misses
            total_savings += cache_data.get("savings", 0)

            rate = hits / (hits + misses) if (hits + misses) > 0 else 0
            daily_rates.append({"date": day["date"], "hit_rate": rate})

        overall_rate = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0

        return {
            "total_hits": total_hits,
            "total_misses": total_misses,
            "overall_hit_rate": round(overall_rate, 3),
            "total_savings": round(total_savings, 4),
            "daily": daily_rates
        }

    def get_recent_tool_calls(self, limit: int = 20) -> List[Dict]:
        """
        Get most recent tool calls.

        Args:
            limit: Max number to return

        Returns:
            List of recent tool call records, newest first
        """
        calls = self.data.get("recent_tool_calls", [])
        return list(reversed(calls[-limit:]))

    def get_summary(self) -> Dict:
        """Get overall analytics summary."""
        all_time = self.get_date_range(365)  # Up to a year

        total_cost = sum(d.get("cost", {}).get("total", 0) for d in all_time)
        total_tool_calls = sum(d.get("tools", {}).get("total_calls", 0) for d in all_time)
        total_api_calls = sum(d.get("api_calls", 0) for d in all_time)

        return {
            "first_record": self.data["metadata"]["first_record"],
            "last_updated": self.data["metadata"]["last_updated"],
            "days_tracked": len([d for d in all_time if d.get("api_calls", 0) > 0]),
            "total_cost": round(total_cost, 4),
            "total_tool_calls": total_tool_calls,
            "total_api_calls": total_api_calls
        }


# Global instance for easy access
_analytics_store: Optional[AnalyticsStore] = None


def get_analytics_store() -> AnalyticsStore:
    """Get the global analytics store instance."""
    global _analytics_store
    if _analytics_store is None:
        _analytics_store = AnalyticsStore()
    return _analytics_store
