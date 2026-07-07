from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

import structlog
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.events.incident_created import IncidentCreated
from atlas_core.domain.repositories.incident_repository import IncidentRepository
from atlas_core.domain.repositories.operational_state_repository import OperationalStateRepository
from atlas_core.domain.value_objects.coordinates import Coordinates

from app.application.events import EventPublisher
from app.application.incidents.dtos import (
    CreateIncidentRequest,
    IncidentResponse,
    UpdateIncidentRequest,
)
from app.application.operational_state.factory import OperationalStateFactory
from app.application.operational_state.updater import OperationalStateUpdater

logger = structlog.get_logger()


class CreateIncidentUseCase:
    """Use Case to report and create a new Incident."""

    def __init__(
        self,
        repository: IncidentRepository[Incident],
        state_repository: OperationalStateRepository[OperationalState],
        event_publisher: EventPublisher,
    ) -> None:
        self.repository = repository
        self.state_repository = state_repository
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

        # 1. Persist incident
        await self.repository.save(incident)

        # 2. Update operational state of the zone
        state = await self.state_repository.get_by_id(request.zone_id)
        if not state:
            state = OperationalStateFactory.create(request.zone_id, density=0.0, queue_waiting_minutes=0)

        # Find the IncidentCreated event from incident's domain events to apply it
        incident_created_event = None
        for ev in incident.domain_events:
            if isinstance(ev, IncidentCreated):
                incident_created_event = ev
                break

        if incident_created_event:
            # Apply event to operational state
            OperationalStateUpdater.apply_incident_created(state, incident_created_event, coords)

        # Persist updated operational state
        await self.state_repository.save(state)

        # 3. Dispatch recorded domain events
        events = list(incident.domain_events) + list(state.domain_events)
        if events:
            await self.event_publisher.publish_many(events)
            incident.clear_events()
            state.clear_events()

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


class UpdateIncidentUseCase:
    """Use Case to update or resolve an existing Incident."""

    def __init__(
        self,
        repository: IncidentRepository[Incident],
        event_publisher: EventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    async def execute(self, incident_id: UUID, request: UpdateIncidentRequest) -> IncidentResponse | None:
        """Applies severity, resolution, or description updates to the incident."""
        logger.info(
            "Executing UpdateIncidentUseCase",
            incident_id=str(incident_id),
            resolved=request.resolved,
            severity=request.severity,
        )
        incident = await self.repository.get_by_id(incident_id)
        if not incident:
            return None

        # Apply updates
        if request.resolved is True and not incident.resolved:
            incident.resolve()
        if request.severity is not None:
            incident.update_severity(Severity(request.severity))
        if request.description is not None:
            incident.description = request.description
            incident.updated_at = datetime.now(UTC)

        # Persist changes
        await self.repository.save(incident)

        # Dispatch events if any
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
