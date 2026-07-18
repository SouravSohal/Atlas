import json
from uuid import UUID

from atlas_core.domain.entities.incident import Incident
from atlas_core.domain.entities.recommendation import Recommendation
from atlas_core.domain.entities.stadium import Stadium
from atlas_core.domain.entities.stadium_node import StadiumNode
from atlas_core.domain.enums.severity import Severity
from atlas_core.domain.value_objects.confidence_score import ConfidenceScore


class StadiumRecommendationEngine:
    """Generates deterministic logistics, crowd rerouting, and safety recommendations based on digital twin states."""

    @staticmethod
    def generate_recommendations(
        stadium: Stadium,
        active_incidents: list[Incident],
        incident_zones: dict[UUID, UUID]
    ) -> list[Recommendation]:
        """Analyzes active incidents, wait times, and crowd densities to produce PENDING recommendations."""
        recommendations: list[Recommendation] = []

        node_map = {n.id: n for n in stadium.nodes}
        active_incident_nodes = {
            incident_zones[i.id]
            for i in active_incidents
            if not i.resolved and i.id in incident_zones
        }

        # 1. Check active incidents and issue emergency responses
        recommendations.extend(
            StadiumRecommendationEngine._process_active_incidents(
                active_incidents, incident_zones, node_map
            )
        )

        # 2. Check turnstile queue chokes
        recommendations.extend(
            StadiumRecommendationEngine._process_queue_chokes(stadium.nodes)
        )

        # 3. Check concourse overcrowding densities
        recommendations.extend(
            StadiumRecommendationEngine._process_overcrowding_densities(
                stadium.nodes, active_incident_nodes
            )
        )

        return recommendations

    @staticmethod
    def _process_active_incidents(
        active_incidents: list[Incident],
        incident_zones: dict[UUID, UUID],
        node_map: dict[UUID, StadiumNode]
    ) -> list[Recommendation]:
        """Iterates over active incidents and returns appropriate emergency recommendations."""
        recommendations: list[Recommendation] = []
        for incident in active_incidents:
            if incident.resolved:
                continue

            zone_uuid = incident_zones.get(incident.id)
            if not zone_uuid or zone_uuid not in node_map:
                continue

            target_node = node_map[zone_uuid]
            rec = StadiumRecommendationEngine._generate_incident_recommendation(incident, target_node)
            if rec:
                recommendations.append(rec)
        return recommendations

    @staticmethod
    def _generate_incident_recommendation(
        incident: Incident,
        target_node: StadiumNode
    ) -> Recommendation | None:
        """Determines the type of incident and generates the matching recommendation."""
        incident_type = incident.incident_type.value
        if incident_type == "medical":
            return StadiumRecommendationEngine._create_medical_recommendation(incident, target_node)
        if incident_type == "security":
            return StadiumRecommendationEngine._create_security_recommendation(incident, target_node)
        if incident_type == "fire":
            return StadiumRecommendationEngine._create_fire_recommendation(incident, target_node)
        return None

    @staticmethod
    def _create_medical_recommendation(
        incident: Incident,
        target_node: StadiumNode
    ) -> Recommendation:
        """Creates emergency dispatch recommendations for medical incidents."""
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
            "alternative_actions": [
                "Reroute nearby patrol with minor first aid kit",
                "Direct spectator to nearest fixed medical post"
            ],
            "trade_offs": "Direct response team deployment temporarily reduces active staff availability at base alpha."
        }
        return Recommendation(
            action_type="Deploy Medical Response Team",
            priority=Severity.CRITICAL if incident.severity == Severity.CRITICAL else Severity.HIGH,
            confidence=ConfidenceScore(value=0.98),
            details=json.dumps(details_dict)
        )

    @staticmethod
    def _create_security_recommendation(
        incident: Incident,
        target_node: StadiumNode
    ) -> Recommendation:
        """Creates emergency containment recommendations for security incidents."""
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
            "alternative_actions": [
                "Reroute concourse supervisor patrol",
                "Activate stationary sector security stewards"
            ],
            "trade_offs": "Concentrating security responders at target node increases response times in adjacent stands."
        }
        return Recommendation(
            action_type="Deploy Security Patrol",
            priority=Severity.CRITICAL if incident.severity == Severity.CRITICAL else Severity.HIGH,
            confidence=ConfidenceScore(value=0.95),
            details=json.dumps(details_dict)
        )

    @staticmethod
    def _create_fire_recommendation(
        incident: Incident,
        target_node: StadiumNode
    ) -> Recommendation:
        """Creates evacuation recommendations for fire incidents."""
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
            "alternative_actions": [
                "Localised sector evacuation to outer plaza",
                "Manual fire warden suppression deployment"
            ],
            "trade_offs": "Evacuating zone sectors creates temporary concourse ingress congestion at nearby gates."
        }
        return Recommendation(
            action_type="Evacuate Stand Sector",
            priority=Severity.CRITICAL,
            confidence=ConfidenceScore(value=0.99),
            details=json.dumps(details_dict)
        )

    @staticmethod
    def _process_queue_chokes(nodes: list[StadiumNode]) -> list[Recommendation]:
        """Checks turnstile queue chokes and creates queue redirection recommendations."""
        recommendations: list[Recommendation] = []
        for node in nodes:
            wait_time = node.operational_state.queue_estimate.waiting_minutes
            if wait_time >= 15:
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
                    "alternative_actions": [
                        "Redirect arriving spectators to adjacent lower-load ingress gates",
                        "Switch to manual backup barcode scanner list checks"
                    ],
                    "trade_offs": "Reassigning volunteers to ticket gates reduces general information booth assistance personnel."
                }
                rec = Recommendation(
                    action_type="Reroute Volunteers to Ingress Queue",
                    priority=Severity.HIGH if wait_time < 25 else Severity.CRITICAL,
                    confidence=ConfidenceScore(value=0.95),
                    details=json.dumps(details_dict)
                )
                recommendations.append(rec)
        return recommendations

    @staticmethod
    def _process_overcrowding_densities(
        nodes: list[StadiumNode],
        active_incident_nodes: set[UUID]
    ) -> list[Recommendation]:
        """Checks concourse overcrowding densities and creates pedestrian flow redirection recommendations."""
        recommendations: list[Recommendation] = []
        for node in nodes:
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
                    "alternative_actions": [
                        "Deploy physical rope gates to guide spectator queues",
                        "Restrict new entries to outer concourse areas"
                    ],
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
