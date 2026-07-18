import { useState, useEffect } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Sparkles,
  Play,
  Pause,
  ArrowRight,
  Brain,
  ShieldCheck,
  Tv,
  CheckCircle,
  Clock,
  Compass,
  ArrowLeft,
  Volume2,
  Sliders,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export const Route = createFileRoute("/final-demo")({
  component: FinalDemoPage,
});

interface DemoStep {
  title: string;
  narratorText: string;
  highlightPanel: string;
  screenTitle: string;
  subtitle: string;
}

const DEMO_STEPS: DemoStep[] = [
  {
    title: "1. Welcome & Project Pitch",
    narratorText: "Welcome to ATLAS, the AI-First Venue Management Platform purpose-built for the FIFA World Cup 2026. ATLAS addresses the critical challenge of managing multi-lingual crowds, transport bottlenecks, and emergency dispatches across 16 host cities. We utilize Gemini to synchronize telemetry, run predictive crowd modeling, and deliver verified operations decision support. Click Start to begin the guided sequence.",
    highlightPanel: "pitch",
    screenTitle: "ATLAS Operations Intelligence",
    subtitle: "AI-First Stadium Command & Control Platform"
  },
  {
    title: "2. Command Center Overview",
    narratorText: "This is the main Command Center for FIFA Match-Day Operations. The upper panel displays real-time telemetry (crowd density, wait times, gate health), while the left-hand panel hosts our Gemini-powered Operational Briefing and Copilot Assistant. The right-hand panel streams live security and logistical incidents via WebSockets.",
    highlightPanel: "mission_control",
    screenTitle: "Operations Command Center",
    subtitle: "Real-time Stadium Telemetry"
  },
  {
    title: "3. Interactive Digital Twin",
    narratorText: "The interactive Stadium Digital Twin maps exact venue nodes (ingress gates, pitch perimeter, VIP lounges, volunteer zones). Upon triggering a security or medical incident, the system executes camera auto-focus tracking, visually highlighting the zone to accelerate dispatch times.",
    highlightPanel: "digital_twin",
    screenTitle: "Stadium Digital Twin",
    subtitle: "Interactive Facility Network & Flow Topology"
  },
  {
    title: "4. Stress Scenario Selection",
    narratorText: "We support pre-configured FIFA operational playbooks: Post-Match Egress Surge at Estadio Azteca, Medical Emergency in General Stands, Ticket Scanner Network Failures, and VIP Delegation Arrivals. Triggering a scenario dispatches database updates and activates AI response workflows.",
    highlightPanel: "scenario_selector",
    screenTitle: "Demo Playbook Selector",
    subtitle: "Stadium Operations Stress-Testing"
  },
  {
    title: "5. Real-time AI Copilot Briefings",
    narratorText: "The Gemini Copilot streams context-aware operational analyses for incoming incidents. The operator can converse naturally with the Copilot (e.g. 'Is there congestion?' or 'List nearest volunteers') to generate instant localized solutions.",
    highlightPanel: "copilot",
    screenTitle: "ATLAS Copilot AI Assistant",
    subtitle: "Context-Aware Operations Conversation"
  },
  {
    title: "6. Structured Decision Engine",
    narratorText: "Every action is evaluated by our structured Decision Engine. Gemini assesses security risks, calculates expected operational impact on spectator safety, estimates recovery time, and isolates staffing constraints against FIFA standard rules.",
    highlightPanel: "decision_engine",
    screenTitle: "ATLAS AI Decision Engine",
    subtitle: "Verified Operations Risk Analyzer"
  },
  {
    title: "7. AI Action Center (Human-in-the-Loop)",
    narratorText: "To ensure absolute safety, the Action Center enforces a 'Human-in-the-Loop' workflow. Stadium operators can simulate, reject, or approve recommendations. Approval fires domain events, updates digital twin states, and logs auditable action records.",
    highlightPanel: "action_center",
    screenTitle: "AI Action Review Center",
    subtitle: "Human Operator Oversight Console"
  },
  {
    title: "8. Executive Situation Room",
    narratorText: "The Executive Situation Room delivers high-level tournament operational intelligence. It integrates transit status feeds (shuttles/metro), weather telemetry, and a Gemini-summarized briefing of match-day highlights for FIFA directors.",
    highlightPanel: "executive_room",
    screenTitle: "Executive Situation Room",
    subtitle: "Strategic Leadership Overview Panel"
  },
  {
    title: "9. Match Operations Timeline Replay",
    narratorText: "The Match Operations Timeline allows operators to scrub through match-day history, reviewing chronological security incident logs, crowd density fluctuations, and the corresponding operator decisions.",
    highlightPanel: "timeline_scrubber",
    screenTitle: "Match Operations Timeline",
    subtitle: "Historical Event Scrubber & Playback"
  },
  {
    title: "10. Mission Success Summary",
    narratorText: "Operational intelligence confirms all stadium zones are stabilized. Crowds are balanced, ticket queues have resolved, and volunteer FAs are back to nominal standby. ATLAS has successfully guided tournament operations to a secure outcome.",
    highlightPanel: "success",
    screenTitle: "Operations Successfully Stabilized",
    subtitle: "ATLAS Guided Match Complete"
  }
];

function FinalDemoPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);

  // Auto-progress timer
  useEffect(() => {
    if (!isPlaying) return;

    // Step length roughly 24 seconds (total 240 seconds = 4 minutes for 10 steps)
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < DEMO_STEPS.length - 1) {
          return prev + 1;
        } else {
          setIsPlaying(false);
          return prev;
        }
      });
    }, 24000);

    return () => clearInterval(interval);
  }, [isPlaying]);

  const currentStep = DEMO_STEPS[activeStep];

  return (
    <div className="flex flex-col gap-6 text-foreground min-h-[calc(100vh-6rem)] relative">
      {/* Upper Presenter Narrator Guide Block */}
      <div className="rounded-2xl border border-amber-500/30 bg-card/95 backdrop-blur-md shadow-2xl p-5 relative overflow-hidden text-left">
        <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl pointer-events-none" />
        
        <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
          <div className="flex items-center gap-2">
            <Volume2 className="h-5 w-5 text-amber-400 animate-bounce" />
            <span className="text-xs font-black text-amber-400 uppercase tracking-widest">
              ATLAS PRESENTATION GUIDE (JUDGING MODE)
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded uppercase">
              Phase {activeStep + 1} of {DEMO_STEPS.length}
            </span>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="text-muted-foreground hover:text-foreground text-xs font-black uppercase flex items-center gap-1"
            >
              {isPlaying ? <Pause className="h-3 w-3 fill-current" /> : <Play className="h-3 w-3 fill-current" />}
              {isPlaying ? "Autoplay On" : "Autoplay Paused"}
            </button>
          </div>
        </div>

        <p className="text-sm font-semibold leading-relaxed text-foreground/90 italic">
          "{currentStep.narratorText}"
        </p>

        {/* Phase progress timeline bar */}
        <div className="mt-5 w-full bg-amber-950/20 rounded-full h-1 overflow-hidden">
          <motion.div
            className="bg-amber-400 h-1"
            animate={{ width: `${((activeStep + 1) / DEMO_STEPS.length) * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between gap-4">
        <button
          disabled={activeStep === 0}
          onClick={() => {
            setActiveStep((prev) => Math.max(0, prev - 1));
            setIsPlaying(false);
          }}
          className="rounded-xl border border-border bg-card hover:bg-muted px-4 py-2 text-xs font-black uppercase tracking-wider flex items-center gap-1.5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ArrowLeft className="h-4 w-4" />
          Previous Phase
        </button>

        <button
          disabled={activeStep === DEMO_STEPS.length - 1}
          onClick={() => {
            setActiveStep((prev) => Math.min(DEMO_STEPS.length - 1, prev + 1));
            setIsPlaying(false);
          }}
          className="rounded-xl bg-primary text-primary-foreground hover:opacity-90 px-5 py-2.5 text-xs font-black uppercase tracking-wider flex items-center gap-1.5 shadow-lg shadow-primary/10 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next Phase
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>

      {/* Visual Simulation Body */}
      <div className="flex-1 rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 relative overflow-hidden flex flex-col items-center justify-center text-center min-h-[400px]">
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.03] pointer-events-none" />

        <AnimatePresence mode="wait">
          <motion.div
            key={activeStep}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.3 }}
            className="w-full max-w-2xl flex flex-col items-center"
          >
            {/* Displaying relevant icon depending on step */}
            <div className="mb-6 p-4 rounded-3xl bg-primary/10 border border-primary/20 text-primary">
              {activeStep === 0 && <Sparkles className="h-10 w-10 animate-spin" />}
              {activeStep === 1 && <Tv className="h-10 w-10" />}
              {activeStep === 2 && <Compass className="h-10 w-10" />}
              {activeStep === 3 && <Play className="h-10 w-10" />}
              {activeStep === 4 && <Brain className="h-10 w-10 text-primary animate-pulse" />}
              {activeStep === 5 && <Sliders className="h-10 w-10" />}
              {activeStep === 6 && <ShieldCheck className="h-10 w-10 text-emerald-400" />}
              {activeStep === 7 && <Tv className="h-10 w-10 text-amber-400" />}
              {activeStep === 8 && <Clock className="h-10 w-10" />}
              {activeStep === 9 && <CheckCircle className="h-10 w-10 text-emerald-400" />}
            </div>

            <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest block">
              {currentStep.subtitle}
            </span>
            <h2 className="text-3xl font-black tracking-tight text-foreground uppercase mt-2">
              {currentStep.screenTitle}
            </h2>

            {/* Quick Actions Links to real routes */}
            <div className="mt-10 flex flex-wrap justify-center gap-4">
              <Link
                to="/"
                className="rounded-xl border border-border bg-card/60 hover:bg-muted p-4 flex items-center gap-3 transition-all text-left w-64"
              >
                <div className="p-2 rounded-lg bg-primary/10 text-primary">
                  <Tv className="h-4 w-4" />
                </div>
                <div>
                  <span className="text-xs font-black uppercase text-foreground block">Mission Control</span>
                  <span className="text-[9px] text-muted-foreground block">View real-time dashboard</span>
                </div>
              </Link>

              <Link
                to="/executive-situation-room"
                className="rounded-xl border border-border bg-card/60 hover:bg-muted p-4 flex items-center gap-3 transition-all text-left w-64"
              >
                <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
                  <ShieldCheck className="h-4 w-4" />
                </div>
                <div>
                  <span className="text-xs font-black uppercase text-foreground block">Situation Room</span>
                  <span className="text-[9px] text-muted-foreground block">Strategic executive status</span>
                </div>
              </Link>

              <Link
                to="/timeline"
                className="rounded-xl border border-border bg-card/60 hover:bg-muted p-4 flex items-center gap-3 transition-all text-left w-64"
              >
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                  <Clock className="h-4 w-4" />
                </div>
                <div>
                  <span className="text-xs font-black uppercase text-foreground block">Operations Timeline</span>
                  <span className="text-[9px] text-muted-foreground block">Scrub historical playback</span>
                </div>
              </Link>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
