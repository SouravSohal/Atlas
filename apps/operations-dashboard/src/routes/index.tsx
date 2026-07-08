import { useState, useMemo } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
} from "@xyflow/react";
import type { Node, Edge, NodeProps } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  ShieldCheck,
  AlertTriangle,
  Users,
  Brain,
  Clock,
  Activity,
  Wifi,
  Sparkles,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  fetchDashboardOverview,
  fetchDashboardIncidents,
  fetchDashboardRecommendations,
  fetchOperationalState,
  createIncident,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/")({
  component: OperationsCommandCenter,
});

type StadiumNodeData = {
  label: string;
  value: string;
  status: "stable" | "warning" | "critical";
  type: string;
};

type StadiumNode = Node<StadiumNodeData, "stadiumNode">;

// Custom React flow nodes configuration
const CustomNode = ({ data }: NodeProps<StadiumNode>) => {
  const borderColors: Record<string, string> = {
    stable: "border-emerald-500/30 shadow-emerald-500/5",
    warning: "border-amber-500/40 shadow-amber-500/5 animate-pulse",
    critical: "border-destructive/50 shadow-destructive/5 animate-pulse",
  };

  const bgColors: Record<string, string> = {
    stable: "bg-emerald-500/5",
    warning: "bg-amber-500/5",
    critical: "bg-destructive/5",
  };

  const textColors: Record<string, string> = {
    stable: "text-emerald-400",
    warning: "text-amber-400",
    critical: "text-destructive",
  };

  const status = data.status || "stable";

  return (
    <div className={`rounded-xl border bg-card p-3 shadow-md min-w-[140px] text-left transition-all ${borderColors[status]} ${bgColors[status]}`}>
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <div className="flex flex-col gap-1">
        <span className="text-[8px] uppercase tracking-wider text-muted-foreground font-bold">{data.type}</span>
        <span className="text-xs font-extrabold text-foreground">{data.label}</span>
        <div className="flex items-center gap-1.5 mt-1.5">
          <span className={`h-1.5 w-1.5 rounded-full ${status === "stable" ? "bg-emerald-400" : status === "warning" ? "bg-amber-400" : "bg-destructive"}`} />
          <span className={`text-[10px] font-black tracking-tight ${textColors[status]}`}>{data.value}</span>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
};

const nodeTypes = {
  stadiumNode: CustomNode,
};

// AI Situation Summary Placeholder Hook
function useAiSituationSummary() {
  return useQuery({
    queryKey: ["ai-situation-summary-cc"],
    queryFn: async () => {
      return {
        summary: "Live stadium telemetry indicates moderate ingress congestion around Gate 1. All turnstiles are operational, but spectator flow rates are currently at 84% capacity. Deployed 2 additional volunteers to guide flow. Security status is stable with 3 active minor incidents under control by zone dispatch teams.",
        security_status: "Stable - Normal Patrols",
        medical_status: "Ready - All stations active",
        crowd_status: "Moderate - Steady flow rates",
        confidence: 0.96,
        generated_at: new Date().toISOString(),
      };
    },
    refetchInterval: 15000,
  });
}

function OperationsCommandCenter() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"incidents" | "timeline" | "feed">("feed");
  const [approvedRecs, setApprovedRecs] = useState<Record<string, boolean>>({});
  const [demoOpen, setDemoOpen] = useState(false);
  const [demoMessage, setDemoMessage] = useState<string | null>(null);

  // Query actual backend data
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
    queryFn: () => fetchDashboardIncidents(1, 5),
    refetchInterval: 5000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["cc-recommendations"],
    queryFn: () => fetchDashboardRecommendations(1, 5),
    refetchInterval: 5000,
  });

  const aiSummaryQuery = useAiSituationSummary();

  const demoMutation = useMutation({
    mutationFn: createIncident,
    onSuccess: (data) => {
      // Invalidate queries immediately for visual feedback
      queryClient.invalidateQueries({ queryKey: ["cc-overview"] });
      queryClient.invalidateQueries({ queryKey: ["cc-state"] });
      queryClient.invalidateQueries({ queryKey: ["cc-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["cc-recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["ai-situation-summary-cc"] });

      setDemoMessage(`Scenario triggered: ${data.incident_type.toUpperCase()} registered!`);
      setTimeout(() => setDemoMessage(null), 5000);
    },
    onError: (err: any) => {
      setDemoMessage(`Error: ${err.message || "Failed to trigger scenario"}`);
      setTimeout(() => setDemoMessage(null), 5000);
    },
  });

  const triggerScenario = (type: string, severity: string, description: string) => {
    const zones = stateQuery.data || [];
    const zoneId = zones[0]?.zone_id || "00000000-0000-0000-0000-000000000000";
    
    demoMutation.mutate({
      incident_type: type,
      severity,
      description,
      latitude: 37.7749,
      longitude: -122.4194,
      reporter_id: "00000000-0000-0000-0000-000000000000",
      zone_id: zoneId,
    });
  };

  const handleApproveRecommendation = (id: string) => {
    setApprovedRecs((prev) => ({ ...prev, [id]: true }));
  };

  // Node transformations based on operational state data
  const flowNodes = useMemo(() => {
    if (!stateQuery.data) return [];
    
    // Map zones to custom node locations
    const zones = stateQuery.data;
    const labels = ["Gate 1 Ingress", "Gate 2 Exit", "Security Command", "Medical Post Alpha", "Main Parking Area", "Central Food Plaza"];
    const types = ["Gate Entry", "Gate Exit", "Dispatch HQ", "Medical Hub", "Parking Zone", "Food sector"];
    
    return labels.map((label, index) => {
      const zoneData = zones[index] || { density: 0.2, queue_waiting_minutes: 0 };
      
      let status: "stable" | "warning" | "critical" = "stable";
      if (zoneData.density > 0.75) status = "critical";
      else if (zoneData.density > 0.4) status = "warning";

      return {
        id: `node-${index}`,
        type: "stadiumNode",
        position: { x: index * 180 + 40, y: (index % 2) * 120 + 60 },
        data: {
          label,
          type: types[index],
          value: `${Math.round(zoneData.density * 100)}% Occ (${zoneData.queue_waiting_minutes}m Wait)`,
          status,
        },
      } as Node;
    });
  }, [stateQuery.data]);

  // Edges mapping flow movement
  const flowEdges = useMemo(() => {
    return [
      { id: "e0-2", source: "node-0", target: "node-2", animated: true, style: { stroke: "#3b82f6" } },
      { id: "e2-5", source: "node-2", target: "node-5", animated: true, style: { stroke: "#10b981" } },
      { id: "e5-1", source: "node-5", target: "node-1", animated: true, style: { stroke: "#6366f1" } },
      { id: "e3-5", source: "node-3", target: "node-5", animated: true, style: { stroke: "#a855f7" } },
      { id: "e4-0", source: "node-4", target: "node-0", animated: true, style: { stroke: "#ec4899" } },
    ] as Edge[];
  }, []);

  if (overviewQuery.isLoading || stateQuery.isLoading || incidentsQuery.isLoading || recommendationsQuery.isLoading || aiSummaryQuery.isLoading) {
    return <LoadingScreen />;
  }

  if (overviewQuery.isError || stateQuery.isError || incidentsQuery.isError || recommendationsQuery.isError || aiSummaryQuery.isError) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center text-center p-6 bg-card border border-border rounded-2xl max-w-sm mx-auto mt-10">
        <AlertTriangle className="h-10 w-10 text-destructive mb-3" />
        <h3 className="text-sm font-bold">API Connection Error</h3>
        <p className="text-xs text-muted-foreground mt-1">Unable to connect to active backend telemetry streams.</p>
      </div>
    );
  }

  const overview = overviewQuery.data!;
  const zones = stateQuery.data || [];
  const incidents = incidentsQuery.data?.items || [];
  const recommendations = recommendationsQuery.data?.items || [];
  const aiSummary = aiSummaryQuery.data!;

  // Telemetry indicators
  const metrics = [
    {
      title: "Stadium Health",
      value: `${Math.round(overview.stadium_health * 100)}%`,
      status: "Safe",
      icon: <ShieldCheck className="h-4 w-4 text-emerald-400" />,
    },
    {
      title: "Active Alerts",
      value: String(overview.active_incidents_count),
      status: overview.active_incidents_count > 0 ? "Dispatching" : "Clear",
      icon: <AlertTriangle className="h-4 w-4 text-destructive" />,
    },
    {
      title: "Crowd Density",
      value: `${Math.round(overview.average_crowd_density * 100)}%`,
      status: "Flowing",
      icon: <Activity className="h-4 w-4 text-primary" />,
    },
    {
      title: "Total Volunteers",
      value: String(overview.allocated_volunteers_count),
      status: "Allocated",
      icon: <Users className="h-4 w-4 text-blue-400" />,
    },
    {
      title: "AI Confidence",
      value: `${Math.round(aiSummary.confidence * 100)}%`,
      status: "Verified",
      icon: <Brain className="h-4 w-4 text-purple-400" />,
    },
    {
      title: "Telemetry Stream",
      value: "99.8%",
      status: "Active",
      icon: <Wifi className="h-4 w-4 text-emerald-400" />,
    },
  ];

  return (
    <div className="flex flex-col gap-6 text-left">
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Operations Command Center</h1>
          <p className="text-xs text-muted-foreground mt-1">Live stadium tactical dispatch, digital twin monitoring, and AI situation summary support.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 rounded-full border border-border bg-emerald-500/10 px-3.5 py-1.5 text-xs font-bold text-emerald-400">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span>Real-time link active</span>
          </div>
        </div>
      </div>

      {/* Flagship KPI Matrix */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
        {metrics.map((m) => (
          <div key={m.title} className="rounded-xl border border-border bg-card p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-[10px] font-bold uppercase tracking-wider">{m.title}</span>
              {m.icon}
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-black tracking-tight">{m.value}</span>
              <span className="text-[9px] font-bold text-muted-foreground uppercase">{m.status}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Grid: Interactive Stadium Twin (Left) & AI Command Panel (Right) */}
      <div className="grid gap-6 lg:grid-cols-3">
        
        {/* Left Area: Digital Twin (React Flow) */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="rounded-2xl border border-border bg-card overflow-hidden h-[450px] flex flex-col relative shadow-sm">
            <div className="absolute top-4 left-4 z-10 bg-card/85 backdrop-blur-md border border-border rounded-xl p-3 shadow-md">
              <span className="text-xs font-bold text-foreground block">Stadium Digital Twin Layout</span>
              <span className="text-[9px] text-muted-foreground mt-0.5 block">Interact to inspect gate nodes and flow vectors.</span>
            </div>

            <div className="flex-1 h-full w-full">
              <ReactFlow
                nodes={flowNodes}
                edges={flowEdges}
                nodeTypes={nodeTypes}
                fitView
                className="bg-muted/10"
              >
                <Background color="var(--color-border)" gap={16} size={1} />
                <Controls showInteractive={false} className="bg-card border-border fill-foreground" />
              </ReactFlow>
            </div>
          </div>
        </div>

        {/* Right Panel: AI Situation & recommendations */}
        <div className="flex flex-col gap-6">
          
          {/* AI Situation Summary Card */}
          <div className="rounded-2xl border border-primary/20 bg-primary/[0.02] p-6 relative overflow-hidden shadow-sm">
            <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-primary/10 blur-3xl" />
            
            <div className="flex items-center gap-2 mb-4">
              <Brain className="h-5 w-5 text-primary" />
              <span className="text-xs font-bold text-primary uppercase tracking-wider flex items-center gap-1.5">
                AI Operations Copilot
                <span className="flex h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
              </span>
            </div>

            <p className="text-xs font-medium leading-relaxed text-foreground bg-card/30 rounded-xl p-4 border border-border/40 backdrop-blur-md">
              {aiSummary.summary}
            </p>

            <div className="grid grid-cols-3 gap-2 mt-4 text-center">
              <div className="rounded-lg bg-card border border-border p-2">
                <span className="text-[8px] font-bold text-muted-foreground uppercase">Security</span>
                <span className="block text-[10px] font-bold text-emerald-400 mt-0.5">Stable</span>
              </div>
              <div className="rounded-lg bg-card border border-border p-2">
                <span className="text-[8px] font-bold text-muted-foreground uppercase">Medical</span>
                <span className="block text-[10px] font-bold text-emerald-400 mt-0.5">Active</span>
              </div>
              <div className="rounded-lg bg-card border border-border p-2">
                <span className="text-[8px] font-bold text-muted-foreground uppercase">Crowd</span>
                <span className="block text-[10px] font-bold text-amber-400 mt-0.5">Moderate</span>
              </div>
            </div>
          </div>

          {/* Recommendations list */}
          <div className="rounded-2xl border border-border bg-card p-6 flex flex-col justify-between flex-1">
            <div className="mb-4">
              <h2 className="text-lg font-bold">Action mitigations panel</h2>
              <p className="text-xs text-muted-foreground">Action items determined by operational parameters.</p>
            </div>

            <div className="space-y-3 flex-1 overflow-y-auto max-h-[220px] pr-1">
              {recommendations.length === 0 ? (
                <div className="text-xs text-muted-foreground text-center py-6">All sector flows nominal.</div>
              ) : (
                recommendations.map((rec) => (
                  <div key={rec.id} className="p-3 border border-border rounded-xl bg-muted/20 hover:bg-muted/40 transition-colors">
                    <div className="flex justify-between items-start mb-1 text-xs">
                      <span className="font-extrabold text-foreground uppercase tracking-wider">{rec.action_type}</span>
                      <span className="text-[9px] font-bold text-muted-foreground font-mono">{Math.round(rec.confidence * 100)}% confidence</span>
                    </div>
                    <p className="text-[11px] text-muted-foreground mt-1">{rec.details}</p>
                    
                    <div className="flex justify-end mt-3">
                      <button
                        onClick={() => handleApproveRecommendation(rec.id)}
                        disabled={approvedRecs[rec.id]}
                        className={`rounded-lg px-3 py-1.5 text-[10px] font-bold transition-all focus-visible:ring-2 focus-visible:ring-primary outline-none ${
                          approvedRecs[rec.id]
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : "bg-primary text-primary-foreground hover:opacity-90"
                        }`}
                      >
                        {approvedRecs[rec.id] ? "Approved" : "Approve Dispatch"}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>

      </div>

      {/* Bottom Layout: Timeline, Incidents & Activity Feed Tabs */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        
        {/* Nav Tabs */}
        <div className="flex border-b border-border bg-muted/30">
          <button
            onClick={() => setActiveTab("feed")}
            className={`px-6 py-3.5 text-xs font-bold transition-colors ${
              activeTab === "feed" ? "border-b-2 border-primary text-primary" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Live Activity Feed
          </button>
          <button
            onClick={() => setActiveTab("incidents")}
            className={`px-6 py-3.5 text-xs font-bold transition-colors ${
              activeTab === "incidents" ? "border-b-2 border-primary text-primary" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Active Incidents ({incidents.length})
          </button>
          <button
            onClick={() => setActiveTab("timeline")}
            className={`px-6 py-3.5 text-xs font-bold transition-colors ${
              activeTab === "timeline" ? "border-b-2 border-primary text-primary" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Operational Timeline
          </button>
        </div>

        {/* Tab contents */}
        <div className="p-6">
          <AnimatePresence mode="wait">
            
            {activeTab === "feed" && (
              <motion.div
                key="feed"
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className="space-y-3 font-mono text-xs text-muted-foreground text-left"
              >
                <div className="flex gap-2 items-start">
                  <span className="text-primary font-bold">[SYS]</span>
                  <span>Sensors connection live. Telemetry healthy.</span>
                </div>
                <div className="flex gap-2 items-start">
                  <span className="text-primary font-bold">[SYS]</span>
                  <span>Ingress turnstiles monitored: 12 open.</span>
                </div>
                {zones.slice(0, 3).map((zone, idx) => (
                  <div key={zone.zone_id} className="flex gap-2 items-start">
                    <span className="text-amber-500 font-bold">[TELEMETRY]</span>
                    <span>Zone {idx + 1} density currently at {Math.round(zone.density * 100)}% with average wait {zone.queue_waiting_minutes}m.</span>
                  </div>
                ))}
              </motion.div>
            )}

            {activeTab === "incidents" && (
              <motion.div
                key="incidents"
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className="space-y-3"
              >
                {incidents.length === 0 ? (
                  <div className="flex flex-col items-center py-6 text-center text-xs text-muted-foreground border border-dashed border-border rounded-xl">
                    <ShieldCheck className="h-6 w-6 text-emerald-400 mb-1" />
                    <span>No active incidents reported.</span>
                  </div>
                ) : (
                  incidents.map((inc) => (
                    <div key={inc.id} className="flex items-center justify-between p-3 bg-muted/20 border border-border/60 rounded-xl">
                      <div className="flex items-center gap-3">
                        <AlertTriangle className="h-4 w-4 text-destructive shrink-0" />
                        <div className="flex flex-col text-left">
                          <span className="text-xs font-bold text-foreground">{inc.description}</span>
                          <span className="text-[9px] text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
                            {inc.incident_type} &bull; Severity: {inc.severity}
                          </span>
                        </div>
                      </div>
                      <span className="text-[10px] text-muted-foreground font-mono">
                        {new Date(inc.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  ))
                )}
              </motion.div>
            )}

            {activeTab === "timeline" && (
              <motion.div
                key="timeline"
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className="relative pl-6 border-l border-border space-y-6 text-left"
              >
                {incidents.length === 0 ? (
                  <div className="text-xs text-muted-foreground py-4">No events logged in the current shift.</div>
                ) : (
                  incidents.map((inc) => (
                    <div key={inc.id} className="relative">
                      <div className="absolute -left-[31px] mt-0.5 rounded-full bg-card border-2 border-border p-1 text-primary">
                        <Clock className="h-3 w-3" />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs font-bold">{inc.resolved ? "Incident Cleared" : "Alert Triggered"}</span>
                        <span className="text-[10px] text-muted-foreground mt-0.5">{inc.description}</span>
                        <span className="text-[9px] text-primary font-bold mt-1">
                          {new Date(inc.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </motion.div>
            )}

          </AnimatePresence>
        </div>
      </div>

      {/* Floating Demo Control Panel */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
        <AnimatePresence>
          {demoOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="mb-3 w-80 rounded-2xl border border-primary/30 bg-card/95 backdrop-blur-md shadow-2xl p-5"
            >
              <div className="flex items-center justify-between border-b border-border pb-2.5 mb-4">
                <span className="text-xs font-bold text-primary uppercase tracking-wider flex items-center gap-1.5">
                  Demo Control Console
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
                </span>
                <button
                  onClick={() => setDemoOpen(false)}
                  className="text-muted-foreground hover:text-foreground text-xs"
                >
                  Hide
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2.5">
                <button
                  onClick={() => triggerScenario("crowd_control", "high", "High congestion alert at Gate 1 Ingress turnstiles.")}
                  className="rounded-xl border border-border bg-muted/40 hover:bg-primary/10 hover:text-primary transition-all p-3 text-left text-[11px] font-bold"
                >
                  Gate Congestion
                </button>
                <button
                  onClick={() => triggerScenario("medical", "critical", "Spectator collapse reported near Section 104.")}
                  className="rounded-xl border border-border bg-muted/40 hover:bg-primary/10 hover:text-primary transition-all p-3 text-left text-[11px] font-bold"
                >
                  Medical Emergency
                </button>
                <button
                  onClick={() => triggerScenario("facility", "critical", "Local power failure reported in central food sector.")}
                  className="rounded-xl border border-border bg-muted/40 hover:bg-primary/10 hover:text-primary transition-all p-3 text-left text-[11px] font-bold"
                >
                  Power Failure
                </button>
                <button
                  onClick={() => triggerScenario("weather", "medium", "Sudden heavy rainfall starting. Evacuating open parking lots.")}
                  className="rounded-xl border border-border bg-muted/40 hover:bg-primary/10 hover:text-primary transition-all p-3 text-left text-[11px] font-bold"
                >
                  Heavy Rain
                </button>
                <button
                  onClick={() => triggerScenario("security", "low", "VIP Motorcade approaching Gate 2 Ingress plaza.")}
                  className="rounded-xl border border-border bg-muted/40 hover:bg-primary/10 hover:text-primary transition-all p-3 text-left text-[11px] font-bold"
                >
                  VIP Arrival
                </button>
                <button
                  onClick={() => triggerScenario("security", "medium", "7-year-old child reported separated from guardians near Section 208.")}
                  className="rounded-xl border border-border bg-muted/40 hover:bg-primary/10 hover:text-primary transition-all p-3 text-left text-[11px] font-bold"
                >
                  Lost Child
                </button>
              </div>

              {demoMessage && (
                <div className="mt-4 rounded-xl bg-primary/10 border border-primary/20 p-3 text-[10px] font-bold text-primary animate-pulse text-center">
                  {demoMessage}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        <button
          onClick={() => setDemoOpen(!demoOpen)}
          className="flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-xs font-bold text-primary-foreground shadow-2xl hover:opacity-90 transition-all border border-primary-foreground/10 focus-visible:ring-2 focus-visible:ring-primary outline-none"
        >
          <Sparkles className="h-4 w-4" />
          Demo Mode Console
        </button>
      </div>
    </div>
  );
}
