export interface AppConfig {
  apiUrl: string;
  wsUrl: string;
  environment: string;
  geminiModel: string;
  appVersion: string;
  defaultCrowdDensityThreshold: number;
  defaultQueueTimeThreshold: number;
  defaultAiConfidenceThreshold: number;
  defaultDemoMode: boolean;
  defaultSimulationSpeed: number;
  dbEngine: string;
}

export const envConfig: AppConfig = {
  apiUrl: import.meta.env.VITE_API_URL || "http://localhost:8000",
  wsUrl: import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws",
  environment: import.meta.env.VITE_ENVIRONMENT || "development",
  geminiModel: import.meta.env.VITE_GEMINI_MODEL || "gemini-2.5-pro",
  appVersion: import.meta.env.VITE_APP_VERSION || "v0.9.4-rc2",
  defaultCrowdDensityThreshold: Number(import.meta.env.VITE_CROWD_DENSITY_THRESHOLD || "75"),
  defaultQueueTimeThreshold: Number(import.meta.env.VITE_QUEUE_TIME_THRESHOLD || "15"),
  defaultAiConfidenceThreshold: Number(import.meta.env.VITE_AI_CONFIDENCE_THRESHOLD || "80"),
  defaultDemoMode: import.meta.env.VITE_DEMO_MODE !== "false",
  defaultSimulationSpeed: Number(import.meta.env.VITE_SIMULATION_SPEED || "2"),
  dbEngine: import.meta.env.VITE_DB_ENGINE || "Cloud Firestore",
};
