import { useState, useMemo, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useWebSocket } from "../providers/WebSocketProvider";
import {
  Clock,
  Filter,
  Play,
  Pause,
  Brain,
  RotateCcw,
  Zap,
} from "lucide-react";
import { motion } from "framer-motion";
import {
  fetchDashboardOverview,
  fetchDashboardIncidents,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/timeline")({
  component: MatchTimelinePage,
});

// Seed data representing match timeline events
interface TimelineEvent {
  timeOffset: string;
  timestamp: string;
  eventType: "incident" | "recommendation" | "state_change";
  severity: "low" | "medium" | "high" | "critical";
  title: string;
  description: string;
  correlatedId?: string;
  aiNarrative: string;
}

const HISTORICAL_EVENTS: TimelineEvent[] = [
  {
    timeOffset: "-60m",
    timestamp: "18:00",
    eventType: "state_change",
    severity: "low",
    title: "Gates Opened",
    description: "Primary gates 1 and 2 activated. Spectator ingress begins.",
    aiNarrative: "Operations initiated. Inflow rates are standard, gate queues are balanced under 5 minutes."
  },
  {
    timeOffset: "-45m",
    timestamp: "18:15",
    eventType: "state_change",
    severity: "medium",
    title: "Parking Lot Bottleneck",
    description: "Main parking area reaches 85% capacity. Queue times spike.",
    aiNarrative: "First parking density spike observed. Rerouting suggestions dispatched to gate monitors."
  },
  {
    timeOffset: "-30m",
    timestamp: "18:30",
    eventType: "incident",
    severity: "high",
    title: "Gate 1 Crowd Ingress Surge",
    description: "Spectator surge at main turnstiles causing wait times of 18 minutes.",
    correlatedId: "rec-1",
    aiNarrative: "Gate 1 ingress surge detected. Spectator flow rates exceed capacity threshold."
  },
  {
    timeOffset: "-25m",
    timestamp: "18:35",
    eventType: "recommendation",
    severity: "high",
    title: "Deploy Volunteer Team Alpha",
    description: "Reroute 6 volunteers from Sector B to assist with Gate 1 ticket scanning.",
    correlatedId: "inc-1",
    aiNarrative: "Optimizing scanner lanes. AI recommendations deployed to volunteer coordinators."
  },
  {
    timeOffset: "0m",
    timestamp: "19:00",
    eventType: "state_change",
    severity: "low",
    title: "Match Kickoff",
    description: "Stands are fully seated. Entrance gates return to nominal flows.",
    aiNarrative: "Stands density reaches 92%. Ingress successfully resolved and stabilized."
  },
  {
    timeOffset: "15m",
    timestamp: "19:15",
    eventType: "incident",
    severity: "critical",
    title: "Medical Collapse Sector 104",
    description: "Spectator heat exhaustion reported in eastern stands.",
    correlatedId: "rec-2",
    aiNarrative: "Medical dispatch requested. Responder units routed to sector 104 access point."
  },
  {
    timeOffset: "20m",
    timestamp: "19:20",
    eventType: "recommendation",
    severity: "critical",
    title: "Dispatch Medical Post Alpha Response",
    description: "Route 2 responders with stretcher kit to Section 104 corridors.",
    correlatedId: "inc-2",
    aiNarrative: "Corridor clearances checked. Medical crew dispatched to stands."
  },
  {
    timeOffset: "45m",
    timestamp: "19:45",
    eventType: "state_change",
    severity: "low",
    title: "Half-Time Interval",
    description: "High concourse flow towards restrooms and food courts.",
    aiNarrative: "Food court occupancy spikes to 88%. Cleaning and facility teams placed on high alert."
  }
];

function MatchTimelinePage() {
  const { subscribe, unsubscribe } = useWebSocket();
  const [playbackActive, setPlaybackActive] = useState(false);
  const [playbackStep, setPlaybackStep] = useState(HISTORICAL_EVENTS.length - 1);
  const [playbackSpeed, setPlaybackSpeed] = useState(1); // 1x, 2x, 5x
  const [filterType, setFilterType] = useState<string>("all");
  const [filterSeverity, setFilterSeverity] = useState<string>("all");

  useEffect(() => {
    subscribe("telemetry");
    subscribe("incidents");
    return () => {
      unsubscribe("telemetry");
      unsubscribe("incidents");
    };
  }, [subscribe, unsubscribe]);

  const overviewQuery = useQuery({
    queryKey: ["cc-overview"],
    queryFn: fetchDashboardOverview,
    refetchInterval: 5000,
  });

  const incidentsQuery = useQuery({
    queryKey: ["cc-incidents"],
    queryFn: () => fetchDashboardIncidents(1, 10),
    refetchInterval: 5000,
  });

  // Playback timer effect
  useEffect(() => {
    if (!playbackActive) return;

    const delay = 4000 / playbackSpeed;
    const timer = setInterval(() => {
      setPlaybackStep((prev) => {
        if (prev < HISTORICAL_EVENTS.length - 1) {
          return prev + 1;
        } else {
          return 0; // Loop playback
        }
      });
    }, delay);

    return () => clearInterval(timer);
  }, [playbackActive, playbackSpeed]);

  const activeEvents = useMemo(() => {
    // Slice based on current scrubber step
    const sliced = HISTORICAL_EVENTS.slice(0, playbackStep + 1);
    
    // Filter
    return sliced.filter((e) => {
      const typeMatch = filterType === "all" || e.eventType === filterType;
      const severityMatch = filterSeverity === "all" || e.severity === filterSeverity;
      return typeMatch && severityMatch;
    });
  }, [playbackStep, filterType, filterSeverity]);

  const currentNarrative = useMemo(() => {
    const lastEvent = HISTORICAL_EVENTS[playbackStep];
    return lastEvent ? lastEvent.aiNarrative : "No narrative available for this timestamp.";
  }, [playbackStep]);

  if (overviewQuery.isLoading || incidentsQuery.isLoading) {
    return <LoadingScreen />;
  }

  return (
    <div className="flex flex-col gap-6 text-foreground">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-border pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <Clock className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight uppercase">MATCH OPERATIONS TIMELINE</h1>
            <p className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
              Live & Historical Operations Playback Control System
            </p>
          </div>
        </div>
      </div>

      {/* Playback Controls Console */}
      <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-5 shadow-lg flex flex-col md:flex-row items-center gap-5 justify-between">
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => setPlaybackActive(!playbackActive)}
            className={`rounded-xl px-4 py-2.5 text-xs font-black uppercase tracking-wider flex items-center gap-2 transition-all ${
              playbackActive
                ? "bg-amber-500 text-black shadow-md shadow-amber-500/10"
                : "bg-primary text-primary-foreground hover:opacity-90"
            }`}
          >
            {playbackActive ? <Pause className="h-4 w-4 fill-black" /> : <Play className="h-4 w-4 fill-primary-foreground" />}
            {playbackActive ? "Pause" : "Play Replay"}
          </button>
          
          <button
            onClick={() => {
              setPlaybackActive(false);
              setPlaybackStep(HISTORICAL_EVENTS.length - 1);
            }}
            className="rounded-xl border border-border bg-muted/20 hover:bg-muted/40 p-2.5 text-muted-foreground hover:text-foreground transition-colors"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>

        {/* Scrubber slider */}
        <div className="flex-1 w-full flex items-center gap-3">
          <span className="text-[10px] font-black text-muted-foreground uppercase font-mono">
            {HISTORICAL_EVENTS[0]?.timeOffset}
          </span>
          <input
            type="range"
            min="0"
            max={HISTORICAL_EVENTS.length - 1}
            value={playbackStep}
            onChange={(e) => {
              setPlaybackStep(parseInt(e.target.value));
              setPlaybackActive(false);
            }}
            className="flex-1 h-1.5 rounded-full accent-primary cursor-pointer w-full"
          />
          <span className="text-[10px] font-black text-muted-foreground uppercase font-mono">
            {HISTORICAL_EVENTS[HISTORICAL_EVENTS.length - 1]?.timeOffset}
          </span>
          <span className="text-xs font-bold text-foreground font-mono bg-muted/40 border border-border px-2 py-1 rounded">
            Step {playbackStep + 1}/{HISTORICAL_EVENTS.length}
          </span>
        </div>

        {/* Speed Selector */}
        <div className="flex items-center gap-1.5 border border-border rounded-xl bg-card p-1 shrink-0">
          {[1, 2, 5].map((speed) => (
            <button
              key={speed}
              onClick={() => setPlaybackSpeed(speed)}
              className={`rounded-lg px-2.5 py-1.5 text-[10px] font-black uppercase tracking-wider transition-colors ${
                playbackSpeed === speed
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted text-muted-foreground hover:text-foreground"
              }`}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left 2 Cols: Replay Event List */}
        <div className="lg:col-span-2 flex flex-col gap-5">
          {/* Filters Bar */}
          <div className="rounded-2xl border border-border bg-card/65 backdrop-blur-md p-4 flex flex-wrap items-center gap-4 justify-between">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Filter className="h-4 w-4" />
              <span className="text-[10px] font-black uppercase tracking-wider">Filter Events</span>
            </div>

            <div className="flex items-center gap-3">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer"
              >
                <option value="all">All Types</option>
                <option value="incident">Incidents</option>
                <option value="recommendation">Recommendations</option>
                <option value="state_change">State Changes</option>
              </select>

              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer"
              >
                <option value="all">All Severities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>

          {/* Timeline Feed Container */}
          <div className="flex flex-col gap-4">
            {activeEvents.length === 0 ? (
              <div className="rounded-2xl border border-border bg-card/40 p-8 text-center text-xs text-muted-foreground">
                No events match the selected filters for this time offset.
              </div>
            ) : (
              activeEvents.map((evt, idx) => {
                const eventColors = {
                  incident: "border-destructive/30 bg-destructive/5 text-destructive",
                  recommendation: "border-primary/30 bg-primary/5 text-primary",
                  state_change: "border-emerald-500/30 bg-emerald-500/5 text-emerald-400",
                };

                return (
                  <motion.div
                    key={`${evt.title}-${idx}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`rounded-2xl border p-5 transition-all flex flex-col md:flex-row items-start justify-between gap-4 ${
                      eventColors[evt.eventType]
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      {/* Event indicator */}
                      <div className="text-center font-mono mt-1 shrink-0">
                        <span className="text-[10px] font-black block tracking-tight uppercase">OFFSET</span>
                        <span className="text-lg font-black block leading-none mt-0.5">{evt.timeOffset}</span>
                        <span className="text-[9px] text-muted-foreground block mt-1">({evt.timestamp})</span>
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`text-[8px] font-black uppercase px-1.5 py-0.5 rounded border border-current`}>
                            {evt.eventType}
                          </span>
                          <span className={`text-[8px] font-black uppercase px-1.5 py-0.5 rounded border border-current`}>
                            {evt.severity}
                          </span>
                        </div>
                        <h3 className="text-xs font-black uppercase mt-2.5 text-foreground">{evt.title}</h3>
                        <p className="text-xs text-muted-foreground mt-1 leading-relaxed">
                          {evt.description}
                        </p>
                      </div>
                    </div>

                    {/* Correlations Badge */}
                    {evt.correlatedId && (
                      <div className="rounded-xl border border-border bg-muted/40 p-3 text-[10px] font-black tracking-wide text-muted-foreground shrink-0 uppercase flex items-center gap-1.5">
                        <Zap className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                        <span>Correlated to Action: {evt.correlatedId}</span>
                      </div>
                    )}
                  </motion.div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Col: AI Narrative Summarizer & Telemetry */}
        <div className="flex flex-col gap-6">
          {/* AI Narrator feed */}
          <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 shadow-lg relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
            
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <span className="text-xs font-black text-emerald-400 uppercase tracking-widest flex items-center gap-1.5">
                <Brain className="h-4 w-4 text-emerald-400 animate-pulse" />
                Live AI Narrator Feed
              </span>
              <span className="text-[9px] font-mono text-muted-foreground">TIMESTAMP SUMMARY</span>
            </div>

            <p className="text-xs font-semibold leading-relaxed text-foreground/90">
              {currentNarrative}
            </p>
          </div>

          {/* Telemetry info */}
          <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 shadow-lg">
            <span className="text-xs font-black text-primary uppercase tracking-widest block mb-4">
              Scrub Timeline Telemetry
            </span>

            <div className="flex flex-col gap-3.5 font-mono text-xs">
              <div className="flex justify-between border-b border-border/40 pb-2">
                <span className="text-muted-foreground uppercase font-bold">Total Playback Events</span>
                <span className="font-bold">{HISTORICAL_EVENTS.length}</span>
              </div>
              <div className="flex justify-between border-b border-border/40 pb-2">
                <span className="text-muted-foreground uppercase font-bold">Active Playback Speed</span>
                <span className="font-bold text-emerald-400">{playbackSpeed}x</span>
              </div>
              <div className="flex justify-between border-b border-border/40 pb-2">
                <span className="text-muted-foreground uppercase font-bold">Active Filter Type</span>
                <span className="font-bold text-amber-500 uppercase">{filterType}</span>
              </div>
              <div className="flex justify-between border-b border-border/40 pb-2">
                <span className="text-muted-foreground uppercase font-bold">Active Filter Severity</span>
                <span className="font-bold text-primary uppercase">{filterSeverity}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
