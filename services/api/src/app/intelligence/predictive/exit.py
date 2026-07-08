class ExitPredictor:
    """Estimates egress exit patterns based on match progression phase."""

    def predict_egress_pressure(self, match_phase: str, current_density: float) -> float:
        """Determines expected outflow pressure percentage (0.0 to 1.0) relative to match progression."""
        phase = match_phase.lower()
        pressure = 0.1
        if "final" in phase or "completed" in phase:
            pressure = 0.90
        elif "half" in phase:
            pressure = 0.40
            
        if current_density > 0.6:
            pressure += 0.05
            
        return max(0.0, min(1.0, round(pressure, 2)))
