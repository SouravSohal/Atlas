import json
from typing import Any

from app.intelligence import AIOrchestrator
from app.intelligence.predictive.arrival import ArrivalPredictor
from app.intelligence.predictive.congestion import CongestionPredictor
from app.intelligence.predictive.demand import VolunteerDemandPredictor
from app.intelligence.predictive.exit import ExitPredictor
from app.intelligence.predictive.models import PredictionResult
from app.intelligence.predictive.prompts import PredictiveIntelligencePrompt
from app.intelligence.predictive.queue import QueuePredictor
from app.intelligence.predictive.risk import RiskPredictor


class PredictiveIntelligenceEngine:
    """Main facade orchestrating deterministic forecasting rules and cognitive explanations."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.congestion_predictor = CongestionPredictor()
        self.queue_predictor = QueuePredictor()
        self.volunteer_demand_predictor = VolunteerDemandPredictor()
        self.risk_predictor = RiskPredictor()
        self.arrival_predictor = ArrivalPredictor()
        self.exit_predictor = ExitPredictor()
        self.prompt_definition = PredictiveIntelligencePrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def predict(
        self,
        overview: Any,
        states: list[Any],
        incidents: list[Any],
        recommendations: list[Any]
    ) -> PredictionResult:
        """Calculates rules-based forecasting metrics and explains trends using the AI Orchestrator."""
        predicted_density = {}
        predicted_queues = {}
        incident_probs = {}
        volunteer_demands = {}
        gate_utilizations = {}

        volunteers = getattr(overview, "allocated_volunteers_count", 0) if overview else 0
        active_incidents = [i for i in incidents if not getattr(i, "resolved", False)]

        for state in states:
            zone_id = str(getattr(state, "zone_id", ""))
            if not zone_id:
                continue

            density = getattr(state, "density", 0.0)
            density_val = getattr(density, "value", float(density)) if hasattr(density, "value") else float(density or 0)
            queue = getattr(state, "queue_waiting_minutes", 0)

            # 1. Congestion
            zone_incidents = [i for i in active_incidents if getattr(i, "zone_id", None) == zone_id]
            pred_dens = self.congestion_predictor.predict(density_val, True, len(zone_incidents) > 0)
            predicted_density[zone_id] = pred_dens

            # 2. Queue Length
            pred_q = self.queue_predictor.predict(queue, density_val, volunteers)
            predicted_queues[zone_id] = pred_q

            # 3. Incident Probability
            pred_risk = self.risk_predictor.predict(density_val, len(zone_incidents))
            incident_probs[zone_id] = pred_risk

            # 4. Volunteer Demand
            pred_dem = self.volunteer_demand_predictor.predict(density_val, len(zone_incidents))
            volunteer_demands[zone_id] = pred_dem

            # 5. Gate Utilization
            pred_gate = self.arrival_predictor.predict_gate_utilization(density_val, 45)
            gate_utilizations[zone_id] = pred_gate

        # Call AI Orchestrator to generate explainability narrative
        report = await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=PredictionResult,
            predicted_density=json.dumps(predicted_density),
            predicted_queues=json.dumps(predicted_queues),
            incident_probs=json.dumps(incident_probs),
            volunteer_demands=json.dumps(volunteer_demands),
            gate_utilizations=json.dumps(gate_utilizations),
            context="",
            min_confidence=0.0,
        )

        # Enforce the pre-calculated deterministic values on the final response
        report.predicted_crowd_density = predicted_density
        report.predicted_queue_length = predicted_queues
        report.incident_probability = incident_probs
        report.volunteer_demand = volunteer_demands
        report.gate_utilization = gate_utilizations

        return report
