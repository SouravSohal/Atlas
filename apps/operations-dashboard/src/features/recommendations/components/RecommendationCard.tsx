import {
  CheckCircle,
  XCircle,
  HelpCircle,
  Play,
  UserCheck,
} from "lucide-react";
import type { Recommendation } from "../types";

interface RecommendationCardProps {
  rec: Recommendation;
  isSelected: boolean;
  onSelectedChange: (checked: boolean) => void;
  onExplainRequest: () => void;
  onSimulateRequest: () => void;
  onDelegateRequest: () => void;
  onStatusChange: (status: string) => void;
}

export function RecommendationCard({
  rec,
  isSelected,
  onSelectedChange,
  onExplainRequest,
  onSimulateRequest,
  onDelegateRequest,
  onStatusChange,
}: RecommendationCardProps) {
  const formatDetails = (detailsStr: string) => {
    try {
      const parsed = JSON.parse(detailsStr);
      if (parsed.explanation) return parsed.explanation;
      if (parsed.trigger_reason) return parsed.trigger_reason;
      if (parsed.expected_impact) return `Impact: ${parsed.expected_impact}`;
      return detailsStr;
    } catch {
      return detailsStr;
    }
  };

  return (
    <div
      className={`rounded-2xl border bg-card/65 backdrop-blur-md p-5 hover:shadow-lg transition-all flex flex-col justify-between relative ${
        rec.status === "approved"
          ? "border-emerald-500/30 shadow-emerald-950/5"
          : rec.status === "rejected"
          ? "border-destructive/30 shadow-destructive-950/5 opacity-70"
          : "border-border"
      }`}
    >
      <div>
        {/* Card Header */}
        <div className="flex items-start justify-between gap-3 border-b border-border/40 pb-2.5">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={(e) => onSelectedChange(e.target.checked)}
              className="rounded border-border accent-primary cursor-pointer w-4 h-4"
            />
            <span className="text-[10px] font-black text-foreground uppercase tracking-wider font-mono">
              {rec.action_type}
            </span>
          </div>

          <span
            className={`text-[8px] font-black uppercase px-2 py-0.5 rounded border ${
              rec.status === "approved"
                ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                : rec.status === "rejected"
                ? "bg-destructive/10 border-destructive/20 text-destructive"
                : "bg-amber-500/10 border-amber-500/20 text-amber-500 animate-pulse"
            }`}
          >
            {rec.status}
          </span>
        </div>

        {/* Recommendation Details */}
        <p className="text-xs font-black text-foreground uppercase mt-3 leading-snug">
          {formatDetails(rec.details)}
        </p>

        {/* Metric Metadata pills */}
        <div className="grid grid-cols-2 gap-2 mt-4 text-[9px] font-mono text-muted-foreground bg-muted/20 border border-border/40 rounded-xl p-3">
          <div className="flex flex-col">
            <span>PRIORITY</span>
            <span className="font-bold text-foreground mt-0.5 uppercase">
              {rec.priority}
            </span>
          </div>
          <div className="flex flex-col">
            <span>CONFIDENCE</span>
            <span className="font-bold text-foreground mt-0.5">
              {((rec.confidence || 0) * 100).toFixed(0)}%
            </span>
          </div>
          <div className="flex flex-col">
            <span>TIME TO RESOLVE</span>
            <span className="font-bold text-foreground mt-0.5">
              {rec.resolutionTime}
            </span>
          </div>
          <div className="flex flex-col">
            <span>EXPECTED IMPACT</span>
            <span className="font-bold text-foreground mt-0.5 uppercase tracking-tight">
              {rec.impact}
            </span>
          </div>
        </div>

        <div className="mt-3.5 flex flex-wrap gap-1">
          {rec.resources?.map((res: string, idx: number) => (
            <span
              key={idx}
              className="bg-muted/40 border border-border text-[8px] font-black uppercase text-muted-foreground px-2 py-0.5 rounded"
            >
              {res}
            </span>
          ))}
        </div>
      </div>

      {/* Card Actions Bottom Row */}
      <div className="mt-5 border-t border-border/40 pt-4 flex flex-wrap gap-2 items-center justify-between">
        <div className="flex items-center gap-1.5">
          {/* Explain drawer button */}
          <button
            onClick={onExplainRequest}
            className="rounded-lg border border-border bg-muted/25 hover:bg-muted/50 p-2 text-muted-foreground hover:text-foreground transition-colors"
            title="Request Explanation"
          >
            <HelpCircle className="h-4 w-4" />
          </button>
          <button
            onClick={onSimulateRequest}
            className="rounded-lg border border-border bg-muted/25 hover:bg-muted/50 p-2 text-muted-foreground hover:text-foreground transition-colors"
            title="Simulate Impact"
          >
            <Play className="h-4 w-4" />
          </button>
          <button
            onClick={onDelegateRequest}
            className="rounded-lg border border-border bg-muted/25 hover:bg-muted/50 p-2 text-muted-foreground hover:text-foreground transition-colors"
            title="Delegate Task"
          >
            <UserCheck className="h-4 w-4" />
          </button>
        </div>

        <div className="flex items-center gap-1.5">
          {rec.status !== "approved" && rec.status !== "completed" && (
            <button
              onClick={() => onStatusChange("approved")}
              className="rounded-lg bg-emerald-500 px-3 py-1.5 text-[10px] font-black text-black uppercase tracking-wider hover:opacity-90 flex items-center gap-1"
            >
              <CheckCircle className="h-3 w-3" />
              Approve
            </button>
          )}
          {rec.status !== "rejected" && rec.status !== "completed" && (
            <button
              onClick={() => onStatusChange("rejected")}
              className="rounded-lg bg-destructive px-3 py-1.5 text-[10px] font-black text-destructive-foreground uppercase tracking-wider hover:opacity-90 flex items-center gap-1"
            >
              <XCircle className="h-3 w-3" />
              Reject
            </button>
          )}
          {rec.status === "approved" && (
            <button
              onClick={() => onStatusChange("completed")}
              className="rounded-lg bg-primary px-3 py-1.5 text-[10px] font-black text-primary-foreground uppercase tracking-wider hover:opacity-90 flex items-center gap-1"
            >
              <CheckCircle className="h-3 w-3" />
              Complete
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
