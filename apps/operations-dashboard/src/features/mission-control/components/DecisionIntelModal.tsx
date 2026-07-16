import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";

interface DecisionIntelModalProps {
  selectedWhyRec: any | null;
  onClose: () => void;
}

export function DecisionIntelModal({
  selectedWhyRec,
  onClose,
}: DecisionIntelModalProps) {
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

  return (
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
              <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />

              {/* Header */}
              <div className="flex items-start justify-between border-b border-border pb-3.5 mb-5">
                <div>
                  <span className="text-xs font-black text-purple-400 uppercase tracking-widest block font-mono">
                    AI Decision Intelligence Context
                  </span>
                  <h3 className="text-sm font-black text-foreground uppercase mt-1">
                    {selectedWhyRec.action_type}
                  </h3>
                </div>
                <button
                  onClick={onClose}
                  className="rounded-lg p-1.5 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
                  aria-label="Close details"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Body Content */}
              <div className="space-y-4 max-h-[380px] overflow-y-auto pr-1">
                {/* Why */}
                <div>
                  <span className="text-xs font-black text-purple-400 uppercase tracking-wider block font-mono">
                    Why is this action recommended?
                  </span>
                  <p className="text-xs text-foreground mt-1 leading-relaxed font-semibold">
                    {details.why}
                  </p>
                </div>

                {/* Evidence */}
                <div>
                  <span className="text-xs font-black text-muted-foreground uppercase tracking-wider block font-mono">
                    Evidence base
                  </span>
                  <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                    {details.evidence}
                  </p>
                </div>

                {/* Operational Data Used */}
                <div>
                  <span className="text-xs font-black text-muted-foreground uppercase tracking-wider block font-mono">
                    Operational parameters analyzed
                  </span>
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {details.operational_data_used.map((field: string, idx: number) => (
                      <span
                        key={idx}
                        className="rounded-md border border-border bg-muted/30 px-2 py-0.5 text-xs font-mono font-bold text-foreground uppercase"
                      >
                        {field}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Confidence Level & Priority */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs font-black text-muted-foreground uppercase tracking-wider block font-mono">
                      Confidence Level
                    </span>
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-purple-500/20 bg-purple-500/10 px-2.5 py-1 text-xs font-mono font-black text-purple-400 uppercase mt-1">
                      {((selectedWhyRec.confidence || 0.95) * 100).toFixed(0)}% Certitude
                    </span>
                  </div>
                  <div>
                    <span className="text-xs font-black text-muted-foreground uppercase tracking-wider block font-mono">
                      Priority Classification
                    </span>
                    <span
                      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-mono font-black uppercase mt-1 ${
                        selectedWhyRec.priority === "critical"
                          ? "bg-destructive/10 border-destructive/20 text-destructive"
                          : "bg-amber-500/10 border-amber-500/20 text-amber-500"
                      }`}
                    >
                      {selectedWhyRec.priority}
                    </span>
                  </div>
                </div>

                {/* Alternative Actions */}
                <div>
                  <span className="text-xs font-black text-muted-foreground uppercase tracking-wider block font-mono">
                    Alternative responses
                  </span>
                  <ul className="list-disc pl-4 space-y-1 mt-1 text-xs text-muted-foreground">
                    {details.alternative_actions.map((act: string, idx: number) => (
                      <li key={idx}>{act}</li>
                    ))}
                  </ul>
                </div>

                {/* Trade-offs */}
                <div>
                  <span className="text-xs font-black text-purple-400/80 uppercase tracking-wider block font-mono">
                    Operational trade-offs
                  </span>
                  <p className="text-xs text-purple-200 mt-1 leading-relaxed bg-purple-500/5 border border-purple-500/10 p-2.5 rounded-xl">
                    {details.trade_offs}
                  </p>
                </div>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-end border-t border-border pt-4 mt-5">
                <button
                  onClick={onClose}
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
  );
}
