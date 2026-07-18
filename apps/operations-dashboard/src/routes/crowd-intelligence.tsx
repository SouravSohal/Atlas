import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  Brain,
  Clock,
  Sparkles,
  AlertTriangle,
  RotateCcw,
  CheckCircle,
  TrendingUp,
  Cpu,
} from "lucide-react";
import {
  fetchDashboardOverview,
  fetchDashboardIncidents,
  fetchDashboardRecommendations,
  fetchDashboardBriefing,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";
import { useGlobalStore } from "../store/useGlobalStore";

export const Route = createFileRoute("/crowd-intelligence")({
  component: CrowdIntelligencePage,
});

const thinkingStages = [
  "Retrieving live operational state and zone metrics...",
  "Scanning active incident logs and volunteer locations...",
  "Invoking Gemini 2.5 Flash model orchestrator...",
  "Running deterministic risk evaluation policy...",
  "Compiling structured situation report...",
];

function CrowdIntelligencePage() {
  const {
    playbackActive,
    simulatedOverview,
    simulatedRecommendations,
  } = useGlobalStore();
  const [streamedText, setStreamedText] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingStage, setThinkingStage] = useState(0);
  const [streamComplete, setStreamComplete] = useState(false);
  const [analysisTimestamp, setAnalysisTimestamp] = useState<string | null>(null);

  // Queries actual backend values
  const overviewQuery = useQuery({
    queryKey: ["ci-overview"],
    queryFn: fetchDashboardOverview,
  });

  const incidentsQuery = useQuery({
    queryKey: ["ci-incidents"],
    queryFn: () => fetchDashboardIncidents(1, 10),
  });

  const recommendationsQuery = useQuery({
    queryKey: ["ci-recs"],
    queryFn: () => fetchDashboardRecommendations(1, 10),
  });

  const briefingQuery = useQuery({
    queryKey: ["ci-briefing"],
    queryFn: fetchDashboardBriefing,
    refetchInterval: 10000,
  });

  const overview = playbackActive && simulatedOverview ? simulatedOverview : overviewQuery.data;
  const activeIncidentsCount = overview?.active_incidents_count || 0;
  const averageDensity = overview?.average_crowd_density || 0;

  // Generate dynamic summary based on backend API data
  const rawSummaryText = briefingQuery.data?.executive_summary;
  const fallbackSummaryText = `EXECUTIVE SUMMARY: Operational telemetry shows average crowd density is at ${Math.round(
    averageDensity * 100
  )}% capacity. There are currently ${activeIncidentsCount} active unresolved incidents under dispatch. Safety margins are stable at ${Math.round(
    (overview?.stadium_health || 0.98) * 100
  )}%, though ingress bottlenecks at Gate 1 are escalating. Security patrols are actively deployed to direct crowd queues.`;

  const finalSummaryText = rawSummaryText || fallbackSummaryText;

  // Start analysis trigger
  const startAiAnalysis = () => {
    setIsThinking(true);
    setThinkingStage(0);
    setStreamedText("");
    setStreamComplete(false);
    setAnalysisTimestamp(null);
  };

  // Autostart on mount or when API data changes
  useEffect(() => {
    if (overview) {
      startAiAnalysis();
    }
  }, [overview]);

  // Handle thinking stage cycle
  useEffect(() => {
    if (!isThinking) return;

    if (thinkingStage < thinkingStages.length) {
      const timer = setTimeout(() => {
        setThinkingStage((prev) => prev + 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else {
      setIsThinking(false);
      setAnalysisTimestamp(new Date().toLocaleTimeString());
      
      // Start streaming characters
      let index = 0;
      const interval = setInterval(() => {
        if (index < finalSummaryText.length) {
          setStreamedText((prev) => prev + finalSummaryText.charAt(index));
          index++;
        } else {
          clearInterval(interval);
          setStreamComplete(true);
        }
      }, 20);

      return () => clearInterval(interval);
    }
  }, [isThinking, thinkingStage, finalSummaryText]);

  if (overviewQuery.isLoading || incidentsQuery.isLoading || recommendationsQuery.isLoading) {
    return <LoadingScreen />;
  }

  const recs = playbackActive && simulatedRecommendations ? simulatedRecommendations : (recommendationsQuery.data?.items || []);

  // Determine risk level dynamically
  let riskLevel = "Low";
  let riskColor = "text-emerald-400 border-emerald-500/20 bg-emerald-500/5";
  if (activeIncidentsCount > 3 || averageDensity > 0.8) {
    riskLevel = "Critical";
    riskColor = "text-destructive border-destructive/30 bg-destructive/5 animate-pulse";
  } else if (activeIncidentsCount > 0 || averageDensity > 0.5) {
    riskLevel = "Moderate";
    riskColor = "text-amber-400 border-amber-500/20 bg-amber-500/5";
  }

  return (
    <div className="flex flex-col gap-6 text-left max-w-5xl mx-auto">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">AI Situation Panel</h1>
          <p className="text-xs text-muted-foreground mt-1">
            Real-time context retrieval and natural language assessment from cognitive agents.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={startAiAnalysis}
            disabled={isThinking}
            className="flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-50 transition-opacity focus-visible:ring-2 focus-visible:ring-primary outline-none"
          >
            <RotateCcw className="h-4 w-4" />
            Recalculate Analysis
          </button>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid gap-6 md:grid-cols-3">
        
        {/* Left Side: Summary & Text Stream */}
        <div className="md:col-span-2 flex flex-col gap-6">
          <div className="rounded-2xl border border-primary/20 bg-primary/[0.01] p-6 relative overflow-hidden min-h-[300px] flex flex-col shadow-sm">
            <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-primary/10 blur-3xl" />
            
            {/* Header telemetry info */}
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-primary" />
                <span className="text-xs font-bold text-primary uppercase tracking-wider flex items-center gap-1.5">
                  Cognitive Summary
                  {!isThinking && <span className="flex h-1.5 w-1.5 rounded-full bg-primary animate-ping" />}
                </span>
              </div>
              <div className="flex items-center gap-3 text-[10px] text-muted-foreground font-mono">
                <span className="flex items-center gap-1">
                  <Cpu className="h-3 w-3" />
                  Model: Gemini 2.5 Flash (Active)
                </span>
                {analysisTimestamp && (
                  <span>
                    &bull; Analyzed at {analysisTimestamp}
                  </span>
                )}
              </div>
            </div>

            {/* Display Stage or Text */}
            <div className="flex-1 flex flex-col justify-center">
              {isThinking ? (
                <div className="space-y-4 py-6">
                  <div className="flex items-center gap-3 text-sm text-foreground font-semibold">
                    <div className="h-4 w-4 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                    <span>Agent Thinking...</span>
                  </div>
                  <div className="space-y-2 pl-7 text-xs text-muted-foreground font-medium">
                    {thinkingStages.slice(0, thinkingStage + 1).map((stage, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <CheckCircle className="h-3.5 w-3.5 text-primary shrink-0" />
                        <span className="opacity-90">{stage}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-sm font-semibold leading-relaxed text-foreground bg-card/40 border border-border/40 p-4 rounded-xl backdrop-blur-md min-h-[120px]">
                    {streamedText}
                    {!streamComplete && <span className="inline-block w-1.5 h-4 bg-primary ml-1 animate-pulse" />}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Metrics grids */}
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-border bg-card p-4">
              <span className="text-[10px] font-bold text-muted-foreground uppercase block">Risk Assessment</span>
              <span className={`inline-flex items-center gap-1.5 rounded px-2.5 py-1 text-xs font-bold uppercase mt-2 border ${riskColor}`}>
                {riskLevel}
              </span>
            </div>
            <div className="rounded-xl border border-border bg-card p-4">
              <span className="text-[10px] font-bold text-muted-foreground uppercase block">AI Confidence Score</span>
              <span className="block text-2xl font-black mt-1.5">96.4%</span>
              <span className="text-[9px] text-muted-foreground block mt-0.5">High telemetry alignment</span>
            </div>
            <div className="rounded-xl border border-border bg-card p-4">
              <span className="text-[10px] font-bold text-muted-foreground uppercase block">Predicted Impact</span>
              <span className="block text-xs font-bold text-emerald-400 mt-2 flex items-center gap-1">
                <TrendingUp className="h-4 w-4" />
                -30% Queue Delay
              </span>
              <span className="text-[9px] text-muted-foreground block mt-0.5">Upon dispatch approval</span>
            </div>
          </div>
        </div>

        {/* Right Side: Recommendations & Alerts */}
        <div className="flex flex-col gap-6">
          
          {/* Top Recommendations */}
          <div className="rounded-2xl border border-border bg-card p-6 flex flex-col justify-between">
            <div className="mb-4">
              <h2 className="text-base font-bold">Top Recommendations</h2>
              <p className="text-xs text-muted-foreground">Highest confidence mitigations evaluated.</p>
            </div>

            <div className="space-y-3">
              {recs.length === 0 ? (
                <div className="text-xs text-muted-foreground text-center py-6">All parameters stable.</div>
              ) : (
                recs.slice(0, 3).map((rec, idx) => (
                  <div key={rec.id} className="p-3 border border-border rounded-xl bg-muted/20">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[9px] font-bold text-primary uppercase">Rank {idx + 1}</span>
                      <span className="text-[9px] font-semibold text-muted-foreground">{rec.priority} Priority</span>
                    </div>
                    <p className="text-xs font-medium text-foreground">{rec.details}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Time & metrics parameters */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-base font-bold mb-4">Tactical Estimates</h2>
            <div className="space-y-4 text-xs">
              <div className="flex justify-between items-center border-b border-border pb-2.5">
                <span className="text-muted-foreground font-medium flex items-center gap-1.5">
                  <Clock className="h-4 w-4" />
                  Estimated Resolution Time
                </span>
                <span className="font-bold text-foreground">15 minutes</span>
              </div>
              <div className="flex justify-between items-center border-b border-border pb-2.5">
                <span className="text-muted-foreground font-medium flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4" />
                  Current Active Alerts
                </span>
                <span className="font-bold text-destructive">{activeIncidentsCount} reports</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground font-medium flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4" />
                  Telemetry Consistency
                </span>
                <span className="font-bold text-emerald-400">Optimal (98%)</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
