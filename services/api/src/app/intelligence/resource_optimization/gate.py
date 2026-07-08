from typing import List, Dict, Any

class GateOptimizer:
    """Recommends which gates to activate/deactivate to optimize ingress/egress."""

    def optimize_gates(self, zones: List[Dict[str, Any]]) -> List[str]:
        """Returns list of gate zone IDs that should be actively open to optimize flows."""
        active_gates = []
        for zone in zones:
            zone_id = zone.get("zone_id", "z-default")
            density = zone.get("density", 0.0)
            
            # Recommends opening if crowd density is high
            if density > 0.5:
                active_gates.append(zone_id)
        return active_gates
