from dataclasses import dataclass, field

from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.enums.stadium_phase import StadiumPhase
from atlas_core.domain.value_objects.simulation_tick import SimulationTick
from atlas_core.domain.value_objects.stadium_edge import StadiumEdge


@dataclass(kw_only=True)
class Stadium(BaseEntity):
    """Aggregate Root representing the international football stadium digital twin."""

    name: str
    capacity: int
    nodes: list[StadiumNode] = field(default_factory=list)
    edges: list[StadiumEdge] = field(default_factory=list)
    history_ticks: list[SimulationTick] = field(default_factory=list)
    phase: StadiumPhase = StadiumPhase.CLOSED

    def add_node(self, node: StadiumNode) -> None:
        """Add an operational node to the stadium twin."""
        if any(n.id == node.id for n in self.nodes):
            raise ValueError(f"Node with ID {node.id} already exists in stadium.")
        self.nodes.append(node)

    def add_edge(self, edge: StadiumEdge) -> None:
        """Add an interconnected edge to the stadium twin."""
        node_ids = {n.id for n in self.nodes}
        if edge.source_id not in node_ids or edge.destination_id not in node_ids:
            raise ValueError("Edge source and destination node IDs must exist in stadium.")
        self.edges.append(edge)

    def record_tick(self, tick: SimulationTick) -> None:
        """Append a new simulation step state record to history."""
        self.history_ticks.append(tick)

    def transition_to_phase(self, new_phase: StadiumPhase) -> None:
        """Transitions the stadium to a new tournament match operational phase with validation invariants."""
        if self.phase == StadiumPhase.CLOSED and new_phase == StadiumPhase.POST_MATCH_EGRESS:
            raise ValueError("Cannot transition directly from Closed to Post-Match Egress.")
        if self.phase == StadiumPhase.EMERGENCY_EVACUATION and new_phase == StadiumPhase.MATCH_ACTIVE:
            raise ValueError("Cannot transition directly from Emergency Evacuation to Match Active without inspection.")
        self.phase = new_phase
