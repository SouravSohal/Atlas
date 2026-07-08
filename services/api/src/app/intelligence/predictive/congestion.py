class CongestionPredictor:
    """Estimates future crowd densities based on active flows, current density, and gate states."""

    def predict(self, current_density: float, gate_active: bool, has_incidents: bool) -> float:
        """Determines future density considering gate openings and active incidents."""
        future_density = current_density
        if has_incidents:
            future_density += 0.15
        if not gate_active:
            future_density += 0.1
        else:
            future_density -= 0.05
        return max(0.0, min(1.0, round(future_density, 2)))
