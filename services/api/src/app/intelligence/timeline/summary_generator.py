from datetime import datetime
from typing import Any, List

class SummaryGenerator:
    """Pre-processes and filters events by time ranges or incident focus areas."""

    def filter_by_time_range(
        self,
        events: List[dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
    ) -> List[dict[str, Any]]:
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
        events: List[dict[str, Any]],
        incident_id: str,
    ) -> List[dict[str, Any]]:
        """Filters events relating to a specific incident ID."""
        filtered = []
        for e in events:
            if incident_id in e.get("details", ""):
                filtered.append(e)
        return filtered
