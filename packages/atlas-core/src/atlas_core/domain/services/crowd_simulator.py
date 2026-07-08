import random
import uuid
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import List, Dict, Any

from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.services.graph_engine import StadiumGraphEngine

@dataclass
class SpectatorAgent:
    """Represents an individual simulated spectator moving through the stadium graph."""
    id: UUID
    category: str  # "regular", "vip", "media"
    current_node_id: UUID
    destination_node_id: UUID
    route: List[UUID] = field(default_factory=list)
    route_index: int = 0
    walking_speed: float = 1.2  # meters per second
    patience: float = 1.0       # decodes queue tolerance [0.0, 1.0]
    state: str = "walking"      # "walking", "queuing", "sitting", "leaving"
    ticks_in_queue: int = 0

    def calculate_path(self, graph: Any) -> None:
        """Computes the shortest route to the destination node using StadiumGraphEngine."""
        try:
            path_strs = StadiumGraphEngine.find_shortest_route(graph, self.current_node_id, self.destination_node_id)
            self.route = [UUID(nid) for nid in path_strs]
            self.route_index = 0
        except Exception:
            # Fallback if no route exists
            self.route = [self.current_node_id]
            self.route_index = 0

class CrowdSimulationEngine:
    """Agent-based crowd dynamics simulator moving individual spectator agents over graph nodes."""

    def __init__(self, stadium: Stadium):
        self.stadium = stadium
        self.graph = StadiumGraphEngine.build_graph(stadium)
        self.agents: List[SpectatorAgent] = []

    def spawn_agents(self, count: int, category: str, start_node_id: UUID, end_node_id: UUID) -> None:
        """Spawns spectator agents at a starting node."""
        for _ in range(count):
            agent = SpectatorAgent(
                id=uuid4(),
                category=category,
                current_node_id=start_node_id,
                destination_node_id=end_node_id,
                walking_speed=random.uniform(0.9, 1.4),
                patience=random.uniform(0.5, 1.0)
            )
            agent.calculate_path(self.graph)
            self.agents.append(agent)

    def tick(self, step_duration_minutes: float = 5.0) -> Dict[UUID, int]:
        """Runs one movement tick, updating agent positions and node queues."""
        step_seconds = step_duration_minutes * 60.0

        # Build node id mapping
        nodes_dict = {n.id: n for n in self.stadium.nodes}

        # Tracks updated node occupancies
        occupancies = {n.id: 0 for n in self.stadium.nodes}

        # Re-build graph to get updated congestion metrics
        self.graph = StadiumGraphEngine.build_graph(self.stadium)

        for agent in self.agents:
            if agent.state == "sitting":
                occupancies[agent.current_node_id] += 1
                continue

            if agent.state == "queuing":
                agent.ticks_in_queue += 1
                agent.patience = max(0.0, agent.patience - 0.05)
                
                # Check if they clear the queue or lose patience
                node = nodes_dict.get(agent.current_node_id)
                wait_minutes = node.operational_state.queue_estimate.waiting_minutes if node else 0
                
                # Reroute if patience is exhausted
                if agent.patience <= 0.1 and wait_minutes > 15:
                    # Choose a random adjacent node or alternative
                    # For simplicity, reset queue state and try to move on
                    agent.patience = 0.5
                    agent.ticks_in_queue = 0
                    agent.state = "walking"
                elif agent.ticks_in_queue >= max(1, int(wait_minutes / step_duration_minutes)):
                    # Clear queue
                    agent.state = "walking"
                    agent.ticks_in_queue = 0
                
                occupancies[agent.current_node_id] += 1
                continue

            if agent.state == "walking":
                # Ensure they have a route and are not at the end
                if not agent.route or agent.route_index >= len(agent.route) - 1:
                    if agent.current_node_id == agent.destination_node_id:
                        node = nodes_dict.get(agent.current_node_id)
                        if node and "Gate" in node.category:
                            agent.state = "leaving"
                        else:
                            agent.state = "sitting"
                    occupancies[agent.current_node_id] += 1
                    continue

                # Move along the current edge
                next_node_id = agent.route[agent.route_index + 1]
                
                # Fetch edge walking time adjusted by congestion factor
                try:
                    congestion = StadiumGraphEngine.calculate_congestion(self.graph, agent.current_node_id, next_node_id)
                except Exception:
                    congestion = 0.0

                # Base average walking time
                base_time = 60.0  # default 1 min
                # Find matching edge in stadium
                matching_edge = next((e for e in self.stadium.edges 
                                      if e.source_id == agent.current_node_id and e.destination_id == next_node_id), None)
                if matching_edge:
                    base_time = matching_edge.avg_walk_seconds

                adjusted_walk_time = base_time * (1.0 + congestion * 2.5)

                if step_seconds >= adjusted_walk_time:
                    # Successfully crossed the edge
                    agent.current_node_id = next_node_id
                    agent.route_index += 1

                    # Check if next node has a long queue
                    target_node = nodes_dict.get(next_node_id)
                    if target_node and target_node.operational_state.queue_estimate.waiting_minutes > 5:
                        agent.state = "queuing"
                        agent.ticks_in_queue = 0

                occupancies[agent.current_node_id] += 1

        return occupancies
