import json
import uuid
from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate
from atlas_core.domain.value_objects.stadium_edge import StadiumEdge


# Pydantic Schemas for validation
class StadiumMetadataSchema(BaseModel):
    name: str
    city: str
    capacity: int
    timestamp: datetime

class NodeSchema(BaseModel):
    id: str
    name: str
    category: str
    capacity: int
    health: float
    density: float
    queue_waiting_minutes: int
    resources: str | None = None

class EdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    distance_meters: float
    avg_walk_seconds: float
    max_throughput_pax_min: float
    congestion_factor: float
    emergency_access: bool

class SensorSchema(BaseModel):
    id: str
    node_id: str
    type: str
    metric: str
    status: str
    value: float

class VolunteerSchema(BaseModel):
    id: str
    name: str
    team: str
    zone: str
    status: str
    skills: list[str] = Field(default_factory=list)
    assignment: str | None = None
    battery: int

class SecurityOfficerSchema(BaseModel):
    id: str
    name: str
    team: str
    zone: str
    status: str
    radio_channel: str

class MedicalTeamSchema(BaseModel):
    id: str
    name: str
    zone: str
    status: str
    vehicle_id: str

class WorkforceSchema(BaseModel):
    volunteers: list[VolunteerSchema] = Field(default_factory=list)
    security_officers: list[SecurityOfficerSchema] = Field(default_factory=list)
    medical_teams: list[MedicalTeamSchema] = Field(default_factory=list)

class IncidentSchema(BaseModel):
    id: str
    type: str
    severity: str
    description: str
    zone_id: str
    resolved: bool

class RecommendationSchema(BaseModel):
    id: str
    action_type: str
    priority: str
    confidence: float
    details: str
    status: str

class StadiumSeedDataSchema(BaseModel):
    stadium_metadata: StadiumMetadataSchema
    nodes: list[NodeSchema]
    edges: list[EdgeSchema]
    sensors: list[SensorSchema] = Field(default_factory=list)
    workforce: WorkforceSchema | None = None
    incidents: list[IncidentSchema] = Field(default_factory=list)
    recommendations: list[RecommendationSchema] = Field(default_factory=list)

class StadiumDataLoader:
    """Service to load and validate stadium JSON configs into Domain aggregates."""

    @staticmethod
    def load_from_json(json_str: str) -> Stadium:
        """Parses, validates, and initializes a Stadium digital twin aggregate from JSON."""
        # 1. Parse JSON content
        data = json.loads(json_str)

        # 2. Validate using Pydantic
        schema = StadiumSeedDataSchema.model_validate(data)

        # 3. Create Stable UUID namespace mapping for Node IDs
        # Node string IDs (e.g. "node-0") are mapped to UUIDs consistently
        node_id_map: dict[str, UUID] = {}
        for n in schema.nodes:
            # Generate deterministic UUID based on node string name
            node_id_map[n.id] = uuid.uuid5(uuid.NAMESPACE_DNS, n.id)

        # 4. Construct Stadium aggregate root
        stadium = Stadium(
            name=schema.stadium_metadata.name,
            capacity=schema.stadium_metadata.capacity
        )

        # 5. Populate nodes
        for n in schema.nodes:
            node_uuid = node_id_map[n.id]

            # Scale density between 0.0 and 1.0 (if written as percentage, e.g. 45% -> 0.45)
            density_val = n.density
            if density_val > 1.0:
                density_val = density_val / 100.0
            density_val = max(0.0, min(1.0, density_val))

            op_state = OperationalState(
                id=uuid.uuid4(),
                zone_id=node_uuid,
                density=CrowdDensity(value=density_val),
                queue_estimate=QueueEstimate(waiting_minutes=n.queue_waiting_minutes),
                last_updated=datetime.now(UTC)
            )

            # Node creation
            node = StadiumNode(
                id=node_uuid,
                name=n.name,
                category=n.category,
                capacity=n.capacity,
                operational_state=op_state,
                health_score=n.health / 100.0 if n.health > 1.0 else n.health,
                dwell_time_seconds=120.0,
                ai_importance=0.90
            )
            stadium.add_node(node)

        # 6. Populate edges
        for e in schema.edges:
            src_uuid = node_id_map.get(e.source)
            dest_uuid = node_id_map.get(e.target)

            if not src_uuid or not dest_uuid:
                continue

            edge = StadiumEdge(
                source_id=src_uuid,
                destination_id=dest_uuid,
                distance_meters=e.distance_meters,
                avg_walk_seconds=e.avg_walk_seconds,
                max_throughput_pax_min=e.max_throughput_pax_min,
                congestion_factor=e.congestion_factor,
                emergency_access=e.emergency_access
            )
            stadium.add_edge(edge)

        return stadium
