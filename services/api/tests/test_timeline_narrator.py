from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.intelligence import AIOrchestrator, PromptRegistry
from app.intelligence.timeline import (
    EventAggregator,
    SummaryGenerator,
    TimelineFormatter,
    TimelineNarrator,
    TimelineNarratorResponse,
)


# Simulated domain objects for testing
class MockDomainEvent:
    def __init__(self, name: str, occurred_at: datetime) -> None:
        self.name = name
        self.occurred_at = occurred_at

    def __str__(self) -> str:
        return f"Event: {self.name}"

class MockOperationalState:
    def __init__(self, zone_id: str, density: float, queue: int, last_updated: datetime) -> None:
        self.zone_id = zone_id
        self.density = density
        self.queue_waiting_minutes = queue
        self.last_updated = last_updated

class MockIncident:
    def __init__(self, incident_type: str, severity: str, description: str, resolved: bool, created_at: datetime) -> None:
        self.incident_type = incident_type
        self.severity = severity
        self.description = description
        self.resolved = resolved
        self.created_at = created_at

class MockRecommendation:
    def __init__(self, action_type: str, priority: str, details: str, created_at: datetime) -> None:
        self.action_type = action_type
        self.priority = priority
        self.details = details
        self.created_at = created_at

@pytest.fixture
def mock_orchestrator() -> MagicMock:
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry
    return orchestrator

def test_event_aggregator() -> None:
    aggregator = EventAggregator()
    ts_1 = datetime.now(UTC) - timedelta(minutes=10)
    ts_2 = datetime.now(UTC) - timedelta(minutes=5)
    ts_3 = datetime.now(UTC)

    events = [MockDomainEvent("IngressStart", ts_1)]
    states = [MockOperationalState("zone-1", 0.4, 8, ts_2)]
    incidents = [MockIncident("security", "high", "Unattended package", False, ts_3)]
    recommendations = []

    aggregated = aggregator.aggregate(events, states, incidents, recommendations)
    assert len(aggregated) == 3
    assert aggregated[0]["type"] == "DomainEvent"
    assert aggregated[1]["type"] == "OperationalStateChange"
    assert aggregated[2]["type"] == "IncidentCreated"

def test_timeline_formatter() -> None:
    formatter = TimelineFormatter()
    ts_1 = datetime(2026, 7, 8, 12, 5, 0)
    events = [
        {"type": "IncidentCreated", "timestamp": ts_1, "details": "Unattended package"},
    ]
    formatted = formatter.format(events)
    assert "[12:05:00] IncidentCreated: Unattended package" in formatted

    empty_formatted = formatter.format([])
    assert "No operational events logged" in empty_formatted

def test_summary_generator() -> None:
    generator = SummaryGenerator()
    ts_base = datetime(2026, 7, 8, 12, 0, 0)
    events = [
        {"type": "Ev", "timestamp": ts_base, "details": "Inc reference #1"},
        {"type": "Ev", "timestamp": ts_base + timedelta(minutes=10), "details": "Normal update"},
        {"type": "Ev", "timestamp": ts_base + timedelta(minutes=20), "details": "Inc reference #2"},
    ]

    # Time filtering
    time_filtered = generator.filter_by_time_range(
        events, ts_base + timedelta(minutes=5), ts_base + timedelta(minutes=15)
    )
    assert len(time_filtered) == 1
    assert "Normal update" in time_filtered[0]["details"]

    # Incident filtering
    inc_filtered = generator.filter_by_incident(events, "#1")
    assert len(inc_filtered) == 1
    assert "Inc reference #1" in inc_filtered[0]["details"]

@pytest.mark.asyncio
async def test_timeline_narrator(mock_orchestrator: MagicMock) -> None:
    expected_response = TimelineNarratorResponse(
        confidence_score=0.97,
        rationale="Completed narration.",
        executive_timeline="Executive summary of the day.",
        security_timeline="Security patrol active.",
        medical_timeline="No medical warnings.",
        crowd_timeline="Safe gate crowd density.",
        volunteer_timeline="All volunteers assigned.",
        narrative_summary="Excellent day at the stadium.",
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_response)

    narrator = TimelineNarrator(mock_orchestrator)
    
    # Verify registry
    registered_prompt = mock_orchestrator.registry.get("timeline_narrator_agent", "latest")
    assert "You are the ATLAS Stadium Operations Timeline Narrator Agent." in registered_prompt.template

    ts_base = datetime.now(UTC)
    
    # Provide all kinds of mock events to cover EventAggregator branches
    domain_events = [MockDomainEvent("IngressStart", ts_base)]
    states = [MockOperationalState("zone-1", 0.4, 8, ts_base + timedelta(minutes=1))]
    incidents = [
        MockIncident("security", "high", "Unattended package", False, ts_base + timedelta(minutes=2)),
        MockIncident("medical", "low", "Sprained ankle", True, ts_base + timedelta(minutes=3))
    ]
    recommendations = [MockRecommendation("dispatch", "high", "Deploy team", ts_base + timedelta(minutes=4))]

    # Act 1: Basic narration
    response = await narrator.narrate(
        domain_events=domain_events,
        operational_states=states,
        incidents=incidents,
        recommendations=recommendations,
        language="Spanish",
        style="short summary",
    )

    assert response.confidence_score == 0.97
    assert response.narrative_summary == "Excellent day at the stadium."
    assert mock_orchestrator.execute.call_count == 1

    # Act 2: Narration with time range filters
    response_time = await narrator.narrate(
        domain_events=domain_events,
        operational_states=states,
        incidents=incidents,
        recommendations=recommendations,
        start_time=ts_base - timedelta(minutes=5),
        end_time=ts_base + timedelta(minutes=10),
    )
    assert response_time.confidence_score == 0.97
    assert mock_orchestrator.execute.call_count == 2

    # Act 3: Narration with incident centric filter
    response_inc = await narrator.narrate(
        domain_events=domain_events,
        operational_states=states,
        incidents=incidents,
        recommendations=recommendations,
        incident_centric_id="Unattended package",
    )
    assert response_inc.confidence_score == 0.97
    assert mock_orchestrator.execute.call_count == 3
