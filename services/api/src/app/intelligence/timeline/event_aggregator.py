from datetime import UTC, datetime
from typing import Any


class EventAggregator:
    """Aggregates and chronologically sorts domain events, incidents, recommendations, and operational state modifications."""

    def aggregate(
        self,
        domain_events: list[Any],
        operational_states: list[Any],
        incidents: list[Any],
        recommendations: list[Any],
    ) -> list[dict[str, Any]]:
        """Compiles raw domain lists into a unified, timestamp-sorted list of event dictionaries."""
        aggregated: list[dict[str, Any]] = []

        # 1. Parse Domain Events
        for ev in domain_events:
            occurred_at = getattr(ev, "occurred_at", None) or getattr(ev, "created_at", None)
            if not occurred_at:
                occurred_at = datetime.now(UTC)
            
            aggregated.append({
                "type": "DomainEvent",
                "name": ev.__class__.__name__,
                "timestamp": occurred_at,
                "details": str(ev),
            })

        # 2. Parse Operational States
        for state in operational_states:
            last_updated = getattr(state, "last_updated", None) or getattr(state, "timestamp", None)
            if not last_updated:
                last_updated = datetime.now(UTC)
            
            zone_id = getattr(state, "zone_id", "Unknown")
            density = getattr(state, "density", None)
            queue_mins = getattr(state, "queue_waiting_minutes", None)
            
            aggregated.append({
                "type": "OperationalStateChange",
                "timestamp": last_updated,
                "details": f"Zone {zone_id} state updated. Crowd Density: {density}. Queue: {queue_mins}m.",
            })

        # 3. Parse Incidents
        for inc in incidents:
            created_at = getattr(inc, "created_at", None)
            if not created_at:
                created_at = datetime.now(UTC)
            
            itype = getattr(inc, "incident_type", "other")
            itype_val = getattr(itype, "value", str(itype))
            severity = getattr(inc, "severity", "medium")
            severity_val = getattr(severity, "value", str(severity))
            desc = getattr(inc, "description", "")
            resolved = getattr(inc, "resolved", False)
            
            aggregated.append({
                "type": "IncidentCreated" if not resolved else "IncidentResolved",
                "timestamp": created_at,
                "details": f"[{severity_val.upper()} {itype_val.upper()}] {desc} (Resolved: {resolved})",
            })

        # 4. Parse Recommendations
        for rec in recommendations:
            created_at = getattr(rec, "created_at", None)
            if not created_at:
                created_at = datetime.now(UTC)
            
            action = getattr(rec, "action_type", "Mitigation")
            action_val = getattr(action, "value", str(action))
            priority = getattr(rec, "priority", "medium")
            priority_val = getattr(priority, "value", str(priority))
            details = getattr(rec, "details", "")
            
            aggregated.append({
                "type": "RecommendationGenerated",
                "timestamp": created_at,
                "details": f"[{priority_val.upper()} Recommendation] Action: {action_val} - {details}",
            })

        # Helper to normalize timestamp for sorting
        def parse_ts(item: dict[str, Any]) -> datetime:
            ts = item["timestamp"]
            if isinstance(ts, str):
                try:
                    return datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    return datetime.now(UTC)
            if isinstance(ts, datetime):
                return ts
            return datetime.now(UTC)

        return sorted(aggregated, key=parse_ts)
