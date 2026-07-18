from unittest.mock import AsyncMock, MagicMock

import pytest

from app.intelligence import AIOrchestrator, PromptRegistry
from app.intelligence.briefings import (
    BriefingGenerator,
    BriefingReport,
    BriefingType,
    KPICollector,
    MarkdownExporter,
    PDFExporter,
)


# Simulated domain objects for testing
class MockOverview:
    def __init__(self, health: float, volunteers: int) -> None:
        self.stadium_health = health
        self.allocated_volunteers_count = volunteers

class MockState:
    def __init__(self, density: float) -> None:
        self.density = density

class MockIncident:
    def __init__(self, severity: str, description: str, resolved: bool) -> None:
        self.severity = severity
        self.description = description
        self.resolved = resolved

@pytest.fixture
def mock_orchestrator() -> MagicMock:
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry
    return orchestrator

def test_kpi_collector() -> None:
    collector = KPICollector()
    overview = MockOverview(0.9, 15)
    states = [MockState(0.4), MockState(0.6)]
    incidents = [
        MockIncident("high", "Crowd density high at gate A", False),
        MockIncident("critical", "Power grid fail", False),
        MockIncident("low", "Resolved spill", True),
    ]

    kpis = collector.collect(overview, states, incidents)
    assert kpis["stadium_health_pct"] == 90.0
    assert kpis["active_incidents_count"] == 2
    assert kpis["critical_incidents_count"] == 2
    assert kpis["average_crowd_density_pct"] == 50.0
    assert kpis["allocated_volunteers_count"] == 15

def test_exporters() -> None:
    report = BriefingReport(
        confidence_score=0.98,
        rationale="Completed compilation.",
        executive_summary="Brief summary",
        key_metrics={"stadium_health_pct": 95.0},
        operational_highlights=["All clear"],
        major_incidents=["Gate 1 congestion"],
        ai_recommendations=["Deploy 2 volunteers"],
        risk_assessment="Low risk",
        suggested_next_actions=["Deploy teams"],
    )

    # Markdown Exporter
    md_exporter = MarkdownExporter()
    md_content = md_exporter.export(report)
    assert "# Executive Briefing Report" in md_content
    assert "## 1. Executive Summary" in md_content
    assert "Brief summary" in md_content
    assert "* **Stadium Health Pct**: 95.0" in md_content
    assert "* All clear" in md_content
    assert "* Gate 1 congestion" in md_content
    assert "* Deploy 2 volunteers" in md_content
    assert "Low risk" in md_content
    assert "* Deploy teams" in md_content

    # PDF Exporter
    pdf_exporter = PDFExporter()
    pdf_content = pdf_exporter.export(report)
    assert pdf_content.startswith(b"%PDF-1.4\n%...\n")
    assert b"Brief summary" in pdf_content

@pytest.mark.asyncio
async def test_briefing_generator(mock_orchestrator: MagicMock) -> None:
    expected_report = BriefingReport(
        confidence_score=0.95,
        rationale="Briefing computed.",
        executive_summary="Summary text",
        key_metrics={"ai_custom_metric": 42},
        operational_highlights=["Highlights"],
        major_incidents=["Incident"],
        ai_recommendations=["Recs"],
        risk_assessment="Low",
        suggested_next_actions=["Next"],
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_report)

    generator = BriefingGenerator(mock_orchestrator)
    registered_prompt = mock_orchestrator.registry.get("executive_briefing_agent", "latest")
    assert "You are the ATLAS Stadium Operations Executive Briefing AI Agent." in registered_prompt.template

    overview = MockOverview(0.95, 12)
    states = [MockState(0.3)]
    incidents = [MockIncident("critical", "Fires detected", False)]

    # Act
    report = await generator.generate_briefing(
        briefing_type=BriefingType.MATCH_OPS,
        overview=overview,
        states=states,
        incidents=incidents,
    )

    # Assert
    assert report.confidence_score == 0.95
    assert report.key_metrics["stadium_health_pct"] == 95.0
    assert report.key_metrics["active_incidents_count"] == 1
    assert report.key_metrics["ai_custom_metric"] == 42
    mock_orchestrator.execute.assert_called_once()
