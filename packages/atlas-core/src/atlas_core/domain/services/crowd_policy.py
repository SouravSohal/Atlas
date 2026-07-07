from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate


class CrowdPolicy:
    """Domain policy defining rules and limits for crowd density management."""

    OVERCROWDED_THRESHOLD = 0.8
    REROUTE_DENSITY_THRESHOLD = 0.7
    REROUTE_WAIT_THRESHOLD_MINUTES = 15

    @staticmethod
    def is_overcrowded(density: CrowdDensity) -> bool:
        """Determine if a given crowd density is considered overcrowded."""
        return density.value >= CrowdPolicy.OVERCROWDED_THRESHOLD

    @staticmethod
    def should_trigger_rerouting(density: CrowdDensity, queue: QueueEstimate) -> bool:
        """Determine if crowd density and queue wait times warrant rerouting fans."""
        return (
            density.value >= CrowdPolicy.REROUTE_DENSITY_THRESHOLD
            and queue.waiting_minutes >= CrowdPolicy.REROUTE_WAIT_THRESHOLD_MINUTES
        )

    @staticmethod
    def determine_required_staff_count(density: CrowdDensity) -> int:
        """Calculate the required staff/volunteer count based on current crowd density."""
        if density.value < 0.3:
            return 2
        if density.value < 0.6:
            return 5
        if density.value < 0.8:
            return 10
        return 20
