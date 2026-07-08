import { createFileRoute } from "@tanstack/react-router";
import { BarChart3 } from "lucide-react";

export const Route = createFileRoute("/metrics")({
  component: MetricsPage,
});

function MetricsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <BarChart3 className="h-7 w-7 text-primary" />
        <div>
          <h1 className="text-2xl font-bold tracking-tight">System Metrics</h1>
          <p className="text-xs text-muted-foreground mt-0.5">Stadium operations charts, telemetry metrics, and volunteer response graphs.</p>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-6 min-h-[400px] flex flex-col justify-between">
        <div className="flex flex-1 items-center justify-center border-2 border-dashed border-border rounded-xl bg-muted/20">
          <div className="text-center p-6 max-w-sm">
            <BarChart3 className="mx-auto h-8 w-8 text-muted-foreground/60 mb-3" />
            <h3 className="text-sm font-semibold">Charts Canvas</h3>
            <p className="text-xs text-muted-foreground mt-1">
              Time-series plots and historical telemetry comparison visual widgets.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
