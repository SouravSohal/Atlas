import json
from typing import Any, List

from app.intelligence import AIOrchestrator
from app.intelligence.resource_optimization.models import ResourceOptimizationResult, AllocationPlan
from app.intelligence.resource_optimization.volunteer import VolunteerAllocator
from app.intelligence.resource_optimization.security import SecurityAllocator
from app.intelligence.resource_optimization.medical import MedicalAllocator
from app.intelligence.resource_optimization.gate import GateOptimizer
from app.intelligence.resource_optimization.queue import QueueBalancer
from app.intelligence.resource_optimization.prompts import ResourceOptimizationPrompt

class ResourceOptimizationEngine:
    """Facade orchestrating rules-based resource allocations and cognitive AI justifications."""

    def __init__(self, orchestrator: AIOrchestrator) -> None:
        self.orchestrator = orchestrator
        self.volunteer_allocator = VolunteerAllocator()
        self.security_allocator = SecurityAllocator()
        self.medical_allocator = MedicalAllocator()
        self.gate_optimizer = GateOptimizer()
        self.queue_balancer = QueueBalancer()
        self.prompt_definition = ResourceOptimizationPrompt()

        # Register prompt template in the registry
        latest_version = self.prompt_definition.get_version("latest")
        self.orchestrator.registry.register(
            name=self.prompt_definition.metadata.name,
            version=latest_version.version,
            template=latest_version.template,
            description=latest_version.description,
        )

    async def optimize(
        self,
        overview: Any,
        states: List[Any],
        incidents: List[Any],
        recommendations: List[Any]
    ) -> ResourceOptimizationResult:
        """Calculates allocation metrics deterministically and justifies strategies using the AI Orchestrator."""
        # Convert state domain objects into simple dictionaries for rule allocations
        zones_payload = []
        for state in states:
            density = getattr(state, "density", 0.0)
            density_val = getattr(density, "value", float(density)) if hasattr(density, "value") else float(density or 0)
            zones_payload.append({
                "zone_id": str(getattr(state, "zone_id", "")),
                "density": density_val,
                "queue_waiting_minutes": getattr(state, "queue_waiting_minutes", 0),
            })

        incidents_payload = []
        for inc in incidents:
            severity = getattr(inc, "severity", "medium")
            severity_val = getattr(severity, "value", str(severity))
            incidents_payload.append({
                "zone_id": str(getattr(inc, "zone_id", "")),
                "incident_type": getattr(inc, "incident_type", "other"),
                "severity": severity_val,
                "resolved": getattr(inc, "resolved", False),
            })

        # 1. Deterministic Rule Allocations
        vol_allocs = self.volunteer_allocator.allocate(zones_payload, incidents_payload)
        sec_allocs = self.security_allocator.allocate(zones_payload, incidents_payload)
        med_allocs = self.medical_allocator.allocate(zones_payload, incidents_payload)
        gates = self.gate_optimizer.optimize_gates(zones_payload)
        queues = self.queue_balancer.balance_queues(zones_payload)

        # 2. Call AI Orchestrator to explain expected improvements and trade-offs
        report = await self.orchestrator.execute(
            prompt_name=self.prompt_definition.metadata.name,
            prompt_version="latest",
            context_zone_id=None,
            schema=ResourceOptimizationResult,
            volunteer_allocations=json.dumps(vol_allocs),
            security_allocations=json.dumps(sec_allocs),
            medical_allocations=json.dumps(med_allocs),
            gate_openings=json.dumps(gates),
            queue_rules=json.dumps(queues),
            context="",
            min_confidence=0.0,
        )

        # Enforce pre-calculated allocations
        report.allocation_plan = AllocationPlan(
            volunteer_allocations=vol_allocs,
            security_allocations=sec_allocs,
            medical_allocations=med_allocs,
            active_gates=gates,
            crowd_flow_directions=queues,
        )

        return report
        
