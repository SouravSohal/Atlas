from collections.abc import Sequence

from atlas_core.domain.value_objects.crowd_density import CrowdDensity


class NavigationPolicy:
    """Domain policy defining routing safety and route optimization penalties."""

    CRITICAL_DENSITY_THRESHOLD = 0.9

    @staticmethod
    def is_route_safe(path_densities: Sequence[CrowdDensity]) -> bool:
        """Check if a route is safe to traverse, based on path densities."""
        return not any(
            d.value >= NavigationPolicy.CRITICAL_DENSITY_THRESHOLD for d in path_densities
        )

    @staticmethod
    def calculate_route_penalty(distance_meters: float, average_density: CrowdDensity) -> float:
        """Calculate a routing penalty factor based on distance and crowd density.

        Returns a virtual distance score used for comparing routes.
        """
        return distance_meters * (1.0 + average_density.value * 2.0)
