import { envConfig } from "../config/env";

const API_BASE_URL = envConfig.apiUrl;

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export interface DashboardOverview {
  stadium_health: number;
  active_incidents_count: number;
  average_crowd_density: number;
  pending_recommendations_count: number;
  allocated_volunteers_count: number;
  timestamp: string;
}

export interface IncidentItem {
  id: string;
  incident_type: string;
  severity: string;
  description: string;
  latitude: number;
  longitude: number;
  reporter_id: string;
  resolved: boolean;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface IncidentsResponse {
  total_count: number;
  page: number;
  limit: number;
  items: IncidentItem[];
}

export interface OperationalStateItem {
  zone_id: string;
  density: number;
  queue_waiting_minutes: number;
  last_updated: string;
}

export interface RecommendationItem {
  id: string;
  action_type: string;
  priority: string;
  confidence: number;
  details: string;
  status: string;
  approved_by_id: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface RecommendationsResponse {
  total_count: number;
  page: number;
  limit: number;
  items: RecommendationItem[];
}

export interface DashboardMetrics {
  average_queue_wait_minutes: number;
  congestion_rate: number;
  incident_resolution_rate: number;
  incidents_by_severity: Record<string, number>;
  incidents_by_type: Record<string, number>;
  recommendations_by_status: Record<string, number>;
}

export async function fetchDashboardOverview(): Promise<DashboardOverview> {
  const res = await fetch(`${API_BASE_URL}/dashboard/overview`);
  if (!res.ok) throw new Error("Failed to fetch dashboard overview");
  const data: ApiResponse<DashboardOverview> = await res.json();
  return data.data;
}

export async function fetchDashboardIncidents(
  page = 1,
  limit = 10,
  sortBy = "created_at",
  order = "desc"
): Promise<IncidentsResponse> {
  const res = await fetch(
    `${API_BASE_URL}/dashboard/incidents?page=${page}&limit=${limit}&sort_by=${sortBy}&order=${order}`
  );
  if (!res.ok) throw new Error("Failed to fetch incidents");
  const data: ApiResponse<IncidentsResponse> = await res.json();
  return data.data;
}

export async function fetchOperationalState(): Promise<OperationalStateItem[]> {
  const res = await fetch(`${API_BASE_URL}/dashboard/operational-state`);
  if (!res.ok) throw new Error("Failed to fetch operational state");
  const data: ApiResponse<OperationalStateItem[]> = await res.json();
  return data.data;
}

export async function fetchDashboardRecommendations(page = 1, limit = 10): Promise<RecommendationsResponse> {
  const res = await fetch(`${API_BASE_URL}/dashboard/recommendations?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch recommendations");
  const data: ApiResponse<RecommendationsResponse> = await res.json();
  return data.data;
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  const res = await fetch(`${API_BASE_URL}/dashboard/metrics`);
  if (!res.ok) throw new Error("Failed to fetch dashboard metrics");
  const data: ApiResponse<DashboardMetrics> = await res.json();
  return data.data;
}

export async function updateIncident(
  id: string,
  resolved: boolean,
  severity?: string,
  description?: string
): Promise<IncidentItem> {
  const res = await fetch(`${API_BASE_URL}/incidents/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ resolved, severity, description }),
  });
  if (!res.ok) throw new Error("Failed to update incident");
  const data: ApiResponse<IncidentItem> = await res.json();
  return data.data;
}

export interface CreateIncidentPayload {
  incident_type: string;
  severity: string;
  description: string;
  latitude: number;
  longitude: number;
  reporter_id: string;
  zone_id: string;
}

export async function createIncident(
  payload: CreateIncidentPayload
): Promise<IncidentItem> {
  const res = await fetch(`${API_BASE_URL}/incidents`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create incident");
  const data: ApiResponse<IncidentItem> = await res.json();
  return data.data;
}

export interface CopilotMessage {
  role: "user" | "assistant";
  text: string;
}

export interface CopilotChatResponse {
  text: string;
  thinking: string[];
  citations?: { label: string; text: string }[];
  model_version?: string;
  execution_time_ms?: number;
}

export async function postCopilotChat(
  message: string,
  history: CopilotMessage[],
  language = "en"
): Promise<CopilotChatResponse> {
  const res = await fetch(`${API_BASE_URL}/copilot/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, history, language }),
  });
  if (!res.ok) throw new Error("Failed to call copilot chat");
  const data: ApiResponse<CopilotChatResponse> = await res.json();
  return data.data;
}
