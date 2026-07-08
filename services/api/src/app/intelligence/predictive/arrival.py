class ArrivalPredictor:
    """Estimates ingress arrival patterns based on stadium operational timeline steps."""

    def predict_gate_utilization(self, current_density: float, minutes_to_kickoff: int) -> float:
        """Determines expected gate utilization percentage (0.0 to 1.0) relative to match kickoff."""
        util = 0.2
        if minutes_to_kickoff <= 30:
            util = 0.85
        elif minutes_to_kickoff <= 90:
            util = 0.55
            
        # Density increases utilization pressure
        if current_density > 0.8:
            util += 0.1
            
        return max(0.0, min(1.0, round(util, 2)))
