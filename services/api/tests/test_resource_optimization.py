import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.intelligence import AIOrchestrator, PromptRegistry
from app.intelligence.resource_optimization import (
    ResourceOptimizationResult,
    AllocationPlan,
    VolunteerAllocator,
    SecurityAllocator,
    MedicalAllocator,
    GateOptimizer,
    QueueBalancer,
    ResourceOptimizationEngine,
)

# Simulated domain objects for testing
class MockState:
    def __init__(self, zone_id: str, density: float, queue: int) -> None:
        self.zone_id = zone_id
        self.density = density
        self.queue_waiting_minutes = queue

class MockIncident:
    def __init__(self, severity: str, description: str, resolved: bool, zone_id: str, incident_type: str) -> None:
        self.severity = severity
        self.description = description
        self.resolved = resolved
        self.zone_id = zone_id
        self.incident_type = incident_type

@pytest.fixture
def mock_orchestrator() -> MagicMock:
    registry = PromptRegistry()
    orchestrator = MagicMock(spec=AIOrchestrator)
    orchestrator.registry = registry
    return orchestrator

def test_volunteer_allocator() -> None:
    allocator = VolunteerAllocator()
    zones = [{"zone_id": "zone-1", "density": 0.85}, {"zone_id": "zone-2", "density": 0.3}]
    incidents = [{"zone_id": "zone-1", "resolved": False}]
    
    allocs = allocator.allocate(zones, incidents)
    assert allocs["zone-1"] == 11 # 3 base + 6 (density > 0.8) + 2 (incidents)
    assert allocs["zone-2"] == 3

def test_security_allocator() -> None:
    allocator = SecurityAllocator()
    zones = [{"zone_id": "zone-1", "density": 0.85}]
    incidents = [{"zone_id": "zone-1", "incident_type": "security", "resolved": False}]

    allocs = allocator.allocate(zones, incidents)
    assert allocs["zone-1"] == 7 # 2 base + 3 (density > 0.8) + 2 (incidents)

def test_medical_allocator() -> None:
    allocator = MedicalAllocator()
    zones = [{"zone_id": "zone-1"}]
    incidents = [{"zone_id": "zone-1", "incident_type": "medical", "resolved": False}]

    allocs = allocator.allocate(zones, incidents)
    assert allocs["zone-1"] == 3 # 1 base + 2 (incidents)

def test_gate_optimizer() -> None:
    optimizer = GateOptimizer()
    zones = [{"zone_id": "zone-1", "density": 0.85}, {"zone_id": "zone-2", "density": 0.3}]
    active = optimizer.optimize_gates(zones)
    assert len(active) == 1
    assert active[0] == "zone-1"

def test_queue_balancer() -> None:
    balancer = QueueBalancer()
    zones = [{"zone_id": "zone-1", "density": 0.85}, {"zone_id": "zone-2", "density": 0.3}]
    rules = balancer.balance_queues(zones)
    assert rules["zone-1"] == "REDIRECT_TO_CORRIDOR_B"
    assert rules["zone-2"] == "KEEP_FORWARD"

@pytest.mark.asyncio
async def test_resource_optimization_engine(mock_orchestrator: MagicMock) -> None:
    expected_response = ResourceOptimizationResult(
        confidence_score=0.98,
        rationale="Completed allocation plan.",
        allocation_plan=AllocationPlan(
            volunteer_allocations={},
            security_allocations={},
            medical_allocations={},
            active_gates=[],
            crowd_flow_directions={},
        ),
        expected_improvement="Wait time decreased",
        confidence=0.95,
        trade_offs=["Cost increase"],
    )
    mock_orchestrator.execute = AsyncMock(return_value=expected_response)

    engine = ResourceOptimizationEngine(mock_orchestrator)
    
    # Assert registry
    registered_prompt = mock_orchestrator.registry.get("resource_optimization_agent", "latest")
    assert "You are the ATLAS Stadium Operations Resource Optimization AI Agent." in registered_prompt.template

    zone_id = str(uuid4())
    states = [MockState(zone_id, 0.85, 20)]
    incidents = [MockIncident("critical", "Gate failure", False, zone_id, "security")]
    recommendations = []

    # Act
    optimization = await engine.optimize(None, states, incidents, recommendations)

    # Assert
    assert optimization.expected_improvement == "Wait time decreased"
    assert optimization.allocation_plan.volunteer_allocations[zone_id] == 11
    assert optimization.allocation_plan.security_allocations[zone_id] == 7
    assert optimization.allocation_plan.medical_allocations[zone_id] == 1
    mock_orchestrator.execute.assert_called_once()
