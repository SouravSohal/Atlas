class VolunteerDemandPredictor:
    """Estimates volunteer demand based on crowd bottlenecks and incident dispatches."""

    def predict(self, crowd_density: float, active_incidents: int) -> int:
        """Determines needed volunteers to stabilize crowd density bottlenecks."""
        demand = 5
        if crowd_density > 0.8:
            demand += 8
        elif crowd_density > 0.5:
            demand += 4
            
        if active_incidents > 0:
            demand += active_incidents * 3
            
        return demand
