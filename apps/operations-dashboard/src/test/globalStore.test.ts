import { describe, it, expect, beforeEach } from "vitest";
import { useGlobalStore } from "../store/useGlobalStore";

describe("Zustand Global Store state management tests", () => {
  beforeEach(() => {
    // Reset state to nominal values
    useGlobalStore.setState({
      userRole: "Administrator",
      focusedNodeIndex: null,
      playbackActive: false,
      playbackScenario: null,
      playbackSpeed: 1,
      playbackIsPaused: false,
    });
  });

  it("should update userRole via setter", () => {
    const { setUserRole } = useGlobalStore.getState();
    setUserRole("Security Officer");
    expect(useGlobalStore.getState().userRole).toBe("Security Officer");
  });

  it("should focus node index via focusedNodeIndex state", () => {
    const { setFocusedNodeIndex } = useGlobalStore.getState();
    setFocusedNodeIndex(4);
    expect(useGlobalStore.getState().focusedNodeIndex).toBe(4);

    setFocusedNodeIndex(null);
    expect(useGlobalStore.getState().focusedNodeIndex).toBeNull();
  });

  it("should set playback active and speed options", () => {
    const { setPlaybackActive, setPlaybackSpeed } = useGlobalStore.getState();
    setPlaybackActive(true);
    setPlaybackSpeed(5);

    expect(useGlobalStore.getState().playbackActive).toBe(true);
    expect(useGlobalStore.getState().playbackSpeed).toBe(5);
  });

  it("should start and stop simulation correctly", () => {
    const { startSimulation, stopSimulation } = useGlobalStore.getState();
    startSimulation("Crowd Surge");

    expect(useGlobalStore.getState().playbackActive).toBe(true);
    expect(useGlobalStore.getState().playbackScenario).toBe("Crowd Surge");
    expect(useGlobalStore.getState().playbackStep).toBe(0);

    stopSimulation();
    expect(useGlobalStore.getState().playbackActive).toBe(false);
    expect(useGlobalStore.getState().playbackScenario).toBeNull();
  });
});
