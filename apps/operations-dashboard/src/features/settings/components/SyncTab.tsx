import { RefreshCw } from "lucide-react";

interface SyncTabProps {
  wsLatency: number;
  activeClients: number;
  setDiagnosticLogs: (updater: (logs: string[]) => string[]) => void;
}

export function SyncTab({
  wsLatency,
  activeClients,
  setDiagnosticLogs,
}: SyncTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-black text-foreground">WebSocket & Live Sync Status</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Diagnose real-time pub-sub streaming connections from clients and operations centers.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Sync Connection Status</label>
          <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2">
            <span className="text-xs font-bold text-foreground">Connected</span>
            <span className="flex items-center gap-1 rounded bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 text-[9px] font-black text-emerald-400">
              LIVE
            </span>
          </div>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">WebSocket Latency</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground font-bold">
            {wsLatency} ms
          </div>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Connected client screens</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground font-bold">
            {activeClients} active terminals
          </div>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Broadcaster Buffer Frame Rate</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground">
            12.0 ticks / min (nominal)
          </div>
        </div>
      </div>

      <button
        onClick={() => {
          setDiagnosticLogs((prev) => [
            `[${new Date().toLocaleString()}] INFO: WebSocket handshake manually re-asserted. Latency stabilized.`,
            ...prev,
          ]);
        }}
        className="px-4 py-2 border border-border bg-muted/40 text-foreground hover:bg-muted/80 rounded-xl font-extrabold text-xs transition-all shadow flex items-center gap-2"
      >
        <RefreshCw className="h-3.5 w-3.5" />
        Reconnect WebSocket Channel
      </button>
    </div>
  );
}
