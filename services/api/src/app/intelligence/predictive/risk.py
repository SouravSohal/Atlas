class RiskPredictor:
    """Estimates risk score index and incident probability based on density and unresolved reports."""

    def predict(self, crowd_density: float, active_incidents: int) -> float:
        """Determines probability (0.0 to 1.0) of new incidents developing."""
        prob = 0.05
        if crowd_density > 0.8:
            prob += 0.35
        elif crowd_density > 0.5:
            prob += 0.15
            
        if active_incidents > 0:
            prob += active_incidents * 0.1
            
        return max(0.0, min(0.99, round(prob, 2)))
