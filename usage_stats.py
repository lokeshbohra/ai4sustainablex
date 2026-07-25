"""
ai4sustainablex — Usage Statistics Tracker
Tracks user activity: tokens used, reports generated, session times,
search queries, and generates a formatted .md usage report.
"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict

USAGE_STATS_FILE = os.path.expanduser("~/.ai4sustainablex/usage_stats.json")


class UsageTracker:
    """
    Tracks and persists usage statistics for ai4sustainablex.

    Tracks:
    - Total tokens used (per provider per session)
    - Context lengths (average, max)
    - Reports generated (count, templates used)
    - Session times (start, end, duration)
    - Search queries (count)
    - Companies used
    - Instances/sessions count

    Outputs a formatted usage_stats.md in the workspace directory.
    Can be shown/hidden via config switch: show_stats.
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or os.path.expanduser("~/ai4sustainablex_workspace")
        self._stats: Dict[str, Any] = {}
        self._session_start = None
        self._load()
        self._start_session()

    def _load(self) -> None:
        """Load usage statistics from disk."""
        if os.path.exists(USAGE_STATS_FILE):
            try:
                with open(USAGE_STATS_FILE, "r") as f:
                    self._stats = json.load(f)
            except Exception:
                self._stats = self._default_stats()

        if not self._stats:
            self._stats = self._default_stats()

    def _save(self) -> None:
        """Save usage statistics to disk."""
        os.makedirs(os.path.dirname(USAGE_STATS_FILE), exist_ok=True)
        with open(USAGE_STATS_FILE, "w") as f:
            json.dump(self._stats, f, indent=2)

        # Also write a human-readable .md file
        self._write_md_report()

    def _default_stats(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0",
            "first_used": datetime.now().isoformat(),
            "total_sessions": 0,
            "total_tokens_used": 0,
            "total_reports_generated": 0,
            "total_search_queries": 0,
            "tokens_by_provider": {},
            "reports_by_template": {},
            "reports_by_company": {},
            "daily_usage": {},
            "session_history": [],
            "companies": [],
            "average_context_length": 0,
            "max_context_length": 0,
            "context_lengths": [],  # last 100
        }

    def _start_session(self) -> None:
        """Record a new session start."""
        self._session_start = datetime.now()
        self._stats["total_sessions"] = self._stats.get("total_sessions", 0) + 1

    def end_session(self) -> None:
        """Record session end and duration."""
        if self._session_start:
            end = datetime.now()
            duration = (end - self._session_start).total_seconds()
            self._stats.setdefault("session_history", []).append({
                "start": self._session_start.isoformat(),
                "end": end.isoformat(),
                "duration_minutes": round(duration / 60, 1),
            })
            # Keep last 100 sessions
            if len(self._stats["session_history"]) > 100:
                self._stats["session_history"] = self._stats["session_history"][-100:]
            self._session_start = None
            self._save()

    def track_tokens(self, provider: str, tokens: int) -> None:
        """Record token usage for a provider."""
        self._stats["total_tokens_used"] = self._stats.get("total_tokens_used", 0) + tokens
        tokens_by_provider = self._stats.setdefault("tokens_by_provider", {})
        tokens_by_provider[provider] = tokens_by_provider.get(provider, 0) + tokens

        today = datetime.now().strftime("%Y-%m-%d")
        daily = self._stats.setdefault("daily_usage", {})
        daily[today] = daily.get(today, 0) + tokens

        self._save()

    def track_context_length(self, length: int) -> None:
        """Track context window usage."""
        contexts = self._stats.setdefault("context_lengths", [])
        contexts.append(length)
        if len(contexts) > 100:
            contexts.pop(0)

        if contexts:
            self._stats["average_context_length"] = round(sum(contexts) / len(contexts))
            self._stats["max_context_length"] = max(contexts)

        self._save()

    def track_report(self, template_id: str, company: str) -> None:
        """Record a report generation."""
        self._stats["total_reports_generated"] = self._stats.get("total_reports_generated", 0) + 1

        by_template = self._stats.setdefault("reports_by_template", {})
        by_template[template_id] = by_template.get(template_id, 0) + 1

        by_company = self._stats.setdefault("reports_by_company", {})
        by_company[company] = by_company.get(company, 0) + 1

        if company not in self._stats.get("companies", []):
            self._stats.setdefault("companies", []).append(company)

        today = datetime.now().strftime("%Y-%m-%d")
        daily = self._stats.setdefault("daily_usage", {})
        daily[today] = daily.get(today, 0) + 1

        self._save()

    def track_search(self, query_preview: str = "") -> None:
        """Record a search query."""
        self._stats["total_search_queries"] = self._stats.get("total_search_queries", 0) + 1
        self._save()

    def track_telemetry(self, event: str, data: Optional[Dict] = None) -> None:
        """Record telemetry event. Only used if telemetry is enabled."""
        config_path = os.path.expanduser("~/.ai4sustainablex/config.json")
        telemetry_enabled = False
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
                telemetry_enabled = config.get("telemetry_enabled", False)
            except Exception:
                pass

        if not telemetry_enabled:
            return

        # Send lightweight anonymous telemetry
        try:
            import requests
            payload = {
                "version": self._stats.get("version", "1.0.0"),
                "event": event,
                "timestamp": datetime.now().isoformat(),
                "data": data or {},
            }
            requests.post(
                "https://api.sustainablex.in/v1/telemetry",
                json=payload,
                timeout=3,
            )
        except Exception:
            pass  # Telemetry failures are silent

    def get_stats(self) -> Dict[str, Any]:
        """Return current usage statistics."""
        return {
            **self._stats,
            "context_lengths_note": f"Last {len(self._stats.get('context_lengths', []))} context lengths tracked",
            "session_history_note": f"Last {len(self._stats.get('session_history', []))} sessions tracked",
        }

    def _write_md_report(self) -> None:
        """Write a human-readable usage statistics markdown file."""
        stats = self._stats
        workspace_stats_dir = os.path.join(self.workspace_path, "stats")
        os.makedirs(workspace_stats_dir, exist_ok=True)
        md_path = os.path.join(workspace_stats_dir, "usage_stats.md")

        today = datetime.now().strftime("%Y-%m-%d")

        lines = [
            f"# 📊 ai4sustainablex Usage Statistics",
            f"*Generated: {datetime.now().isoformat()}*",
            "",
            "## Overview",
            f"- **Total Sessions**: {stats.get('total_sessions', 0)}",
            f"- **Total Tokens Used**: {stats.get('total_tokens_used', 0):,}",
            f"- **Total Reports Generated**: {stats.get('total_reports_generated', 0)}",
            f"- **Total Search Queries**: {stats.get('total_search_queries', 0)}",
            f"- **Average Context Length**: {stats.get('average_context_length', 0):,} tokens",
            f"- **Max Context Length**: {stats.get('max_context_length', 0):,} tokens",
            f"- **Companies**: {', '.join(stats.get('companies', [])) or 'None'}",
            f"- **First Used**: {stats.get('first_used', 'Unknown')}",
            "",
            "## Tokens by Provider",
        ]

        for provider, tokens in stats.get("tokens_by_provider", {}).items():
            lines.append(f"- **{provider}**: {tokens:,} tokens")

        lines.extend([
            "",
            "## Reports by Template",
        ])
        for template, count in stats.get("reports_by_template", {}).items():
            lines.append(f"- **{template}**: {count} reports")

        lines.extend([
            "",
            "## Reports by Company",
        ])
        for company, count in stats.get("reports_by_company", {}).items():
            lines.append(f"- **{company}**: {count} reports")

        lines.extend([
            "",
            "## Daily Usage (Last 30 Days)",
        ])
        daily = stats.get("daily_usage", {})
        sorted_days = sorted(daily.items(), reverse=True)[:30]
        for day, count in sorted_days:
            bar = "█" * min(count, 30)
            lines.append(f"- **{day}**: {count} {bar}")

        lines.extend([
            "",
            "## Recent Sessions",
        ])
        for session in stats.get("session_history", [])[-10:]:
            lines.append(f"- {session.get('start', '')[:10]}: {session.get('duration_minutes', 0)} min")

        lines.extend([
            "",
            "---",
            "*Generated by ai4sustainablex. To disable, run: python cli.py config set show_stats false*",
        ])

        with open(md_path, "w") as f:
            f.write("\n".join(lines) + "\n")

    def show_stats_text(self) -> str:
        """Return a compact text summary suitable for CLI display."""
        s = self._stats
        return (
            f"📊 Sessions: {s.get('total_sessions', 0)} | "
            f"Tokens: {s.get('total_tokens_used', 0):,} | "
            f"Reports: {s.get('total_reports_generated', 0)} | "
            f"Searches: {s.get('total_search_queries', 0)}"
        )


# Singleton
_usage_tracker: Optional[UsageTracker] = None


def get_usage_tracker(workspace_path: Optional[str] = None) -> UsageTracker:
    global _usage_tracker
    if _usage_tracker is None:
        _usage_tracker = UsageTracker(workspace_path)
    return _usage_tracker