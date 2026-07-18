import { Handle, Position } from "@xyflow/react";
import type { NodeProps, Node } from "@xyflow/react";
import {
  Maximize2,
  Shield,
  HeartPulse,
  Car,
  Utensils,
  Zap,
  Bus,
  UserCheck,
  Activity,
  Clock,
  AlertTriangle,
} from "lucide-react";

export type TwinNodeData = {
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

export type TwinNode = Node<TwinNodeData, "digitalTwinNode">;

export const DigitalTwinNodeComponent = ({ data }: NodeProps<TwinNode>) => {
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
    Gates: <Maximize2 className="h-3.5 w-3.5" />,
    Security: <Shield className="h-3.5 w-3.5" />,
    Medical: <HeartPulse className="h-3.5 w-3.5" />,
    Parking: <Car className="h-3.5 w-3.5" />,
    "Food Courts": <Utensils className="h-3.5 w-3.5" />,
    Restrooms: <Zap className="h-3.5 w-3.5" />,
    Transportation: <Bus className="h-3.5 w-3.5" />,
    "Volunteer Stations": <UserCheck className="h-3.5 w-3.5" />,
  };

  return (
    <div className={`rounded-xl border bg-card/90 backdrop-blur-md p-2.5 text-left w-44 shadow-2xl transition-all duration-300 hover:scale-105 hover:shadow-primary/5 ${statusBorderColors[data.status]} ${statusBgColors[data.status]}`}>
      <Handle type="target" position={Position.Left} className="w-2 h-2 bg-border rounded-full border-2 border-card" />
      
      {/* Header */}
      <div className="flex justify-between items-start mb-1.5">
        <div className="flex items-center gap-1.5">
          <div className={`p-1 rounded-lg border bg-muted/40 ${statusTextColors[data.status]}`}>
            {typeIcons[data.type] || <Activity className="h-3.5 w-3.5" />}
          </div>
          <div>
            <span className="text-[8px] font-bold text-muted-foreground uppercase tracking-wider block leading-none">{data.type}</span>
            <span className="text-[10px] font-black text-foreground block truncate max-w-[90px] mt-0.5 leading-tight">{data.label}</span>
          </div>
        </div>
        <span className={`text-[8px] font-bold uppercase tracking-wider ${statusTextColors[data.status]}`}>
          {data.status}
        </span>
      </div>

      {/* Health & Density Gauges */}
      <div className="space-y-1.5 text-[10px]">
        <div>
          <div className="flex justify-between text-[8px] font-bold text-muted-foreground mb-0.5">
            <span>HEALTH INDEX</span>
            <span className="text-foreground">{data.health}%</span>
          </div>
          <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                data.health > 80 ? "bg-emerald-500" : data.health > 50 ? "bg-amber-500" : "bg-destructive"
              }`}
              style={{ width: `${data.health}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-[8px] font-bold text-muted-foreground mb-0.5">
            <span>CROWD DENSITY</span>
            <span className="text-foreground">{Math.round(data.density * 100)}%</span>
          </div>
          <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full bg-primary transition-all duration-500`}
              style={{ width: `${Math.round(data.density * 100)}%` }}
            />
          </div>
        </div>

        <div className="flex justify-between items-center text-[8px] font-bold pt-1 border-t border-border/40">
          <span className="text-muted-foreground flex items-center gap-0.5">
            <Clock className="h-2.5 w-2.5" />
            Wait Time
          </span>
          <span className="text-foreground">{data.queueLength}m</span>
        </div>
      </div>

      {/* Badges indicators (Alerts & Recommendations) */}
      <div className="mt-1.5 flex gap-1.5">
        {data.alertsCount > 0 && (
          <span className="flex items-center gap-0.5 rounded bg-destructive/10 border border-destructive/20 px-1 py-0.5 text-[8px] font-black text-destructive animate-pulse">
            <AlertTriangle className="h-2 w-2" />
            {data.alertsCount}
          </span>
        )}
        {data.recsCount > 0 && (
          <span className="flex items-center gap-0.5 rounded bg-primary/10 border border-primary/20 px-1 py-0.5 text-[8px] font-black text-primary">
            <Activity className="h-2 w-2" />
            {data.recsCount}
          </span>
        )}
      </div>

      <Handle type="source" position={Position.Right} className="w-2 h-2 bg-border rounded-full border-2 border-card" />
    </div>
  );
};
