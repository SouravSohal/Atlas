

class ReasoningBuilder:
    """Helper class to construct logical reasoning chains and business rule lists."""

    def build_business_rules(self, crowd_density: float, queue_wait: int) -> list[str]:
        """Maps operational parameters to triggered security and operations policy codes."""
        rules = ["Rule #DefaultOperations"]
        if crowd_density > 0.8:
            rules.append("Rule #CrowdRedThreshold: density exceeded 80%")
        if queue_wait > 15:
            rules.append("Rule #QueueBottleneck: turnstile delay > 15m")
        return rules
