interface ThresholdsTabProps {
  thresholdDensity: number;
  setThresholdDensity: (val: number) => void;
  thresholdQueue: number;
  setThresholdQueue: (val: number) => void;
  confidenceThreshold: number;
  setConfidenceThreshold: (val: number) => void;
  weatherOverride: string;
  setWeatherOverride: (val: string) => void;
  medAutoDispatch: boolean;
  setMedAutoDispatch: (val: boolean) => void;
}

export function ThresholdsTab({
  thresholdDensity,
  setThresholdDensity,
  thresholdQueue,
  setThresholdQueue,
  confidenceThreshold,
  setConfidenceThreshold,
  weatherOverride,
  setWeatherOverride,
  medAutoDispatch,
  setMedAutoDispatch,
}: ThresholdsTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-black text-foreground">Alert Threshold & Automation Rules</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Adjust telemetry boundaries triggering warning states and automated EMT/Police dispatcher triggers.</p>
      </div>

      <div className="space-y-4">
        <div className="space-y-3">
          <div className="flex justify-between text-xs">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Crowd Density Warning Limit</label>
            <span className="font-bold text-destructive">{thresholdDensity}% capacity</span>
          </div>
          <input
            type="range"
            min="50"
            max="95"
            value={thresholdDensity}
            onChange={(e) => setThresholdDensity(parseInt(e.target.value))}
            className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>

        <div className="space-y-3">
          <div className="flex justify-between text-xs">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Queue Waiting Warning Duration</label>
            <span className="font-bold text-amber-500">{thresholdQueue} minutes</span>
          </div>
          <input
            type="range"
            min="5"
            max="45"
            value={thresholdQueue}
            onChange={(e) => setThresholdQueue(parseInt(e.target.value))}
            className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>

        <div className="space-y-3">
          <div className="flex justify-between text-xs">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">AI Inference Confidence Cut-off</label>
            <span className="font-bold text-primary">{confidenceThreshold}% confidence</span>
          </div>
          <input
            type="range"
            min="60"
            max="95"
            value={confidenceThreshold}
            onChange={(e) => setConfidenceThreshold(parseInt(e.target.value))}
            className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 pt-4 border-t border-border/40">
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Weather Warning Severity Threshold</label>
          <select
            value={weatherOverride}
            onChange={(e) => setWeatherOverride(e.target.value)}
            className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-bold"
          >
            <option value="Low">Low (Shower alerts only)</option>
            <option value="Medium">Medium (Rain / Wind warnings)</option>
            <option value="High">High (Severe lightning warnings)</option>
          </select>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Medical Event Dispatch</label>
          <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl p-3">
            <span className="text-xs text-muted-foreground">Auto-dispatch EMT responders</span>
            <button
              onClick={() => setMedAutoDispatch(!medAutoDispatch)}
              className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                medAutoDispatch ? "bg-primary" : "bg-muted"
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  medAutoDispatch ? "translate-x-4" : "translate-x-0"
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
