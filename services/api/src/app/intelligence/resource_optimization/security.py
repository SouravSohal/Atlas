from typing import Any


class SecurityAllocator:
    """Computes recommended security staff allocations based on security incidents and surge points."""

    def allocate(self, zones: list[dict[str, Any]], incidents: list[dict[str, Any]]) -> dict[str, int]:
        """Maps zone IDs to recommended security teams count."""
        allocations = {}
        for zone in zones:
            zone_id = zone.get("zone_id", "z-default")
            density = zone.get("density", 0.0)
            
            count = 2
            if density > 0.8:
                count += 3
                
            zone_incidents = [i for i in incidents if i.get("zone_id") == zone_id and i.get("incident_type") == "security" and not i.get("resolved", False)]
            count += len(zone_incidents) * 2
            
            allocations[zone_id] = count
        return allocations
