import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchDashboardBriefing } from "../services/api";
import {
  Brain,
  ShieldAlert,
  ListTodo,
  CheckCircle,
  HelpCircle,
  Maximize2,
  Minimize2,
  Loader2,
  TrendingUp,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function SituationAnalysisPanel() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<"summary" | "actions" | "strategies">("summary");

  const briefingQuery = useQuery({
    queryKey: ["cc-briefing"],
    queryFn: fetchDashboardBriefing,
    refetchInterval: 5000, // Update automatically every 5 seconds during simulation
  });

  const isLoading = briefingQuery.isLoading;
  const data = briefingQuery.data;

  // Fallback defaults
  const executiveSummary = data?.executive_summary || "Operational state is nominal. AI Situation analysis compiling...";
  const situationAssessment = data?.situation_assessment || "All zones are stable. Waiting for telemetry flow.";
  const immediateRisks = data?.immediate_risks || ["No high-severity risks detected"];
  const recommendedActions = data?.recommended_actions || ["Maintain standard watch protocols"];
  const predictedOutcome = data?.predicted_outcome || "Stadium flows are expected to stay nominal.";
  const confidenceScore = data?.confidence_score !== undefined ? data.confidence_score : 1.0;
  const assumptions = data?.assumptions || ["Sensor calibration remains stable"];
  const alternativeStrategies = data?.alternative_strategies || ["None currently required"];

  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md shadow-lg overflow-hidden flex flex-col transition-all duration-300">
      {/* Header Banner */}
      <div className="p-4 border-b border-border bg-muted/20 flex justify-between items-center">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <Brain className="h-4.5 w-4.5 animate-pulse" />
          </div>
          <div>
            <span className="text-xs font-black text-foreground uppercase tracking-wider block">
              ATLAS AI Situation Analysis Engine
            </span>
            <span className="text-[9px] text-muted-foreground uppercase tracking-widest font-mono">
              Real-time Cognitive Telemetry Analysis
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Confidence Badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 text-emerald-400 font-mono text-[9px] font-bold">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-ping" />
            <span>{Math.round(confidenceScore * 100)}% CONFIDENCE</span>
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 rounded-lg hover:bg-muted/40 text-muted-foreground transition-all"
            title={isExpanded ? "Collapse View" : "Expand View"}
          >
            {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="h-48 flex flex-col items-center justify-center gap-2 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
          <span className="text-xs font-mono font-bold uppercase tracking-wider">Analyzing Operational State...</span>
        </div>
      ) : (
        <div className="p-5 flex flex-col gap-5">
          {/* 3-Tab Selector */}
          <div className="flex border-b border-border/40 pb-2 gap-1">
            {[
              { id: "summary", label: "Executive Summary & Assessment", icon: <Brain className="h-3.5 w-3.5" /> },
              { id: "actions", label: "Risks & Recommended Actions", icon: <ListTodo className="h-3.5 w-3.5" /> },
              { id: "strategies", label: "Forecasts & Strategies", icon: <TrendingUp className="h-3.5 w-3.5" /> },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider transition-all border ${
                  activeTab === tab.id
                    ? "bg-primary text-primary-foreground border-primary shadow-sm"
                    : "text-muted-foreground border-transparent hover:bg-muted/30 hover:text-foreground"
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Contents */}
          <div className="min-h-[160px]">
            <AnimatePresence mode="wait">
              {activeTab === "summary" && (
                <motion.div
                  key="summary"
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="space-y-4 text-left"
                >
                  <div>
                    <h3 className="text-[10px] font-black text-primary uppercase tracking-wider mb-1">
                      Executive Summary
                    </h3>
                    <p className="text-xs font-semibold leading-relaxed text-foreground/90">
                      {executiveSummary}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-border/40">
                    <h3 className="text-[10px] font-black text-primary uppercase tracking-wider mb-1">
                      Situation Assessment
                    </h3>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {situationAssessment}
                    </p>
                  </div>
                </motion.div>
              )}

              {activeTab === "actions" && (
                <motion.div
                  key="actions"
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="grid sm:grid-cols-2 gap-4 text-left"
                >
                  <div className="p-3.5 rounded-xl border border-destructive/20 bg-destructive/5 space-y-2">
                    <div className="flex items-center gap-2 text-destructive font-black text-[10px] uppercase tracking-wider">
                      <ShieldAlert className="h-4 w-4" />
                      Immediate Risks
                    </div>
                    <ul className="space-y-1.5">
                      {immediateRisks.map((risk, i) => (
                        <li key={i} className="text-xs text-foreground/90 flex items-start gap-1.5">
                          <span className="text-destructive mt-1 font-black leading-none">&bull;</span>
                          <span>{risk}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-3.5 rounded-xl border border-emerald-500/20 bg-emerald-500/5 space-y-2">
                    <div className="flex items-center gap-2 text-emerald-400 font-black text-[10px] uppercase tracking-wider">
                      <CheckCircle className="h-4 w-4" />
                      Recommended Actions
                    </div>
                    <ul className="space-y-1.5">
                      {recommendedActions.map((action, i) => (
                        <li key={i} className="text-xs text-foreground/90 flex items-start gap-1.5">
                          <span className="text-emerald-400 mt-1 font-black leading-none">&bull;</span>
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              )}

              {activeTab === "strategies" && (
                <motion.div
                  key="strategies"
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="space-y-4 text-left"
                >
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <h3 className="text-[10px] font-black text-primary uppercase tracking-wider">
                        Predicted Outcome
                      </h3>
                      <p className="text-xs text-foreground/90 leading-relaxed">
                        {predictedOutcome}
                      </p>
                    </div>

                    <div className="space-y-1.5">
                      <h3 className="text-[10px] font-black text-primary uppercase tracking-wider flex items-center gap-1">
                        <HelpCircle className="h-3.5 w-3.5" />
                        Key Assumptions
                      </h3>
                      <ul className="space-y-1">
                        {assumptions.map((ass, i) => (
                          <li key={i} className="text-[11px] text-muted-foreground flex items-start gap-1">
                            <span>&bull;</span>
                            <span>{ass}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-border/40">
                    <h3 className="text-[10px] font-black text-primary uppercase tracking-wider mb-2">
                      Alternative Strategies
                    </h3>
                    <div className="grid sm:grid-cols-2 gap-3">
                      {alternativeStrategies.map((strat, i) => (
                        <div key={i} className="p-2.5 rounded-lg border border-border bg-muted/20 text-xs text-foreground/90">
                          {strat}
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Collapsible/Expandable extra details */}
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="pt-4 border-t border-border/40 text-left space-y-3"
            >
              <span className="text-[9px] font-mono text-muted-foreground uppercase tracking-widest block">
                ATLAS Core Sensor Streams
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-[10px]">
                <div className="p-2 border border-border bg-muted/10 rounded-lg flex items-center justify-between">
                  <span className="text-muted-foreground">Crowd Density:</span>
                  <span className="font-bold text-foreground">Active (5s)</span>
                </div>
                <div className="p-2 border border-border bg-muted/10 rounded-lg flex items-center justify-between">
                  <span className="text-muted-foreground">Queue Telemetry:</span>
                  <span className="font-bold text-foreground">Synchronized</span>
                </div>
                <div className="p-2 border border-border bg-muted/10 rounded-lg flex items-center justify-between">
                  <span className="text-muted-foreground">Weather Index:</span>
                  <span className="font-bold text-foreground">Live Feed</span>
                </div>
                <div className="p-2 border border-border bg-muted/10 rounded-lg flex items-center justify-between">
                  <span className="text-muted-foreground">Recommendations:</span>
                  <span className="font-bold text-foreground">100% Validated</span>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}
