import { Play, Pause, RefreshCw } from "lucide-react";

interface SimulationTabProps {
  demoMode: boolean;
  setDemoMode: (val: boolean) => void;
  selectedSeed: string;
  setSelectedSeed: (val: string) => void;
  simSpeed: number;
  setSimSpeed: (val: number) => void;
  simPaused: boolean;
  setSimPaused: (val: boolean) => void;
  resetSimulation: () => void;
  setDiagnosticLogs: (updater: (logs: string[]) => string[]) => void;
}

export function SimulationTab({
  demoMode,
  setDemoMode,
  selectedSeed,
  setSelectedSeed,
  simSpeed,
  setSimSpeed,
  simPaused,
  setSimPaused,
  resetSimulation,
  setDiagnosticLogs,
}: SimulationTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-black text-foreground">Simulation Engine Settings</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Control the active Digital Twin simulation execution loops, speed multipliers, and seeds.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Demo Mode</label>
          <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl p-3">
            <span className="text-xs text-muted-foreground">Toggle automated scenario execution</span>
            <button
              onClick={() => setDemoMode(!demoMode)}
              className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                demoMode ? "bg-primary" : "bg-muted"
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  demoMode ? "translate-x-4" : "translate-x-0"
                }`}
              />
            </button>
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Seed Config Dataset</label>
          <select
            value={selectedSeed}
            onChange={(e) => setSelectedSeed(e.target.value)}
            className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-bold"
          >
            <option value="stadium_seed_data.json">stadium_seed_data.json (Aurelia Arena - Standard)</option>
            <option value="stadium_seed_congestion.json">stadium_seed_congestion.json (High-Load Congestion)</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between text-xs">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Simulation Speed</label>
          <span className="font-bold text-primary">{simSpeed}x Realtime speed</span>
        </div>
        <input
          type="range"
          min="1"
          max="10"
          value={simSpeed}
          onChange={(e) => setSimSpeed(parseInt(e.target.value))}
          className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
        />
        <div className="flex justify-between text-[9px] font-bold text-muted-foreground uppercase tracking-wider">
          <span>1x (Nominal)</span>
          <span>5x</span>
          <span>10x (Maximum)</span>
        </div>
      </div>

      <div className="flex items-center gap-3 pt-4 border-t border-border/40">
        <button
          onClick={() => setSimPaused(!simPaused)}
          className={`px-4 py-2 border rounded-xl font-extrabold text-xs transition-all shadow flex items-center gap-2 ${
            simPaused
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20"
              : "bg-destructive/10 border-destructive/20 text-destructive hover:bg-destructive/20"
          }`}
        >
          {simPaused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
          {simPaused ? "Resume Simulation" : "Pause Simulation"}
        </button>
        <button
          onClick={() => {
            resetSimulation();
            setDiagnosticLogs((prev) => [
              `[${new Date().toLocaleString()}] INFO: Manual Simulation Engine restart/replay triggered. Centralized Simulation Clock reset to T-120m (18:00).`,
              ...prev
            ]);
          }}
          className="px-4 py-2 border border-border bg-muted/40 text-foreground hover:bg-muted/80 rounded-xl font-extrabold text-xs transition-all shadow flex items-center gap-2"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Reset Simulation
        </button>
      </div>
    </div>
  );
}
