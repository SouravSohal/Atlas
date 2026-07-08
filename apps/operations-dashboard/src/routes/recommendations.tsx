import { createFileRoute } from "@tanstack/react-router";
import { Compass } from "lucide-react";

export const Route = createFileRoute("/recommendations")({
  component: RecommendationsPage,
});

function RecommendationsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Compass className="h-7 w-7 text-primary" />
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Routing Recommendations</h1>
          <p className="text-xs text-muted-foreground mt-0.5">Decision-support routing suggestions, dispatcher overrides, and automation recommendations.</p>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-6 min-h-[400px] flex flex-col justify-between">
        <div className="flex flex-1 items-center justify-center border-2 border-dashed border-border rounded-xl bg-muted/20">
          <div className="text-center p-6 max-w-sm">
            <Compass className="mx-auto h-8 w-8 text-muted-foreground/60 mb-3" />
            <h3 className="text-sm font-semibold">Recommendations Engine</h3>
            <p className="text-xs text-muted-foreground mt-1">
              Deterministic routing logic lists and dispatch actions table.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
