interface AboutTabProps {}

export function AboutTab({}: AboutTabProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-primary to-violet-600 flex items-center justify-center shadow-lg">
          <span className="font-extrabold text-white text-3xl">A</span>
        </div>
        <div>
          <h2 className="text-xl font-black text-foreground">ATLAS Stadium Intelligence</h2>
          <span className="text-xs text-muted-foreground block font-mono">Build 0.9.4-rc2 (Hatch / Hatchling)</span>
        </div>
      </div>

      <div className="space-y-4 text-xs leading-relaxed text-muted-foreground">
        <p>
          <strong>ATLAS</strong> (Adaptive Tournament Logistics & Autonomous Stadium Intelligence) is a state-of-the-art Digital Twin orchestration suite. It synchronizes live crowd density sensors, coordinates medical/security anomalies, and generates logistical recommendation actions using Gemini LLM reasoning models.
        </p>

        <div className="grid gap-3 sm:grid-cols-2 pt-4 border-t border-border/40">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase block">AI Reasoning Engine</span>
            <span className="font-bold text-foreground block">Gemini 2.5 Flash APIs</span>
          </div>
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase block">Graph Layout Compiler</span>
            <span className="font-bold text-foreground block">Dagre Automatic Solver v0.8.5</span>
          </div>
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase block">Websocket Router</span>
            <span className="font-bold text-foreground block">FastAPI Broadcast PubSub</span>
          </div>
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase block">Database Storage</span>
            <span className="font-bold text-foreground block">Google Cloud Firestore (atlas-01)</span>
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-border/40 text-[10px] text-muted-foreground">
        © 2026 AdiMita Technologies. Under LICENSE. All rights reserved.
      </div>
    </div>
  );
}
