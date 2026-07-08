import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
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
  ShieldCheck,
  AlertTriangle,
  Clock,
  Activity,
  Info,
} from "lucide-react";
import {
  fetchDashboardOverview,
  fetchOperationalState,
  fetchDashboardIncidents,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/operational-state")({
  component: OperationalStateDashboardPage,
});

// Custom Digital Twin Node type definitions
type TwinNodeData = {
  label: string;
  type: string;
  density: number;
  health: number;
  queueLength: number;
  alertsCount: number;
  status: "stable" | "warning" | "critical";
  zoneId: string;
};

type TwinNode = Node<TwinNodeData, "digitalTwinNode">;

// Custom Node Component
const DigitalTwinNode = ({ data }: NodeProps<TwinNode>) => {
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
    <div className={`rounded-2xl border bg-card p-4 shadow-lg min-w-[200px] text-left transition-all ${borderColors[status]} ${bgColors[status]}`}>
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <div className="flex flex-col gap-2">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div className="flex flex-col">
            <span className="text-[8px] font-bold uppercase tracking-wider text-muted-foreground">{data.type}</span>
            <span className="text-xs font-black text-foreground mt-0.5">{data.label}</span>
          </div>
          <span className={`inline-flex rounded px-1.5 py-0.5 text-[8px] font-bold uppercase ${
            status === "stable" ? "bg-emerald-500/10 text-emerald-400" : status === "warning" ? "bg-amber-500/10 text-amber-400" : "bg-destructive/10 text-destructive"
          }`}>
            {status}
          </span>
        </div>

        {/* Metrics details */}
        <div className="grid grid-cols-2 gap-2 py-1.5 border-y border-border/40 text-[9px]">
          <div>
            <span className="text-muted-foreground block">Health</span>
            <span className="font-bold text-foreground">{data.health}%</span>
          </div>
          <div>
            <span className="text-muted-foreground block">Wait Time</span>
            <span className="font-bold text-foreground">{data.queueLength}m</span>
          </div>
        </div>

        {/* Crowd Density progress */}
        <div className="space-y-1">
          <div className="flex justify-between text-[8px] font-bold text-muted-foreground">
            <span>Crowd Density</span>
            <span className={textColors[status]}>{Math.round(data.density * 100)}%</span>
          </div>
          <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                status === "critical" ? "bg-destructive" : status === "warning" ? "bg-amber-500" : "bg-primary"
              }`}
              style={{ width: `${Math.min(data.density * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* Active Alerts */}
        {data.alertsCount > 0 && (
          <div className="flex items-center gap-1.5 rounded-lg bg-destructive/10 border border-destructive/20 p-1.5 text-[9px] font-bold text-destructive animate-pulse mt-0.5">
            <AlertTriangle className="h-3 w-3 shrink-0" />
            <span>{data.alertsCount} Active incident(s)</span>
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
};

const nodeTypes = {
  digitalTwinNode: DigitalTwinNode,
};

// Static templates mapping indices to logical coords & metadata
const ZONE_METADATA_TEMPLATES = [
  { label: "Gate A Ingress Plaza", type: "Gate Entrance", x: 100, y: 100 },
  { label: "North Security Outpost", type: "Security", x: 350, y: 60 },
  { label: "First Aid Medical Hub", type: "Medical", x: 150, y: 280 },
  { label: "Parking Sector Delta", type: "Parking", x: 380, y: 380 },
  { label: "Central Plaza Food Court", type: "Food Court", x: 600, y: 180 },
  { label: "Restroom Facilities West", type: "Restrooms", x: 620, y: 380 },
  { label: "Gate B General Exit", type: "Gate Exit", x: 820, y: 260 },
];

function OperationalStateDashboardPage() {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Queries
  const overviewQuery = useQuery({
    queryKey: ["ops-twin-overview"],
    queryFn: fetchDashboardOverview,
    refetchInterval: 5000,
  });

  const stateQuery = useQuery({
    queryKey: ["ops-twin-state"],
    queryFn: fetchOperationalState,
    refetchInterval: 5000,
  });

  const incidentsQuery = useQuery({
    queryKey: ["ops-twin-incidents"],
    queryFn: () => fetchDashboardIncidents(1, 100),
    refetchInterval: 5000,
  });

  if (overviewQuery.isLoading || stateQuery.isLoading || incidentsQuery.isLoading) {
    return <LoadingScreen />;
  }

  if (overviewQuery.isError || stateQuery.isError || incidentsQuery.isError) {
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

  // Map incidents to zones deterministically using index/modulo since the API doesn't return zone_id directly
  const incidents = rawIncidents.map((inc) => {
    const index = parseInt(inc.id.replace(/-/g, "").slice(0, 4), 16) % Math.max(1, zones.length);
    return {
      ...inc,
      zoneId: zones[index]?.zone_id || "",
    };
  });

  // Map zone records dynamically to React Flow nodes using metadata templates
  const flowNodes = zones.map((zone, index) => {
    const template = ZONE_METADATA_TEMPLATES[index] || {
      label: `Sector Zone ${zone.zone_id.slice(0, 4)}`,
      type: "Zone",
      x: 100 + (index * 160) % 700,
      y: 100 + (index * 110) % 400,
    };

    // Calculate matching alerts for this zone
    const zoneIncidents = incidents.filter((inc) => inc.zoneId === zone.zone_id && !inc.resolved);

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
        status,
        zoneId: zone.zone_id,
      },
    } as TwinNode;
  });

  // Flow connections showing circulation movement
  const flowEdges = [
    { id: "e1", source: flowNodes[0]?.id || "", target: flowNodes[1]?.id || "", animated: true, style: { stroke: "#3b82f6" } },
    { id: "e2", source: flowNodes[1]?.id || "", target: flowNodes[4]?.id || "", animated: true, style: { stroke: "#10b981" } },
    { id: "e3", source: flowNodes[0]?.id || "", target: flowNodes[2]?.id || "", animated: true, style: { stroke: "#6366f1" } },
    { id: "e4", source: flowNodes[2]?.id || "", target: flowNodes[3]?.id || "", animated: true, style: { stroke: "#f59e0b" } },
    { id: "e5", source: flowNodes[3]?.id || "", target: flowNodes[5]?.id || "", animated: true, style: { stroke: "#ec4899" } },
    { id: "e6", source: flowNodes[4]?.id || "", target: flowNodes[6]?.id || "", animated: true, style: { stroke: "#a855f7" } },
  ].filter((e) => e.source && e.target) as Edge[];

  // Find currently selected node details
  const selectedNode = flowNodes.find((n) => n.id === selectedNodeId);
  const selectedNodeIncidents = selectedNode
    ? incidents.filter((inc) => inc.zoneId === selectedNode.id && !inc.resolved)
    : [];

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
          <span>Polling state active</span>
        </div>
      </div>

      {/* Main split dashboard (Canvas Left / Inspector Right) */}
      <div className="grid gap-6 lg:grid-cols-4 flex-1 items-stretch">
        
        {/* React Flow Layout Twin Canvas */}
        <div className="lg:col-span-3 rounded-2xl border border-border bg-card overflow-hidden h-[600px] flex flex-col relative shadow-sm">
          <div className="absolute top-4 left-4 z-10 bg-card/85 backdrop-blur-md border border-border rounded-xl p-3 shadow-md">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <span className="text-xs font-bold text-foreground">Interactive Digital Twin Model</span>
            </div>
            <span className="text-[9px] text-muted-foreground mt-0.5 block">Select a node card to inspect its telemetry and log detail.</span>
          </div>

          <div className="flex-1 h-full w-full">
            <ReactFlow
              nodes={flowNodes}
              edges={flowEdges}
              nodeTypes={nodeTypes}
              fitView
              onNodeClick={(_, node) => setSelectedNodeId(node.id)}
              onPaneClick={() => setSelectedNodeId(null)}
              className="bg-muted/10"
            >
              <Background color="var(--color-border)" gap={16} size={1} />
              <Controls showInteractive={false} className="bg-card border-border fill-foreground" />
              <MiniMap
                nodeColor={(node) => {
                  const status = (node as TwinNode).data?.status;
                  return status === "critical"
                    ? "var(--color-destructive)"
                    : status === "warning"
                    ? "var(--color-amber-500)"
                    : "var(--color-emerald-500)";
                }}
                className="bg-card border-border"
              />
            </ReactFlow>
          </div>
        </div>

        {/* Dynamic Node Telemetry Inspector Panel (Right) */}
        <div className="rounded-2xl border border-border bg-card p-6 flex flex-col justify-between shadow-sm">
          {selectedNode ? (
            <div className="space-y-6 flex-1 flex flex-col justify-between h-full">
              {/* Node Details Header */}
              <div className="space-y-4">
                <div className="flex justify-between items-start border-b border-border pb-3">
                  <div className="flex flex-col">
                    <span className="text-[10px] font-bold text-primary uppercase tracking-wider">
                      {selectedNode.data.type}
                    </span>
                    <h2 className="text-base font-black text-foreground mt-0.5">{selectedNode.data.label}</h2>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    selectedNode.data.status === "stable"
                      ? "bg-emerald-500/10 text-emerald-400"
                      : selectedNode.data.status === "warning"
                      ? "bg-amber-500/10 text-amber-400"
                      : "bg-destructive/10 text-destructive animate-pulse"
                  }`}>
                    {selectedNode.data.status}
                  </span>
                </div>

                {/* Technical UUID */}
                <div className="flex flex-col gap-1 text-[10px] font-mono text-muted-foreground bg-muted/40 p-2.5 rounded-lg border border-border/50">
                  <span className="font-bold">Zone Reference UUID:</span>
                  <span className="truncate">{selectedNode.data.zoneId}</span>
                </div>

                {/* Telemetry charts/meters */}
                <div className="space-y-4 pt-2">
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground font-medium flex items-center gap-1.5">
                        <Activity className="h-3.5 w-3.5" />
                        Crowd Density
                      </span>
                      <span className="font-bold">{Math.round(selectedNode.data.density * 100)}%</span>
                    </div>
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-300 ${
                          selectedNode.data.status === "critical"
                            ? "bg-destructive"
                            : selectedNode.data.status === "warning"
                            ? "bg-amber-500"
                            : "bg-primary"
                        }`}
                        style={{ width: `${Math.min(selectedNode.data.density * 100, 100)}%` }}
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground font-medium flex items-center gap-1.5">
                        <ShieldCheck className="h-3.5 w-3.5" />
                        Zone Health Score
                      </span>
                      <span className="font-bold">{selectedNode.data.health}%</span>
                    </div>
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full bg-emerald-500 transition-all duration-300"
                        style={{ width: `${selectedNode.data.health}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs pt-1.5 border-t border-border/40">
                    <span className="text-muted-foreground font-medium flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5" />
                      Queue Wait Time
                    </span>
                    <span className="font-bold text-foreground">{selectedNode.data.queueLength} minutes</span>
                  </div>
                </div>
              </div>

              {/* Incidents logs */}
              <div className="space-y-3 pt-4 border-t border-border mt-6">
                <span className="text-xs font-bold text-muted-foreground block">Active Zone Alerts</span>
                {selectedNodeIncidents.length === 0 ? (
                  <div className="flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3 text-xs font-bold text-emerald-400">
                    <ShieldCheck className="h-4 w-4 shrink-0" />
                    <span>No incidents active in this zone.</span>
                  </div>
                ) : (
                  <div className="space-y-2.5 max-h-[160px] overflow-y-auto pr-1">
                    {selectedNodeIncidents.map((inc) => (
                      <div key={inc.id} className="p-3 rounded-xl border border-destructive/20 bg-destructive/10 text-xs font-semibold text-destructive flex gap-2">
                        <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5 animate-pulse" />
                        <span className="leading-snug">{inc.description}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center text-center py-20 my-auto text-muted-foreground">
              <Info className="h-10 w-10 mb-3 opacity-60" />
              <span className="text-xs font-bold">No Node Selected</span>
              <p className="text-[10px] mt-1 max-w-[150px]">
                Click on any facility node in the twin canvas to inspect live telemetry.
              </p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
