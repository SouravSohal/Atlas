from datetime import UTC, datetime
from typing import Any

from app.application.operational_state.snapshot import OperationalSnapshot
from app.application.scenario_simulator.models import Scenario


class ScenarioExecutor:
    """Simulates the direct, deterministic physical changes of a scenario on a cloned operational snapshot."""

    def execute(self, snapshot: OperationalSnapshot, scenario: Scenario) -> tuple[OperationalSnapshot, dict[str, Any]]:
        """Simulates the scenario on an immutable snapshot, returning the updated snapshot and direct effects dictionary."""
        # Deep clone maps to avoid mutation of parent snapshot
        crowd_conditions = dict(snapshot.crowd_conditions)
        queue_information = dict(snapshot.queue_information)
        volunteer_allocation = dict(snapshot.volunteer_allocation)
        active_incidents = list(snapshot.active_incidents)

        effects: dict[str, Any] = {}
        stype = scenario.scenario_type
        zone = scenario.zone_id

        # Dispatch to specific scenario simulator helpers
        self._apply_scenario_effects(
            stype=stype,
            zone=zone,
            scenario_id=scenario.id,
            crowd_conditions=crowd_conditions,
            queue_information=queue_information,
            active_incidents=active_incidents,
            effects=effects
        )

        # Recalculate stadium health based on new simulated values
        health = self._calculate_simulated_health(active_incidents, crowd_conditions, queue_information)

        cloned_snapshot = OperationalSnapshot(
            active_incidents=active_incidents,
            crowd_conditions=crowd_conditions,
            recommendations=list(snapshot.recommendations),
            volunteer_allocation=volunteer_allocation,
            queue_information=queue_information,
            stadium_health=health,
            timestamp=datetime.now(UTC),
        )

        return cloned_snapshot, effects

    def _apply_scenario_effects(
        self,
        stype: str,
        zone: Any,
        scenario_id: Any,
        crowd_conditions: dict[Any, float],
        queue_information: dict[Any, int],
        active_incidents: list[Any],
        effects: dict[str, Any]
    ) -> None:
        """Dispatches simulation handler based on scenario type."""
        handlers = {
            "Gate Closure": lambda: self._simulate_gate_closure(zone, crowd_conditions, queue_information, effects),
            "Crowd Surge": lambda: self._simulate_crowd_surge(zone, crowd_conditions, queue_information, effects),
            "Medical Emergency": lambda: self._simulate_medical_emergency(zone, active_incidents, queue_information, scenario_id, effects),
            "Heavy Rain": lambda: self._simulate_heavy_rain(crowd_conditions, queue_information, effects),
            "Public Transport Delay": lambda: self._simulate_transport_delay(crowd_conditions, effects),
            "Power Failure": lambda: self._simulate_power_failure(queue_information, effects),
            "VIP Arrival": lambda: self._simulate_vip_arrival(zone, queue_information, effects),
            "Security Incident": lambda: self._simulate_security_incident(crowd_conditions, active_incidents, scenario_id, effects),
            "Lost Child": lambda: self._simulate_lost_child(zone, queue_information, effects),
            "Evacuation": lambda: self._simulate_evacuation(crowd_conditions, queue_information, effects),
        }
        if stype in handlers:
            handlers[stype]()

    def _simulate_gate_closure(
        self, zone: Any, crowd_conditions: dict[Any, float], queue_information: dict[Any, int], effects: dict[str, Any]
    ) -> None:
        effects["action"] = f"Closure of gate/zone {zone}"
        if zone in crowd_conditions:
            crowd_conditions[zone] = 0.0
            queue_information[zone] = 0
            effects["rerouted_surge"] = "Density redirected to adjacent sectors."
            for z in crowd_conditions:
                if z != zone:
                    crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.15)
                    queue_information[z] = queue_information[z] + 5

    def _simulate_crowd_surge(
        self, zone: Any, crowd_conditions: dict[Any, float], queue_information: dict[Any, int], effects: dict[str, Any]
    ) -> None:
        effects["action"] = "Surge in spectator ingress rates"
        if zone and zone in crowd_conditions:
            crowd_conditions[zone] = min(1.0, crowd_conditions[zone] + 0.35)
            queue_information[zone] = queue_information[zone] + 12
        else:
            for z in crowd_conditions:
                crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.20)
                queue_information[z] = queue_information[z] + 8

    def _simulate_medical_emergency(
        self, zone: Any, active_incidents: list[Any], queue_information: dict[Any, int], scenario_id: Any, effects: dict[str, Any]
    ) -> None:
        effects["action"] = "Registered high-priority medical incident"
        active_incidents.append(scenario_id)
        if zone in queue_information:
            queue_information[zone] = queue_information[zone] + 4

    def _simulate_heavy_rain(
        self, crowd_conditions: dict[Any, float], queue_information: dict[Any, int], effects: dict[str, Any]
    ) -> None:
        effects["action"] = "Severe weather condition initiated"
        for z in crowd_conditions:
            crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.10)
            queue_information[z] = queue_information[z] + 10

    def _simulate_transport_delay(self, crowd_conditions: dict[Any, float], effects: dict[str, Any]) -> None:
        effects["action"] = "Subway/bus connection delays"
        for z in crowd_conditions:
            crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.15)

    def _simulate_power_failure(self, queue_information: dict[Any, int], effects: dict[str, Any]) -> None:
        effects["action"] = "Grid blackout reported"
        for z in queue_information:
            queue_information[z] = queue_information[z] + 25

    def _simulate_vip_arrival(self, zone: Any, queue_information: dict[Any, int], effects: dict[str, Any]) -> None:
        effects["action"] = "Secured escort transport corridor active"
        if zone in queue_information:
            queue_information[zone] = queue_information[zone] + 8

    def _simulate_security_incident(
        self, crowd_conditions: dict[Any, float], active_incidents: list[Any], scenario_id: Any, effects: dict[str, Any]
    ) -> None:
        effects["action"] = "Active threat report"
        active_incidents.append(scenario_id)
        for z in crowd_conditions:
            crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.05)

    def _simulate_lost_child(self, zone: Any, queue_information: dict[Any, int], effects: dict[str, Any]) -> None:
        effects["action"] = "Search and containment protocols active"
        if zone in queue_information:
            queue_information[zone] = queue_information[zone] + 5

    def _simulate_evacuation(
        self, crowd_conditions: dict[Any, float], queue_information: dict[Any, int], effects: dict[str, Any]
    ) -> None:
        effects["action"] = "Initiating stadium evacuation protocol"
        for z in crowd_conditions:
            crowd_conditions[z] = 0.95
            queue_information[z] = 99

    def _calculate_simulated_health(
        self, active_incidents: list[Any], crowd_conditions: dict[Any, float], queue_information: dict[Any, int]
    ) -> float:
        """Recalculates stadium health based on new simulated values."""
        health = 1.0
        health -= len(active_incidents) * 0.15
        for density in crowd_conditions.values():
            if density > 0.8:
                health -= 0.10
        for wait_mins in queue_information.values():
            if wait_mins > 20:
                health -= 0.05
        return max(0.0, min(1.0, health))
