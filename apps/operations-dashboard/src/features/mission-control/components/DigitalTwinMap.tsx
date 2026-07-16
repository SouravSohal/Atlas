import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
  MiniMap,
} from "@xyflow/react";
import type { NodeProps, Edge } from "@xyflow/react";
import { motion } from "framer-motion";
import { Brain } from "lucide-react";
import type { StadiumNode } from "../types";
import "@xyflow/react/dist/style.css";

// Custom React flow nodes configuration
const CustomNode = ({ data }: NodeProps<StadiumNode>) => {
  const borderColors = {
    stable: data.isFocused
      ? "border-amber-400 ring-2 ring-amber-400/50"
      : "border-emerald-500/50 shadow-emerald-500/5",
    warning: data.isFocused
      ? "border-amber-400 ring-2 ring-amber-400/50"
      : "border-amber-500/50 shadow-amber-500/5",
    critical: data.isFocused
      ? "border-amber-400 ring-2 ring-amber-400/50"
      : "border-destructive/60 shadow-destructive/5",
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
    <motion.div
      animate={data.isFocused ? { scale: [1, 1.03, 1], y: [0, -2, 0] } : {}}
      transition={{ repeat: Infinity, duration: 2 }}
      className={`rounded-xl border ${borderColors[data.status]} ${bgColors[data.status]} p-2.5 text-left w-44 backdrop-blur-md shadow-lg relative text-foreground`}
    >
      {data.isFocused && (
        <span className="absolute -top-2.5 -right-2 bg-amber-500 text-black text-[7px] font-black px-1.5 py-0.5 rounded border border-black shadow uppercase animate-pulse">
          🎯 focus
        </span>
      )}
      <Handle type="target" position={Position.Left} className="w-1.5 h-1.5 bg-border" />

      {/* Node Title */}
      <div className="flex items-center justify-between gap-1.5 border-b border-border/40 pb-1.5">
        <div className="flex items-center gap-1.5">
          <span className={`h-1.5 w-1.5 rounded-full ${indicatorColors[data.status]}`} />
          <span className="text-[9px] font-black tracking-wide uppercase tracking-wider block truncate w-24">
            {data.label}
          </span>
        </div>
        <span className="text-[7px] font-mono text-muted-foreground uppercase">{data.type}</span>
      </div>

      {/* Grid details */}
      <div className="grid grid-cols-2 gap-1.5 mt-2 text-[8px] font-mono text-muted-foreground">
        <div>
          <span>HEALTH</span>
          <span className="font-bold text-foreground block">{data.health}%</span>
        </div>
        <div>
          <span>DENSITY</span>
          <span className="font-bold text-foreground block">{data.density}%</span>
        </div>
        <div>
          <span>QUEUE</span>
          <span className="font-bold text-foreground block">{data.queue}m</span>
        </div>
        <div>
          <span>ALERTS</span>
          <span className={`font-bold block ${data.alerts > 0 ? "text-destructive" : "text-foreground"}`}>
            {data.alerts}
          </span>
        </div>
      </div>

      <div className="mt-2 border-t border-border/40 pt-1.5 flex items-center justify-between text-[7px] font-mono text-muted-foreground">
        <span>STAFF: {data.resources}</span>
        {data.recs > 0 && <span className="text-amber-400 font-bold">RECS: {data.recs}</span>}
      </div>

      {data.predictionOverlay && (
        <div className="mt-2.5 border-t border-purple-500/30 pt-2 flex flex-col gap-1 text-[8px] text-purple-300">
          <div className="flex items-center gap-1 font-bold">
            <span className="relative flex h-1.5 w-1.5 shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-purple-500" />
            </span>
            <span className="uppercase font-black text-purple-400">Predicted Risk:</span>
          </div>
          <p className="font-medium text-foreground leading-tight line-clamp-2">
            {data.predictionOverlay.prediction}
          </p>
          <div className="flex items-center justify-between text-[7px] font-mono mt-0.5 text-purple-400/80">
            <span>Conf: {Math.round(data.predictionOverlay.confidence * 100)}%</span>
            <span>Time: {data.predictionOverlay.timeline}</span>
          </div>
        </div>
      )}

      <Handle type="source" position={Position.Right} className="w-1.5 h-1.5 bg-border" />
    </motion.div>
  );
};

const nodeTypes = {
  stadiumNode: CustomNode,
};

interface DigitalTwinMapProps {
  flowNodes: StadiumNode[];
  flowEdges: Edge[];
  focusedNodeIndex: number | null;
  setFocusedNodeIndex: (idx: number | null) => void;
  showPredictionsOverlay: boolean;
  setShowPredictionsOverlay: (val: boolean) => void;
  setToastMessage: (msg: string | null) => void;
}

export function DigitalTwinMap({
  flowNodes,
  flowEdges,
  focusedNodeIndex,
  setFocusedNodeIndex,
  showPredictionsOverlay,
  setShowPredictionsOverlay,
  setToastMessage,
}: DigitalTwinMapProps) {
  const currentFocusedNode = focusedNodeIndex !== null ? flowNodes[focusedNodeIndex] : null;

  return (
    <div className="lg:col-span-2 rounded-2xl border border-border bg-card/45 backdrop-blur-md overflow-hidden h-[540px] flex flex-col relative shadow-sm">
      {/* Header Controls */}
      <div className="p-4 border-b border-border bg-muted/20 flex flex-wrap items-center justify-between gap-3">
        <div className="text-left">
          <span className="text-xs font-bold text-foreground block">Stadium Digital Twin</span>
          <span className="text-[9px] text-muted-foreground mt-0.5 block">Interact to inspect flow vectors.</span>
        </div>

        {/* Quick Node Search Select */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowPredictionsOverlay(!showPredictionsOverlay)}
            className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-[10px] font-bold transition-all ${
              showPredictionsOverlay
                ? "bg-purple-500/20 border-purple-500/40 text-purple-300 shadow-md shadow-purple-500/10"
                : "bg-card border-border hover:bg-muted text-muted-foreground"
            }`}
          >
            <Brain className={`h-3 w-3 ${showPredictionsOverlay ? "text-purple-400 animate-pulse" : ""}`} />
            <span>Predictions Overlay</span>
          </button>

          <span className="text-[9px] font-black text-muted-foreground uppercase font-mono border-l border-border/60 pl-2">
            Go to:
          </span>
          <select
            value={focusedNodeIndex !== null ? `node-${focusedNodeIndex}` : ""}
            onChange={(e) => {
              const val = e.target.value;
              if (!val) {
                setFocusedNodeIndex(null);
              } else {
                const idx = parseInt(val.split("-")[1]);
                setFocusedNodeIndex(idx);
              }
            }}
            className="rounded-lg border border-border bg-card px-2 py-1 text-[10px] font-bold outline-none cursor-pointer text-foreground"
          >
            <option value="">Select Sector...</option>
            {flowNodes.map((n, idx) => (
              <option key={n.id} value={`node-${idx}`}>
                {n.data.label}
              </option>
            ))}
          </select>
          {focusedNodeIndex !== null && (
            <button
              onClick={() => setFocusedNodeIndex(null)}
              className="p-1 rounded bg-muted hover:bg-muted/40 text-[9px] font-black uppercase text-muted-foreground"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col md:flex-row h-full w-full overflow-hidden">
        {/* Map Canvas */}
        <div className="flex-1 h-full relative border-r border-border/40">
          <ReactFlow
            nodes={flowNodes}
            edges={flowEdges}
            nodeTypes={nodeTypes}
            fitView
            onNodeClick={(_, node) => {
              const idx = flowNodes.findIndex((n) => n.id === node.id);
              if (idx !== -1) setFocusedNodeIndex(idx);
            }}
            className="bg-muted/10 h-full w-full"
          >
            <Background color="var(--color-border)" gap={16} size={1} />
            <Controls showInteractive={false} className="bg-card border-border fill-foreground" />
            <MiniMap
              className="bg-card border-border border rounded-xl"
              nodeColor={(node) => {
                if (node.data?.status === "critical") return "#ref4444";
                if (node.data?.status === "warning") return "#f59e0b";
                return "#10b981";
              }}
              maskColor="rgba(0, 0, 0, 0.4)"
            />
          </ReactFlow>
        </div>

        {/* Inspector Panel */}
        <div className="w-full md:w-64 h-full bg-card/25 backdrop-blur-md p-4 flex flex-col justify-between overflow-y-auto border-t md:border-t-0 md:border-l border-border/40 text-left">
          {currentFocusedNode ? (
            (() => {
              const node = currentFocusedNode;
              const statusColors = {
                stable: "text-emerald-400",
                warning: "text-amber-500",
                critical: "text-destructive",
              };

              return (
                <div className="flex flex-col gap-4 h-full justify-between">
                  <div className="flex flex-col gap-3.5">
                    <div className="border-b border-border/40 pb-2">
                      <span className={`text-[8px] font-black uppercase font-mono ${statusColors[node.data.status]}`}>
                        {node.data.type} status: {node.data.status}
                      </span>
                      <h4 className="text-xs font-black uppercase text-foreground mt-0.5">
                        {node.data.label}
                      </h4>
                    </div>

                    {/* Telemetry specs */}
                    <div className="grid grid-cols-2 gap-2 text-[9px] font-mono text-muted-foreground bg-muted/20 p-2.5 rounded-lg border border-border/40">
                      <div>
                        <span>HEALTH</span>
                        <span className="font-bold text-foreground block">{node.data.health}%</span>
                      </div>
                      <div>
                        <span>DENSITY</span>
                        <span className="font-bold text-foreground block">{node.data.density}%</span>
                      </div>
                      <div>
                        <span>WAIT TIME</span>
                        <span className="font-bold text-foreground block">{node.data.queue} min</span>
                      </div>
                      <div>
                        <span>LIMIT</span>
                        <span className="font-bold text-foreground block">{node.data.capacity} pax</span>
                      </div>
                    </div>

                    {/* Staff / Alerts */}
                    <div className="flex flex-col gap-1 text-[9px] font-mono">
                      <span className="text-muted-foreground uppercase">ASSIGNED STAFF:</span>
                      <span className="font-bold text-foreground uppercase">{node.data.resources}</span>
                    </div>

                    {node.data.recs > 0 && (
                      <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-[9px] text-amber-500 leading-relaxed font-semibold">
                        ⚠️ AI Recommendations active: Reallocate volunteer squad to clear local bottlenecks.
                      </div>
                    )}
                  </div>

                  {/* Action */}
                  <button
                    onClick={() => {
                      setToastMessage(`Command dispatched: Staff rerouted to ${node.data.label}.`);
                      setTimeout(() => setToastMessage(null), 3000);
                    }}
                    className="w-full rounded-lg bg-primary py-2 text-[10px] font-black uppercase text-primary-foreground tracking-wider hover:opacity-90 transition-opacity"
                  >
                    Optimize Sector
                  </button>
                </div>
              );
            })()
          ) : (
            <div className="flex flex-col justify-between h-full">
              <div className="flex flex-col gap-4">
                <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest border-b border-border/40 pb-2">
                  Sector Inspector
                </span>
                <p className="text-[10px] text-muted-foreground leading-relaxed font-medium">
                  Click any node on the stadium map to inspect real-time flow telemetry, pending recommendations, incident history, and workforce assignments.
                </p>
              </div>

              {/* Legend */}
              <div className="flex flex-col gap-1.5 border-t border-border/40 pt-4 text-[8px] font-black uppercase text-muted-foreground tracking-wider">
                <span className="mb-1 block text-[7px] text-muted-foreground font-semibold">Status Legend</span>
                <div className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" /> Nominal state
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" /> Warning limits
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-destructive animate-pulse" /> Critical bottleneck
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
