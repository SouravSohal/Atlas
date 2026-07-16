import { RefreshCw, CheckCircle2 } from "lucide-react";

interface DatabaseTabProps {
  dbEngine: string;
  dbSyncStatus: "idle" | "syncing" | "success";
  handleSyncDatabase: () => void;
  lastDbSync: string;
  dbTotalRecords: number;
}

export function DatabaseTab({
  dbEngine,
  dbSyncStatus,
  handleSyncDatabase,
  lastDbSync,
  dbTotalRecords,
}: DatabaseTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-black text-foreground">Database Configuration</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Verify Google Cloud Firestore connectivity states and document sync details.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Database Engine</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-xs text-foreground font-bold">
            {dbEngine}
          </div>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Total Synced Documents</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground font-bold">
            {dbTotalRecords.toLocaleString()} docs
          </div>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Last Synchronization</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground">
            {lastDbSync}
          </div>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Database Health Status</label>
          <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2">
            <span className="text-xs font-bold text-foreground">Healthy</span>
            <span className="flex items-center gap-1 rounded bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 text-[9px] font-black text-emerald-400">
              NOMINAL
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleSyncDatabase}
          disabled={dbSyncStatus === "syncing"}
          className="px-4 py-2 bg-primary text-primary-foreground font-extrabold text-xs rounded-xl hover:bg-primary/95 transition-all shadow flex items-center gap-2"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${dbSyncStatus === "syncing" ? "animate-spin" : ""}`} />
          Trigger Synchronization
        </button>
        {dbSyncStatus === "success" && (
          <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4" /> Databases synchronized successfully
          </span>
        )}
      </div>
    </div>
  );
}
