import {
  Clock,
  Users,
  AlertTriangle,
  Brain,
  Sparkles,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// AnalyticsKpiCards
export function AnalyticsKpiCards() {
  const kpis = [
    { title: "Average Queue Time", value: "8.5 min", delta: "-3.2m", positive: true, icon: <Clock className="h-4 w-4 text-emerald-400" /> },
    { title: "Peak Density", value: "85%", delta: "+12%", positive: false, icon: <Users className="h-4 w-4 text-primary" /> },
    { title: "Incident Rate", value: "0.4 / hr", delta: "-0.2/h", positive: true, icon: <AlertTriangle className="h-4 w-4 text-destructive" /> },
    { title: "Rec Acceptance Rate", value: "94.5%", delta: "+2.5%", positive: true, icon: <Brain className="h-4 w-4 text-amber-500" /> },
  ];

  return (
    <div className="grid gap-4 grid-cols-2 md:grid-cols-4 text-left">
      {kpis.map((kpi, idx) => (
        <div key={idx} className="rounded-xl border border-border bg-card/45 backdrop-blur-md p-4 shadow flex items-center justify-between">
          <div>
            <span className="text-[8px] font-black text-muted-foreground uppercase tracking-widest block">{kpi.title}</span>
            <span className="text-2xl font-black mt-2 block text-foreground">{kpi.value}</span>
            <div className="flex items-center gap-1 mt-1">
              <span className={`text-[9px] font-bold uppercase ${kpi.positive ? "text-emerald-400" : "text-destructive"}`}>
                {kpi.delta}
              </span>
              <span className="text-[8px] text-muted-foreground">vs baseline</span>
            </div>
          </div>
          <div className="p-2.5 rounded-xl bg-muted/25 border border-border/40 shrink-0">
            {kpi.icon}
          </div>
        </div>
      ))}
    </div>
  );
}

// QueueWaitTimeChart
interface QueueWaitTimeChartProps {
  chartPoints: string;
  playbackActive: boolean;
  playbackStep: number;
  stepSize: number;
  waitTimes: number[];
}
export function QueueWaitTimeChart({
  chartPoints,
  playbackActive,
  playbackStep,
  stepSize,
  waitTimes,
}: QueueWaitTimeChartProps) {
  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-5 shadow-lg text-left">
      <span className="text-xs font-black text-primary uppercase tracking-widest block mb-4">
        Queue Wait Time Trends (Minutes vs Timeline)
      </span>
      <div className="w-full min-h-[260px] border border-border/40 bg-muted/15 rounded-xl p-3 flex items-center justify-center">
        <svg className="w-full h-full min-h-[220px]" viewBox="0 0 580 260">
          <line x1="40" y1="40" x2="540" y2="40" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1="40" y1="100" x2="540" y2="100" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1="40" y1="160" x2="540" y2="160" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1="40" y1="220" x2="540" y2="220" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5" />

          <text x="30" y="44" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">20m</text>
          <text x="30" y="104" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">12m</text>
          <text x="30" y="164" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">6m</text>
          <text x="30" y="224" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">0m</text>

          <text x="40" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">18:00</text>
          <text x="140" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">18:30</text>
          <text x="240" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">19:00</text>
          <text x="340" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">19:30</text>
          <text x="440" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">20:00</text>
          <text x="540" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">20:30</text>

          <polyline
            fill="none"
            stroke="#10b981"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={chartPoints}
          />

          {playbackActive && (
            <>
              <line
                x1={playbackStep * stepSize + 40}
                y1="40"
                x2={playbackStep * stepSize + 40}
                y2="220"
                stroke="rgba(16, 185, 129, 0.4)"
                strokeWidth="1.5"
                strokeDasharray="4 4"
              />
              <circle
                cx={playbackStep * stepSize + 40}
                cy={220 - (waitTimes[playbackStep] || 0) * 6}
                r="5"
                fill="#10b981"
                className="animate-pulse"
              />
            </>
          )}
        </svg>
      </div>
    </div>
  );
}

// SpectatorFlowChart
interface SpectatorFlowChartProps {
  areaPoints: string;
  playbackActive: boolean;
  playbackStep: number;
  stepSize: number;
  arrivals: number[];
}
export function SpectatorFlowChart({
  areaPoints,
  playbackActive,
  playbackStep,
  stepSize,
  arrivals,
}: SpectatorFlowChartProps) {
  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-5 shadow-lg text-left">
      <span className="text-xs font-black text-primary uppercase tracking-widest block mb-4">
        Spectator Inflow Outflow Curve (Flow Volume)
      </span>
      <div className="w-full min-h-[260px] border border-border/40 bg-muted/15 rounded-xl p-3 flex items-center justify-center">
        <svg className="w-full h-full min-h-[220px]" viewBox="0 0 580 260">
          <line x1="40" y1="40" x2="540" y2="40" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1="40" y1="100" x2="540" y2="100" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1="40" y1="160" x2="540" y2="160" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1="40" y1="220" x2="540" y2="220" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5" />

          <text x="30" y="44" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">10k</text>
          <text x="30" y="104" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">6k</text>
          <text x="30" y="164" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">3k</text>
          <text x="30" y="224" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">0</text>

          <polygon
            fill="rgba(59, 130, 246, 0.15)"
            stroke="#3b82f6"
            strokeWidth="3.5"
            points={areaPoints}
          />

          {playbackActive && (
            <>
              <line
                x1={playbackStep * stepSize + 40}
                y1="40"
                x2={playbackStep * stepSize + 40}
                y2="220"
                stroke="rgba(59, 130, 246, 0.4)"
                strokeWidth="1.5"
                strokeDasharray="4 4"
              />
              <circle
                cx={playbackStep * stepSize + 40}
                cy={220 - (arrivals[playbackStep] || 0) * 1.8}
                r="5"
                fill="#3b82f6"
                className="animate-pulse"
              />
            </>
          )}
        </svg>
      </div>
    </div>
  );
}

// IncidentSeverityChart
interface IncidentSeverityChartProps {
  maxCount: number;
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  critHeight: number;
  highHeight: number;
  medHeight: number;
  lowHeight: number;
}
export function IncidentSeverityChart({
  maxCount,
  criticalCount,
  highCount,
  mediumCount,
  lowCount,
  critHeight,
  highHeight,
  medHeight,
  lowHeight,
}: IncidentSeverityChartProps) {
  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-5 shadow-lg text-left">
      <span className="text-xs font-black text-primary uppercase tracking-widest block mb-4">
        Active Incidents by Severity Classification
      </span>
      <div className="w-full min-h-[260px] border border-border/40 bg-muted/15 rounded-xl p-5 flex items-center justify-center">
        <svg className="w-full h-full min-h-[220px]" viewBox="0 0 580 260">
          <line x1="40" y1="40" x2="540" y2="40" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1="40" y1="100" x2="540" y2="100" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1="40" y1="160" x2="540" y2="160" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
          <line x1="40" y1="220" x2="540" y2="220" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5" />

          <text x="30" y="44" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">{maxCount}</text>
          <text x="30" y="104" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">{Math.round(maxCount * 0.67)}</text>
          <text x="30" y="164" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">{Math.round(maxCount * 0.33)}</text>
          <text x="30" y="224" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">0</text>

          {/* Bar 1: Critical */}
          <rect x="80" y={220 - rxSafe(critHeight)} width="60" height={rxSafe(critHeight)} rx="4" fill="#ef4444" opacity="0.8" />
          {criticalCount > 0 && <text x="110" y={Math.max(50, 215 - critHeight)} textAnchor="middle" fill="#ef4444" fontSize="9" fontWeight="extrabold">{criticalCount}</text>}
          <text x="110" y="236" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">Critical</text>

          {/* Bar 2: High */}
          <rect x="200" y={220 - rxSafe(highHeight)} width="60" height={rxSafe(highHeight)} rx="4" fill="#f59e0b" opacity="0.8" />
          {highCount > 0 && <text x="230" y={Math.max(50, 215 - highHeight)} textAnchor="middle" fill="#f59e0b" fontSize="9" fontWeight="extrabold">{highCount}</text>}
          <text x="230" y="236" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">High</text>

          {/* Bar 3: Medium */}
          <rect x="320" y={220 - rxSafe(medHeight)} width="60" height={rxSafe(medHeight)} rx="4" fill="#3b82f6" opacity="0.8" />
          {mediumCount > 0 && <text x="350" y={Math.max(50, 215 - medHeight)} textAnchor="middle" fill="#3b82f6" fontSize="9" fontWeight="extrabold">{mediumCount}</text>}
          <text x="350" y="236" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">Medium</text>

          {/* Bar 4: Low */}
          <rect x="440" y={220 - rxSafe(lowHeight)} width="60" height={rxSafe(lowHeight)} rx="4" fill="#10b981" opacity="0.8" />
          {lowCount > 0 && <text x="470" y={Math.max(50, 215 - lowHeight)} textAnchor="middle" fill="#10b981" fontSize="9" fontWeight="extrabold">{lowCount}</text>}
          <text x="470" y="236" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">Low</text>
        </svg>
      </div>
    </div>
  );
}

function rxSafe(val: number) {
  return Math.max(0, val);
}

// CrowdDensityHeatmap
export function CrowdDensityHeatmap() {
  const cells = [
    { label: "Gate 1 Ingress", value: "85% (Critical)", color: "bg-destructive/40 text-destructive border-destructive/30" },
    { label: "Gate 2 Exit", value: "35% (Stable)", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
    { label: "Main Parking Area", value: "65% (Warning)", color: "bg-amber-500/10 text-amber-400 border-amber-500/20" },
    { label: "Central Food Plaza", value: "48% (Stable)", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
  ];

  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-5 shadow-lg text-left">
      <span className="text-xs font-black text-primary uppercase tracking-widest block mb-4">
        Zone Crowd Density Heatmap (Matrix grid)
      </span>
      <div className="w-full min-h-[260px] border border-border/40 bg-muted/15 rounded-xl p-5 flex flex-col gap-3 justify-center">
        {cells.map((cell, idx) => (
          <div key={idx} className={`rounded-xl border p-4 flex items-center justify-between ${cell.color}`}>
            <span className="text-xs font-black uppercase tracking-wider">{cell.label}</span>
            <span className="text-xs font-black font-mono">{cell.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// AiExecutiveSummary
export function AiExecutiveSummary() {
  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 shadow-lg text-left relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
      
      <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
        <span className="text-xs font-black text-primary uppercase tracking-widest flex items-center gap-1.5">
          <Brain className="h-4 w-4 text-primary animate-pulse" />
          AI Executive Summary
        </span>
        <span className="text-[9px] font-mono text-muted-foreground">GENERATED LIVE</span>
      </div>

      <p className="text-xs font-semibold leading-relaxed text-foreground/90">
        Match operations reached an overall stabilization index of 95% after successful volunteer deployment. Ingress congestion spikes experienced at 18:30 (T-minus 30) were mitigated via Gate 2 rerouting directives, bringing average queue wait duration down from 18m to 8.5m. AI prediction accuracy score registers at 98.2% based on turnstile sensor aggregates.
      </p>
    </div>
  );
}

// AnalyticsToast
interface AnalyticsToastProps {
  toastMessage: string | null;
}
export function AnalyticsToast({ toastMessage }: AnalyticsToastProps) {
  return (
    <AnimatePresence>
      {toastMessage && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          className="fixed bottom-6 right-6 z-50 rounded-xl border border-primary/30 bg-card/95 backdrop-blur-md px-4 py-3 shadow-xl text-xs font-bold text-primary flex items-center gap-2 uppercase tracking-wide"
        >
          <Sparkles className="h-4 w-4 animate-spin text-primary" />
          {toastMessage}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
