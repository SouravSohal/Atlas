import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { KpiMatrix } from "../features/mission-control/components/KpiMatrix";
import { DigitalTwinMap } from "../features/mission-control/components/DigitalTwinMap";
import type { StadiumNode } from "../features/mission-control/types";

describe("Mission Control Components tests", () => {
  it("should render KpiMatrix with overview numbers", () => {
    const mockOverview = {
      stadium_health: 0.98,
      active_incidents_count: 3,
      average_crowd_density: 0.55,
      allocated_volunteers_count: 14,
    };

    render(<KpiMatrix overview={mockOverview} />);

    expect(screen.getByText("Stadium Health")).toBeInTheDocument();
    expect(screen.getByText("98%")).toBeInTheDocument();
    expect(screen.getByText("Active Incidents")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("Crowd Density")).toBeInTheDocument();
    expect(screen.getByText("55%")).toBeInTheDocument();
  });

  it("should render DigitalTwinMap with custom inspector panel when focused", () => {
    const mockNodes: StadiumNode[] = [
      {
        id: "node-0",
        type: "stadiumNode",
        position: { x: 0, y: 0 },
        data: {
          label: "Gate 1 Ingress",
          type: "Entrance Gate",
          value: "Density: 45%",
          status: "stable",
          isFocused: true,
          health: 85,
          density: 45,
          queue: 3,
          capacity: 15000,
          alerts: 0,
          recs: 0,
          resources: "Standard",
        },
      },
    ];

    const setFocused = vi.fn();
    const setShowOverlay = vi.fn();
    const setToast = vi.fn();

    render(
      <DigitalTwinMap
        flowNodes={mockNodes}
        flowEdges={[]}
        focusedNodeIndex={0}
        setFocusedNodeIndex={setFocused}
        showPredictionsOverlay={false}
        setShowPredictionsOverlay={setShowOverlay}
        setToastMessage={setToast}
      />
    );

    // Node contents in the Inspector panel
    expect(screen.getByRole("heading", { name: "Gate 1 Ingress" })).toBeInTheDocument();
    expect(screen.getByText("HEALTH")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
    expect(screen.getByText("DENSITY")).toBeInTheDocument();
    expect(screen.getByText("45%")).toBeInTheDocument();
    expect(screen.getByText("WAIT TIME")).toBeInTheDocument();
    expect(screen.getByText("3 min")).toBeInTheDocument();
  });

  it("should render fallback text in Inspector if no node is focused", () => {
    const setFocused = vi.fn();
    const setShowOverlay = vi.fn();
    const setToast = vi.fn();

    render(
      <DigitalTwinMap
        flowNodes={[]}
        flowEdges={[]}
        focusedNodeIndex={null}
        setFocusedNodeIndex={setFocused}
        showPredictionsOverlay={false}
        setShowPredictionsOverlay={setShowOverlay}
        setToastMessage={setToast}
      />
    );

    expect(screen.getByText("Sector Inspector")).toBeInTheDocument();
    expect(
      screen.getByText(/Click any node on the stadium map to inspect/i)
    ).toBeInTheDocument();
  });
});
