from typing import Any


class MedicalAllocator:
    """Computes medical responder allocations based on medical incidents and sector density."""

    def allocate(self, zones: list[dict[str, Any]], incidents: list[dict[str, Any]]) -> dict[str, int]:
        """Maps zone IDs to recommended medical teams count."""
        allocations = {}
        for zone in zones:
            zone_id = zone.get("zone_id", "z-default")
            
            count = 1
            zone_incidents = [i for i in incidents if i.get("zone_id") == zone_id and i.get("incident_type") == "medical" and not i.get("resolved", False)]
            count += len(zone_incidents) * 2
            
            allocations[zone_id] = count
        return allocations
