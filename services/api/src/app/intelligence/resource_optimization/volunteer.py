from typing import Dict, List, Any

class VolunteerAllocator:
    """Computes recommended volunteer counts by zone based on crowd density and active incidents."""

    def allocate(self, zones: List[Dict[str, Any]], incidents: List[Dict[str, Any]]) -> Dict[str, int]:
        """Maps zone IDs to recommended volunteer staff counts."""
        allocations = {}
        for zone in zones:
            zone_id = zone.get("zone_id", "z-default")
            density = zone.get("density", 0.0)
            
            # Base volunteer count
            count = 3
            if density > 0.8:
                count += 6
            elif density > 0.5:
                count += 3
                
            # Increase if there are active incidents in this zone
            zone_incidents = [i for i in incidents if i.get("zone_id") == zone_id and not i.get("resolved", False)]
            count += len(zone_incidents) * 2
            
            allocations[zone_id] = count
        return allocations
