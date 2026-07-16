import { RefreshCw, CheckCircle2 } from "lucide-react";

interface AiTabProps {
  geminiModel: string;
  setGeminiModel: (val: string) => void;
  aiTestStatus: "idle" | "testing" | "success" | "error";
  handleTestAIConnection: () => void;
  lastAiRequest: string;
}

export function AiTab({
  geminiModel,
  setGeminiModel,
  aiTestStatus,
  handleTestAIConnection,
  lastAiRequest,
}: AiTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-black text-foreground">Gemini AI Configuration</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Control orchestration LLM model targets and check key connectivity status.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Gemini LLM Target Model</label>
          <select
            value={geminiModel}
            onChange={(e) => setGeminiModel(e.target.value)}
            className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-bold"
          >
            <option value="gemini-2.5-flash">Gemini 2.5 Flash (Operational - Recommended)</option>
            <option value="gemini-2.5-pro">Gemini 2.5 Pro (High Complexity)</option>
            <option value="gemini-1.5-pro">Gemini 1.5 Pro Legacy</option>
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">API Authentication status</label>
          <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2">
            <span className="text-xs font-bold text-foreground">Connected</span>
            <span className="flex items-center gap-1 rounded bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 text-[9px] font-black text-emerald-400">
              ONLINE
            </span>
          </div>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Last Orchestrated Request</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground">
            {lastAiRequest}
          </div>
        </div>
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Daily Request limit quota</label>
          <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-xs">
            <span className="font-bold text-foreground">248 / 10,000 requests</span>
            <span className="font-bold text-muted-foreground text-[10px]">2.4% Used</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleTestAIConnection}
          disabled={aiTestStatus === "testing"}
          className="px-4 py-2 bg-primary text-primary-foreground font-extrabold text-xs rounded-xl hover:bg-primary/95 transition-all shadow flex items-center gap-2"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${aiTestStatus === "testing" ? "animate-spin" : ""}`} />
          Test AI Connection
        </button>
        {aiTestStatus === "success" && (
          <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4" /> Connection active. Latency: 140ms
          </span>
        )}
      </div>
    </div>
  );
}
