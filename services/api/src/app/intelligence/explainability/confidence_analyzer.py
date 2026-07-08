class ConfidenceAnalyzer:
    """Analyzes parameters to calculate confidence ratings for proposed mitigations."""

    def calculate(self, crowd_density: float, volunteer_count: int, active_incidents: int) -> float:
        """Determines base confidence scales based on density thresholds and volunteer availability."""
        base = 0.95
        if crowd_density > 0.8:
            base -= 0.1
        if active_incidents > 2:
            base -= 0.15
        if volunteer_count < 10:
            base -= 0.1
        return max(0.4, min(1.0, base))
