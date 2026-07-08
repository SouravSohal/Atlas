import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
} from "@xyflow/react";
import type { Node, Edge, NodeProps } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  Shield,
  HeartPulse,
  Clock,
  Activity,
  AlertTriangle,
  Info,
  Car,
  Utensils,
  Maximize2,
  Bus,
  UserCheck,
  Zap,
} from "lucide-react";
import {
  fetchOperationalState,
  fetchDashboardIncidents,
  fetchDashboardRecommendations,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/operational-state")({
  component: OperationalStateDashboardPage,
});

type TwinNodeData = {
  label: string;
  type: "Gates" | "Security" | "Medical" | "Parking" | "Food Courts" | "Restrooms" | "Transportation" | "Volunteer Stations";
  density: number;
  health: number;
  queueLength: number;
  alertsCount: number;
  recsCount: number;
  status: "stable" | "warning" | "critical";
  zoneId: string;
};

type TwinNode = Node<TwinNodeData, "digitalTwinNode">;

// Custom high-fidelity Node component for stadium facilities
const DigitalTwinNodeComponent = ({ data }: NodeProps<TwinNode>) => {
  const statusBorderColors = {
    stable: "border-emerald-500/40 shadow-emerald-500/5",
    warning: "border-amber-500/40 shadow-amber-500/5",
    critical: "border-destructive/60 shadow-destructive/5",
  };

  const statusBgColors = {
    stable: "bg-emerald-500/[0.02]",
    warning: "bg-amber-500/[0.02]",
    critical: "bg-destructive/[0.02] animate-pulse",
  };

  const statusTextColors = {
    stable: "text-emerald-400",
    warning: "text-amber-400",
    critical: "text-destructive",
  };

  const typeIcons = {
    Gates: <Maximize2 className="h-4 w-4" />,
    Security: <Shield className="h-4 w-4" />,
    Medical: <HeartPulse className="h-4 w-4" />,
    Parking: <Car className="h-4 w-4" />,
    "Food Courts": <Utensils className="h-4 w-4" />,
    Restrooms: <Zap className="h-4 w-4" />,
    Transportation: <Bus className="h-4 w-4" />,
    "Volunteer Stations": <UserCheck className="h-4 w-4" />,
  };

  return (
    <div className={`rounded-2xl border bg-card/90 backdrop-blur-md p-4 text-left w-52 shadow-2xl transition-all duration-300 hover:scale-105 hover:shadow-primary/5 ${statusBorderColors[data.status]} ${statusBgColors[data.status]}`}>
      <Handle type="target" position={Position.Left} className="w-2.5 h-2.5 bg-border rounded-full border-2 border-card" />
      
      {/* Header */}
      <div className="flex justify-between items-start mb-2.5">
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg border bg-muted/40 ${statusTextColors[data.status]}`}>
            {typeIcons[data.type] || <Activity className="h-4 w-4" />}
          </div>
          <div>
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">{data.type}</span>
            <span className="text-xs font-black text-foreground block truncate max-w-[110px]">{data.label}</span>
          </div>
        </div>
        <span className={`text-[10px] font-bold uppercase tracking-wider ${statusTextColors[data.status]}`}>
          {data.status}
        </span>
      </div>

      {/* Health & Density Gauges */}
      <div className="space-y-2 text-xs">
        <div>
          <div className="flex justify-between text-[10px] font-bold text-muted-foreground mb-0.5">
            <span>HEALTH INDEX</span>
            <span className="text-foreground">{data.health}%</span>
          </div>
          <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                data.health > 80 ? "bg-emerald-500" : data.health > 50 ? "bg-amber-500" : "bg-destructive"
              }`}
              style={{ width: `${data.health}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-[10px] font-bold text-muted-foreground mb-0.5">
            <span>CROWD DENSITY</span>
            <span className="text-foreground">{Math.round(data.density * 100)}%</span>
          </div>
          <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full bg-primary transition-all duration-500`}
              style={{ width: `${Math.round(data.density * 100)}%` }}
            />
          </div>
        </div>

        <div className="flex justify-between items-center text-[10px] font-bold pt-1 border-t border-border/40">
          <span className="text-muted-foreground flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Wait Time
          </span>
          <span className="text-foreground">{data.queueLength}m</span>
        </div>
      </div>

      {/* Badges indicators (Alerts & Recommendations) */}
      <div className="mt-3 flex gap-2">
        {data.alertsCount > 0 && (
          <span className="flex items-center gap-1 rounded bg-destructive/10 border border-destructive/20 px-1.5 py-0.5 text-[9px] font-black text-destructive animate-pulse">
            <AlertTriangle className="h-2.5 w-2.5" />
            {data.alertsCount} Alerts
          </span>
        )}
        {data.recsCount > 0 && (
          <span className="flex items-center gap-1 rounded bg-primary/10 border border-primary/20 px-1.5 py-0.5 text-[9px] font-black text-primary">
            <Activity className="h-2.5 w-2.5" />
            {data.recsCount} Recs
          </span>
        )}
      </div>

      <Handle type="source" position={Position.Right} className="w-2.5 h-2.5 bg-border rounded-full border-2 border-card" />
    </div>
  );
};



// Layout coordinates for 8 facility nodes returned from backend
const ZONE_METADATA_TEMPLATES = [
  { label: "Gate 1 Turnstiles", type: "Gates" as const, x: 50, y: 150 },
  { label: "Sector Security Command", type: "Security" as const, x: 300, y: 50 },
  { label: "First Aid Post Alpha", type: "Medical" as const, x: 300, y: 280 },
  { label: "North VIP Parking Area", type: "Parking" as const, x: 50, y: 50 },
  { label: "Central Plaza Food Court", type: "Food Courts" as const, x: 550, y: 280 },
  { label: "East Plaza Restrooms", type: "Restrooms" as const, x: 550, y: 150 },
  { label: "Bus Loop Transit Hub", type: "Transportation" as const, x: 50, y: 280 },
  { label: "Volunteer Depot Command", type: "Volunteer Stations" as const, x: 550, y: 50 },
];

function OperationalStateDashboardPage() {
  const queryClient = useQueryClient();
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // TanStack Query
  const stateQuery = useQuery({
    queryKey: ["twin-state"],
    queryFn: fetchOperationalState,
    refetchInterval: 5000,
  });

  const incidentsQuery = useQuery({
    queryKey: ["twin-incidents"],
    queryFn: () => fetchDashboardIncidents(1, 100),
    refetchInterval: 5000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["twin-recs"],
    queryFn: () => fetchDashboardRecommendations(1, 100),
    refetchInterval: 5000,
  });

  // Future-ready WebSockets Connection
  useEffect(() => {
    const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
    // Replaces client dev port (5173) with backend api port (8000)
    const wsHost = window.location.host.replace("5173", "8000");
    const socket = new WebSocket(`${wsProto}//${wsHost}/api/v1/operational-state/ws`);

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === "state_update") {
          // Dynamically mutate query cache value
          queryClient.setQueryData(["twin-state"], (prev: any) => {
            if (!prev) return prev;
            return prev.map((zone: any) =>
              zone.zone_id === payload.zone_id ? { ...zone, ...payload.metrics } : zone
            );
          });
        }
      } catch (err) {
        console.error("WebSocket message parsing failed:", err);
      }
    };

    return () => {
      socket.close();
    };
  }, [queryClient]);

  if (stateQuery.isLoading || incidentsQuery.isLoading || recommendationsQuery.isLoading) {
    return <LoadingScreen />;
  }

  if (stateQuery.isError) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center text-center p-6 bg-card border border-border rounded-2xl max-w-sm mx-auto mt-10">
        <AlertTriangle className="h-10 w-10 text-destructive mb-3 animate-bounce" />
        <h3 className="text-sm font-bold">API Offline</h3>
        <p className="text-xs text-muted-foreground mt-1">Unable to load stadium state coordinates from backend.</p>
      </div>
    );
  }

  const zones = stateQuery.data || [];
  const rawIncidents = incidentsQuery.data?.items || [];
  const rawRecs = recommendationsQuery.data?.items || [];

  // Map incidents to zones deterministically using index/modulo since the API doesn't return zone_id directly
  const incidents = rawIncidents.map((inc) => {
    const index = parseInt(inc.id.replace(/-/g, "").slice(0, 4), 16) % Math.max(1, zones.length);
    return { ...inc, zoneId: zones[index]?.zone_id || "" };
  });

  const recs = rawRecs.map((rec) => {
    const index = parseInt(rec.id.replace(/-/g, "").slice(0, 4), 16) % Math.max(1, zones.length);
    return { ...rec, zoneId: zones[index]?.zone_id || "" };
  });

  // Map zone records dynamically to React Flow nodes using metadata templates
  const flowNodes = zones.map((zone, index) => {
    const template = ZONE_METADATA_TEMPLATES[index] || {
      label: `Sector Zone ${zone.zone_id.slice(0, 4)}`,
      type: "Gates" as const,
      x: 100 + (index * 160) % 700,
      y: 100 + (index * 110) % 400,
    };

    // Calculate matching alerts and recommendations
    const zoneIncidents = incidents.filter((inc) => inc.zoneId === zone.zone_id && !inc.resolved);
    const zoneRecs = recs.filter((rec) => rec.zoneId === zone.zone_id);

    // Calculate health score based on density and incidents
    const healthScore = Math.max(
      0,
      Math.round(100 - zoneIncidents.length * 25 - (zone.density > 0.8 ? 20 : 0))
    );

    let status: "stable" | "warning" | "critical" = "stable";
    if (zone.density > 0.8 || zoneIncidents.length > 0) status = "critical";
    else if (zone.density > 0.4) status = "warning";

    return {
      id: zone.zone_id,
      type: "digitalTwinNode",
      position: { x: template.x, y: template.y },
      data: {
        label: template.label,
        type: template.type,
        density: zone.density,
        health: healthScore,
        queueLength: zone.queue_waiting_minutes,
        alertsCount: zoneIncidents.length,
        recsCount: zoneRecs.length,
        status,
        zoneId: zone.zone_id,
      },
    } as TwinNode;
  });

  // Flow connections showing circulation movement between gates, arenas, and hubs
  const flowEdges = [
    { id: "e1", source: flowNodes[0]?.id || "", target: flowNodes[1]?.id || "", animated: true, style: { stroke: "#3b82f6" } },
    { id: "e2", source: flowNodes[0]?.id || "", target: flowNodes[2]?.id || "", animated: true, style: { stroke: "#10b981" } },
    { id: "e3", source: flowNodes[1]?.id || "", target: flowNodes[5]?.id || "", animated: true, style: { stroke: "#f59e0b" } },
    { id: "e4", source: flowNodes[2]?.id || "", target: flowNodes[3]?.id || "", animated: true, style: { stroke: "#6366f1" } },
    { id: "e5", source: flowNodes[3]?.id || "", target: flowNodes[4]?.id || "", animated: true, style: { stroke: "#ec4899" } },
    { id: "e6", source: flowNodes[5]?.id || "", target: flowNodes[7]?.id || "", animated: true, style: { stroke: "#a855f7" } },
    { id: "e7", source: flowNodes[6]?.id || "", target: flowNodes[0]?.id || "", animated: true, style: { stroke: "#14b8a6" } },
  ].filter((e) => e.source && e.target) as Edge[];

  // Find currently selected node details
  const selectedNode = flowNodes.find((n) => n.id === selectedNodeId);
  const selectedNodeIncidents = selectedNode
    ? incidents.filter((inc) => inc.zoneId === selectedNode.id && !inc.resolved)
    : [];

  const actualNodeTypes = {
    digitalTwinNode: DigitalTwinNodeComponent,
  };

  return (
    <div className="flex flex-col gap-6 text-left h-full">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Stadium Digital Twin</h1>
          <p className="text-xs text-muted-foreground mt-1">Live physical-to-digital spatial maps representing visitor flows and incident dispatch coordinates.</p>
        </div>
        <div className="text-xs text-muted-foreground bg-muted/50 px-3 py-1.5 rounded-full border border-border flex items-center gap-1.5 font-bold">
          <Clock className="h-3.5 w-3.5" />
          <span>Updates active (WebSockets ready)</span>
        </div>
      </div>

      {/* Main Split Layout: Map Twin (Left) & Inspector Pane (Right) */}
      <div className="grid gap-6 lg:grid-cols-4 flex-1 overflow-hidden min-h-[500px]">
        {/* React Flow Container */}
        <div className="lg:col-span-3 rounded-2xl border border-border bg-card overflow-hidden h-[65vh] flex flex-col relative shadow-md">
          <div className="flex-1 h-full w-full">
            <ReactFlow
              nodes={flowNodes}
              edges={flowEdges}
              nodeTypes={actualNodeTypes}
              onNodeClick={(_, node) => setSelectedNodeId(node.id)}
              fitView
              className="bg-muted/10"
            >
              <Background color="var(--color-border)" gap={18} size={1} />
              <Controls showInteractive={false} className="bg-card border-border fill-foreground" />
              <MiniMap
                className="bg-card/90 border border-border rounded-xl shadow-lg"
                maskColor="rgba(0,0,0,0.2)"
                nodeColor={(node) => {
                  const data = node.data as TwinNodeData;
                  if (data.status === "critical") return "var(--color-destructive)";
                  if (data.status === "warning") return "var(--color-amber-500)";
                  return "var(--color-emerald-500)";
                }}
              />
            </ReactFlow>
          </div>
        </div>

        {/* Floating Inspector Panel */}
        <div className="rounded-2xl border border-border bg-card p-6 flex flex-col shadow-sm h-[65vh] overflow-y-auto">
          {selectedNode ? (
            <div className="space-y-6">
              {/* Header Title */}
              <div>
                <span className="text-[10px] font-bold text-primary uppercase block">Zone Telemetry Inspector</span>
                <h2 className="text-lg font-black text-foreground mt-0.5">{selectedNode.data.label}</h2>
                <span className="text-xs text-muted-foreground block font-semibold mt-1">ID: {selectedNode.id}</span>
              </div>

              {/* Status details indicators */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 border border-border rounded-xl bg-muted/20">
                  <span className="text-[9px] font-bold text-muted-foreground block uppercase">Health Index</span>
                  <span className={`text-base font-black mt-0.5 block ${
                    selectedNode.data.health > 80 ? "text-emerald-400" : selectedNode.data.health > 50 ? "text-amber-400" : "text-destructive"
                  }`}>
                    {selectedNode.data.health}%
                  </span>
                </div>
                <div className="p-3 border border-border rounded-xl bg-muted/20">
                  <span className="text-[9px] font-bold text-muted-foreground block uppercase">Density</span>
                  <span className="text-base font-black text-foreground mt-0.5 block">
                    {Math.round(selectedNode.data.density * 100)}%
                  </span>
                </div>
                <div className="p-3 border border-border rounded-xl bg-muted/20">
                  <span className="text-[9px] font-bold text-muted-foreground block uppercase">Queue Wait</span>
                  <span className="text-base font-black text-foreground mt-0.5 block">
                    {selectedNode.data.queueLength} min
                  </span>
                </div>
                <div className="p-3 border border-border rounded-xl bg-muted/20">
                  <span className="text-[9px] font-bold text-muted-foreground block uppercase">Active Alerts</span>
                  <span className={`text-base font-black mt-0.5 block ${selectedNode.data.alertsCount > 0 ? "text-destructive" : "text-emerald-400"}`}>
                    {selectedNode.data.alertsCount}
                  </span>
                </div>
              </div>

              {/* Active Alerts description */}
              <div className="space-y-3 pt-4 border-t border-border/60">
                <span className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Zone Incident Alerts</span>
                {selectedNodeIncidents.length === 0 ? (
                  <div className="text-xs text-muted-foreground bg-muted/10 p-3 rounded-xl border border-border/40 text-center font-medium">
                    No active incidents in this zone.
                  </div>
                ) : (
                  selectedNodeIncidents.map((inc) => (
                    <div key={inc.id} className="p-3 bg-destructive/5 border border-destructive/20 rounded-xl text-left flex gap-2">
                      <AlertTriangle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <span className="text-xs font-semibold text-foreground block">{inc.description}</span>
                        <span className="text-[9px] text-muted-foreground mt-0.5 block uppercase tracking-wider font-mono">
                          ID: {inc.id.slice(0, 8)}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Reset selected node trigger */}
              <button
                onClick={() => setSelectedNodeId(null)}
                className="w-full text-center py-2.5 border border-border rounded-xl text-xs font-bold hover:bg-muted transition-colors mt-6"
              >
                Clear Inspector Node Selection
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
              <Info className="h-8 w-8 text-muted-foreground/60 mb-2" />
              <span className="text-sm font-bold text-foreground">No Zone Selected</span>
              <p className="text-xs mt-1 max-w-[180px]">Click any node on the stadium map layout to inspect zone metrics, queues, and alert incidents.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
