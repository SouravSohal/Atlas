class ConfidenceCalculator:
    """Calculates confidence score ratings for generated stadium operations decisions."""

    def calculate_confidence(self, risk_score: float, available_volunteers: int) -> float:
        """Determines confidence metrics based on risk bounds and volunteer availability."""
        conf = 0.95
        if risk_score > 0.6:
            conf -= 0.15
        elif risk_score > 0.3:
            conf -= 0.05
            
        if available_volunteers < 10:
            conf -= 0.1
            
        return max(0.4, min(1.0, round(conf, 2)))
