import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X, Info } from "lucide-react";
import type { Recommendation, ExplanationDetails } from "../types";

interface ExplanationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedRec: Recommendation | null;
  explanationDetails: ExplanationDetails | null;
}

export function ExplanationDrawer({
  isOpen,
  onClose,
  selectedRec,
  explanationDetails,
}: ExplanationDrawerProps) {
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
    <AnimatePresence>
      {isOpen && selectedRec && explanationDetails && (
        <div className="fixed inset-0 z-50 flex justify-end">
          {/* Overlay backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Sliding Container */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 220 }}
            className="relative w-full max-w-md h-full bg-card/95 border-l border-border p-6 shadow-2xl overflow-y-auto flex flex-col justify-between text-left"
          >
            <div>
              {/* Header */}
              <div className="flex items-center justify-between border-b border-border pb-4 mb-6">
                <div className="flex items-center gap-2 text-primary">
                  <Sparkles className="h-5 w-5 text-primary animate-pulse" />
                  <span className="text-xs font-black uppercase tracking-widest">
                    AI Explanation Summary
                  </span>
                </div>
                <button
                  onClick={onClose}
                  className="p-1.5 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Explanation Content */}
              <div className="flex flex-col gap-6">
                {/* Recommendation details card */}
                <div className="rounded-xl border border-border bg-muted/30 p-4">
                  <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
                    Target Action
                  </span>
                  <span className="text-xs font-black text-foreground uppercase tracking-wide block mt-1.5">
                    {formatDetails(selectedRec.details)}
                  </span>
                </div>

                {/* Why generated */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-[9px] font-black text-primary uppercase tracking-widest block">
                    Reasoning Analysis
                  </span>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {explanationDetails.why}
                  </p>
                </div>

                {/* Telemetry data */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-[9px] font-black text-primary uppercase tracking-widest block">
                    Operational State Considered
                  </span>
                  <ul className="flex flex-col gap-1 text-xs text-muted-foreground list-disc pl-4">
                    {explanationDetails.data_considered.map((d, idx) => (
                      <li key={idx}>{d}</li>
                    ))}
                  </ul>
                </div>

                {/* Business Rules */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-[9px] font-black text-primary uppercase tracking-widest block">
                    Business Rules Triggered
                  </span>
                  <ul className="flex flex-col gap-1.5 text-xs text-muted-foreground list-disc pl-4">
                    {explanationDetails.business_rules.map((rule, idx) => (
                      <li key={idx}>{rule}</li>
                    ))}
                  </ul>
                </div>

                {/* Alternatives */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-[9px] font-black text-primary uppercase tracking-widest block">
                    Alternative Strategic Actions
                  </span>
                  <ul className="flex flex-col gap-1 text-xs text-muted-foreground list-disc pl-4">
                    {explanationDetails.alternatives.map((alt, idx) => (
                      <li key={idx}>{alt}</li>
                    ))}
                  </ul>
                </div>

                {/* Risks */}
                <div className="flex flex-col gap-1.5">
                  <span className="text-[9px] font-black text-destructive uppercase tracking-widest block">
                    Expected Risks & Trade-offs
                  </span>
                  <ul className="flex flex-col gap-1 text-xs text-muted-foreground list-disc pl-4">
                    {explanationDetails.risks.map((risk, idx) => (
                      <li key={idx} className="text-destructive/80 font-semibold">
                        {risk}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Bottom Confidence dial */}
            <div className="border-t border-border pt-5 mt-6 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Info className="h-4 w-4 text-muted-foreground" />
                <span className="text-[10px] font-black text-muted-foreground uppercase">
                  AI Accuracy Rating
                </span>
              </div>
              <span className="text-xs font-black text-foreground font-mono bg-primary/10 border border-primary/20 text-primary px-3 py-1 rounded-full">
                {(explanationDetails.confidence * 100).toFixed(0)}% Confidence
              </span>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
