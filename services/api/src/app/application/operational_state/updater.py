import structlog
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.events.crowd_density_changed import CrowdDensityChanged
from atlas_core.domain.events.incident_created import IncidentCreated
from atlas_core.domain.events.recommendation_approved import RecommendationApproved
from atlas_core.domain.events.recommendation_generated import RecommendationGenerated
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate

from app.application.operational_state.dto import GateStatusChanged, VolunteerAssigned

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

    @staticmethod
    def apply_incident_created(state: OperationalState, event: IncidentCreated, coordinates: Coordinates) -> None:
        """Applies an IncidentCreated event to adjust density and wait times."""
        from atlas_core.domain.enums.severity import Severity
        old_density = state.density.value
        old_wait = state.queue_estimate.waiting_minutes

        new_density_val = old_density
        if event.severity == Severity.CRITICAL or event.severity == Severity.HIGH:
            new_density_val = min(1.0, old_density + 0.2)
        elif event.severity == Severity.MEDIUM:
            new_density_val = min(1.0, old_density + 0.1)

        new_wait = old_wait + 5

        state.update_state(
            new_density=CrowdDensity(value=new_density_val),
            new_queue_estimate=QueueEstimate(waiting_minutes=new_wait),
            location_coords=coordinates,
        )

    @staticmethod
    def apply_crowd_density_changed(state: OperationalState, event: CrowdDensityChanged, coordinates: Coordinates) -> None:
        """Applies a CrowdDensityChanged event to adjust density."""
        state.update_state(
            new_density=event.new_density,
            new_queue_estimate=state.queue_estimate,
            location_coords=coordinates,
        )

    @staticmethod
    def apply_recommendation_approved(state: OperationalState, event: RecommendationApproved, coordinates: Coordinates) -> None:
        """Applies a RecommendationApproved event to decrease congestion density and queues."""
        old_density = state.density.value
        old_wait = state.queue_estimate.waiting_minutes

        new_density_val = max(0.0, old_density - 0.1)
        new_wait = max(0, old_wait - 5)

        state.update_state(
            new_density=CrowdDensity(value=new_density_val),
            new_queue_estimate=QueueEstimate(waiting_minutes=new_wait),
            location_coords=coordinates,
        )

    @staticmethod
    def apply_recommendation_generated(state: OperationalState, event: RecommendationGenerated, coordinates: Coordinates) -> None:
        """Applies a RecommendationGenerated event."""
        state.update_state(
            new_density=state.density,
            new_queue_estimate=state.queue_estimate,
            location_coords=coordinates,
        )

    @staticmethod
    def apply_gate_status_changed(state: OperationalState, event: GateStatusChanged, coordinates: Coordinates) -> None:
        """Applies a GateStatusChanged event to adjust congestion when gates close or open."""
        old_density = state.density.value
        old_wait = state.queue_estimate.waiting_minutes

        if event.status == "closed":
            new_density_val = min(1.0, old_density + 0.15)
            new_wait = old_wait + 10
        else:  # "open"
            new_density_val = max(0.0, old_density - 0.05)
            new_wait = max(0, old_wait - 5)

        state.update_state(
            new_density=CrowdDensity(value=new_density_val),
            new_queue_estimate=QueueEstimate(waiting_minutes=new_wait),
            location_coords=coordinates,
        )

    @staticmethod
    def apply_volunteer_assigned(state: OperationalState, event: VolunteerAssigned, coordinates: Coordinates) -> None:
        """Applies a VolunteerAssigned event to decrease density."""
        old_density = state.density.value
        new_density_val = max(0.0, old_density - 0.05)

        state.update_state(
            new_density=CrowdDensity(value=new_density_val),
            new_queue_estimate=state.queue_estimate,
            location_coords=coordinates,
        )
