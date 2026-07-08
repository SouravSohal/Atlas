from app.application.demo.definition import ScenarioDefinition, ScenarioStep

class ScenarioFactory:
    """Factory creating configured instances of standard demo scenarios."""

    @staticmethod
    def create_crowd_surge(zone_id: str) -> ScenarioDefinition:
        return ScenarioDefinition(
            name="Crowd Surge",
            description="Replays crowd density bottleneck surge near primary stadium gate turnstiles.",
            steps=[
                ScenarioStep(
                    tick_index=0,
                    operational_state_updates={zone_id: 0.45},
                    notifications_to_publish=["Ingress starting. Gate operations normal."],
                    events_to_publish=[{"type": "IngressInitialized", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=1,
                    operational_state_updates={zone_id: 0.75},
                    notifications_to_publish=["Warning: Gate ingress crowd density rising."],
                    events_to_publish=[{"type": "DensityWarning", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=2,
                    operational_state_updates={zone_id: 0.95},
                    incidents_to_create=[{
                        "incident_type": "crowd_control",
                        "severity": "high",
                        "description": "Gate ingress bottleneck alert at turnstile check-points.",
                        "zone_id": zone_id,
                    }],
                    notifications_to_publish=["High Alert: Severe bottleneck detected. Rerouting recommended."],
                    events_to_publish=[{"type": "CrowdBottleneckActive", "zone_id": zone_id}]
                )
            ]
        )

    @staticmethod
    def create_medical_emergency(zone_id: str) -> ScenarioDefinition:
        return ScenarioDefinition(
            name="Medical Emergency",
            description="Replays medical warning distress, responder routing, and clearance.",
            steps=[
                ScenarioStep(
                    tick_index=0,
                    operational_state_updates={zone_id: 0.45},
                    notifications_to_publish=["System status nominal. Medical team standby."],
                    events_to_publish=[{"type": "StandbyVerification", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=1,
                    operational_state_updates={zone_id: 0.55},
                    incidents_to_create=[{
                        "incident_type": "medical",
                        "severity": "critical",
                        "description": "Spectator collapse reported near Section 104 corridors.",
                        "zone_id": zone_id,
                    }],
                    notifications_to_publish=["Emergency: Medical dispatch warning registered."],
                    events_to_publish=[{"type": "MedicalAlert", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=2,
                    operational_state_updates={zone_id: 0.45},
                    notifications_to_publish=["Clear: Medical rescue completed successfully."],
                    events_to_publish=[{"type": "EmergencyCleared", "zone_id": zone_id}]
                )
            ]
        )

    @staticmethod
    def create_heavy_rain(zone_id: str) -> ScenarioDefinition:
        return ScenarioDefinition(
            name="Heavy Rain",
            description="Replays weather event warning, covered plaza diversion, and dispersal.",
            steps=[
                ScenarioStep(
                    tick_index=0,
                    operational_state_updates={zone_id: 0.40},
                    notifications_to_publish=["Clear sky forecast. Ingress nominal."],
                    events_to_publish=[{"type": "WeatherNominal", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=1,
                    operational_state_updates={zone_id: 0.70},
                    incidents_to_create=[{
                        "incident_type": "weather",
                        "severity": "medium",
                        "description": "Sudden heavy rainfall starting. Evacuating open parking lots.",
                        "zone_id": zone_id,
                    }],
                    notifications_to_publish=["Warning: Rain showers starting. Directing spectators to cover."],
                    events_to_publish=[{"type": "RainShowerInitiated", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=2,
                    operational_state_updates={zone_id: 0.45},
                    notifications_to_publish=["Clear: Weather event dispersed. Normal flow resuming."],
                    events_to_publish=[{"type": "WeatherCleared", "zone_id": zone_id}]
                )
            ]
        )

    @staticmethod
    def create_lost_child(zone_id: str) -> ScenarioDefinition:
        return ScenarioDefinition(
            name="Lost Child",
            description="Replays lost child search, checkpoint alert, and reunion.",
            steps=[
                ScenarioStep(
                    tick_index=0,
                    operational_state_updates={zone_id: 0.40},
                    notifications_to_publish=["Security checks nominal."],
                    events_to_publish=[{"type": "SecurityChecksPassed", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=1,
                    operational_state_updates={zone_id: 0.50},
                    incidents_to_create=[{
                        "incident_type": "security",
                        "severity": "medium",
                        "description": "7-year-old child separated from guardians near Section 208.",
                        "zone_id": zone_id,
                    }],
                    notifications_to_publish=["Warning: Lost child alert registered. Security notified."],
                    events_to_publish=[{"type": "LostChildReported", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=2,
                    operational_state_updates={zone_id: 0.40},
                    notifications_to_publish=["Clear: Child reunited with guardians. Security alert stand-down."],
                    events_to_publish=[{"type": "ChildReunited", "zone_id": zone_id}]
                )
            ]
        )

    @staticmethod
    def create_match_end(zone_id: str) -> ScenarioDefinition:
        return ScenarioDefinition(
            name="Match End",
            description="Replays spectator exit egress flows and volunteer staffing redirection.",
            steps=[
                ScenarioStep(
                    tick_index=0,
                    operational_state_updates={zone_id: 0.30},
                    notifications_to_publish=["Match in final minutes. Pre-exit routing active."],
                    events_to_publish=[{"type": "MatchFinals", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=1,
                    operational_state_updates={zone_id: 0.85},
                    incidents_to_create=[{
                        "incident_type": "crowd_control",
                        "severity": "medium",
                        "description": "Exit egress congestion rising near transit terminals.",
                        "zone_id": zone_id,
                    }],
                    notifications_to_publish=["Warning: High crowd density at exit gates. Deploying support."],
                    events_to_publish=[{"type": "EgressCrowdSurge", "zone_id": zone_id}]
                ),
                ScenarioStep(
                    tick_index=2,
                    operational_state_updates={zone_id: 0.20},
                    notifications_to_publish=["Clear: Egress complete. Stadium corridors clear."],
                    events_to_publish=[{"type": "EgressFinished", "zone_id": zone_id}]
                )
            ]
        )
