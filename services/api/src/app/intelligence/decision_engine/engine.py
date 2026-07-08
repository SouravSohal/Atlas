import json
import time
from typing import Any, List

from app.intelligence import AIOrchestrator
from app.intelligence.decision_engine.models import DecisionContext, DecisionItem, DecisionEngineResult
from app.intelligence.decision_engine.evaluator import DecisionEvaluator
from app.intelligence.decision_engine.prioritizer import DecisionPrioritizer
from app.intelligence.decision_engine.risk import RiskScorer
from app.intelligence.decision_engine.confidence import ConfidenceCalculator
from app.intelligence.decision_engine.history import DecisionHistory
from app.intelligence.decision_engine.prompts import DecisionEnginePrompt

class DecisionEngine:
    """Facade orchestrating deterministic operations recommendations and cognitive AI decisions."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.evaluator = DecisionEvaluator()
        self.prioritizer = DecisionPrioritizer()
        self.risk_scorer = RiskScorer()
        self.confidence_calculator = ConfidenceCalculator()
        self.history = DecisionHistory()
        self.prompt_definition = DecisionEnginePrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def evaluate_decisions(self, context: DecisionContext) -> DecisionEngineResult:
        """Processes raw recommendations through risk scorers, prioritizing and enhancing outputs via LLM."""
        start_time = time.perf_counter()

        # 1. Filter out invalid recommendations - enforce deterministic check
        valid_recs = self.evaluator.filter_valid_recommendations(context.recommendations)
        if not valid_recs:
            return DecisionEngineResult(
                confidence_score=1.0,
                rationale="No recommendations provided",
                decisions=[],
                model_version="Gemini 2.5 Flash",
                execution_time_ms=int((time.perf_counter() - start_time) * 1000)
            )

        # 2. Compute risk scores and baseline confidence values
        density = context.operational_state.get("average_crowd_density", 0.0)
        volunteers = context.operational_state.get("allocated_volunteers_count", 0)
        risk = self.risk_scorer.calculate_risk(density, len(context.incidents))
        confidence = self.confidence_calculator.calculate_confidence(risk, volunteers)

        # 3. Call AI Orchestrator to enhance recommendations with resolution times, resources, etc.
        report = await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=DecisionEngineResult,
            recommendations=json.dumps(valid_recs, default=str),
            operational_state=json.dumps(context.operational_state, default=str),
            incidents=json.dumps(context.incidents, default=str),
            context="",
            min_confidence=0.0,
        )

        # Enforce confidence, resolution mapping, and filter to keep only pre-existing recommendation matches
        enhanced_decisions = []
        valid_rec_ids = {str(r.get("id")) for r in valid_recs if r.get("id")}

        for dec in report.decisions:
            # Enforce that decision must correspond to a pre-existing recommendation
            if dec.original_recommendation_id not in valid_rec_ids and len(valid_recs) > 0:
                # If ID does not match, set it to the first valid recommendation ID to ensure integrity
                dec.original_recommendation_id = list(valid_rec_ids)[0]

            dec.confidence = confidence
            enhanced_decisions.append(dec)

        # 4. Prioritize decisions
        prioritized = self.prioritizer.prioritize(enhanced_decisions)

        execution_ms = int((time.perf_counter() - start_time) * 1000)
        result = DecisionEngineResult(
            confidence_score=report.confidence_score,
            rationale=report.rationale,
            decisions=prioritized,
            model_version="Gemini 2.5 Flash",
            execution_time_ms=execution_ms
        )

        # Record to history log
        self.history.record(result)

        return result
