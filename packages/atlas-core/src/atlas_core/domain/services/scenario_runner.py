from uuid import UUID

from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.services.simulation_engine import (
    SimulationContext,
    SimulationEngine,
    SimulationEvent,
)


class ScenarioRunner:
    """Configures and injects specific operational scenario events into the Simulation Engine context."""

    def __init__(self, context: SimulationContext) -> None:
        self.context = context

    def inject_scenario_events(self, scenario_name: str, target_node_id: UUID, trigger_tick: int = 1) -> None:
        """Injects scenario-specific event configurations into the active simulation schedule queue."""
        
        event: SimulationEvent | None = None

        if scenario_name == "Crowd Surge":
            event = SimulationEvent(
                name="Crowd Surge",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.CROWD_CONTROL,
                severity=Severity.HIGH,
                description="Turnstile validation bottleneck crowd surge"
            )
        elif scenario_name == "Medical Emergency":
            event = SimulationEvent(
                name="Medical Emergency",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.MEDICAL,
                severity=Severity.CRITICAL,
                description="Spectator heat collapse and medical distress"
            )
        elif scenario_name == "Heavy Rain":
            event = SimulationEvent(
                name="Heavy Rain",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.WEATHER,
                severity=Severity.MEDIUM,
                description="Heavy rainfall causing spectator concourse crowding"
            )
        elif scenario_name == "Bomb Threat":
            event = SimulationEvent(
                name="Bomb Threat",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.SECURITY,
                severity=Severity.CRITICAL,
                description="Suspicious unattended backpack package found"
            )
        elif scenario_name == "Fire":
            event = SimulationEvent(
                name="Fire",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.FACILITY,
                severity=Severity.CRITICAL,
                description="Electrical fire outbreak in food court kitchen"
            )
        elif scenario_name == "Power Failure":
            event = SimulationEvent(
                name="Power Failure",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.FACILITY,
                severity=Severity.HIGH,
                description="Transformer grid power failure concourse blackouts"
            )
        elif scenario_name == "Lost Child":
            event = SimulationEvent(
                name="Lost Child",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.SECURITY,
                severity=Severity.MEDIUM,
                description="8-year-old child separated from guardians near sector vomitory"
            )
        elif scenario_name == "VIP Arrival":
            event = SimulationEvent(
                name="VIP Arrival",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.CROWD_CONTROL,
                severity=Severity.LOW,
                description="High priority diplomatic transport routing logistics"
            )
        elif scenario_name == "Parking Overflow":
            event = SimulationEvent(
                name="Parking Overflow",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.FACILITY,
                severity=Severity.HIGH,
                description="Main north parking lot full and overflowing"
            )
        elif scenario_name == "Metro Delay":
            event = SimulationEvent(
                name="Metro Delay",
                target_node_id=target_node_id,
                trigger_tick=trigger_tick,
                incident_type=IncidentType.FACILITY,
                severity=Severity.HIGH,
                description="Transit line train signaling failure delay backlog"
            )

        if event:
            self.context.scheduled_events.append(event)
            
    def run_tick(self) -> None:
        """Executes one simulation cycle tick updating all nodes, crowd flows, and active incidents."""
        SimulationEngine.tick(self.context)
