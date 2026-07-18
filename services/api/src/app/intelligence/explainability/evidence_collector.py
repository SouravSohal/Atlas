from typing import Any


class EvidenceCollector:
    """Gathers operational evidence from active incidents and state metrics."""

    def collect(self, overview: Any, state: Any, incidents: list[Any]) -> list[str]:
        """Compiles incident severity and queue wait time details into text evidence list."""
        evidence = []
        active_incidents = [i for i in incidents if not getattr(i, "resolved", False)]
        if active_incidents:
            evidence.append(f"Found {len(active_incidents)} active incidents in the stadium.")
            for inc in active_incidents:
                severity = getattr(inc, "severity", "medium")
                severity_val = getattr(severity, "value", str(severity))
                desc = getattr(inc, "description", "")
                evidence.append(f"Incident Alert: [{severity_val.upper()}] {desc}")
        else:
            evidence.append("No active incidents logged.")

        if state:
            density = getattr(state, "density", None)
            # Handle float vs CrowdDensity VO
            if density is not None:
                density_val = float(density.value) if hasattr(density, "value") else float(density)
            else:
                density_val = 0.0
            queue = getattr(state, "queue_waiting_minutes", 0)
            evidence.append(f"Zone crowd density is at {round(density_val * 100)}%.")
            evidence.append(f"Turnstile queue wait time: {queue} minutes.")

        return evidence
