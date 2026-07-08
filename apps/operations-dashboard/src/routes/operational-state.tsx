import { createFileRoute } from "@tanstack/react-router";
import { Activity } from "lucide-react";

export const Route = createFileRoute("/operational-state")({
  component: OperationalStatePage,
});

function OperationalStatePage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Activity className="h-7 w-7 text-primary animate-pulse" />
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Zone Operational State</h1>
          <p className="text-xs text-muted-foreground mt-0.5">Stadium sectors flow status, gate rates, and live occupancy.</p>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-6 min-h-[400px] flex flex-col justify-between">
        <div className="flex flex-1 items-center justify-center border-2 border-dashed border-border rounded-xl bg-muted/20">
          <div className="text-center p-6 max-w-sm">
            <Activity className="mx-auto h-8 w-8 text-muted-foreground/60 mb-3" />
            <h3 className="text-sm font-semibold">Zone Map & Heat grid</h3>
            <p className="text-xs text-muted-foreground mt-1">
              Visual grid overlay detailing crowd congestion and active status warnings per zone.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
