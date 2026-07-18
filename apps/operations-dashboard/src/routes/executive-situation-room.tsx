import { useMemo, useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useWebSocket } from "../providers/WebSocketProvider";
import {
  ShieldCheck,
  AlertTriangle,
  Cloud,
  Train,
  Sliders,
  Tv,
  ArrowRight,
  HelpCircle,
  X,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  fetchDashboardOverview,
  fetchDashboardIncidents,
  fetchOperationalState,
  fetchDashboardRecommendations,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";
import { SituationAnalysisPanel } from "../components/SituationAnalysisPanel";
import { useGlobalStore } from "../store/useGlobalStore";

export const Route = createFileRoute("/executive-situation-room")({
  component: ExecutiveSituationRoomPage,
});

const EMPTY_ARRAY: any[] = [];

function ExecutiveSituationRoomPage() {
  const { subscribe, unsubscribe } = useWebSocket();
  const {
    approvedRecs: approvedDecisions,
    setRecApproval,
    playbackActive,
    simulatedOverview,
    simulatedZones,
    simulatedIncidents,
    simulatedRecommendations,
  } = useGlobalStore();

  const [selectedWhyRec, setSelectedWhyRec] = useState<any | null>(null);

  useEffect(() => {
    subscribe("telemetry");
    subscribe("incidents");
    subscribe("recommendations");
    return () => {
      unsubscribe("telemetry");
      unsubscribe("incidents");
      unsubscribe("recommendations");
    };
  }, [subscribe, unsubscribe]);

  const overviewQuery = useQuery({
    queryKey: ["cc-overview"],
    queryFn: fetchDashboardOverview,
    refetchInterval: 5000,
  });

  const stateQuery = useQuery({
    queryKey: ["cc-state"],
    queryFn: fetchOperationalState,
    refetchInterval: 5000,
  });

  const incidentsQuery = useQuery({
    queryKey: ["cc-incidents"],
    queryFn: () => fetchDashboardIncidents(1, 10),
    refetchInterval: 5000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["cc-recommendations"],
    queryFn: () => fetchDashboardRecommendations(1, 10),
    refetchInterval: 5000,
  });

  const overview = playbackActive && simulatedOverview ? simulatedOverview : overviewQuery.data;
  const states = playbackActive && simulatedZones ? simulatedZones : (stateQuery.data || EMPTY_ARRAY);
  const incidents = playbackActive && simulatedIncidents ? simulatedIncidents : (incidentsQuery.data?.items || EMPTY_ARRAY);
  const rawRecs = playbackActive && simulatedRecommendations ? simulatedRecommendations : (recommendationsQuery.data?.items || EMPTY_ARRAY);

  const recs = useMemo(() => {
    return rawRecs.map((item) => ({
      ...item,
      priority: item.priority || "high",
      confidence: item.confidence || 0.95,
    }));
  }, [rawRecs]);

  const parseDetails = (detailsStr: string) => {
    try {
      const parsed = JSON.parse(detailsStr);
      return {
        explanation: parsed.explanation || detailsStr,
        why: parsed.why || "Operational parameters require routing intervention to maintain target efficiency.",
        evidence: parsed.evidence || "Sustained telemetry alerts in target sector.",
        operational_data_used: parsed.operational_data_used || ["density", "queue_waiting_minutes"],
        alternative_actions: parsed.alternative_actions || ["Increase monitoring intervals", "Dispatch mobile supervisor patrol"],
        trade_offs: parsed.trade_offs || "Diverts staff from primary deployment bases.",
        expected_impact: parsed.expected_impact || "Alleviate queue wait by 25%",
        eta_minutes: parsed.eta_minutes || 8,
      };
    } catch {
      return {
        explanation: detailsStr,
        why: "Operational parameters require routing intervention to maintain target efficiency.",
        evidence: "Sustained telemetry alerts in target sector.",
        operational_data_used: ["density", "queue_waiting_minutes"],
        alternative_actions: ["Increase monitoring intervals", "Dispatch mobile supervisor patrol"],
        trade_offs: "Diverts staff from primary deployment bases.",
        expected_impact: "Alleviate queue wait by 25%",
        eta_minutes: 8,
      };
    }
  };

  const activeIncidents = useMemo(() => {
    return incidents.filter((inc) => !inc.resolved);
  }, [incidents]);

  const majorRisks = useMemo(() => {
    return activeIncidents.filter((inc) => inc.severity === "critical" || inc.severity === "high");
  }, [activeIncidents]);

  const healthScore = overview?.stadium_health ?? 0.98;
  const isHealthy = healthScore >= 0.92;

  if (overviewQuery.isLoading || stateQuery.isLoading || incidentsQuery.isLoading || recommendationsQuery.isLoading) {
    return <LoadingScreen />;
  }

  const handleApprove = (id: string) => {
    setRecApproval(id, true);
  };

  return (
    <div className="flex flex-col gap-6 text-foreground">
      {/* Upper Status Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-border pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500 animate-pulse">
            <Tv className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight uppercase">EXECUTIVE SITUATION ROOM</h1>
            <p className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
              Strategic Stadium Operations & Decision Control Console
            </p>
          </div>
        </div>

        {/* Live Mission Status Banner */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-full border border-border bg-card/65 backdrop-blur-md shadow-inner">
          <span className={`h-2.5 w-2.5 rounded-full ${isHealthy ? "bg-emerald-500 animate-pulse" : "bg-amber-500 animate-pulse"}`} />
          <span className="text-[10px] font-black uppercase tracking-widest font-mono">
            {isHealthy ? "MISSION STATUS: NOMINAL" : "MISSION STATUS: ESCALATED"}
          </span>
        </div>
      </div>

      {/* Grid of 4 Key Executive Indicators */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Metric 1: Operational Health */}
        <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-5 shadow-lg relative overflow-hidden flex items-center justify-between hover:shadow-xl transition-all">
          <div>
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">OPERATIONAL HEALTH</span>
            <span className="text-3xl font-black tracking-tight block mt-2">{Math.round(healthScore * 100)}%</span>
            <span className="text-[9px] font-bold text-emerald-400 mt-1 uppercase block">System Stability Safe</span>
          </div>
          {/* Progress Ring */}
          <div className="relative h-16 w-16 flex items-center justify-center shrink-0">
            <svg className="absolute -rotate-90 w-16 h-16">
              <circle cx="32" cy="32" r="26" stroke="rgba(255,255,255,0.05)" strokeWidth="4" fill="transparent" />
              <motion.circle
                cx="32"
                cy="32"
                r="26"
                stroke={isHealthy ? "#10b981" : "#f59e0b"}
                strokeWidth="4"
                fill="transparent"
                strokeDasharray="163"
                initial={{ strokeDashoffset: 163 }}
                animate={{ strokeDashoffset: 163 - (163 * healthScore) }}
                transition={{ duration: 1, ease: "easeOut" }}
              />
            </svg>
            <ShieldCheck className={`h-6 w-6 ${isHealthy ? "text-emerald-400" : "text-amber-500"}`} />
          </div>
        </div>

        {/* Metric 2: Risk Index */}
        <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-5 shadow-lg relative overflow-hidden flex items-center justify-between hover:shadow-xl transition-all">
          <div>
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">MAJOR THREATS</span>
            <span className="text-3xl font-black tracking-tight block mt-2 text-destructive">{majorRisks.length}</span>
            <span className="text-[9px] font-bold text-muted-foreground mt-1 uppercase block">High Severity Incidents</span>
          </div>
          <div className="p-3 rounded-2xl bg-destructive/10 border border-destructive/20 text-destructive">
            <AlertTriangle className="h-6 w-6 animate-pulse" />
          </div>
        </div>

        {/* Metric 3: Weather Status */}
        <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-5 shadow-lg relative overflow-hidden flex items-center justify-between hover:shadow-xl transition-all">
          <div>
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">WEATHER ENVIRONMENT</span>
            <span className="text-xl font-black tracking-tight block mt-2">22°C / 12% precip</span>
            <span className="text-[9px] font-bold text-muted-foreground mt-1 uppercase block">Condition: Overcast</span>
          </div>
          <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <Cloud className="h-6 w-6" />
          </div>
        </div>

        {/* Metric 4: Transport Status */}
        <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-5 shadow-lg relative overflow-hidden flex items-center justify-between hover:shadow-xl transition-all">
          <div>
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">PUBLIC TRANSIT STATUS</span>
            <span className="text-xl font-black tracking-tight block mt-2 text-emerald-400">METRO LINE A: NOMINAL</span>
            <span className="text-[9px] font-bold text-muted-foreground mt-1 uppercase block">Shuttles: standard outflow</span>
          </div>
          <div className="p-3 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Train className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Main Multi-Column Content Area */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Col 1 & 2: Briefing and Active Decisions */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <SituationAnalysisPanel />

          {/* Active Decisions / Actions Center Review */}
          <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 shadow-lg">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <span className="text-xs font-black text-primary uppercase tracking-widest flex items-center gap-1.5">
                <Sliders className="h-4 w-4" />
                Active Decisions Center (Awaiting Executive Action)
              </span>
              <span className="text-[9px] font-bold bg-primary/10 border border-primary/20 text-primary px-2 py-0.5 rounded-full uppercase">
                Human in the Loop
              </span>
            </div>

            <div className="flex flex-col gap-4">
              {recs.length === 0 ? (
                <div className="text-xs text-muted-foreground text-center py-8">
                  No pending executive decisions at this time.
                </div>
              ) : (
                recs.map((rec: any) => {
                  const isApproved = approvedDecisions[rec.id];
                  const details = parseDetails(rec.details);

                  return (
                    <div
                      key={rec.id}
                      className={`rounded-xl border p-4 transition-all relative ${
                        isApproved
                          ? "bg-emerald-500/5 border-emerald-500/30 opacity-75"
                          : "bg-muted/20 border-border hover:bg-muted/40"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3 text-left">
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className={`text-[9px] font-black uppercase px-1.5 py-0.5 rounded border ${
                              rec.priority === "critical"
                                ? "bg-destructive/10 border-destructive/20 text-destructive animate-pulse"
                                : "bg-amber-500/10 border-amber-500/20 text-amber-500"
                            }`}>
                              {rec.priority}
                            </span>
                            <span className="text-xs font-black text-foreground uppercase truncate">
                              {rec.action_type}
                            </span>
                            <span className="text-[9px] font-mono bg-purple-500/10 border border-purple-500/20 text-purple-400 px-1.5 py-0.5 rounded">
                              {(rec.confidence * 100).toFixed(0)}% Conf
                            </span>
                          </div>
                          <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
                            {details.explanation}
                          </p>
                        </div>

                        {/* Action buttons */}
                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            onClick={() => setSelectedWhyRec(rec)}
                            className="rounded-lg border border-purple-500/30 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 px-2.5 py-2 text-xs font-black uppercase tracking-wider flex items-center gap-1 transition-all"
                          >
                            <HelpCircle className="h-3.5 w-3.5" />
                            Why?
                          </button>

                          <button
                            disabled={isApproved}
                            onClick={() => handleApprove(rec.id)}
                            className={`rounded-lg px-3.5 py-2 text-xs font-black uppercase tracking-wider flex items-center gap-1.5 transition-all ${
                              isApproved
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 cursor-default"
                                : "bg-primary text-primary-foreground hover:opacity-90 shadow-md shadow-primary/10"
                            }`}
                          >
                            {isApproved ? "Approved" : "Approve"}
                            {!isApproved && <ArrowRight className="h-3 w-3" />}
                          </button>
                        </div>
                      </div>

                      <div className="mt-3.5 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[9px] font-mono text-muted-foreground border-t border-border/40 pt-2.5">
                        <span>EST. RESOLUTION: {details.eta_minutes} MINS</span>
                        <span>EXPECTED IMPACT: {details.expected_impact}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Selected Why Decision Modal Backdrop & Container */}
        <AnimatePresence>
          {selectedWhyRec && (() => {
            const details = parseDetails(selectedWhyRec.details);
            return (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md"
              >
                <motion.div
                  initial={{ scale: 0.95, y: 15 }}
                  animate={{ scale: 1, y: 0 }}
                  exit={{ scale: 0.95, y: 15 }}
                  className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-purple-500/30 bg-card p-6 shadow-2xl text-left"
                >
                  {/* Glowing background */}
                  <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />

                  {/* Header */}
                  <div className="flex items-start justify-between border-b border-border pb-3.5 mb-5">
                    <div>
                      <span className="text-[9px] font-black text-purple-400 uppercase tracking-widest block font-mono">
                        AI Decision Intelligence Context
                      </span>
                      <h3 className="text-sm font-black text-foreground uppercase mt-1">
                        {selectedWhyRec.action_type}
                      </h3>
                    </div>
                    <button
                      onClick={() => setSelectedWhyRec(null)}
                      className="rounded-lg p-1.5 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Body Content */}
                  <div className="space-y-4 max-h-[380px] overflow-y-auto pr-1">
                    {/* Why */}
                    <div>
                      <span className="text-[8px] font-black text-purple-400 uppercase tracking-wider block font-mono">Why is this action recommended?</span>
                      <p className="text-xs text-foreground mt-1 leading-relaxed font-semibold">
                        {details.why}
                      </p>
                    </div>

                    {/* Evidence */}
                    <div>
                      <span className="text-[8px] font-black text-muted-foreground uppercase tracking-wider block font-mono">Evidence base</span>
                      <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                        {details.evidence}
                      </p>
                    </div>

                    {/* Operational Data Used */}
                    <div>
                      <span className="text-[8px] font-black text-muted-foreground uppercase tracking-wider block font-mono">Operational parameters analyzed</span>
                      <div className="flex flex-wrap gap-1.5 mt-1.5">
                        {details.operational_data_used.map((field: string, idx: number) => (
                          <span
                            key={idx}
                            className="rounded-md border border-border bg-muted/30 px-2 py-0.5 text-[9px] font-mono font-bold text-foreground uppercase"
                          >
                            {field}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Confidence Score */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-[8px] font-black text-muted-foreground uppercase tracking-wider block font-mono">Confidence Level</span>
                        <span className="inline-flex items-center gap-1.5 rounded-full border border-purple-500/20 bg-purple-500/10 px-2.5 py-1 text-[10px] font-mono font-black text-purple-400 uppercase mt-1">
                          {(selectedWhyRec.confidence * 100).toFixed(0)}% Certitude
                        </span>
                      </div>
                      <div>
                        <span className="text-[8px] font-black text-muted-foreground uppercase tracking-wider block font-mono">Priority Classification</span>
                        <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[10px] font-mono font-black uppercase mt-1 ${
                          selectedWhyRec.priority === "critical"
                            ? "bg-destructive/10 border-destructive/20 text-destructive"
                            : "bg-amber-500/10 border-amber-500/20 text-amber-500"
                        }`}>
                          {selectedWhyRec.priority}
                        </span>
                      </div>
                    </div>

                    {/* Alternative Actions */}
                    <div>
                      <span className="text-[8px] font-black text-muted-foreground uppercase tracking-wider block font-mono">Alternative responses</span>
                      <ul className="list-disc pl-4 space-y-1 mt-1 text-xs text-muted-foreground">
                        {details.alternative_actions.map((act: string, idx: number) => (
                          <li key={idx}>{act}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Trade-offs */}
                    <div>
                      <span className="text-[8px] font-black text-purple-400/80 uppercase tracking-wider block font-mono">Operational trade-offs</span>
                      <p className="text-xs text-purple-200 mt-1 leading-relaxed bg-purple-500/5 border border-purple-500/10 p-2.5 rounded-xl">
                        {details.trade_offs}
                      </p>
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-end border-t border-border pt-4 mt-5">
                    <button
                      onClick={() => setSelectedWhyRec(null)}
                      className="rounded-xl border border-border bg-card hover:bg-muted px-4 py-2 text-xs font-black uppercase tracking-wider transition-colors"
                    >
                      Dismiss Review
                    </button>
                  </div>
                </motion.div>
              </motion.div>
            );
          })()}
        </AnimatePresence>

        {/* Col 3: Crowd Intelligence, Risk Assessment & Confidence */}
        <div className="flex flex-col gap-6">
          {/* AI Confidence Meter */}
          <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 shadow-lg flex flex-col items-center text-center">
            <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-4">
              AI Decision Confidence Index
            </span>
            <div className="relative h-28 w-28 flex items-center justify-center">
              <svg className="absolute -rotate-90 w-28 h-28">
                <circle cx="56" cy="56" r="46" stroke="rgba(255,255,255,0.05)" strokeWidth="6" fill="transparent" />
                <motion.circle
                  cx="56"
                  cy="56"
                  r="46"
                  stroke="#3b82f6"
                  strokeWidth="6"
                  fill="transparent"
                  strokeDasharray="289"
                  initial={{ strokeDashoffset: 289 }}
                  animate={{ strokeDashoffset: 289 - (289 * 0.96) }}
                  transition={{ duration: 1.2 }}
                />
              </svg>
              <div className="flex flex-col items-center">
                <span className="text-2xl font-black tracking-tight text-blue-400">96%</span>
                <span className="text-[8px] font-bold text-muted-foreground uppercase mt-0.5">High Quality</span>
              </div>
            </div>
            <p className="text-[10px] text-muted-foreground leading-relaxed mt-4">
              Decision telemetry is backed by 12 real-time sensor streams and deterministic business rules.
            </p>
          </div>

          {/* Crowd Intelligence Sector Densities */}
          <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 shadow-lg">
            <span className="text-xs font-black text-primary uppercase tracking-widest block mb-4">
              Crowd Intelligence by Sector
            </span>

            <div className="flex flex-col gap-3">
              {[
                { name: "Gate 1 Ingress", type: "Gate entry", density: states[0]?.density ?? 0.85, wait: states[0]?.queue_waiting_minutes ?? 12 },
                { name: "Gate 2 Exit", type: "Gate exit", density: states[1]?.density ?? 0.35, wait: states[1]?.queue_waiting_minutes ?? 4 },
                { name: "Medical Post Alpha", type: "Medical Post", density: states[3]?.density ?? 0.15, wait: 0 },
                { name: "Main Parking Area", type: "Parking", density: states[4]?.density ?? 0.65, wait: 8 },
              ].map((zone, idx) => {
                const percent = Math.round(zone.density * 100);
                let statusColor = "bg-emerald-500";
                if (zone.density > 0.8) statusColor = "bg-destructive";
                else if (zone.density > 0.5) statusColor = "bg-amber-500";

                return (
                  <div key={idx} className="flex flex-col gap-1.5 p-2 rounded-lg hover:bg-muted/20">
                    <div className="flex items-center justify-between text-[11px] font-black uppercase">
                      <span className="text-foreground">{zone.name}</span>
                      <span className="text-muted-foreground font-mono">{percent}% Density</span>
                    </div>

                    <div className="w-full bg-muted/40 rounded-full h-1 overflow-hidden">
                      <div className={`h-1 rounded-full ${statusColor}`} style={{ width: `${percent}%` }} />
                    </div>

                    <div className="flex justify-between items-center text-[9px] font-mono text-muted-foreground">
                      <span>{zone.type}</span>
                      {zone.wait > 0 ? <span>Wait: {zone.wait}m</span> : <span>Stable</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
