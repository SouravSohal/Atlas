import { http, HttpResponse } from "msw";
import { envConfig } from "../../config/env";

const API_BASE_URL = envConfig.apiUrl;

export const handlers = [
  // Mock Get Current User Profile
  http.get(`${API_BASE_URL}/auth/me`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        id: "usr-001",
        email: "demo@atlas.ai",
        name: "Demo Admin",
        role: "Administrator",
      },
    });
  }),

  // Mock Overview
  http.get(`${API_BASE_URL}/dashboard/overview`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        stadium_health: 0.95,
        active_incidents_count: 2,
        average_crowd_density: 0.48,
        pending_recommendations_count: 1,
        allocated_volunteers_count: 12,
        timestamp: new Date().toISOString(),
      },
    });
  }),

  // Mock Incidents
  http.get(`${API_BASE_URL}/dashboard/incidents`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        total_count: 2,
        page: 1,
        limit: 10,
        items: [
          {
            id: "inc-001",
            incident_type: "crowd_control",
            severity: "warning",
            description: "High crowd congestion at gate A",
            latitude: 37.7749,
            longitude: -122.4194,
            reporter_id: "usr-002",
            resolved: false,
            resolved_at: null,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: "inc-002",
            incident_type: "medical",
            severity: "critical",
            description: "Spectator collapse in Section 104",
            latitude: 37.775,
            longitude: -122.419,
            reporter_id: "usr-003",
            resolved: false,
            resolved_at: null,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
      },
    });
  }),

  // Mock Recommendations
  http.get(`${API_BASE_URL}/dashboard/recommendations`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        total_count: 1,
        page: 1,
        limit: 10,
        items: [
          {
            id: "rec-001",
            action_type: "reallocate_staff",
            priority: "medium",
            confidence: 0.92,
            details: JSON.stringify({
              explanation: "Reroute 4 floaters to gate A.",
              why: "High queue waits matching late arrivals.",
              evidence: "Zone telemetry is stable but ingress queue is 20 minutes.",
              operational_data_used: ["density"],
              alternative_actions: ["Wait for clearance"],
              trade_offs: "Fewer guides on concession area",
            }),
            status: "pending",
            approved_by_id: null,
            approved_at: null,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
      },
    });
  }),

  // Mock Operational State
  http.get(`${API_BASE_URL}/dashboard/operational-state`, () => {
    return HttpResponse.json({
      success: true,
      data: [
        { zone_id: "zone-1", density: 0.35, queue_waiting_minutes: 5, last_updated: new Date().toISOString() },
        { zone_id: "zone-2", density: 0.85, queue_waiting_minutes: 25, last_updated: new Date().toISOString() },
      ],
    });
  }),

  // Mock Predictions
  http.get(`${API_BASE_URL}/dashboard/predictions`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        confidence_score: 0.94,
        rationale: "Rationale summary",
        queue_growth: { prediction: "P1", confidence: 0.88, reason: "R1", mitigation: "M1", timeline: "T1" },
        crowd_movement: { prediction: "P2", confidence: 0.85, reason: "R2", mitigation: "M2", timeline: "T2" },
        volunteer_shortages: { prediction: "P3", confidence: 0.75, reason: "R3", mitigation: "M3", timeline: "T3" },
        medical_demand: { prediction: "P4", confidence: 0.68, reason: "R4", mitigation: "M4", timeline: "T4" },
        transport_congestion: { prediction: "P5", confidence: 0.9, reason: "R5", mitigation: "M5", timeline: "T5" },
        gate_overload: { prediction: "P6", confidence: 0.82, reason: "R6", mitigation: "M6", timeline: "T6" },
        parking_saturation: { prediction: "P7", confidence: 0.95, reason: "R7", mitigation: "M7", timeline: "T7" },
        weather_impact: { prediction: "P8", confidence: 0.99, reason: "R8", mitigation: "M8", timeline: "T8" },
      },
    });
  }),

  // Mock Copilot Chat
  http.post(`${API_BASE_URL}/copilot/chat`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        text: "This is a mock Copilot response answering your question.",
        thinking: ["analyzing telemetry", "formulating mitigation strategy"],
        citations: [{ label: "Gate A Ingress", text: "Crowd density was at 85%." }],
        model_version: "Gemini 2.5 Flash",
        execution_time_ms: 120,
      },
    });
  }),
];
