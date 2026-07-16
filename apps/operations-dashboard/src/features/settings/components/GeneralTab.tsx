import { ExternalLink } from "lucide-react";

interface GeneralTabProps {
  backendUrl: string;
  setBackendUrl: (val: string) => void;
  frontendUrl: string;
  setFrontendUrl: (val: string) => void;
  environment: string;
  setEnvironment: (val: string) => void;
  deploymentStatus: string;
}

export function GeneralTab({
  backendUrl,
  setBackendUrl,
  frontendUrl,
  setFrontendUrl,
  environment,
  setEnvironment,
  deploymentStatus,
}: GeneralTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-black text-foreground">Environment & Application Settings</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Manage hosting URLs and deployment environment variables.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Backend Gateway URL</label>
          <input
            type="text"
            value={backendUrl}
            onChange={(e) => setBackendUrl(e.target.value)}
            className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Dashboard Client URL</label>
          <input
            type="text"
            value={frontendUrl}
            onChange={(e) => setFrontendUrl(e.target.value)}
            className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Target Environment</label>
          <select
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
            className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-bold"
          >
            <option value="Development">Development (Localhost)</option>
            <option value="Staging">Staging (QA Sandbox)</option>
            <option value="Production">Production (Live Operations)</option>
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Deployment Status</label>
          <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2">
            <span className="text-xs font-bold text-foreground">{deploymentStatus}</span>
            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-muted/20 p-4 space-y-2">
        <div className="flex justify-between text-xs">
          <span className="font-bold text-muted-foreground">Console Host Build</span>
          <span className="font-mono text-foreground">v0.9.4-rc2 (Hatch-Compiled)</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="font-bold text-muted-foreground">Git Commit Revision</span>
          <span className="font-mono text-foreground text-primary hover:underline cursor-pointer flex items-center gap-1">
            a82e9b1 <ExternalLink className="h-3 w-3" />
          </span>
        </div>
      </div>
    </div>
  );
}
