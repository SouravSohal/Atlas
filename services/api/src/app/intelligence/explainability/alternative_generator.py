

class AlternativeGenerator:
    """Computes alternative options and their qualitative trade-offs."""

    def generate(self, action_type: str) -> list[str]:
        """Suggests viable fallback methods based on recommendation type."""
        if "reroute" in action_type.lower():
            return ["Hold crowd at current gate entrances", "Add more physical barriers without redirection"]
        if "dispatch" in action_type.lower():
            return ["Deploy static security personnel", "Request spectator self-routing via digital signage"]
        return ["Maintain status quo operations", "Request manual override confirmation"]
