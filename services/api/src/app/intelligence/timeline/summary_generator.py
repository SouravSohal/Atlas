from datetime import datetime
from typing import Any


class SummaryGenerator:
    """Pre-processes and filters events by time ranges or incident focus areas."""

    def filter_by_time_range(
        self,
        events: list[dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Filters events list to fall between start_time and end_time boundaries."""
        filtered = []
        for e in events:
            ts = e["timestamp"]
            if ts.tzinfo is not None and start_time.tzinfo is None:
                ts = ts.replace(tzinfo=None)
            if start_time <= ts <= end_time:
                filtered.append(e)
        return filtered

    def filter_by_incident(
        self,
        events: list[dict[str, Any]],
        incident_id: str,
    ) -> list[dict[str, Any]]:
        """Filters events relating to a specific incident ID."""
        filtered = []
        for e in events:
            if incident_id in e.get("details", ""):
                filtered.append(e)
        return filtered
