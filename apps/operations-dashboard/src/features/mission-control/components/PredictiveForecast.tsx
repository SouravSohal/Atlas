import { Brain, Zap, Clock, Users, ShieldCheck, Activity, AlertTriangle } from "lucide-react";

interface PredictiveForecastProps {
  predictionsQuery: any;
}

export function PredictiveForecast({ predictionsQuery }: PredictiveForecastProps) {
  const isFetching = predictionsQuery.isFetching;
  const data = predictionsQuery.data;

  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col shadow-sm text-left">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 border-b border-border/40 pb-4">
        <div>
          <h2 className="text-base font-bold flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-400 animate-pulse" />
            Gemini Predictive Intelligence
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Live forecasting models analyzing crowd flows, safety thresholds, and venue resources.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => predictionsQuery.refetch()}
            disabled={isFetching}
            className="rounded-lg border border-border bg-card hover:bg-muted px-3 py-1.5 text-xs font-bold text-foreground transition-all flex items-center gap-1.5 disabled:opacity-60"
          >
            <Zap className={`h-3 w-3 ${isFetching ? "animate-spin" : ""}`} />
            {isFetching ? "Analyzing..." : "Run Forecast"}
          </button>

          <div className="flex items-center gap-1.5 rounded-full border border-purple-500/20 bg-purple-500/10 px-3 py-1.5 text-[10px] font-bold text-purple-400 uppercase font-mono">
            Confidence: {data ? `${Math.round(data.confidence_score * 100)}%` : "N/A"}
          </div>
        </div>
      </div>

      {predictionsQuery.isLoading ? (
        <div className="text-xs text-muted-foreground text-center py-12 flex flex-col items-center justify-center gap-3">
          <div className="relative flex h-8 w-8 items-center justify-center">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-20" />
            <Brain className="h-6 w-6 text-purple-400 animate-pulse" />
          </div>
          <span>Running predictive analysis models...</span>
        </div>
      ) : predictionsQuery.error ? (
        <div className="text-xs text-destructive text-center py-10">
          Failed to load Gemini predictions. Ensure the backend server is running.
        </div>
      ) : !data ? (
        <div className="text-xs text-muted-foreground text-center py-10">
          No predictive data available.
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Object.entries({
            "Queue Growth": { data: data.queue_growth, icon: <Clock className="h-4 w-4 text-purple-400" /> },
            "Crowd Movement": { data: data.crowd_movement, icon: <Users className="h-4 w-4 text-purple-400" /> },
            "Volunteer Shortages": { data: data.volunteer_shortages, icon: <Brain className="h-4 w-4 text-purple-400" /> },
            "Medical Demand": { data: data.medical_demand, icon: <Activity className="h-4 w-4 text-purple-400" /> },
            "Transport Congestion": { data: data.transport_congestion, icon: <Zap className="h-4 w-4 text-purple-400" /> },
            "Gate Overload": { data: data.gate_overload, icon: <ShieldCheck className="h-4 w-4 text-purple-400" /> },
            "Parking Saturation": { data: data.parking_saturation, icon: <Activity className="h-4 w-4 text-purple-400" /> },
            "Weather Impact": { data: data.weather_impact, icon: <AlertTriangle className="h-4 w-4 text-purple-400" /> },
          }).map(([title, item]) => {
            const confidenceColor =
              item.data.confidence > 0.85
                ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
                : item.data.confidence > 0.7
                ? "text-amber-400 bg-amber-500/10 border-amber-500/20"
                : "text-red-400 bg-red-500/10 border-red-500/20";

            return (
              <div
                key={title}
                className="rounded-xl border border-border bg-card/65 p-4 hover:shadow-lg transition-all duration-300 flex flex-col justify-between text-left group hover:border-purple-500/30"
              >
                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400">
                        {item.icon}
                      </div>
                      <h4 className="text-xs font-black uppercase text-foreground">{title}</h4>
                    </div>
                    <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border ${confidenceColor}`}>
                      {Math.round(item.data.confidence * 100)}%
                    </span>
                  </div>

                  <div className="mt-2.5">
                    <span className="text-[8px] font-black uppercase tracking-wider text-purple-400 block font-mono">
                      Prediction
                    </span>
                    <p className="text-xs font-semibold text-foreground mt-0.5 leading-relaxed">
                      {item.data.prediction}
                    </p>
                  </div>

                  <div className="mt-2.5">
                    <span className="text-[8px] font-black uppercase tracking-wider text-muted-foreground block font-mono">
                      Reason
                    </span>
                    <p className="text-[10px] text-muted-foreground mt-0.5 leading-relaxed">
                      {item.data.reason}
                    </p>
                  </div>

                  <div className="mt-2.5 bg-purple-500/5 p-2 rounded-lg border border-purple-500/10">
                    <span className="text-[8px] font-black uppercase tracking-wider text-purple-400 block font-mono">
                      Suggested Mitigation
                    </span>
                    <p className="text-[10px] text-purple-200 mt-0.5 leading-relaxed font-medium">
                      {item.data.mitigation}
                    </p>
                  </div>
                </div>

                <div className="mt-4 pt-2.5 border-t border-border/40 flex items-center justify-between text-[9px] font-mono text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3 text-muted-foreground" />
                    {item.data.timeline}
                  </span>
                  <span className="opacity-0 group-hover:opacity-100 transition-opacity text-[8px] font-black text-purple-400 uppercase tracking-widest">
                    Live Alert
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
