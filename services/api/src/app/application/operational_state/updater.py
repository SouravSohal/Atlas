import structlog
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate

logger = structlog.get_logger()

class OperationalStateUpdater:
    """Applies mutations to an OperationalState entity and handles domain validation."""

    @staticmethod
    def update(
        state: OperationalState,
        density_value: float,
        queue_waiting_minutes: int,
        coordinates: Coordinates,
    ) -> None:
        """Updates the operational state, producing domain events if values change."""
        density = CrowdDensity(value=density_value)
        queue_estimate = QueueEstimate(waiting_minutes=queue_waiting_minutes)

        logger.info(
            "Updating operational state",
            zone_id=str(state.zone_id),
            old_density=state.density.value,
            new_density=density_value,
            old_queue=state.queue_estimate.waiting_minutes,
            new_queue=queue_waiting_minutes,
        )
        state.update_state(
            new_density=density,
            new_queue_estimate=queue_estimate,
            location_coords=coordinates,
        )
