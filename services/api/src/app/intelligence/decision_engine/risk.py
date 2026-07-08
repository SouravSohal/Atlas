class RiskScorer:
    """Computes operational risk metrics based on stadium sensors and incidents."""

    def calculate_risk(self, crowd_density: float, incident_count: int) -> float:
        """Determines a risk index between 0.0 and 1.0 based on crowd density and active incident logs."""
        risk = 0.1
        if crowd_density > 0.8:
            risk += 0.4
        elif crowd_density > 0.5:
            risk += 0.2
            
        risk += min(0.4, incident_count * 0.15)
        return round(risk, 2)
