import json
from typing import Any

from app.intelligence import AIOrchestrator
from app.intelligence.briefings.kpi_collector import KPICollector
from app.intelligence.briefings.models import BriefingReport
from app.intelligence.briefings.prompts import ExecutiveBriefingPrompt


class BriefingGenerator:
    """ATLAS AI Executive Briefing Generator facade orchestrating telemetry aggregation and cognitive generation."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.kpi_collector = KPICollector()
        self.prompt_definition = ExecutiveBriefingPrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def generate_briefing(
        self,
        briefing_type: str,
        overview: Any,
        states: list[Any],
        incidents: list[Any],
    ) -> BriefingReport:
        """Collects metrics, formats incident context logs, and executes briefing AI agent."""
        # 1. Collect KPIs
        kpis = self.kpi_collector.collect(overview, states, incidents)

        # 2. Serialize context parameters
        kpis_str = json.dumps(kpis, indent=2)
        
        incident_list = []
        for inc in incidents:
            desc = getattr(inc, "description", "")
            resolved = getattr(inc, "resolved", False)
            severity = getattr(inc, "severity", "medium")
            severity_val = getattr(severity, "value", str(severity))
            incident_list.append(f"[{severity_val.upper()}] {desc} (Resolved: {resolved})")
        incidents_str = "\n".join(incident_list) if incident_list else "No incidents reported."

        # 3. Call AI Orchestrator
        report = await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=BriefingReport,
            briefing_type=briefing_type,
            kpis=kpis_str,
            incidents=incidents_str,
            context="",
            min_confidence=0.0,
        )

        # Ensure metrics returned inside structured report incorporates our collected KPIs
        report.key_metrics = {**kpis, **report.key_metrics}
        
        return report
