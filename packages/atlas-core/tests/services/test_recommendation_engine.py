import pytest
import json
from datetime import datetime, UTC
from uuid import uuid4

from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.entities.operational_state import OperationalState
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.value_objects.crowd_density import CrowdDensity
from atlas_core.domain.value_objects.queue_estimate import QueueEstimate
from atlas_core.domain.value_objects.coordinates import Coordinates
from atlas_core.domain.enums.incident_type import IncidentType
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.services.recommendation_engine import StadiumRecommendationEngine

def test_stadium_recommendation_engine_generation():
    # 1. Setup Stadium & Nodes
    stadium = Stadium(name="Aurelia Arena", capacity=65000)
    
    n0_id = uuid4()
    n0_state = OperationalState(
        zone_id=n0_id,
        density=CrowdDensity(value=0.45),
        queue_estimate=QueueEstimate(waiting_minutes=20),  # Wait > 15m (triggers queue rule)
        last_updated=datetime.now(UTC)
    )
    node_0 = StadiumNode(
        id=n0_id,
        name="Gate A Ingress",
        category="Entrance Gate",
        capacity=15000,
        operational_state=n0_state
    )

    n1_id = uuid4()
    n1_state = OperationalState(
        zone_id=n1_id,
        density=CrowdDensity(value=0.85),  # Density > 80% (triggers density rule)
        queue_estimate=QueueEstimate(waiting_minutes=2),
        last_updated=datetime.now(UTC)
    )
    node_1 = StadiumNode(
        id=n1_id,
        name="Central Food Plaza",
        category="Food Court",
        capacity=3000,
        operational_state=n1_state
    )

    stadium.add_node(node_0)
    stadium.add_node(node_1)

    # 2. Setup active medical incident
    incident = Incident(
        id=uuid4(),
        incident_type=IncidentType.MEDICAL,
        severity=Severity.CRITICAL,
        description="Heat exhaustion collapse in corridor",
        location=Coordinates(latitude=0.0, longitude=0.0),
        reporter_id=uuid4()
    )

    active_incidents = [incident]
    incident_zones = {incident.id: n1_id}

    # 3. Generate recommendations
    recs = StadiumRecommendationEngine.generate_recommendations(stadium, active_incidents, incident_zones)

    # We expect:
    # 1. A medical team dispatch recommendation (critical severity)
    # 2. A volunteer queue rerouting recommendation (due to Gate A wait time = 20m)
    # Note: Central Food Plaza has density = 0.85, but since it has an active incident,
    # the density recommendation is skipped to prevent rule overlap.
    assert len(recs) == 2

    # Verify medical recommendation
    med_rec = next((r for r in recs if "Medical" in r.action_type), None)
    assert med_rec is not None
    assert med_rec.priority == Severity.CRITICAL
    assert med_rec.confidence.value == 0.98
    
    med_details = json.loads(med_rec.details)
    assert med_details["eta_minutes"] == 5
    assert med_details["required_personnel"] == "2 EMT responders"
    assert med_details["required_resources"] == "Trauma kit and emergency stretcher"

    # Verify queue recommendation
    queue_rec = next((r for r in recs if "Volunteers" in r.action_type), None)
    assert queue_rec is not None
    assert queue_rec.priority == Severity.HIGH
    assert queue_rec.confidence.value == 0.95
    
    queue_details = json.loads(queue_rec.details)
    assert queue_details["eta_minutes"] == 10
    assert queue_details["required_personnel"] == "6 volunteers"
    assert "Gate A Ingress" in queue_details["trigger_reason"]
