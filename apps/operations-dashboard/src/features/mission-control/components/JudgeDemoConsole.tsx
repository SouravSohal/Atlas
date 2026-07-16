import { motion, AnimatePresence } from "framer-motion";
import { Sparkles } from "lucide-react";
import { SCENARIO_STEPS } from "../../../store/scenarioSteps";

interface JudgeDemoConsoleProps {
  demoOpen: boolean;
  setDemoOpen: (val: boolean) => void;
  demoMessage: string | null;
  judgeDemoActive: boolean;
  demoStatusMilestone: string;
  playbackScenario: string | null;
  playbackStep: number;
  startJudgeDemo: (scenario: string) => void;
}

export function JudgeDemoConsole({
  demoOpen,
  setDemoOpen,
  demoMessage,
  judgeDemoActive,
  demoStatusMilestone,
  playbackScenario,
  playbackStep,
  startJudgeDemo,
}: JudgeDemoConsoleProps) {
  const stepsList = SCENARIO_STEPS[playbackScenario || ""] || [];
  const progressPercent = stepsList.length > 0 ? ((playbackStep + 1) / stepsList.length) * 100 : 0;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      <AnimatePresence>
        {demoOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            className="mb-3 w-96 rounded-2xl border border-amber-500/30 bg-card/95 backdrop-blur-md shadow-2xl p-5 overflow-hidden text-left relative"
          >
            <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl pointer-events-none" />

            <div className="flex items-center justify-between border-b border-border pb-2.5 mb-4">
              <span className="text-xs font-black text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="h-4 w-4" />
                🏆 ATLAS JUDGE DEMO MODE
              </span>
              <button onClick={() => setDemoOpen(false)} className="text-muted-foreground hover:text-foreground text-xs font-bold">
                Hide
              </button>
            </div>

            <p className="text-[10px] text-muted-foreground mb-4 font-semibold">
              Select a playbook to run the automated demo. Focuses Digital Twin cameras, animates metrics, dispatches backend events, and reviews live AI briefs.
            </p>

            <div className="grid grid-cols-2 gap-2.5">
              {[
                { name: "Crowd Surge", desc: "Gate congestion surge egress" },
                { name: "Medical Emergency", desc: "Spectator health heat stroke" },
                { name: "Heavy Rain", desc: "Plaza shelter diversion" },
                { name: "Lost Child", desc: "Section 208 tracking search" },
                { name: "Match End", desc: "Outflow bottleneck clearance" },
              ].map((scen) => (
                <button
                  key={scen.name}
                  onClick={() => startJudgeDemo(scen.name)}
                  className={`rounded-xl border p-3 text-left transition-all flex flex-col justify-between h-20 ${
                    playbackScenario === scen.name
                      ? "bg-amber-500/10 border-amber-500 text-amber-400 font-bold"
                      : "bg-muted/30 border-border hover:bg-amber-500/5 hover:border-amber-500/20 text-foreground"
                  }`}
                >
                  <span className="text-xs font-black leading-tight block">{scen.name}</span>
                  <span className="text-[8px] text-muted-foreground leading-normal block">{scen.desc}</span>
                </button>
              ))}
            </div>

            {/* Milestones status indicator */}
            {judgeDemoActive && (
              <div className="mt-4 rounded-xl bg-amber-500/5 border border-amber-500/20 p-3 flex flex-col gap-2">
                <div className="flex items-center justify-between text-[9px] font-mono text-amber-400">
                  <span className="animate-pulse">{demoStatusMilestone}</span>
                  <span>TICK PROGRESS</span>
                </div>
                <div className="w-full bg-amber-950/30 rounded-full h-1 overflow-hidden">
                  <motion.div
                    className="bg-amber-400 h-1"
                    animate={{ width: `${progressPercent}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>
            )}

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
        className="flex items-center gap-2 rounded-full bg-amber-500 px-5 py-3 text-xs font-black text-black shadow-2xl hover:opacity-90 transition-all border border-amber-400/20 focus-visible:ring-2 focus-visible:ring-amber-500 outline-none uppercase tracking-wider"
      >
        <Sparkles className="h-4 w-4" />
        🏆 Judge Demo Mode
      </button>
    </div>
  );
}
