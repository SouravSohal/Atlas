import type { FC } from "react";
import { Zap } from "lucide-react";
import { SCENARIO_STEPS } from "../../../store/scenarioSteps";

interface ScenarioPlaybackControlsProps {
  playbackScenario: string | null;
  playbackActive: boolean;
  playbackIsPaused: boolean;
  playbackStep: number;
  playbackSpeed: number;
  startSimulation: (scenarioName: string) => void;
  stopSimulation: () => void;
  setPlaybackIsPaused: (paused: boolean) => void;
  setPlaybackStep: (step: number) => void;
  setPlaybackSpeed: (speed: number) => void;
  setFocusedNodeIndex: (index: number | null) => void;
  setJudgeDemoActive: (active: boolean) => void;
}

export const ScenarioPlaybackControls: FC<ScenarioPlaybackControlsProps> = ({
  playbackScenario,
  playbackActive,
  playbackIsPaused,
  playbackStep,
  playbackSpeed,
  startSimulation,
  stopSimulation,
  setPlaybackIsPaused,
  setPlaybackStep,
  setPlaybackSpeed,
  setFocusedNodeIndex,
  setJudgeDemoActive,
}) => {
  return (
    <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
          <Zap className="h-5 w-5" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-foreground">Scenario Playback Engine</h3>
          <p className="text-[11px] text-muted-foreground mt-0.5 font-semibold">Replay hypothetical stadium incidents in real-time.</p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        {/* Selector */}
        <select
          value={playbackScenario || ""}
          onChange={(e) => {
            const val = e.target.value;
            if (val) {
              startSimulation(val);
            } else {
              stopSimulation();
            }
          }}
          className="rounded-xl border border-border bg-card px-3.5 py-2 text-xs font-bold text-foreground outline-none cursor-pointer"
        >
          <option value="">-- Select Scenario Playback --</option>
          <option value="Crowd Surge">Crowd Surge Simulation</option>
          <option value="Medical Emergency">Medical Emergency Simulation</option>
          <option value="Gate Closure">Gate Closure Simulation</option>
          <option value="Heavy Rain">Heavy Rain Simulation</option>
          <option value="Power Failure">Power Failure Simulation</option>
          <option value="VIP Arrival">VIP Arrival Simulation</option>
          <option value="Lost Child">Lost Child Simulation</option>
          <option value="Match End">Match End Simulation</option>
        </select>

        {playbackActive && (
          <>
            {/* Play Pause */}
            <button
              onClick={() => setPlaybackIsPaused(!playbackIsPaused)}
              className="rounded-xl border border-border hover:bg-muted bg-card px-3 py-2 text-xs font-bold transition-colors"
            >
              {playbackIsPaused ? "Resume" : "Pause"}
            </button>

            {/* Scrubber slider */}
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-muted-foreground uppercase">Step</span>
              <input
                type="range"
                min="0"
                max={(SCENARIO_STEPS[playbackScenario || ""]?.length || 5) - 1}
                value={playbackStep}
                onChange={(e) => {
                  setPlaybackStep(parseInt(e.target.value));
                  setPlaybackIsPaused(true);
                }}
                className="w-24 accent-primary cursor-pointer"
              />
              <span className="text-[11px] font-bold text-foreground font-mono">
                {playbackStep + 1}/{SCENARIO_STEPS[playbackScenario || ""]?.length || 5}
              </span>
            </div>

            {/* Playback speed selector */}
            <div className="flex items-center gap-1.5 border border-border rounded-xl bg-card p-1">
              {[1, 2, 5].map((speed) => (
                <button
                  key={speed}
                  onClick={() => setPlaybackSpeed(speed)}
                  className={`rounded-lg px-2.5 py-1 text-[10px] font-bold transition-colors ${
                    playbackSpeed === speed ? "bg-primary text-primary-foreground" : "hover:bg-muted text-muted-foreground"
                  }`}
                >
                  {speed}x
                </button>
              ))}
            </div>

            {/* Exit Playback */}
            <button
              onClick={() => {
                stopSimulation();
                setFocusedNodeIndex(null);
                setJudgeDemoActive(false);
              }}
              className="rounded-xl bg-destructive px-3.5 py-2 text-xs font-bold text-destructive-foreground hover:opacity-90 transition-opacity"
            >
              Exit
            </button>
          </>
        )}
      </div>
    </div>
  );
};
