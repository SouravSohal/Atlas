from datetime import datetime
from typing import Any

from app.intelligence import AIOrchestrator
from app.intelligence.timeline.event_aggregator import EventAggregator
from app.intelligence.timeline.models import TimelineNarratorResponse
from app.intelligence.timeline.story_builder import TimelineNarratorPrompt
from app.intelligence.timeline.summary_generator import SummaryGenerator
from app.intelligence.timeline.timeline_formatter import TimelineFormatter


class TimelineNarrator:
    """ATLAS AI Timeline Narrator facade responsible for converting logs into human-readable narratives."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.aggregator = EventAggregator()
        self.formatter = TimelineFormatter()
        self.summary_generator = SummaryGenerator()
        self.prompt_definition = TimelineNarratorPrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def narrate(
        self,
        domain_events: list[Any],
        operational_states: list[Any],
        incidents: list[Any],
        recommendations: list[Any],
        language: str = "English",
        style: str = "detailed narrative",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        incident_centric_id: str | None = None,
    ) -> TimelineNarratorResponse:
        """Processes and formats raw telemetry to execute cognitive timeline narration."""
        # 1. Aggregate
        events = self.aggregator.aggregate(
            domain_events=domain_events,
            operational_states=operational_states,
            incidents=incidents,
            recommendations=recommendations,
        )

        # 2. Filter if parameters are provided
        if start_time and end_time:
            events = self.summary_generator.filter_by_time_range(events, start_time, end_time)
        elif incident_centric_id:
            events = self.summary_generator.filter_by_incident(events, incident_centric_id)

        # 3. Format
        formatted_logs = self.formatter.format(events)

        # 4. Invoke orchestrator
        return await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=TimelineNarratorResponse,
            language=language,
            style=style,
            formatted_logs=formatted_logs,
            context="",
            min_confidence=0.0,
        )
