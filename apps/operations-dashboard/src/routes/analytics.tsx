import { useState, useMemo, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useWebSocket } from "../providers/WebSocketProvider";
import {
  TrendingUp,
  Download,
  Filter,
  Brain,
  Clock,
  Users,
  AlertTriangle,
  Sparkles,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { fetchDashboardOverview } from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/analytics")({
  component: AnalyticsPage,
});

function AnalyticsPage() {
  const { subscribe, unsubscribe } = useWebSocket();
  const [timeRange, setTimeRange] = useState("match");
  const [filterZone, setFilterZone] = useState("all");
  const [filterType, setFilterType] = useState("all");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    subscribe("telemetry");
    return () => unsubscribe("telemetry");
  }, [subscribe, unsubscribe]);

  const overviewQuery = useQuery({
    queryKey: ["cc-overview"],
    queryFn: fetchDashboardOverview,
    refetchInterval: 5000,
  });

  const handleExport = (format: "CSV" | "PDF") => {
    setToastMessage(`Exporting operations report as ${format}...`);
    setTimeout(() => {
      setToastMessage(`Export completed: ATLAS_Operational_Report.${format.toLowerCase()}`);
      setTimeout(() => setToastMessage(null), 3000);
    }, 1500);
  };


  // Chart seed coordinates calculations
  const chartPoints = useMemo(() => {
    // 6 sample points mapping wait times over match timeline
    const waitTimes = [5, 12, 18, 8, 4, 2];
    const coordinates = waitTimes.map((time, idx) => `${idx * 100 + 40},${220 - time * 10}`);
    return coordinates.join(" ");
  }, []);

  const areaPoints = useMemo(() => {
    // 6 points mapping arrival outflows
    const arrivals = [10, 45, 85, 30, 10, 5];
    const path = arrivals.map((arr, idx) => `${idx * 100 + 40},${220 - arr * 2}`);
    return `40,240 ${path.join(" ")} 540,240`;
  }, []);

  if (overviewQuery.isLoading) {
    return <LoadingScreen />;
  }

  return (
    <div className="flex flex-col gap-6 text-foreground min-h-[calc(100vh-6rem)] relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-border pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500">
            <TrendingUp className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight uppercase">Operational Analytics</h1>
            <p className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
              Stadium Operational Metrics, Performance Analytics & AI Accuracy Audits
            </p>
          </div>
        </div>

        {/* Export buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport("CSV")}
            className="rounded-xl border border-border bg-card hover:bg-muted px-4 py-2.5 text-xs font-black uppercase tracking-wider flex items-center gap-1.5 transition-colors"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </button>
          <button
            onClick={() => handleExport("PDF")}
            className="rounded-xl bg-primary text-primary-foreground hover:opacity-90 px-4 py-2.5 text-xs font-black uppercase tracking-wider flex items-center gap-1.5 shadow-lg shadow-primary/10 transition-opacity"
          >
            <Download className="h-4 w-4" />
            Export PDF
          </button>
        </div>
      </div>

      {/* Analytics Filter Toolbar */}
      <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-4 flex flex-wrap items-center gap-4 justify-between">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Filter className="h-4 w-4" />
          <span className="text-[10px] font-black uppercase tracking-wider">Configure Filters</span>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer"
          >
            <option value="hour">Last 1 Hour</option>
            <option value="6hours">Last 6 Hours</option>
            <option value="match">Full Match Duration</option>
          </select>

          <select
            value={filterZone}
            onChange={(e) => setFilterZone(e.target.value)}
            className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer"
          >
            <option value="all">All Zones</option>
            <option value="gate1">Gate 1 Ingress</option>
            <option value="gate2">Gate 2 Exit</option>
            <option value="med">Medical Post Alpha</option>
          </select>

          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer"
          >
            <option value="all">All Incidents</option>
            <option value="crowd">Crowd Surge</option>
            <option value="medical">Medical emergency</option>
            <option value="weather">Heavy Rain</option>
          </select>
        </div>
      </div>

      {/* Grid of Key Performance Indicators */}
      <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
        {[
          { title: "Average Queue Time", value: "8.5 min", delta: "-3.2m", positive: true, icon: <Clock className="h-4 w-4 text-emerald-400" /> },
          { title: "Peak Density", value: "85%", delta: "+12%", positive: false, icon: <Users className="h-4 w-4 text-primary" /> },
          { title: "Incident Rate", value: "0.4 / hr", delta: "-0.2/h", positive: true, icon: <AlertTriangle className="h-4 w-4 text-destructive" /> },
          { title: "Rec Acceptance Rate", value: "94.5%", delta: "+2.5%", positive: true, icon: <Brain className="h-4 w-4 text-amber-500" /> },
        ].map((kpi, idx) => (
          <div key={idx} className="rounded-xl border border-border bg-card/45 backdrop-blur-md p-4 shadow flex items-center justify-between">
            <div>
              <span className="text-[8px] font-black text-muted-foreground uppercase tracking-widest block">{kpi.title}</span>
              <span className="text-2xl font-black mt-2 block">{kpi.value}</span>
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

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Chart 1: Queue Wait Time Trends (Line Chart) */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-5 shadow-lg">
          <span className="text-xs font-black text-primary uppercase tracking-widest block mb-4">
            Queue Wait Time Trends (Minutes vs Timeline)
          </span>
          <div className="w-full min-h-[260px] border border-border/40 bg-muted/15 rounded-xl p-3 flex items-center justify-center">
            <svg className="w-full h-full min-h-[220px]" viewBox="0 0 580 260">
              {/* Grid lines */}
              <line x1="40" y1="40" x2="540" y2="40" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="40" y1="100" x2="540" y2="100" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="40" y1="160" x2="540" y2="160" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="40" y1="220" x2="540" y2="220" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5" />

              {/* Y Axis labels */}
              <text x="30" y="44" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">20m</text>
              <text x="30" y="104" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">12m</text>
              <text x="30" y="164" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">6m</text>
              <text x="30" y="224" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">0m</text>

              {/* X Axis labels */}
              <text x="40" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">18:00</text>
              <text x="140" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">18:30</text>
              <text x="240" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">19:00</text>
              <text x="340" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">19:30</text>
              <text x="440" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">20:00</text>
              <text x="540" y="240" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">20:30</text>

              {/* Line path */}
              <polyline
                fill="none"
                stroke="#10b981"
                strokeWidth="3.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={chartPoints}
              />
            </svg>
          </div>
        </div>

        {/* Chart 2: Spectator Flow Rate (Area Chart) */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-5 shadow-lg">
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
            </svg>
          </div>
        </div>

        {/* Chart 3: Incident Severity Distributions (Bar Chart) */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-5 shadow-lg">
          <span className="text-xs font-black text-primary uppercase tracking-widest block mb-4">
            Active Incidents by Severity Classification
          </span>
          <div className="w-full min-h-[260px] border border-border/40 bg-muted/15 rounded-xl p-5 flex items-center justify-center">
            <svg className="w-full h-full min-h-[220px]" viewBox="0 0 580 260">
              <line x1="40" y1="40" x2="540" y2="40" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="40" y1="100" x2="540" y2="100" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="40" y1="160" x2="540" y2="160" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="40" y1="220" x2="540" y2="220" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5" />

              <text x="30" y="44" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">12</text>
              <text x="30" y="104" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">8</text>
              <text x="30" y="164" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">4</text>
              <text x="30" y="224" textAnchor="end" fill="gray" fontSize="8" fontWeight="bold">0</text>

              {/* Bar 1: Critical */}
              <rect x="80" y="140" width="60" height="80" rx="4" fill="#ef4444" opacity="0.8" />
              <text x="110" y="236" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">Critical</text>

              {/* Bar 2: High */}
              <rect x="200" y="80" width="60" height="140" rx="4" fill="#f59e0b" opacity="0.8" />
              <text x="230" y="236" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">High</text>

              {/* Bar 3: Medium */}
              <rect x="320" y="120" width="60" height="100" rx="4" fill="#3b82f6" opacity="0.8" />
              <text x="350" y="236" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">Medium</text>

              {/* Bar 4: Low */}
              <rect x="440" y="180" width="60" height="40" rx="4" fill="#10b981" opacity="0.8" />
              <text x="470" y="236" textAnchor="middle" fill="gray" fontSize="8" fontWeight="bold">Low</text>
            </svg>
          </div>
        </div>

        {/* Chart 4: Crowd Density Grid (Heatmap) */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-5 shadow-lg">
          <span className="text-xs font-black text-primary uppercase tracking-widest block mb-4">
            Zone Crowd Density Heatmap (Matrix grid)
          </span>
          <div className="w-full min-h-[260px] border border-border/40 bg-muted/15 rounded-xl p-5 flex flex-col gap-3 justify-center">
            {[
              { label: "Gate 1 Ingress", value: "85% (Critical)", color: "bg-destructive/40 text-destructive border-destructive/30" },
              { label: "Gate 2 Exit", value: "35% (Stable)", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
              { label: "Main Parking Area", value: "65% (Warning)", color: "bg-amber-500/10 text-amber-400 border-amber-500/20" },
              { label: "Central Food Plaza", value: "48% (Stable)", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
            ].map((cell, idx) => (
              <div key={idx} className={`rounded-xl border p-4 flex items-center justify-between ${cell.color}`}>
                <span className="text-xs font-black uppercase tracking-wider">{cell.label}</span>
                <span className="text-xs font-black font-mono">{cell.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Executive Summary Narrative */}
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

      {/* Floating Dynamic Toasts */}
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
    </div>
  );
}
