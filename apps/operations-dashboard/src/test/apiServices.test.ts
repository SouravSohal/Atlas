import { describe, it, expect } from "vitest";
import {
  fetchDashboardOverview,
  fetchStadiumPredictions,
  postCopilotChat,
  fetchOperationalState,
} from "../services/api";

describe("API Services Integration tests with MSW", () => {
  it("should fetch dashboard overview correctly", async () => {
    const data = await fetchDashboardOverview();
    expect(data).toBeDefined();
    expect(data.stadium_health).toBe(0.95);
    expect(data.active_incidents_count).toBe(2);
  });

  it("should fetch stadium predictions successfully", async () => {
    const predictions = await fetchStadiumPredictions();
    expect(predictions).toBeDefined();
    expect(predictions.confidence_score).toBe(0.94);
    expect(predictions.queue_growth.prediction).toBe("P1");
  });

  it("should fetch operational state correctly", async () => {
    const states = await fetchOperationalState();
    expect(states).toBeInstanceOf(Array);
    expect(states.length).toBe(2);
    expect(states[0].density).toBe(0.35);
  });

  it("should submit copilot query and get response details", async () => {
    const reply = await postCopilotChat("What is current crowd count?", []);
    expect(reply).toBeDefined();
    expect(reply.text).toContain("mock Copilot response");
    expect(reply.model_version).toBe("Gemini 2.5 Flash");
    expect(reply.citations?.[0].label).toBe("Gate A Ingress");
  });
});
