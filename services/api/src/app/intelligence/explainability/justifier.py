from typing import Any

from app.intelligence import AIOrchestrator
from app.intelligence.explainability.alternative_generator import AlternativeGenerator
from app.intelligence.explainability.confidence_analyzer import ConfidenceAnalyzer
from app.intelligence.explainability.evidence_collector import EvidenceCollector
from app.intelligence.explainability.models import RecommendationExplanation
from app.intelligence.explainability.prompts import ExplainabilityPrompt
from app.intelligence.explainability.reasoning_builder import ReasoningBuilder


class RecommendationJustifier:
    """Pre-compiles metrics and generates structured parameters for recommendation explanations."""

    def __init__(self) -> None:
        self.evidence_collector = EvidenceCollector()
        self.confidence_analyzer = ConfidenceAnalyzer()
        self.reasoning_builder = ReasoningBuilder()
        self.alternative_generator = AlternativeGenerator()

    def compile_context(
        self,
        recommendation: Any,
        overview: Any,
        state: Any,
        incidents: list[Any]
    ) -> dict[str, Any]:
        """Gathers operational states and processes metrics into structured context variables."""
        evidence = self.evidence_collector.collect(overview, state, incidents)
        
        density = getattr(state, "density", 0.0)
        density_val = getattr(density, "value", float(density)) if hasattr(density, "value") else float(density or 0)
        volunteers = getattr(overview, "allocated_volunteers_count", 0) if overview else 0
        active_incidents = len([i for i in incidents if not getattr(i, "resolved", False)])

        confidence = self.confidence_analyzer.calculate(density_val, volunteers, active_incidents)
        rules = self.reasoning_builder.build_business_rules(
            density_val,
            getattr(state, "queue_waiting_minutes", 0) if state else 0
        )
        alternatives = self.alternative_generator.generate(
            getattr(recommendation, "action_type", "Mitigation")
        )

        return {
            "evidence": evidence,
            "confidence": confidence,
            "rules": rules,
            "alternatives": alternatives,
        }

class ExplainabilityEngine:
    """Main facade class orchestrating explainability prompts and calling the AI Orchestrator."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.justifier = RecommendationJustifier()
        self.prompt_definition = ExplainabilityPrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def explain(
        self,
        recommendation: Any,
        overview: Any,
        state: Any,
        incidents: list[Any]
    ) -> RecommendationExplanation:
        """Compiles background variables and runs the AI Agent to build a concise operational justification."""
        context_vars = self.justifier.compile_context(
            recommendation=recommendation,
            overview=overview,
            state=state,
            incidents=incidents
        )

        action = getattr(recommendation, "details", str(recommendation))
        priority = getattr(recommendation, "priority", "medium")
        priority_val = getattr(priority, "value", str(priority))

        # Call AI Orchestrator
        report = await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=RecommendationExplanation,
            action=action,
            priority=priority_val,
            evidence="\n".join(context_vars["evidence"]),
            operational_data=f"Density: {getattr(state, 'density', 0.0)}. Queue: {getattr(state, 'queue_waiting_minutes', 0)}m.",
            context="",
            min_confidence=0.0,
        )

        # Enforce pre-calculated confidence score and rules onto output schema
        report.confidence = context_vars["confidence"]
        report.business_rules_triggered = list(set(report.business_rules_triggered + context_vars["rules"]))
        report.alternative_actions = list(set(report.alternative_actions + context_vars["alternatives"]))

        return report
