import networkx as nx
from uuid import UUID
from typing import Any
from atlas_core.domain.entities.stadium import Stadium

class StadiumGraphEngine:
    """Core graph processing service for stadium digital twin network routing using NetworkX."""

    @staticmethod
    def build_graph(stadium: Stadium) -> nx.DiGraph:
        """Builds a NetworkX directed weighted graph from stadium aggregates."""
        graph = nx.DiGraph()

        # Add nodes with metadata
        for node in stadium.nodes:
            # Safely handle operational state mapping
            density_val = node.operational_state.density.value
            wait_val = node.operational_state.queue_estimate.waiting_minutes

            graph.add_node(
                str(node.id),
                name=node.name,
                category=node.category,
                capacity=node.capacity,
                density=density_val,
                queue_waiting_minutes=wait_val,
                health_score=node.health_score,
                dwell_time_seconds=node.dwell_time_seconds,
                ai_importance=node.ai_importance
            )

        # Add edges with metadata
        for edge in stadium.edges:
            # Base weight is walking time (seconds), penalized by congestion factor
            congestion = edge.congestion_factor
            penalized_weight = edge.avg_walk_seconds * (1.0 + congestion * 2.5)

            graph.add_edge(
                str(edge.source_id),
                str(edge.destination_id),
                distance_meters=edge.distance_meters,
                avg_walk_seconds=edge.avg_walk_seconds,
                max_throughput_pax_min=edge.max_throughput_pax_min,
                congestion_factor=congestion,
                emergency_access=edge.emergency_access,
                weight=penalized_weight
            )

        return graph

    @staticmethod
    def find_shortest_route(
        graph: nx.DiGraph,
        source_id: UUID | str,
        destination_id: UUID | str,
        weight_attr: str = "weight"
    ) -> list[str]:
        """Calculates the shortest route between two nodes based on a weight attribute."""
        src = str(source_id)
        dest = str(destination_id)
        if src not in graph or dest not in graph:
            raise ValueError(f"Nodes {src} or {dest} do not exist in the graph.")

        try:
            path = nx.shortest_path(graph, source=src, target=dest, weight=weight_attr)
            return list(path)
        except nx.NetworkXNoPath as e:
            raise ValueError(f"No pathway exists between {src} and {dest}.") from e

    @staticmethod
    def calculate_congestion(graph: nx.DiGraph, source_id: UUID | str, destination_id: UUID | str) -> float:
        """Calculates the congestion factor on a specific connecting edge."""
        src = str(source_id)
        dest = str(destination_id)
        if not graph.has_edge(src, dest):
            raise ValueError(f"No edge exists between {src} and {dest}.")
        return float(graph[src][dest].get("congestion_factor", 0.0))

    @staticmethod
    def reroute(
        graph: nx.DiGraph,
        source_id: UUID | str,
        destination_id: UUID | str,
        blocked_nodes: list[UUID | str]
    ) -> list[str]:
        """Recalculates routing path by copying and pruning blocked nodes."""
        temp_graph = graph.copy()
        for node in blocked_nodes:
            node_str = str(node)
            if node_str in temp_graph:
                temp_graph.remove_node(node_str)

        return StadiumGraphEngine.find_shortest_route(temp_graph, source_id, destination_id)

    @staticmethod
    def estimate_travel_time(graph: nx.DiGraph, route: list[str]) -> float:
        """Estimates total travel time in seconds along a planned route."""
        total_time = 0.0
        for i in range(len(route) - 1):
            src, dest = route[i], route[i + 1]
            if graph.has_edge(src, dest):
                edge_data = graph[src][dest]
                # base walk seconds penalized by congestion
                total_time += edge_data["avg_walk_seconds"] * (1.0 + edge_data["congestion_factor"] * 2.5)
            else:
                # Fallback if jumping between unlinked nodes in manual list
                total_time += 60.0
        return total_time

    @staticmethod
    def predict_capacity(graph: nx.DiGraph, node_id: UUID | str) -> dict[str, Any]:
        """Predicts remaining occupancy volume and capacity bounds of a target node."""
        nid = str(node_id)
        if nid not in graph:
            raise ValueError(f"Node {nid} does not exist in graph.")

        node_data = graph.nodes[nid]
        cap = node_data.get("capacity", 15000)
        density = node_data.get("density", 0.0)

        # Estimate current occupancy count based on density ratio
        current_occupancy = int(cap * density)
        remaining_capacity = cap - current_occupancy

        return {
            "capacity_limit": cap,
            "current_occupancy": current_occupancy,
            "remaining_capacity": max(0, remaining_capacity),
            "at_critical_limit": density >= 0.85
        }
