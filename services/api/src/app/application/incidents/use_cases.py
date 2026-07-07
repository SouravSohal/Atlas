from collections.abc import Sequence
from uuid import UUID
import structlog
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.value_objects.coordinates import Coordinates
from app.application.events import EventPublisher
from app.application.operational_state import OperationalStateService
from app.application.incidents.dtos import CreateIncidentRequest, IncidentResponse

logger = structlog.get_logger()

class CreateIncidentUseCase:
    """Use Case to report and create a new Incident."""

    def __init__(
        self,
        repository: IncidentRepository[Incident],
        operational_state_service: OperationalStateService,
        event_publisher: EventPublisher,
    ) -> None:
        self.repository = repository
        self.operational_state_service = operational_state_service
        self.event_publisher = event_publisher

    async def execute(self, request: CreateIncidentRequest) -> IncidentResponse:
        """Executes the incident creation workflow.

        Persists the incident entity, updates the stadium zone's operational state,
        dispatches recorded domain events, and returns the response details.
        """
        logger.info(
            "Executing CreateIncidentUseCase",
            incident_type=request.incident_type,
            severity=request.severity,
            reporter_id=str(request.reporter_id),
            zone_id=str(request.zone_id),
        )

        coords = Coordinates(latitude=request.latitude, longitude=request.longitude)
        incident = Incident(
            incident_type=IncidentType(request.incident_type),
            severity=Severity(request.severity),
            description=request.description,
            location=coords,
            reporter_id=request.reporter_id,
        )

        # Persist incident
        await self.repository.save(incident)

        # Update zone operational state
        current_state = await self.operational_state_service.get_state(request.zone_id)
        density = current_state.density if current_state else 0.0
        queue = current_state.queue_waiting_minutes if current_state else 0

        await self.operational_state_service.update_state(
            zone_id=request.zone_id,
            density=density,
            queue_waiting_minutes=queue,
            coordinates=coords,
        )

        # Dispatch recorded domain events
        events = list(incident.domain_events)
        if events:
            await self.event_publisher.publish_many(events)
            incident.clear_events()

        return IncidentResponse(
            id=incident.id,
            incident_type=incident.incident_type.value,
            severity=incident.severity.value,
            description=incident.description,
            latitude=incident.location.latitude,
            longitude=incident.location.longitude,
            reporter_id=incident.reporter_id,
            resolved=incident.resolved,
            resolved_at=incident.resolved_at,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
        )

class GetIncidentUseCase:
    """Use Case to retrieve a single Incident by its UUID."""

    def __init__(self, repository: IncidentRepository[Incident]) -> None:
        self.repository = repository

    async def execute(self, incident_id: UUID) -> IncidentResponse | None:
        """Retrieves the incident and formats it as a response DTO, or returns None if not found."""
        incident = await self.repository.get_by_id(incident_id)
        if not incident:
            return None

        return IncidentResponse(
            id=incident.id,
            incident_type=incident.incident_type.value,
            severity=incident.severity.value,
            description=incident.description,
            latitude=incident.location.latitude,
            longitude=incident.location.longitude,
            reporter_id=incident.reporter_id,
            resolved=incident.resolved,
            resolved_at=incident.resolved_at,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
        )

class ListIncidentsUseCase:
    """Use Case to list all Incident records in the system."""

    def __init__(self, repository: IncidentRepository[Incident]) -> None:
        self.repository = repository

    async def execute(self) -> Sequence[IncidentResponse]:
        """Retrieves all incidents and formats them as response DTOs."""
        incidents = await self.repository.list()
        return [
            IncidentResponse(
                id=incident.id,
                incident_type=incident.incident_type.value,
                severity=incident.severity.value,
                description=incident.description,
                latitude=incident.location.latitude,
                longitude=incident.location.longitude,
                reporter_id=incident.reporter_id,
                resolved=incident.resolved,
                resolved_at=incident.resolved_at,
                created_at=incident.created_at,
                updated_at=incident.updated_at,
            )
            for incident in incidents
        ]
