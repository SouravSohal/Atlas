from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

class ScenarioState(Enum):
    """Play state of the running demo scenario."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"

@dataclass
class ScenarioStep:
    """Represents a single step or tick in a demo timeline execution."""
    tick_index: int
    operational_state_updates: Dict[str, float] = field(default_factory=dict)  # zone_id -> density
    incidents_to_create: List[Dict[str, Any]] = field(default_factory=list)  # fields for incidents
    notifications_to_publish: List[str] = field(default_factory=list)
    events_to_publish: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ScenarioDefinition:
    """Extensible configuration defining a demo scenario's flow."""
    name: str
    description: str
    steps: List[ScenarioStep] = field(default_factory=list)
