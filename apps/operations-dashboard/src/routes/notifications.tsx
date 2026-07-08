import { createFileRoute } from "@tanstack/react-router";
import { Bell } from "lucide-react";

export const Route = createFileRoute("/notifications")({
  component: NotificationsPage,
});

function NotificationsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Bell className="h-7 w-7 text-primary" />
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Notifications Log</h1>
          <p className="text-xs text-muted-foreground mt-0.5">Historical log of stadium broadcast alerts, dispatcher announcements, and audit traces.</p>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card p-6 min-h-[400px] flex flex-col justify-between">
        <div className="flex flex-1 items-center justify-center border-2 border-dashed border-border rounded-xl bg-muted/20">
          <span className="text-xs text-muted-foreground">Notifications Historical Log Table</span>
        </div>
      </div>
    </div>
  );
}
