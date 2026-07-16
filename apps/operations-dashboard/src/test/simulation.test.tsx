import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { JudgeDemoConsole } from "../features/mission-control/components/JudgeDemoConsole";

describe("JudgeDemoConsole Component tests", () => {
  it("should render launcher button and handle click to open dropdown", () => {
    const setDemoOpen = vi.fn();
    const startJudgeDemo = vi.fn();

    render(
      <JudgeDemoConsole
        demoOpen={false}
        setDemoOpen={setDemoOpen}
        demoMessage={null}
        judgeDemoActive={false}
        demoStatusMilestone=""
        playbackScenario={null}
        playbackStep={0}
        startJudgeDemo={startJudgeDemo}
      />
    );

    const launcher = screen.getByRole("button", { name: /Toggle Judge Demo Mode Menu/i });
    expect(launcher).toBeInTheDocument();
    fireEvent.click(launcher);

    expect(setDemoOpen).toHaveBeenCalledWith(true);
  });

  it("should render scenarios grid when console is open", () => {
    const setDemoOpen = vi.fn();
    const startJudgeDemo = vi.fn();

    render(
      <JudgeDemoConsole
        demoOpen={true}
        setDemoOpen={setDemoOpen}
        demoMessage="Triggered custom surge scenario"
        judgeDemoActive={true}
        demoStatusMilestone="🔬 Testing milestone"
        playbackScenario="Crowd Surge"
        playbackStep={1}
        startJudgeDemo={startJudgeDemo}
      />
    );

    expect(screen.getByText(/ATLAS JUDGE DEMO MODE/i)).toBeInTheDocument();
    expect(screen.getByText("Triggered custom surge scenario")).toBeInTheDocument();
    expect(screen.getByText("🔬 Testing milestone")).toBeInTheDocument();

    // Verify all playbook scenarios are rendered
    expect(screen.getByText("Crowd Surge")).toBeInTheDocument();
    expect(screen.getByText("Medical Emergency")).toBeInTheDocument();
    expect(screen.getByText("Heavy Rain")).toBeInTheDocument();
    expect(screen.getByText("Lost Child")).toBeInTheDocument();
    expect(screen.getByText("Match End")).toBeInTheDocument();
  });

  it("should trigger startJudgeDemo when a playbook scenario is clicked", () => {
    const setDemoOpen = vi.fn();
    const startJudgeDemo = vi.fn();

    render(
      <JudgeDemoConsole
        demoOpen={true}
        setDemoOpen={setDemoOpen}
        demoMessage={null}
        judgeDemoActive={false}
        demoStatusMilestone=""
        playbackScenario={null}
        playbackStep={0}
        startJudgeDemo={startJudgeDemo}
      />
    );

    const surgeBtn = screen.getByRole("button", { name: /Crowd Surge/i });
    fireEvent.click(surgeBtn);

    expect(startJudgeDemo).toHaveBeenCalledWith("Crowd Surge");
  });
});
