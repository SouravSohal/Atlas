import { envConfig } from "../config/env";
import { useGlobalStore } from "../store/useGlobalStore";

const API_BASE_URL = envConfig.apiUrl;

async function authFetch(url: string, init?: RequestInit): Promise<Response> {
  const store = useGlobalStore.getState();
  const token = store.accessToken || localStorage.getItem("atlas_access_token");

  const headers = new Headers(init?.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const newInit: RequestInit = {
    ...init,
    headers,
  };

  let res = await fetch(url, newInit);

  // Auto-refresh token if 401 Unauthorized occurs
  if (res.status === 401) {
    const refresh = store.refreshToken || localStorage.getItem("atlas_refresh_token");
    if (refresh) {
      try {
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh_token: refresh }),
        });

        if (refreshRes.ok) {
          const payload = await refreshRes.json();
          const { access_token, refresh_token: new_refresh, user } = payload.data;

          localStorage.setItem("atlas_access_token", access_token);
          localStorage.setItem("atlas_refresh_token", new_refresh);
          localStorage.setItem("atlas_user", JSON.stringify(user));

          useGlobalStore.setState({
            accessToken: access_token,
            refreshToken: new_refresh,
            user,
            userRole: user.role,
          });

          headers.set("Authorization", `Bearer ${access_token}`);
          res = await fetch(url, newInit);
          return res;
        }
      } catch (err) {
        console.error("Token refresh failed", err);
      }
    }

    localStorage.removeItem("atlas_access_token");
    localStorage.removeItem("atlas_refresh_token");
    localStorage.removeItem("atlas_user");
    localStorage.removeItem("atlas_is_demo");
    useGlobalStore.setState({
      accessToken: null,
      refreshToken: null,
      user: null,
      userRole: "Administrator",
      isDemoSession: false,
    });
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  }

  if (res.status === 403) {
    if (window.location.pathname !== "/access-denied") {
      window.location.href = "/access-denied";
    }
  }

  return res;
}

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
  const res = await authFetch(`${API_BASE_URL}/dashboard/overview`);
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
  const res = await authFetch(
    `${API_BASE_URL}/dashboard/incidents?page=${page}&limit=${limit}&sort_by=${sortBy}&order=${order}`
  );
  if (!res.ok) throw new Error("Failed to fetch incidents");
  const data: ApiResponse<IncidentsResponse> = await res.json();
  return data.data;
}

export async function fetchOperationalState(): Promise<OperationalStateItem[]> {
  const res = await authFetch(`${API_BASE_URL}/dashboard/operational-state`);
  if (!res.ok) throw new Error("Failed to fetch operational state");
  const data: ApiResponse<OperationalStateItem[]> = await res.json();
  return data.data;
}

export async function fetchDashboardRecommendations(page = 1, limit = 10): Promise<RecommendationsResponse> {
  const res = await authFetch(`${API_BASE_URL}/dashboard/recommendations?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch recommendations");
  const data: ApiResponse<RecommendationsResponse> = await res.json();
  return data.data;
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  const res = await authFetch(`${API_BASE_URL}/dashboard/metrics`);
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
  const res = await authFetch(`${API_BASE_URL}/incidents/${id}`, {
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
  const res = await authFetch(`${API_BASE_URL}/incidents`, {
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
  language = "en",
  currentPage?: string
): Promise<CopilotChatResponse> {
  const res = await authFetch(`${API_BASE_URL}/copilot/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, history, language, current_page: currentPage }),
  });
  if (!res.ok) throw new Error("Failed to call copilot chat");
  const data: ApiResponse<CopilotChatResponse> = await res.json();
  return data.data;
}

export interface DashboardBriefingResponse {
  executive_summary: string;
  situation_assessment: string;
  immediate_risks: string[];
  recommended_actions: string[];
  predicted_outcome: string;
  confidence_score: number;
  assumptions: string[];
  alternative_strategies: string[];
}

export async function fetchDashboardBriefing(): Promise<DashboardBriefingResponse> {
  const res = await authFetch(`${API_BASE_URL}/dashboard/briefing`);
  if (!res.ok) throw new Error("Failed to fetch dashboard briefing");
  const data: ApiResponse<DashboardBriefingResponse> = await res.json();
  return data.data;
}

export interface PrioritizedRecommendationItem {
  recommendation_id: string;
  action_type: string;
  priority_order: number;
  priority_level: string;
  explanation: string;
}

export interface RecommendationsExplanationResponse {
  natural_language_explanation: string;
  prioritized_recommendations: PrioritizedRecommendationItem[];
  risk_assessment: string;
  alternative_actions: string[];
}

export async function fetchRecommendationsExplanation(): Promise<RecommendationsExplanationResponse> {
  const res = await authFetch(`${API_BASE_URL}/dashboard/recommendations/explain`);
  if (!res.ok) throw new Error("Failed to fetch recommendations explanation");
  const data: ApiResponse<RecommendationsExplanationResponse> = await res.json();
  return data.data;
}

export async function generateAIRecommendations(): Promise<RecommendationItem[]> {
  const res = await authFetch(`${API_BASE_URL}/dashboard/recommendations/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error("Failed to generate AI recommendations");
  const data: ApiResponse<RecommendationItem[]> = await res.json();
  return data.data;
}

export interface PredictionItem {
  prediction: string;
  confidence: number;
  reason: string;
  mitigation: string;
  timeline: string;
}

export interface StadiumPredictions {
  confidence_score: number;
  rationale: string;
  queue_growth: PredictionItem;
  crowd_movement: PredictionItem;
  volunteer_shortages: PredictionItem;
  medical_demand: PredictionItem;
  transport_congestion: PredictionItem;
  gate_overload: PredictionItem;
  parking_saturation: PredictionItem;
  weather_impact: PredictionItem;
}

export async function fetchStadiumPredictions(): Promise<StadiumPredictions> {
  const res = await authFetch(`${API_BASE_URL}/dashboard/predictions`);
  if (!res.ok) throw new Error("Failed to fetch stadium predictions");
  const data: ApiResponse<StadiumPredictions> = await res.json();
  return data.data;
}
