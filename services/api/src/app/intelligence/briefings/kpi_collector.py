from typing import Any, Dict, List

class KPICollector:
    """Collects and aggregates KPI metrics from stadium operational telemetry databases."""

    def collect(self, overview: Any, states: List[Any], incidents: List[Any]) -> Dict[str, Any]:
        """Aggregates active incidents, health indexes, densities, and volunteer metrics."""
        active_incidents = [i for i in incidents if not getattr(i, "resolved", False)]
        critical_incidents = [
            i for i in active_incidents 
            if getattr(i, "severity", None) in ("critical", "high") or 
               getattr(getattr(i, "severity", None), "value", None) in ("critical", "high")
        ]
        
        avg_density = 0.0
        if states:
            densities = []
            for s in states:
                # Handle snapshots vs entities
                val = getattr(s, "density", None)
                if hasattr(val, "value"):
                    densities.append(val.value)
                elif isinstance(val, (int, float)):
                    densities.append(val)
                else:
                    densities.append(0.0)
            avg_density = sum(densities) / len(states)

        return {
            "stadium_health_pct": round(getattr(overview, "stadium_health", 1.0) * 100, 1) if overview else 100.0,
            "active_incidents_count": len(active_incidents),
            "critical_incidents_count": len(critical_incidents),
            "average_crowd_density_pct": round(avg_density * 100, 1),
            "allocated_volunteers_count": getattr(overview, "allocated_volunteers_count", 0) if overview else 0,
        }
