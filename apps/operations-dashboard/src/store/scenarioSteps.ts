export const SCENARIO_STEPS: Record<string, any[]> = {
  "Crowd Surge": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }, { density: 0.35, queue_waiting_minutes: 3 }],
      incidents: [],
      recs: [],
      summary: "Stadium ingress gates reporting normal spectator arrivals. Staff deployed at check-points.",
      notification: "System initialized. Operations nominal."
    },
    {
      overview: { stadium_health: 0.92, active_incidents_count: 0, average_crowd_density: 0.65, allocated_volunteers_count: 20 },
      zones: [{ density: 0.75, queue_waiting_minutes: 12 }, { density: 0.50, queue_waiting_minutes: 6 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [{ id: "rec-1", action_type: "dispatch", priority: "medium", details: "Deploy 2 additional volunteers to Gate 1 check-points.", age: 60000 }],
      summary: "Spectator density rising rapidly at Gate 1 turnstiles. Queue wait time now at 12 minutes.",
      notification: "Warning: High crowd density detected at Gate 1 Sector."
    },
    {
      overview: { stadium_health: 0.75, active_incidents_count: 1, average_crowd_density: 0.85, allocated_volunteers_count: 20 },
      zones: [{ density: 0.95, queue_waiting_minutes: 25 }, { density: 0.65, queue_waiting_minutes: 15 }, { density: 0.45, queue_waiting_minutes: 5 }],
      incidents: [{ id: "inc-1", incident_type: "crowd_control", severity: "high", description: "Ingress bottleneck alert at Gate 1 check-points.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [
        { id: "rec-1", action_type: "dispatch", priority: "medium", details: "Deploy 2 additional volunteers to Gate 1 check-points.", age: 120000 },
        { id: "rec-2", action_type: "reroute", priority: "high", details: "Reroute incoming flows from Gate 1 to Gate 2.", age: 60000 }
      ],
      summary: "Ingress bottleneck alert at Gate 1 turnstiles. System recommends active flow rerouting.",
      notification: "High Alert: Sector congestion bottleneck active."
    },
    {
      overview: { stadium_health: 0.70, active_incidents_count: 1, average_crowd_density: 0.90, allocated_volunteers_count: 24 },
      zones: [{ density: 0.98, queue_waiting_minutes: 32 }, { density: 0.70, queue_waiting_minutes: 18 }, { density: 0.50, queue_waiting_minutes: 6 }],
      incidents: [{ id: "inc-1", incident_type: "crowd_control", severity: "high", description: "Ingress bottleneck alert at Gate 1 check-points.", resolved: false, created_at: new Date().toISOString(), age: 180000 }],
      recs: [
        { id: "rec-2", action_type: "reroute", priority: "high", details: "Reroute incoming flows from Gate 1 to Gate 2.", age: 120000 }
      ],
      summary: "Rerouting active. Volunteer teams are directing crowd flow to empty Gate 2 corridors.",
      notification: "Rerouting protocol: Gate 2 backup ingress channels active."
    },
    {
      overview: { stadium_health: 0.95, active_incidents_count: 0, average_crowd_density: 0.55, allocated_volunteers_count: 24 },
      zones: [{ density: 0.50, queue_waiting_minutes: 6 }, { density: 0.55, queue_waiting_minutes: 8 }, { density: 0.45, queue_waiting_minutes: 5 }],
      incidents: [],
      recs: [],
      summary: "Bottleneck dispersed successfully. Ingress flow stabilized under recommended routing.",
      notification: "Clear: Gate 1 turnstiles returned to safe operational levels."
    }
  ],
  "Medical Emergency": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Operations normal. Medical responder units placed on standby at Post Alpha.",
      notification: "Medical status check complete. Ready."
    },
    {
      overview: { stadium_health: 0.83, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.55, queue_waiting_minutes: 8 }],
      incidents: [{ id: "inc-2", incident_type: "medical", severity: "critical", description: "Spectator collapse reported in Section 104. Dispatching post units.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-3", action_type: "dispatch", priority: "high", details: "Dispatch First-Aid Team Alpha to Section 104.", age: 60000 }],
      summary: "Spectator collapse reported in Section 104. First Aid responders dispatched.",
      notification: "Emergency: Medical alert registered in Section 104."
    },
    {
      overview: { stadium_health: 0.83, active_incidents_count: 1, average_crowd_density: 0.50, allocated_volunteers_count: 22 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.60, queue_waiting_minutes: 10 }],
      incidents: [{ id: "inc-2", incident_type: "medical", severity: "critical", description: "Spectator collapse reported in Section 104. Dispatching post units.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [{ id: "rec-4", action_type: "reroute", priority: "medium", details: "Clear security corridor near Section 104 exit.", age: 60000 }],
      summary: "Responders arrived on scene. Administering first aid. Corridor cleared for transit.",
      notification: "Update: Responders arrived. Scene secured."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 22 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Patient evacuated and stable. Incident resolved. Corridor reopened.",
      notification: "Resolve: Emergency cleared. Sector nominal."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Medical responders returned to standby. Ready.",
      notification: "System initialized. Standby."
    }
  ],
  "Gate Closure": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "All gates active and operating. Flow rate nominal.",
      notification: "All check-points online."
    },
    {
      overview: { stadium_health: 0.83, active_incidents_count: 1, average_crowd_density: 0.50, allocated_volunteers_count: 20 },
      zones: [{ density: 0.0, queue_waiting_minutes: 0 }, { density: 0.65, queue_waiting_minutes: 12 }],
      incidents: [{ id: "inc-3", incident_type: "facility", severity: "high", description: "Gate 1 Turnstile malfunction. Structural block.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-5", action_type: "dispatch", priority: "medium", details: "Dispatch maintenance engineers to Gate 1.", age: 60000 }],
      summary: "Turnstile malfunction at Gate 1. Ingress flow halted. Diverting spectators.",
      notification: "Warning: Gate 1 turnstile malfunction."
    },
    {
      overview: { stadium_health: 0.65, active_incidents_count: 1, average_crowd_density: 0.70, allocated_volunteers_count: 20 },
      zones: [{ density: 0.0, queue_waiting_minutes: 0 }, { density: 0.90, queue_waiting_minutes: 25 }],
      incidents: [{ id: "inc-3", incident_type: "facility", severity: "high", description: "Gate 1 Turnstile malfunction. Structural block.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [
        { id: "rec-5", action_type: "dispatch", priority: "medium", details: "Dispatch maintenance engineers to Gate 1.", age: 120000 },
        { id: "rec-6", action_type: "reroute", priority: "high", details: "Divert crowd flow to Gate 2.", age: 60000 }
      ],
      summary: "Engineers on site. Spectators diverted. Gate 2 experiencing heavy load.",
      notification: "Alert: Gate 2 queue times rising."
    },
    {
      overview: { stadium_health: 0.95, active_incidents_count: 0, average_crowd_density: 0.55, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 6 }, { density: 0.55, queue_waiting_minutes: 8 }],
      incidents: [],
      recs: [],
      summary: "Turnstile repaired. Gate 1 reopened. Flow rates normalized.",
      notification: "Clear: Gate 1 turnstile repaired."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Gate operations returned to default presets.",
      notification: "System initialized. Normal."
    }
  ],
  "Heavy Rain": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Weather forecast: Clear sky operations.",
      notification: "System initialized."
    },
    {
      overview: { stadium_health: 0.93, active_incidents_count: 0, average_crowd_density: 0.55, allocated_volunteers_count: 20 },
      zones: [{ density: 0.55, queue_waiting_minutes: 10 }, { density: 0.50, queue_waiting_minutes: 8 }],
      incidents: [],
      recs: [{ id: "rec-7", action_type: "dispatch", priority: "medium", details: "Distribute rain covers and clear open plaza paths.", age: 60000 }],
      summary: "Rain initiated. Open plaza areas cleared. Queue speeds slowing down.",
      notification: "Warning: Rain shower starting."
    },
    {
      overview: { stadium_health: 0.88, active_incidents_count: 0, average_crowd_density: 0.65, allocated_volunteers_count: 20 },
      zones: [{ density: 0.65, queue_waiting_minutes: 15 }, { density: 0.60, queue_waiting_minutes: 12 }],
      incidents: [],
      recs: [{ id: "rec-8", action_type: "reroute", priority: "high", details: "Evacuate open parking lots to covered corridors.", age: 60000 }],
      summary: "Spectators moving to covered sectors. Plaza density rising.",
      notification: "Alert: Spectators seeking cover."
    },
    {
      overview: { stadium_health: 0.95, active_incidents_count: 0, average_crowd_density: 0.55, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 6 }, { density: 0.50, queue_waiting_minutes: 7 }],
      incidents: [],
      recs: [],
      summary: "Rain cleared. Operations returning to default layout.",
      notification: "Clear: Rain stopped."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Clear sky operations restored.",
      notification: "System initialized. Normal."
    }
  ],
  "Power Failure": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Power grid stable. All systems operating on main source.",
      notification: "Power systems normal."
    },
    {
      overview: { stadium_health: 0.68, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 15 }, { density: 0.50, queue_waiting_minutes: 14 }],
      incidents: [{ id: "inc-4", incident_type: "facility", severity: "critical", description: "Food Plaza sector power grid blackout.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-9", action_type: "dispatch", priority: "critical", details: "Dispatch emergency engineering crew and activate backup generator.", age: 60000 }],
      summary: "Power outage in Food Plaza sector. Backup generators initiated.",
      notification: "Critical: Food Plaza blackout reported."
    },
    {
      overview: { stadium_health: 0.78, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 22 },
      zones: [{ density: 0.45, queue_waiting_minutes: 10 }, { density: 0.45, queue_waiting_minutes: 8 }],
      incidents: [{ id: "inc-4", incident_type: "facility", severity: "critical", description: "Food Plaza sector power grid blackout.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [{ id: "rec-10", action_type: "dispatch", priority: "medium", details: "Verify main system security loops.", age: 60000 }],
      summary: "Engineers working on restoration. Backup power keeping systems active.",
      notification: "Update: Engineers on scene. Backup power active."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 22 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Main grid restored. Blackout cleared.",
      notification: "Clear: Power restored to Food Plaza."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Operations returned to default grid source.",
      notification: "System initialized. Grid normal."
    }
  ],
  "VIP Arrival": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Gate corridors operating on default ingress flow.",
      notification: "System initialized."
    },
    {
      overview: { stadium_health: 0.93, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 10 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [{ id: "rec-11", action_type: "dispatch", priority: "medium", details: "Secure Gate 2 arrival corridor.", age: 60000 }],
      summary: "VIP motorcade approaching Gate 2. Corridor secure loops initiated.",
      notification: "VIP Warning: Motorcade approaching."
    },
    {
      overview: { stadium_health: 0.88, active_incidents_count: 0, average_crowd_density: 0.50, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 15 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [{ id: "rec-12", action_type: "reroute", priority: "high", details: "Divert public flow from Gate 2 to Gate 1.", age: 60000 }],
      summary: "VIP arrival corridor secured. Public flow diverted to Gate 1.",
      notification: "VIP Alert: Ingress diversion active."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "VIP transit complete. Gate 2 corridors returned to normal.",
      notification: "Clear: VIP escort finished."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "VIP transit completed. Operations returned to default.",
      notification: "System initialized. Normal."
    }
  ],
  "Lost Child": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Security patrols reporting all clear at Sections 200-220.",
      notification: "System initialized. Security nominal."
    },
    {
      overview: { stadium_health: 0.88, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.50, queue_waiting_minutes: 6 }],
      incidents: [{ id: "inc-5", incident_type: "security", severity: "medium", description: "7-year-old child separated from guardians near Section 208.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-13", action_type: "dispatch", priority: "high", details: "Deploy Gate 2 volunteers to support perimeter search.", age: 60000 }],
      summary: "Lost child reported near Section 208. Dispatching nearest search volunteers.",
      notification: "Warning: Lost child alert in Section 208."
    },
    {
      overview: { stadium_health: 0.85, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 24 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.45, queue_waiting_minutes: 5 }],
      incidents: [{ id: "inc-5", incident_type: "security", severity: "medium", description: "7-year-old child separated from guardians near Section 208.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [{ id: "rec-14", action_type: "dispatch", priority: "medium", details: "Broadcast alert description to exit gate turnstiles.", age: 60000 }],
      summary: "Search in progress. Security checkpoints verified. Parent matched details.",
      notification: "Update: Security perimeter sweep in progress."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 24 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Child reunited with guardians. Search stood down.",
      notification: "Clear: Family reunited successfully."
    }
  ],
  "Match End": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Match in final minutes. Gates preparation nominal.",
      notification: "System initialized. Operations ready."
    },
    {
      overview: { stadium_health: 0.85, active_incidents_count: 1, average_crowd_density: 0.75, allocated_volunteers_count: 20 },
      zones: [{ density: 0.85, queue_waiting_minutes: 18 }, { density: 0.70, queue_waiting_minutes: 15 }],
      incidents: [{ id: "inc-6", incident_type: "crowd_control", severity: "medium", description: "Spectator surge at main exit gates.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-15", action_type: "reroute", priority: "high", details: "Open auxiliary egress corridor doors.", age: 60000 }],
      summary: "Egress surge detected at main gates. Auxiliary corridors initiated.",
      notification: "Warning: High egress density detected."
    },
    {
      overview: { stadium_health: 0.95, active_incidents_count: 0, average_crowd_density: 0.30, allocated_volunteers_count: 20 },
      zones: [{ density: 0.30, queue_waiting_minutes: 4 }, { density: 0.25, queue_waiting_minutes: 3 }],
      incidents: [],
      recs: [],
      summary: "Egress completed. Spectators cleared from plaza corridors.",
      notification: "Clear: Stadium egress complete."
    }
  ]
};
