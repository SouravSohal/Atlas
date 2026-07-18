from dataclasses import dataclass

from atlas_core.domain.value_objects.base import ValueObject
from atlas_core.domain.value_objects.crowd_state import CrowdState
from atlas_core.domain.value_objects.incident_state import IncidentState
from atlas_core.domain.value_objects.telemetry_snapshot import TelemetrySnapshot


@dataclass(frozen=True)
class SimulationTick(ValueObject):
    """Represents a discrete simulation step snapshot of stadium metrics."""

    tick_index: int
    time_offset: str
    telemetry: TelemetrySnapshot
    crowd: CrowdState
    incidents: IncidentState
