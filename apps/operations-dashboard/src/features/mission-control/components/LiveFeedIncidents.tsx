import { Zap, Sparkles, Activity, CheckCircle } from "lucide-react";

interface LiveFeedIncidentsProps {
  playbackActive: boolean;
  localNotifications: any[];
  incidents: any[];
  handleResolveIncident: (id: string) => void;
}

export function LiveFeedIncidents({
  playbackActive,
  localNotifications,
  incidents,
  handleResolveIncident,
}: LiveFeedIncidentsProps) {
  const unresolvedIncidents = incidents.filter((i) => !i.resolved);

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Live Feed Widget */}
      <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm text-left">
        <div className="mb-4">
          <h2 className="text-base font-bold flex items-center gap-2">
            <Zap className="h-4 w-4 text-amber-400" />
            Live Activity Feed
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">Real-time telemetry event streams and dispatcher updates.</p>
        </div>
        <div className="flex-1 overflow-y-auto space-y-2.5 text-left">
          {/* Show animated local notifications during playback */}
          {playbackActive &&
            localNotifications.map((notif) => (
              <div
                key={notif.id}
                className="flex items-start gap-2.5 p-2 bg-primary/5 border border-primary/20 rounded-xl text-xs animate-pulse"
              >
                <Sparkles className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <span className="font-bold text-primary block truncate">{notif.text}</span>
                  <span className="text-xs text-muted-foreground mt-0.5 block">{notif.timestamp}</span>
                </div>
              </div>
            ))}

          {incidents.length === 0 && localNotifications.length === 0 ? (
            <div className="text-xs text-muted-foreground py-4">No activity events.</div>
          ) : (
            incidents.map((inc: any) => (
              <div key={inc.id} className="flex items-start gap-2.5 p-2 border-b border-border/40 text-xs">
                <Activity className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <span className="font-semibold block text-foreground truncate">{inc.description}</span>
                  <span className="text-xs text-muted-foreground mt-0.5 block uppercase font-mono">
                    Type: {inc.incident_type} &bull; Timestamp: {new Date(inc.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Active Incidents Queue */}
      <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm text-left">
        <div className="mb-4">
          <h2 className="text-base font-bold">Active Incidents Queue</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Unresolved safety or medical logs under dispatch.</p>
        </div>
        <div className="flex-1 overflow-y-auto space-y-3">
          {unresolvedIncidents.length === 0 ? (
            <div className="text-xs text-muted-foreground text-center py-10 flex flex-col items-center justify-center gap-2">
              <CheckCircle className="h-8 w-8 text-emerald-500" />
              <span className="font-semibold">All incidents cleared.</span>
            </div>
          ) : (
            unresolvedIncidents.map((inc: any) => (
              <div
                key={inc.id}
                className="p-3 border border-border rounded-xl bg-muted/20 flex items-center justify-between gap-3 text-left animate-fadeIn"
              >
                <div className="flex flex-col gap-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-black px-1.5 py-0.5 rounded ${
                        inc.severity === "critical"
                          ? "bg-destructive/10 text-destructive border border-destructive/20 animate-pulse"
                          : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      }`}
                    >
                      {inc.severity.toUpperCase()}
                    </span>
                    <span className="text-xs font-bold text-muted-foreground uppercase">{inc.incident_type}</span>
                  </div>
                  <p className="text-xs font-semibold text-foreground truncate">{inc.description}</p>
                </div>
                <button
                  onClick={() => handleResolveIncident(inc.id)}
                  className="rounded-lg border border-border hover:bg-muted px-2.5 py-1 text-xs font-bold shrink-0 transition-colors focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 outline-none"
                >
                  Resolve
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
