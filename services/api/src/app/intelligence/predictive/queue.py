class QueuePredictor:
    """Estimates turnstile queue lengths based on ingress rates and volunteer staffing levels."""

    def predict(self, current_queue: int, crowd_density: float, volunteers: int) -> int:
        """Determines future queue wait duration based on staff ratio capacity."""
        future_queue = current_queue
        if crowd_density > 0.8:
            future_queue += 8
        elif crowd_density > 0.5:
            future_queue += 3
        
        # Volunteers reduce queue wait times
        if volunteers > 15:
            future_queue -= 4
        elif volunteers > 8:
            future_queue -= 2
            
        return max(1, future_queue)
