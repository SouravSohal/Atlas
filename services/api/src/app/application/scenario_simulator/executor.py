from uuid import UUID
from datetime import datetime, UTC
from typing import Any, Tuple
from app.application.operational_state.snapshot import OperationalSnapshot
from app.application.scenario_simulator.models import Scenario

class ScenarioExecutor:
    """Simulates the direct, deterministic physical changes of a scenario on a cloned operational snapshot."""

    def execute(self, snapshot: OperationalSnapshot, scenario: Scenario) -> Tuple[OperationalSnapshot, dict[str, Any]]:
        """Simulates the scenario on an immutable snapshot, returning the updated snapshot and direct effects dictionary."""
        # Deep clone maps to avoid mutation of parent snapshot
        crowd_conditions = dict(snapshot.crowd_conditions)
        queue_information = dict(snapshot.queue_information)
        volunteer_allocation = dict(snapshot.volunteer_allocation)
        active_incidents = list(snapshot.active_incidents)

        effects: dict[str, Any] = {}
        stype = scenario.scenario_type
        zone = scenario.zone_id

        # Apply deterministic rules based on scenario type
        if stype == "Gate Closure":
            effects["action"] = f"Closure of gate/zone {zone}"
            if zone in crowd_conditions:
                crowd_conditions[zone] = 0.0
                queue_information[zone] = 0
                effects["rerouted_surge"] = "Density redirected to adjacent sectors."
                for z in crowd_conditions:
                    if z != zone:
                        crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.15)
                        queue_information[z] = queue_information[z] + 5

        elif stype == "Crowd Surge":
            effects["action"] = "Surge in spectator ingress rates"
            if zone and zone in crowd_conditions:
                crowd_conditions[zone] = min(1.0, crowd_conditions[zone] + 0.35)
                queue_information[zone] = queue_information[zone] + 12
            else:
                for z in crowd_conditions:
                    crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.20)
                    queue_information[z] = queue_information[z] + 8

        elif stype == "Medical Emergency":
            effects["action"] = "Registered high-priority medical incident"
            active_incidents.append(scenario.id)
            if zone in queue_information:
                queue_information[zone] = queue_information[zone] + 4

        elif stype == "Heavy Rain":
            effects["action"] = "Severe weather condition initiated"
            for z in crowd_conditions:
                crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.10)
                queue_information[z] = queue_information[z] + 10

        elif stype == "Public Transport Delay":
            effects["action"] = "Subway/bus connection delays"
            for z in crowd_conditions:
                crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.15)

        elif stype == "Power Failure":
            effects["action"] = "Grid blackout reported"
            for z in queue_information:
                queue_information[z] = queue_information[z] + 25

        elif stype == "VIP Arrival":
            effects["action"] = "Secured escort transport corridor active"
            if zone in queue_information:
                queue_information[zone] = queue_information[zone] + 8

        elif stype == "Security Incident":
            effects["action"] = "Active threat report"
            active_incidents.append(scenario.id)
            for z in crowd_conditions:
                crowd_conditions[z] = min(1.0, crowd_conditions[z] + 0.05)

        elif stype == "Lost Child":
            effects["action"] = "Search and containment protocols active"
            if zone in queue_information:
                queue_information[zone] = queue_information[zone] + 5

        elif stype == "Evacuation":
            effects["action"] = "Initiating stadium evacuation protocol"
            for z in crowd_conditions:
                crowd_conditions[z] = 0.95
                queue_information[z] = 99

        # Recalculate stadium health based on new simulated values
        health = 1.0
        health -= len(active_incidents) * 0.15
        for density in crowd_conditions.values():
            if density > 0.8:
                health -= 0.10
        for wait_mins in queue_information.values():
            if wait_mins > 20:
                health -= 0.05

        health = max(0.0, min(1.0, health))

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
