import { createFileRoute } from "@tanstack/react-router";
import { MapPin } from "lucide-react";

export const Route = createFileRoute("/navigation")({
  component: NavigationPage,
});

function NavigationPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <MapPin className="h-7 w-7 text-primary" />
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Stadium Navigation</h1>
          <p className="text-xs text-muted-foreground mt-0.5">Route mapping, waypoint routing, and exit planning coordinates.</p>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-6 min-h-[400px] flex flex-col justify-between">
        <div className="flex flex-1 items-center justify-center border-2 border-dashed border-border rounded-xl bg-muted/20">
          <span className="text-xs text-muted-foreground">Mapping Coordinate System Canvas</span>
        </div>
      </div>
    </div>
  );
}
