import { Download } from "lucide-react";

interface LogsTabProps {
  diagnosticLogs: string[];
}

export function LogsTab({ diagnosticLogs }: LogsTabProps) {
  const handleExportLogs = () => {
    const text = diagnosticLogs.join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "atlas_diagnostics.log";
    a.click();
  };

  return (
    <div className="flex-1 flex flex-col gap-4">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-lg font-black text-foreground">Logging & Diagnostics Console</h2>
          <p className="text-xs text-muted-foreground mt-0.5">Monitor real-time system executions, exceptions, and server diagnostics.</p>
        </div>
        <button
          onClick={handleExportLogs}
          className="px-3 py-1.5 border border-border bg-muted/40 text-foreground hover:bg-muted/80 rounded-xl font-extrabold text-[10px] transition-all flex items-center gap-1.5"
        >
          <Download className="h-3.5 w-3.5" />
          Export Logs
        </button>
      </div>

      {/* Terminal View */}
      <div className="flex-1 min-h-[300px] rounded-xl border border-border bg-black/90 p-4 font-mono text-[10px] text-emerald-400 overflow-y-auto space-y-2 text-left">
        {diagnosticLogs.map((log, idx) => (
          <div key={idx} className="leading-relaxed whitespace-pre-wrap">
            {log}
          </div>
        ))}
      </div>
    </div>
  );
}
