from dataclasses import dataclass, field
from atlas_core.domain.entities.base import BaseEntity
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.value_objects.stadium_edge import StadiumEdge
from atlas_core.domain.value_objects.simulation_tick import SimulationTick

@dataclass(kw_only=True)
class Stadium(BaseEntity):
    """Aggregate Root representing the international football stadium digital twin."""

    name: str
    capacity: int
    nodes: list[StadiumNode] = field(default_factory=list)
    edges: list[StadiumEdge] = field(default_factory=list)
    history_ticks: list[SimulationTick] = field(default_factory=list)

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
