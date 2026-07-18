from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion


class ResourceOptimizationPrompt(BasePrompt):
    """Structured prompt template for the Resource Optimization Engine."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="resource_optimization_agent",
            description="Optimizes stadium staff and gateway allocations.",
            author="System",
            tags=["agent", "resource", "optimization"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations Resource Optimization AI Agent.\n"
                    "We have computed the following deterministic resource allocations:\n"
                    "Volunteer Allocations: {volunteer_allocations}\n"
                    "Security Allocations: {security_allocations}\n"
                    "Medical Allocations: {medical_allocations}\n"
                    "Gate Openings: {gate_openings}\n"
                    "Queue Balancing Rules: {queue_rules}\n\n"
                    "Analyze these parameters under the current operational state and write a professional "
                    "explanation detailing expected improvements, confidence, and critical trade-offs.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)
