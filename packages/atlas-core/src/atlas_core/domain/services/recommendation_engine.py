import json
from datetime import datetime, UTC
from uuid import UUID, uuid4
from typing import List, Dict, Any

from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore

class StadiumRecommendationEngine:
    """Generates deterministic logistics, crowd rerouting, and safety recommendations based on digital twin states."""

    @staticmethod
    def generate_recommendations(
        stadium: Stadium,
        active_incidents: List[Incident],
        incident_zones: Dict[UUID, UUID]
    ) -> List[Recommendation]:
        """Analyzes active incidents, wait times, and crowd densities to produce PENDING recommendations."""
        recommendations: List[Recommendation] = []

        # Map incident list to find ones that need action
        node_map = {n.id: n for n in stadium.nodes}
        active_incident_nodes = {incident_zones.get(i.id) for i in active_incidents if not i.resolved}

        # 1. Check active incidents and issue emergency responses
        for incident in active_incidents:
            if incident.resolved:
                continue

            zone_uuid = incident_zones.get(incident.id)
            if not zone_uuid or zone_uuid not in node_map:
                continue

            target_node = node_map[zone_uuid]

            if incident.incident_type.value == "medical":
                details_dict = {
                    "expected_impact": "Stabilize patient and clear corridor access",
                    "eta_minutes": 5,
                    "required_personnel": "2 EMT responders",
                    "required_resources": "Trauma kit and emergency stretcher",
                    "trigger_reason": f"Active medical incident reported at {target_node.name}",
                    "explanation": f"Deploy immediate medical first aid response to {target_node.name}.",
                    "why": f"Active medical incident requiring first-aid intervention has occurred at {target_node.name}.",
                    "evidence": f"Incident log specifies type: medical, severity: {incident.severity.value}.",
                    "operational_data_used": ["incident_type", "severity", "zone_id"],
                    "alternative_actions": ["Reroute nearby patrol with minor first aid kit", "Direct spectator to nearest fixed medical post"],
                    "trade_offs": "Direct response team deployment temporarily reduces active staff availability at base alpha."
                }
                rec = Recommendation(
                    action_type="Deploy Medical Response Team",
                    priority=Severity.CRITICAL if incident.severity == Severity.CRITICAL else Severity.HIGH,
                    confidence=ConfidenceScore(value=0.98),
                    details=json.dumps(details_dict)
                )
                recommendations.append(rec)

            elif incident.incident_type.value == "security":
                details_dict = {
                    "expected_impact": "Contain threat and secure area boundaries",
                    "eta_minutes": 8,
                    "required_personnel": "4 security officers",
                    "required_resources": "Crowd barriers and radio comms",
                    "trigger_reason": f"Active security incident reported at {target_node.name}",
                    "explanation": f"Dispatch localized security patrol to contain incident at {target_node.name}.",
                    "why": f"Active security breach or disturbance at {target_node.name} requires physical containment.",
                    "evidence": f"Incident log flags type: security, severity: {incident.severity.value}.",
                    "operational_data_used": ["incident_type", "severity", "zone_id"],
                    "alternative_actions": ["Reroute concourse supervisor patrol", "Activate stationary sector security stewards"],
                    "trade_offs": "Concentrating security responders at target node increases response times in adjacent stands."
                }
                rec = Recommendation(
                    action_type="Deploy Security Patrol",
                    priority=Severity.CRITICAL if incident.severity == Severity.CRITICAL else Severity.HIGH,
                    confidence=ConfidenceScore(value=0.95),
                    details=json.dumps(details_dict)
                )
                recommendations.append(rec)

            elif incident.incident_type.value == "fire":
                details_dict = {
                    "expected_impact": "Extinguish local fire and clear sector vomitories",
                    "eta_minutes": 6,
                    "required_personnel": "6 safety officers",
                    "required_resources": "Fire extinguishers and thermal sensor cameras",
                    "trigger_reason": f"Active fire outbreak reported at {target_node.name}",
                    "explanation": f"Initiate fire containment protocols and clear exit path corridors at {target_node.name}.",
                    "why": f"Active thermal outbreak at {target_node.name} poses immediate safety risks to stand spectators.",
                    "evidence": f"Sensors and manual dispatch logs indicate active smoke/fire in zone: {target_node.name}.",
                    "operational_data_used": ["incident_type", "severity", "zone_id"],
                    "alternative_actions": ["Localised sector evacuation to outer plaza", "Manual fire warden suppression deployment"],
                    "trade_offs": "Evacuating zone sectors creates temporary concourse ingress congestion at nearby gates."
                }
                rec = Recommendation(
                    action_type="Evacuate Stand Sector",
                    priority=Severity.CRITICAL,
                    confidence=ConfidenceScore(value=0.99),
                    details=json.dumps(details_dict)
                )
                recommendations.append(rec)

        # 2. Check turnstile queue chokes
        for node in stadium.nodes:
            wait_time = node.operational_state.queue_estimate.waiting_minutes
            if wait_time >= 15:
                # Check if we already recommended something for this node
                details_dict = {
                    "expected_impact": "Reduce ticket validation bottlenecks and drop queue times by 8 minutes",
                    "eta_minutes": 10,
                    "required_personnel": "6 volunteers",
                    "required_resources": "Mobile hand-held validation terminals",
                    "trigger_reason": f"Turnstile queue wait time is {wait_time} minutes at {node.name}",
                    "explanation": f"Deploy auxiliary stewards to assist with ticket pre-checks at {node.name}.",
                    "why": f"Wait queue times at {node.name} have exceeded the maximum target threshold of 10 minutes.",
                    "evidence": f"Telemetry indicates wait_time: {wait_time} minutes, exceeds 15 minute action line.",
                    "operational_data_used": ["queue_waiting_minutes", "allocated_volunteers_count"],
                    "alternative_actions": ["Redirect arriving spectators to adjacent lower-load ingress gates", "Switch to manual backup barcode scanner list checks"],
                    "trade_offs": "Reassigning volunteers to ticket gates reduces general information booth assistance personnel."
                }
                rec = Recommendation(
                    action_type="Reroute Volunteers to Ingress Queue",
                    priority=Severity.HIGH if wait_time < 25 else Severity.CRITICAL,
                    confidence=ConfidenceScore(value=0.95),
                    details=json.dumps(details_dict)
                )
                recommendations.append(rec)

        # 3. Check concourse overcrowding densities
        for node in stadium.nodes:
            density = node.operational_state.density.value
            if density >= 0.80 and node.id not in active_incident_nodes:
                details_dict = {
                    "expected_impact": "Clear pedestrian corridors and restore walking velocity to normal",
                    "eta_minutes": 15,
                    "required_personnel": "4 crowd marshals",
                    "required_resources": "Digital signage path redirection",
                    "trigger_reason": f"Crowd density ratio is {density * 100:.1f}% at {node.name}",
                    "explanation": f"Redirect pedestrian corridor flow away from saturated sectors around {node.name}.",
                    "why": f"Crowd density at {node.name} has breached the warning comfort threshold of 80%.",
                    "evidence": f"Telemetry reports crowd density value: {density * 100:.1f}%.",
                    "operational_data_used": ["density_value", "zone_id"],
                    "alternative_actions": ["Deploy physical rope gates to guide spectator queues", "Restrict new entries to outer concourse areas"],
                    "trade_offs": "Diverting path routes increases walking times for spectator ingress to high stands."
                }
                rec = Recommendation(
                    action_type="Redirect Pedestrian Corridor Flow",
                    priority=Severity.MEDIUM,
                    confidence=ConfidenceScore(value=0.90),
                    details=json.dumps(details_dict)
                )
                recommendations.append(rec)

        return recommendations
