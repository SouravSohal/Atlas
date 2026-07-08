from typing import Dict, List, Any

class QueueBalancer:
    """Determines crowd flow redirection rules to balance waiting queues."""

    def balance_queues(self, zones: List[Dict[str, Any]]) -> Dict[str, str]:
        """Maps zone IDs to crowd flow direction rules (e.g. forward, redirect)."""
        rules = {}
        for zone in zones:
            zone_id = zone.get("zone_id", "z-default")
            density = zone.get("density", 0.0)
            
            if density > 0.8:
                rules[zone_id] = "REDIRECT_TO_CORRIDOR_B"
            elif density > 0.5:
                rules[zone_id] = "DIVERT_TO_GATE_2"
            else:
                rules[zone_id] = "KEEP_FORWARD"
        return rules
