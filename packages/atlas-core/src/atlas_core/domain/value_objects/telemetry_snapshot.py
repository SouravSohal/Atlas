from dataclasses import dataclass
from datetime import datetime
from atlas_core.domain.value_objects.base import ValueObject

@dataclass(frozen=True)
class TelemetrySnapshot(ValueObject):
    """Represents a snapshot of utility, safety, and device connectivity telemetry."""

    timestamp: datetime
    power_draw_mw: float
    sensor_status: float
    cctv_online_rate: float
