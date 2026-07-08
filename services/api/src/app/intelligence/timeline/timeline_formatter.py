from typing import Any, List

class TimelineFormatter:
    """Formats aggregated and sorted events into clear, structured textual outputs."""

    def format(self, events: List[dict[str, Any]]) -> str:
        """Converts raw list items into timestamped string records."""
        if not events:
            return "No operational events logged during this timeframe."

        formatted_lines = []
        for event in events:
            ts = event["timestamp"]
            ts_str = ts.strftime("%H:%M:%S") if hasattr(ts, "strftime") else str(ts)
            etype = event.get("type", "Event")
            details = event.get("details", "")
            formatted_lines.append(f"[{ts_str}] {etype}: {details}")

        return "\n".join(formatted_lines)
