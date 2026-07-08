from datetime import datetime, UTC
from app.application.operational_state.state_manager import OperationalStateManager
from app.application.recommendations.engine import RecommendationEngine
from app.application.scenario_simulator.models import Scenario, SimulationRecord
from app.application.scenario_simulator.validator import ScenarioValidator
from app.application.scenario_simulator.executor import ScenarioExecutor
from app.application.scenario_simulator.analyzer import ImpactAnalyzer
from app.application.scenario_simulator.history import SimulationHistory

class SimulationService:
    """Orchestrates scenario creation, state cloning, rule execution, AI analysis, and history mapping."""

    def __init__(
        self,
        state_manager: OperationalStateManager,
        impact_analyzer: ImpactAnalyzer,
        rec_engine: RecommendationEngine,
        history: SimulationHistory,
    ) -> None:
        self.state_manager = state_manager
        self.impact_analyzer = impact_analyzer
        self.rec_engine = rec_engine
        self.history = history
        self.validator = ScenarioValidator()
        self.executor = ScenarioExecutor()

    async def run_simulation(self, scenario: Scenario) -> SimulationRecord:
        """Executes a hypothetical scenario against a read-only state snapshot, returning a SimulationRecord."""
        # 1. Validate scenario config
        self.validator.validate(scenario)

        # 2. Get current real Operational State (never modify it!)
        real_snapshot = await self.state_manager.get_snapshot()

        # 3. Simulate direct effects on immutable clone
        cloned_state, direct_effects = self.executor.execute(real_snapshot, scenario)

        # 4. Generate recommendations on simulated metrics
        avg_density = sum(cloned_state.crowd_conditions.values()) / max(1, len(cloned_state.crowd_conditions))
        avg_queue = sum(cloned_state.queue_information.values()) / max(1, len(cloned_state.queue_information))
        
        simulated_recs = self.rec_engine.generate(
            crowd_density=avg_density,
            incident_severity=scenario.severity,
            queue_length=int(avg_queue),
            volunteer_availability=len(cloned_state.volunteer_allocation),
            stadium_capacity=50000,
        )
        
        # Add generated recommendation details to direct effects
        direct_effects["simulated_recommendations"] = [
            {"action_type": rec.action_type.value, "priority": rec.priority.value, "details": rec.details}
            for rec in simulated_recs
        ]

        # 5. Call AI Orchestrator to analyze secondary impacts
        report = await self.impact_analyzer.analyze(scenario, cloned_state, direct_effects)

        # 6. Save to history log
        record = SimulationRecord(
            scenario=scenario,
            timestamp=datetime.now(UTC),
            report=report,
            direct_effects=direct_effects,
        )
        self.history.add(record)

        return record
