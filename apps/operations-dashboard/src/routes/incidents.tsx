import { createFileRoute } from "@tanstack/react-router";
import { AlertTriangle, Plus, Filter } from "lucide-react";

export const Route = createFileRoute("/incidents")({
  component: IncidentsPage,
});

function IncidentsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="h-7 w-7 text-destructive animate-pulse" />
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Active Incidents</h1>
            <p className="text-xs text-muted-foreground mt-0.5">Real-time alerts, hazard warnings, and safety issues.</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-xs font-semibold text-foreground hover:bg-muted transition-colors">
            <Filter className="h-4 w-4" />
            Filters
          </button>
          <button className="flex items-center gap-2 rounded-xl bg-destructive px-4 py-2.5 text-xs font-semibold text-destructive-foreground hover:opacity-90 transition-opacity">
            <Plus className="h-4 w-4" />
            Raise Incident
          </button>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-6 min-h-[400px] flex flex-col justify-between">
        <div className="flex flex-1 items-center justify-center border-2 border-dashed border-border rounded-xl bg-muted/20">
          <div className="text-center p-6 max-w-sm">
            <AlertTriangle className="mx-auto h-8 w-8 text-muted-foreground/60 mb-3" />
            <h3 className="text-sm font-semibold">Incident Dashboard Canvas</h3>
            <p className="text-xs text-muted-foreground mt-1">
              Provides incident lists, geographical maps markers, and dispatch dispatcher assignments.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
