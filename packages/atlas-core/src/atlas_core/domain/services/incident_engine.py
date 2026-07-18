from uuid import UUID, uuid4

from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate


class IncidentEngine:
    """Manages the lifecycle (Detection, Propagation, Mitigation, Resolution, Recovery) of stadium incidents."""

    def __init__(self) -> None:
        self.mitigation_strategies: dict[UUID, str] = {}
        self.incident_phases: dict[UUID, str] = {}  # Maps incident.id -> phase ("detected", "propagated", "mitigated", "resolved", "recovered")

    def detect_incident(
        self,
        stadium: Stadium,
        incident_type: IncidentType,
        severity: Severity,
        description: str,
        target_node_id: UUID
    ) -> Incident:
        """Triggers detection and constructs a new Incident bound to a target node zone."""
        # Find node location coordinates
        node = next((n for n in stadium.nodes if n.id == target_node_id), None)
        coords = Coordinates(latitude=0.0, longitude=0.0)

        incident = Incident(
            id=uuid4(),
            incident_type=incident_type,
            severity=severity,
            description=description,
            location=coords,
            reporter_id=uuid4()
        )

        self.incident_phases[incident.id] = "detected"
        return incident

    def propagate_risks(self, stadium: Stadium, active_incidents: list[Incident], incident_zones: dict[UUID, UUID]) -> None:
        """Simulates the cascading risk propagation tree. Alters neighboring nodes and edges telemetry."""
        node_map = {n.id: n for n in stadium.nodes}

        for incident in active_incidents:
            if incident.resolved:
                continue

            zone_uuid = incident_zones.get(incident.id)
            if not zone_uuid or zone_uuid not in node_map:
                continue

            # Update phase
            if self.incident_phases.get(incident.id) == "detected":
                self.incident_phases[incident.id] = "propagated"

            target_node = node_map[zone_uuid]
            phase = self.incident_phases.get(incident.id, "detected")

            # 1. Apply primary local damage (Health drops, queue spikes)
            if phase == "propagated":
                target_node.health_score = max(0.2, target_node.health_score - 0.25)
                # Spikes queue waiting times
                current_wait = target_node.operational_state.queue_estimate.waiting_minutes
                target_node.operational_state.queue_estimate = QueueEstimate(waiting_minutes=current_wait + 10)

            # 2. Propagate to adjacent edges (Choke throughput / increase congestion)
            for edge in stadium.edges:
                if edge.source_id == zone_uuid or edge.destination_id == zone_uuid:
                    # Penalize throughput and spike congestion factor
                    edge.__dict__["congestion_factor"] = min(1.0, edge.congestion_factor + 0.35)
                    edge.__dict__["max_throughput_pax_min"] = max(10.0, edge.max_throughput_pax_min * 0.5)

    def apply_mitigation(self, incident: Incident, strategy: str) -> None:
        """Mitigates an active incident, transitioning its phase to mitigated."""
        if incident.resolved:
            return
        self.mitigation_strategies[incident.id] = strategy
        self.incident_phases[incident.id] = "mitigated"

    def resolve_incident(self, incident: Incident) -> None:
        """Resolves the core incident aggregate."""
        incident.resolve()
        self.incident_phases[incident.id] = "resolved"

    def execute_recovery(self, stadium: Stadium, incident: Incident, zone_id: UUID) -> None:
        """Runs the recovery sequence, restoring node health and clearing edge congestion bottlenecks."""
        if not incident.resolved:
            return

        self.incident_phases[incident.id] = "recovered"
        node = next((n for n in stadium.nodes if n.id == zone_id), None)
        
        # 1. Restore node health score
        if node:
            node.health_score = min(1.0, node.health_score + 0.3)
            # Restore wait time queue to nominal
            current_wait = node.operational_state.queue_estimate.waiting_minutes
            node.operational_state.queue_estimate = QueueEstimate(waiting_minutes=max(0, current_wait - 10))

        # 2. Reset adjacent edges throughput and congestion
        for edge in stadium.edges:
            if edge.source_id == zone_id or edge.destination_id == zone_id:
                edge.__dict__["congestion_factor"] = max(0.0, edge.congestion_factor - 0.35)
                edge.__dict__["max_throughput_pax_min"] = edge.max_throughput_pax_min * 2.0  # restore original capacity bounds
