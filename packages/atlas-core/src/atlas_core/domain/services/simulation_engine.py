import asyncio
from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import UUID, uuid4
from typing import Any

from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate
from atlas_core.domain.value_objects.telemetry_snapshot import TelemetrySnapshot
from atlas_core.domain.value_objects.crowd_state import CrowdState
from atlas_core.domain.value_objects.incident_state import IncidentState
from atlas_core.domain.value_objects.simulation_tick import SimulationTick
from atlas_core.domain.services.graph_engine import StadiumGraphEngine

@dataclass
class SimulationClock:
    """Tracks discrete simulation intervals and step indices."""
    tick_index: int = 0
    time_offset_minutes: int = -120  # T-120m start
    step_duration_minutes: int = 5

    @property
    def time_offset_str(self) -> str:
        if self.time_offset_minutes < 0:
            return f"T{self.time_offset_minutes}m"
        if self.time_offset_minutes == 0:
            return "T0m"
        return f"T+{self.time_offset_minutes}m"

    def tick(self) -> None:
        self.tick_index += 1
        self.time_offset_minutes += self.step_duration_minutes

@dataclass(frozen=True)
class SimulationEvent:
    """Represents a scheduled anomaly event that alters simulation variables."""
    name: str
    target_node_id: UUID
    trigger_tick: int
    incident_type: IncidentType
    severity: Severity
    description: str

@dataclass
class SimulationContext:
    """Contains the active runtime state for the simulation cycle."""
    stadium: Stadium
    clock: SimulationClock = field(default_factory=SimulationClock)
    scheduled_events: list[SimulationEvent] = field(default_factory=list)
    active_incidents: list[Incident] = field(default_factory=list)
    node_occupancies: dict[UUID, int] = field(default_factory=dict)  # Tracks live spectator count per node
    incident_zones: dict[UUID, UUID] = field(default_factory=dict)  # Maps incident.id -> node.id

class SimulationEngine:
    """Executes crowd flows, incident triggers, and updates the Digital Twin state on each tick."""

    @staticmethod
    def tick(context: SimulationContext) -> SimulationTick:
        """Executes a single simulation step modifying stadium states."""
        stadium = context.stadium
        clock = context.clock

        # Initialize node occupancies if empty
        if not context.node_occupancies:
            for node in stadium.nodes:
                context.node_occupancies[node.id] = int(node.capacity * node.operational_state.density.value)

        # 1. Update incidents based on schedule
        active_scheduled = [
            e for e in context.scheduled_events if e.trigger_tick == clock.tick_index
        ]
        from atlas_core.domain.value_objects.coordinates import Coordinates
        for evt in active_scheduled:
            # Spawn domain incident conforming to the domain entities constraints
            incident_id = uuid4()
            incident = Incident(
                id=incident_id,
                incident_type=evt.incident_type,
                severity=evt.severity,
                description=evt.description,
                location=Coordinates(latitude=0.0, longitude=0.0),
                reporter_id=uuid4()
            )
            context.active_incidents.append(incident)
            context.incident_zones[incident_id] = evt.target_node_id

        # 2. Move Spectators & Update Queues
        # Spectators flow along edges based on graph throughput bounds
        temp_occupancies = context.node_occupancies.copy()
        for edge in stadium.edges:
            src_occ = context.node_occupancies.get(edge.source_id, 0)
            
            # Flow capacity is limited by throughput and node occupancy
            flow_capacity = int(edge.max_throughput_pax_min * clock.step_duration_minutes)
            actual_flow = min(src_occ, flow_capacity)

            # Apply congestion penalty based on flow ratio
            congestion = min(1.0, actual_flow / max(1, flow_capacity))
            edge.__dict__["congestion_factor"] = congestion  # Update mutable state

            # Move people
            temp_occupancies[edge.source_id] = max(0, temp_occupancies.get(edge.source_id, 0) - actual_flow)
            temp_occupancies[edge.destination_id] = temp_occupancies.get(edge.destination_id, 0) + actual_flow

        context.node_occupancies = temp_occupancies

        # 3. Detect Congestion & Update Nodes OperationalState
        total_pax = 0
        total_wait = 0.0
        max_density = 0.0

        for node in stadium.nodes:
            occ = context.node_occupancies.get(node.id, 0)
            density_ratio = min(1.0, occ / max(1, node.capacity))
            total_pax += occ
            max_density = max(max_density, density_ratio)

            # Queue estimate increases when density breaches 0.70 threshold
            wait_minutes = 0
            if density_ratio > 0.70:
                wait_minutes = int((density_ratio - 0.70) * 40)
            total_wait += wait_minutes

            # Apply incident impact to health score
            node_incidents = [
                i for i in context.active_incidents
                if context.incident_zones.get(i.id) == node.id and not i.resolved
            ]
            if node_incidents:
                node.health_score = max(0.2, 1.0 - (len(node_incidents) * 0.3))
            else:
                node.health_score = min(1.0, node.health_score + 0.05)

            # Mutate core operational state
            node.operational_state.density = CrowdDensity(value=density_ratio)
            node.operational_state.queue_estimate = QueueEstimate(waiting_minutes=wait_minutes)
            node.operational_state.last_updated = datetime.now(UTC)

        # 4. Generate AI telemetry snapshot metrics
        now = datetime.now(UTC)
        telemetry = TelemetrySnapshot(
            timestamp=now,
            power_draw_mw=6.5 + (total_pax / 65000.0) * 3.5,
            sensor_status=0.98 if len(context.active_incidents) == 0 else 0.92,
            cctv_online_rate=0.99
        )

        crowd = CrowdState(
            occupancy_percentage=min(1.0, total_pax / max(1, stadium.capacity)),
            avg_wait_minutes=total_wait / max(1, len(stadium.nodes)),
            peak_density_pax_m2=max_density * 4.0
        )

        warnings_cnt = len([i for i in context.active_incidents if i.severity in (Severity.MEDIUM, Severity.HIGH) and not i.resolved])
        criticals_cnt = len([i for i in context.active_incidents if i.severity == Severity.CRITICAL and not i.resolved])

        incidents_state = IncidentState(
            active_count=len([i for i in context.active_incidents if not i.resolved]),
            critical_count=criticals_cnt,
            warning_count=warnings_cnt
        )

        # 5. Record tick in the digital twin aggregate
        tick = SimulationTick(
            tick_index=clock.tick_index,
            time_offset=clock.time_offset_str,
            telemetry=telemetry,
            crowd=crowd,
            incidents=incidents_state
        )
        stadium.record_tick(tick)

        # Advance Clock
        clock.tick()
        return tick

class SimulationScheduler:
    """Manages active timer intervals to run the simulation engine loop."""

    def __init__(self, engine: SimulationEngine, context: SimulationContext):
        self.engine = engine
        self.context = context
        self._running = False

    async def start(self, interval_seconds: float = 2.0, max_ticks: int = 10) -> None:
        """Runs the simulation engine tick scheduler loop."""
        self._running = True
        ticks_run = 0
        while self._running and ticks_run < max_ticks:
            self.engine.tick(self.context)
            ticks_run += 1
            await asyncio.sleep(interval_seconds)

    def stop(self) -> None:
        """Halts the scheduler loop."""
        self._running = False
