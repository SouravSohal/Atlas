from pydantic import Field

from app.intelligence.structured_output import AIResponse


class TimelineNarratorResponse(AIResponse):
    """Structured response containing operational stories across various timelines."""

    executive_timeline: str = Field(
        ...,
        description="A high-level chronological summary detailing critical operational shifts, decisions, and overall stadium state."
    )
    security_timeline: str = Field(
        ...,
        description="Narrative detailing security incidents, dispatcher activities, perimeter status, and safety alerts."
    )
    medical_timeline: str = Field(
        ...,
        description="Narrative detailing medical emergencies, response times, medical post updates, and transport dispatches."
    )
    crowd_timeline: str = Field(
        ...,
        description="Narrative describing spectator densities, gate ingress/egress flows, bottlenecks, and turnstile changes."
    )
    volunteer_timeline: str = Field(
        ...,
        description="Narrative of volunteer task assignments, check-ins, deployments, and overall labor utilization."
    )
    narrative_summary: str = Field(
        ...,
        description="A concise human-readable narrative story compiling the overall shift sequence of events."
    )
