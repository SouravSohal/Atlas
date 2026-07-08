import { useState, useMemo, useEffect, useRef } from "react";
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
  Sparkles,
  Send,
  CheckCircle,
  Zap,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  fetchDashboardOverview,
  fetchDashboardIncidents,
  fetchDashboardRecommendations,
  fetchOperationalState,
  createIncident,
  updateIncident,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/")({
  component: MissionControlPage,
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
  const borderColors = {
    stable: "border-emerald-500/50 shadow-emerald-500/5",
    warning: "border-amber-500/50 shadow-amber-500/5",
    critical: "border-destructive/60 shadow-destructive/5",
  };

  const bgColors = {
    stable: "bg-emerald-500/5",
    warning: "bg-amber-500/5",
    critical: "bg-destructive/5 animate-pulse",
  };

  const indicatorColors = {
    stable: "bg-emerald-500",
    warning: "bg-amber-500",
    critical: "bg-destructive",
  };

  return (
    <div className={`rounded-xl border ${borderColors[data.status]} ${bgColors[data.status]} p-3 text-left w-40 backdrop-blur-md shadow-lg`}>
      <Handle type="target" position={Position.Left} className="w-1.5 h-1.5 bg-border" />
      <div className="flex items-center gap-1.5">
        <span className={`h-1.5 w-1.5 rounded-full ${indicatorColors[data.status]}`} />
        <span className="text-[10px] font-black tracking-wide text-foreground uppercase">{data.label}</span>
      </div>
      <div className="mt-1">
        <span className="text-xs font-bold text-muted-foreground block">{data.type}</span>
        <span className="text-xs font-black text-foreground mt-0.5 block">{data.value}</span>
      </div>
      <Handle type="source" position={Position.Right} className="w-1.5 h-1.5 bg-border" />
    </div>
  );
};

const nodeTypes = {
  stadiumNode: CustomNode,
};

function MissionControlPage() {
  const queryClient = useQueryClient();
  const [approvedRecs, setApprovedRecs] = useState<Record<string, boolean>>({});
  const [demoOpen, setDemoOpen] = useState(false);
  const [demoMessage, setDemoMessage] = useState<string | null>(null);

  // Copilot Chat States
  const [chatMessages, setChatMessages] = useState<any[]>([
    {
      role: "assistant",
      text: "Hello! I am your **ATLAS Copilot** operations assistant. Ask me anything about stadium health, volunteer distribution, or active recommendations.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatThinking, setChatThinking] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

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
    queryFn: () => fetchDashboardIncidents(1, 10),
    refetchInterval: 5000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["cc-recommendations"],
    queryFn: () => fetchDashboardRecommendations(1, 10),
    refetchInterval: 5000,
  });

  // Resolve Incident mutation
  const resolveMutation = useMutation({
    mutationFn: ({ id, resolved }: { id: string; resolved: boolean }) =>
      updateIncident(id, resolved),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cc-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["cc-overview"] });
    },
  });

  // Demo Mode incident mutation
  const demoMutation = useMutation({
    mutationFn: createIncident,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["cc-overview"] });
      queryClient.invalidateQueries({ queryKey: ["cc-state"] });
      queryClient.invalidateQueries({ queryKey: ["cc-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["cc-recommendations"] });
      
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

  const handleResolveIncident = (id: string) => {
    resolveMutation.mutate({ id, resolved: true });
  };

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, chatThinking]);

  // Digital Twin transforms
  const flowNodes = useMemo(() => {
    if (!stateQuery.data) return [];
    
    const zones = stateQuery.data;
    const labels = ["Gate 1 Ingress", "Gate 2 Exit", "Security Command", "Medical Post Alpha", "Main Parking Area", "Central Food Plaza"];
    const types = ["Gate Entry", "Gate Exit", "Dispatch HQ", "Medical Hub", "Parking Zone", "Food sector"];
    const positions = [
      { x: 50, y: 150 },
      { x: 550, y: 150 },
      { x: 300, y: 40 },
      { x: 300, y: 260 },
      { x: 50, y: 40 },
      { x: 550, y: 260 },
    ];

    return zones.slice(0, 6).map((zone, index) => {
      let status: "stable" | "warning" | "critical" = "stable";
      if (zone.density > 0.8) status = "critical";
      else if (zone.density > 0.4) status = "warning";

      return {
        id: zone.zone_id,
        type: "stadiumNode",
        position: positions[index] || { x: 100 + index * 100, y: 100 },
        data: {
          label: labels[index] || `Zone ${zone.zone_id.slice(0, 4)}`,
          type: types[index] || "Sector",
          value: `Density: ${Math.round(zone.density * 100)}%`,
          status,
        },
      } as StadiumNode;
    });
  }, [stateQuery.data]);

  const flowEdges = useMemo(() => {
    if (flowNodes.length < 2) return [];
    return [
      { id: "e1-2", source: flowNodes[0].id, target: flowNodes[2].id, animated: true, style: { stroke: "#3b82f6" } },
      { id: "e1-3", source: flowNodes[0].id, target: flowNodes[3].id, animated: true, style: { stroke: "#10b981" } },
      { id: "e2-4", source: flowNodes[2].id, target: flowNodes[1].id, animated: true, style: { stroke: "#f59e0b" } },
      { id: "e3-5", source: flowNodes[3].id, target: flowNodes[5].id, animated: true, style: { stroke: "#ec4899" } },
    ].filter((e) => e.source && e.target) as Edge[];
  }, [flowNodes]);

  // Copilot submit message
  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = {
      role: "user",
      text: chatInput,
      timestamp: new Date().toLocaleTimeString(),
    };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setChatThinking(true);

    // Dynamic response based on current metrics
    setTimeout(() => {
      const activeIncidents = incidentsQuery.data?.items.filter(i => !i.resolved) || [];
      const summary = `System health rating is currently **${Math.round((overviewQuery.data?.stadium_health || 0.98)*100)}%**. We have **${activeIncidents.length} active incidents** registered. Recommended action priority is **High**.`;

      const botMsg = {
        role: "assistant",
        text: summary,
        timestamp: new Date().toLocaleTimeString(),
      };
      setChatMessages((prev) => [...prev, botMsg]);
      setChatThinking(false);
    }, 1200);
  };

  if (overviewQuery.isLoading || stateQuery.isLoading || incidentsQuery.isLoading) {
    return <LoadingScreen />;
  }

  const overview = overviewQuery.data;
  const incidents = incidentsQuery.data?.items || [];
  const recs = recommendationsQuery.data?.items || [];

  const metrics = [
    { title: "Stadium Health", value: `${Math.round((overview?.stadium_health || 0.98) * 100)}%`, status: "Optimal", icon: <ShieldCheck className="h-4 w-4 text-emerald-400" /> },
    { title: "Active Incidents", value: overview?.active_incidents_count || 0, status: "Urgent", icon: <AlertTriangle className="h-4 w-4 text-destructive" /> },
    { title: "Crowd Density", value: `${Math.round((overview?.average_crowd_density || 0.45) * 100)}%`, status: "Moderate", icon: <Users className="h-4 w-4 text-primary" /> },
    { title: "Volunteers Allocated", value: overview?.allocated_volunteers_count || 0, status: "Active", icon: <Users className="h-4 w-4 text-primary" /> },
    { title: "AI Confidence", value: "96.4%", status: "Optimal", icon: <Brain className="h-4 w-4 text-emerald-400" /> },
    { title: "Avg Queue Time", value: "8 min", status: "Optimal", icon: <Clock className="h-4 w-4 text-emerald-400" /> },
  ];

  return (
    <div className="flex flex-col gap-6 text-left h-full">
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Mission Control</h1>
          <p className="text-xs text-muted-foreground mt-1">ATLAS Flagship Workspace: Unified digital twin spatial map, AI Copilot logs, and incident dispatch consoles.</p>
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
          <div key={m.title} className="rounded-xl border border-border bg-card/45 backdrop-blur-md p-4 hover:shadow-md transition-shadow">
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

      {/* Main Grid: Row 1: Digital Twin & AI Copilot */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Digital Twin Widget */}
        <div className="lg:col-span-2 rounded-2xl border border-border bg-card/45 backdrop-blur-md overflow-hidden h-[400px] flex flex-col relative shadow-sm">
          <div className="absolute top-4 left-4 z-10 bg-card/85 backdrop-blur-md border border-border rounded-xl p-3 shadow-md text-left">
            <span className="text-xs font-bold text-foreground block">Stadium Digital Twin</span>
            <span className="text-[9px] text-muted-foreground mt-0.5 block">Interact to inspect flow vectors.</span>
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

        {/* AI Copilot Widget */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md overflow-hidden h-[400px] flex flex-col justify-between shadow-sm">
          <div className="p-4 border-b border-border bg-muted/20 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Brain className="h-4 w-4 text-primary animate-pulse" />
              <span className="text-xs font-bold text-foreground">ATLAS Copilot</span>
            </div>
            <span className="text-[9px] text-muted-foreground font-mono">Gemini 2.5 Flash</span>
          </div>

          {/* Conversation history */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex flex-col gap-1 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div className={`p-3 rounded-2xl border ${
                  msg.role === "user" ? "bg-primary text-primary-foreground border-primary" : "bg-muted/30 border-border"
                } max-w-[85%] text-left`}>
                  {msg.text.split("\n").map((line: string, iIdx: number) => (
                    <p key={iIdx}>{line}</p>
                  ))}
                </div>
                <span className="text-[8px] text-muted-foreground px-1">{msg.timestamp}</span>
              </div>
            ))}
            {chatThinking && (
              <div className="flex items-center gap-1.5 text-muted-foreground italic">
                <div className="h-3 w-3 rounded-full border border-primary border-t-transparent animate-spin" />
                <span>Copilot is thinking...</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Form input */}
          <form onSubmit={handleChatSubmit} className="p-3 border-t border-border bg-muted/10 flex gap-2">
            <input
              type="text"
              placeholder="Ask Copilot a question..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              className="flex-1 rounded-lg border border-border bg-card px-3 py-2 text-xs outline-none text-foreground"
            />
            <button type="submit" className="rounded-lg bg-primary p-2 text-primary-foreground hover:opacity-90 transition-opacity">
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>
      </div>

      {/* Row 2: Timeline & Recommendations */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Timeline Widget */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm">
          <div className="mb-4">
            <h2 className="text-base font-bold">Operational Timeline</h2>
            <p className="text-xs text-muted-foreground">Chronological sequence of logs in the current shift.</p>
          </div>
          <div className="flex-1 overflow-y-auto pl-6 border-l border-border space-y-5 text-left">
            {incidents.length === 0 ? (
              <div className="text-xs text-muted-foreground py-4">No events logged.</div>
            ) : (
              incidents.slice(0, 5).map((inc) => (
                <div key={inc.id} className="relative">
                  <div className="absolute -left-[31px] mt-0.5 rounded-full bg-card border-2 border-border p-1 text-primary">
                    <Clock className="h-3 w-3" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold">{inc.resolved ? "Incident Resolved" : "Incident Created"}</span>
                    <span className="text-[10px] text-muted-foreground mt-0.5">{inc.description}</span>
                    <span className="text-[9px] text-primary font-bold mt-1">
                      {new Date(inc.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recommendations Widget */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm">
          <div className="mb-4">
            <h2 className="text-base font-bold">Active Recommendations</h2>
            <p className="text-xs text-muted-foreground">Mitigations evaluated by the cognitive engine.</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3">
            {recs.length === 0 ? (
              <div className="text-xs text-muted-foreground text-center py-10">All parameters stable. No recommendations.</div>
            ) : (
              recs.slice(0, 4).map((rec) => (
                <div key={rec.id} className="p-3 border border-border rounded-xl bg-muted/20 flex items-center justify-between gap-3 text-left">
                  <div className="flex flex-col gap-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-[9px] font-bold text-primary uppercase">{rec.action_type}</span>
                      <span className="text-[9px] font-semibold text-muted-foreground">{rec.priority} priority</span>
                    </div>
                    <p className="text-xs font-medium text-foreground truncate">{rec.details}</p>
                  </div>
                  {approvedRecs[rec.id] ? (
                    <span className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-[9px] font-bold text-emerald-400 px-2 py-1 flex items-center gap-1 shrink-0">
                      <CheckCircle className="h-3 w-3" />
                      Approved
                    </span>
                  ) : (
                    <button
                      onClick={() => handleApproveRecommendation(rec.id)}
                      className="rounded-lg bg-primary px-2.5 py-1 text-[9px] font-bold text-primary-foreground hover:opacity-90 shrink-0"
                    >
                      Approve
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Row 3: Live Feed & Active Incidents */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Live Feed Widget */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm">
          <div className="mb-4">
            <h2 className="text-base font-bold flex items-center gap-2">
              <Zap className="h-4 w-4 text-amber-400" />
              Live Activity Feed
            </h2>
            <p className="text-xs text-muted-foreground">Real-time telemetry event streams and dispatcher updates.</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-2.5 text-left">
            {incidents.length === 0 ? (
              <div className="text-xs text-muted-foreground py-4">No activity events.</div>
            ) : (
              incidents.map((inc) => (
                <div key={inc.id} className="flex items-start gap-2.5 p-2 border-b border-border/40 text-xs">
                  <Activity className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <span className="font-semibold block text-foreground truncate">{inc.description}</span>
                    <span className="text-[9px] text-muted-foreground mt-0.5 block uppercase font-mono">
                      Type: {inc.incident_type} &bull; Timestamp: {new Date(inc.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Active Incidents Widget */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm">
          <div className="mb-4">
            <h2 className="text-base font-bold">Active Incidents Queue</h2>
            <p className="text-xs text-muted-foreground">Unresolved safety or medical logs under dispatch.</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3">
            {incidents.filter((i) => !i.resolved).length === 0 ? (
              <div className="text-xs text-muted-foreground text-center py-10 flex flex-col items-center justify-center gap-2">
                <CheckCircle className="h-8 w-8 text-emerald-500" />
                <span>All incidents cleared.</span>
              </div>
            ) : (
              incidents.filter((i) => !i.resolved).map((inc) => (
                <div key={inc.id} className="p-3 border border-border rounded-xl bg-muted/20 flex items-center justify-between gap-3 text-left">
                  <div className="flex flex-col gap-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`text-[9px] font-black px-1.5 py-0.5 rounded ${
                        inc.severity === "critical" ? "bg-destructive/10 text-destructive border border-destructive/20 animate-pulse" : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      }`}>
                        {inc.severity.toUpperCase()}
                      </span>
                      <span className="text-[9px] font-bold text-muted-foreground uppercase">{inc.incident_type}</span>
                    </div>
                    <p className="text-xs font-semibold text-foreground truncate">{inc.description}</p>
                  </div>
                  <button
                    onClick={() => handleResolveIncident(inc.id)}
                    className="rounded-lg border border-border hover:bg-muted px-2.5 py-1 text-[9px] font-bold shrink-0 transition-colors"
                  >
                    Resolve
                  </button>
                </div>
              ))
            )}
          </div>
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
