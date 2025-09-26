"""
Central Usage Tracker for GPT-5 nano API calls
Tracks usage across all services and maintains cumulative statistics
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import threading

class UsageTracker:
    def __init__(self, tracker_file: str = "usage_tracker.json"):
        self.tracker_file = Path(tracker_file)
        self.lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create the usage tracker file if it doesn't exist"""
        if not self.tracker_file.exists():
            initial_data = {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "sessions": [],
                "daily_usage": {},
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self._write_data(initial_data)

    def _read_data(self) -> Dict[str, Any]:
        """Read current usage data"""
        try:
            with open(self.tracker_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_file_exists()
            return self._read_data()

    def _write_data(self, data: Dict[str, Any]):
        """Write usage data to file"""
        with open(self.tracker_file, 'w') as f:
            json.dump(data, f, indent=2)

    def track_usage(self,
                   request_type: str,
                   tokens_used: int,
                   cost: float,
                   model: str = "gpt-5-nano",
                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Track a GPT API usage event

        Args:
            request_type: Type of request (e.g., 'chat_completion', 'agent_support')
            tokens_used: Number of tokens consumed
            cost: Cost of the request in USD
            model: Model used (default: gpt-5-nano)
            metadata: Additional metadata about the request

        Returns:
            Updated usage statistics
        """
        with self.lock:
            data = self._read_data()
            current_time = datetime.now()
            today = current_time.strftime("%Y-%m-%d")

            # Create session entry
            session_entry = {
                "timestamp": current_time.isoformat(),
                "request_type": request_type,
                "model": model,
                "tokens_used": tokens_used,
                "cost": cost,
                "metadata": metadata or {}
            }

            # Update totals
            data["total_requests"] += 1
            data["total_tokens"] += tokens_used
            data["total_cost"] += cost
            data["last_updated"] = current_time.isoformat()

            # Add to sessions
            data["sessions"].append(session_entry)

            # Update daily usage
            if today not in data["daily_usage"]:
                data["daily_usage"][today] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0
                }

            data["daily_usage"][today]["requests"] += 1
            data["daily_usage"][today]["tokens"] += tokens_used
            data["daily_usage"][today]["cost"] += cost

            # Keep only last 100 sessions to prevent file from growing too large
            if len(data["sessions"]) > 100:
                data["sessions"] = data["sessions"][-100:]

            self._write_data(data)

            return {
                "session_id": len(data["sessions"]) - 1,
                "total_requests": data["total_requests"],
                "total_tokens": data["total_tokens"],
                "total_cost": data["total_cost"],
                "today_usage": data["daily_usage"][today]
            }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        with self.lock:
            data = self._read_data()
            today = datetime.now().strftime("%Y-%m-%d")

            return {
                "total_requests": data["total_requests"],
                "total_tokens": data["total_tokens"],
                "total_cost": data["total_cost"],
                "today_usage": data["daily_usage"].get(today, {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0
                }),
                "last_updated": data["last_updated"],
                "recent_sessions": data["sessions"][-10:] if data["sessions"] else []
            }

    def reset_usage(self) -> Dict[str, Any]:
        """Reset all usage statistics (use with caution)"""
        with self.lock:
            data = {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "sessions": [],
                "daily_usage": {},
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self._write_data(data)
            return data

# Global instance
usage_tracker = UsageTracker()