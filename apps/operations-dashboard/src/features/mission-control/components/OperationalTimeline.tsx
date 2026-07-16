import { Clock } from "lucide-react";

interface OperationalTimelineProps {
  incidents: any[];
}

export function OperationalTimeline({ incidents }: OperationalTimelineProps) {
  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm text-left">
      <div className="mb-4">
        <h2 className="text-base font-bold">Operational Timeline</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Chronological sequence of logs in the current shift.</p>
      </div>
      <div className="flex-1 overflow-y-auto pl-6 border-l border-border space-y-5 text-left">
        {incidents.length === 0 ? (
          <div className="text-xs text-muted-foreground py-4">No events logged.</div>
        ) : (
          incidents.slice(0, 5).map((inc: any) => (
            <div key={inc.id} className="relative text-left">
              <div className="absolute -left-[31px] mt-0.5 rounded-full bg-card border-2 border-border p-1 text-primary">
                <Clock className="h-3 w-3" />
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-bold">{inc.resolved ? "Incident Resolved" : "Incident Created"}</span>
                <span className="text-xs text-muted-foreground mt-0.5">{inc.description}</span>
                <span className="text-xs text-primary font-bold mt-1 font-mono">
                  {new Date(inc.created_at).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
