import { useMemo, useEffect, useRef, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useWebSocket } from "../providers/WebSocketProvider";
import type { Edge } from "@xyflow/react";
import { Zap } from "lucide-react";
import {
  fetchDashboardOverview,
  fetchDashboardIncidents,
  fetchDashboardRecommendations,
  fetchOperationalState,
  createIncident,
  updateIncident,
  postCopilotChat,
  fetchStadiumPredictions,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";
import { SituationAnalysisPanel } from "../components/SituationAnalysisPanel";
import { useGlobalStore } from "../store/useGlobalStore";
import type { ChatMessage } from "../store/useGlobalStore";
import { SCENARIO_STEPS } from "../store/scenarioSteps";

import type { StadiumNode } from "../features/mission-control/types";
import { KpiMatrix } from "../features/mission-control/components/KpiMatrix";
import { DigitalTwinMap } from "../features/mission-control/components/DigitalTwinMap";
import { AiCopilot } from "../features/mission-control/components/AiCopilot";
import { OperationalTimeline } from "../features/mission-control/components/OperationalTimeline";
import { ActiveRecommendations } from "../features/mission-control/components/ActiveRecommendations";
import { DecisionIntelModal } from "../features/mission-control/components/DecisionIntelModal";
import { PredictiveForecast } from "../features/mission-control/components/PredictiveForecast";
import { LiveFeedIncidents } from "../features/mission-control/components/LiveFeedIncidents";
import { JudgeDemoConsole } from "../features/mission-control/components/JudgeDemoConsole";

export const Route = createFileRoute("/")({
  component: MissionControlPage,
});

function MissionControlPage() {
  const queryClient = useQueryClient();
  const { subscribe, unsubscribe } = useWebSocket();
  const {
    approvedRecs,
    setRecApproval,
    demoOpen,
    setDemoOpen,
    demoMessage,
    setDemoMessage,
    judgeDemoActive,
    setJudgeDemoActive,
    demoStatusMilestone,
    setDemoStatusMilestone,
    focusedNodeIndex,
    setFocusedNodeIndex,
    setToastMessage,
    playbackActive,
    playbackScenario,
    playbackStep,
    playbackSpeed,
    playbackIsPaused,
    setPlaybackIsPaused,
    setPlaybackStep,
    setPlaybackSpeed,
    localNotifications,
    chatMessages,
    setChatMessages,
    chatInput,
    setChatInput,
    chatThinking,
    setChatThinking,
    startSimulation,
    stopSimulation,
    simulatedOverview,
    simulatedZones,
    simulatedIncidents,
    simulatedRecommendations,
  } = useGlobalStore();

  // Real-time WebSocket connection to subscribe to updates
  useEffect(() => {
    subscribe("telemetry");
    subscribe("incidents");
    subscribe("recommendations");
    return () => {
      unsubscribe("telemetry");
      unsubscribe("incidents");
      unsubscribe("recommendations");
    };
  }, [subscribe, unsubscribe]);

  // Playback engine states
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [showPredictionsOverlay, setShowPredictionsOverlay] = useState(false);
  const [selectedWhyRec, setSelectedWhyRec] = useState<any | null>(null);

  const predictionsQuery = useQuery({
    queryKey: ["cc-predictions"],
    queryFn: fetchStadiumPredictions,
    refetchInterval: 5000,
  });

  // Query actual backend data
  const overviewQuery = useQuery({
    queryKey: ["cc-overview"],
    queryFn: fetchDashboardOverview,
    refetchInterval: 5000,
  });

  const stateQuery = useQuery({
    queryKey: ["cc-state"],
    queryFn: fetchOperationalState,
    refetchInterval: 5000,
  });

  const incidentsQuery = useQuery({
    queryKey: ["cc-incidents"],
    queryFn: () => fetchDashboardIncidents(1, 10),
    refetchInterval: 5000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["cc-recommendations"],
    queryFn: () => fetchDashboardRecommendations(1, 10),
    refetchInterval: 5000,
  });

  const startJudgeDemo = (scenarioName: string) => {
    startSimulation(scenarioName);
    setPlaybackSpeed(1); // Reset speed to 1x baseline
    setJudgeDemoActive(true);

    let focusNodeIdx = 0;
    if (scenarioName === "Crowd Surge") focusNodeIdx = 0;
    if (scenarioName === "Medical Emergency") focusNodeIdx = 3;
    if (scenarioName === "Heavy Rain") focusNodeIdx = 4;
    if (scenarioName === "Lost Child") focusNodeIdx = 2;
    if (scenarioName === "Match End") focusNodeIdx = 1;
    setFocusedNodeIndex(focusNodeIdx);

    // Call real backend mutation endpoints to demonstrate real-time data link
    if (scenarioName === "Crowd Surge") {
      triggerScenario("crowd_control", "high", "High congestion alert at Gate 1 turnstiles.");
    } else if (scenarioName === "Medical Emergency") {
      triggerScenario("medical", "critical", "Spectator collapse reported near Section 104.");
    } else if (scenarioName === "Heavy Rain") {
      triggerScenario("weather", "medium", "Sudden heavy rainfall starting. Diverting spectators.");
    } else if (scenarioName === "Lost Child") {
      triggerScenario("security", "medium", "7-year-old child reported separated from guardians near Section 208.");
    } else if (scenarioName === "Match End") {
      triggerScenario("crowd_control", "medium", "Match egress exit crowd surge bottleneck.");
    }

    const milestones = [
      "🔄 Initializing Stadium Topology...",
      "📡 Dispatching Backend Scenario Request...",
      "🔬 Cloning state & applying simulator...",
      "🤖 Triggering AI Orchestrator analysis...",
      "✨ Replaying Digital Twin flow metrics...",
      "✅ Demo complete: Operations stabilized!"
    ];

    let currentMilestone = 0;
    setDemoStatusMilestone(milestones[0]);

    const timer = setInterval(() => {
      currentMilestone++;
      if (currentMilestone < milestones.length) {
        setDemoStatusMilestone(milestones[currentMilestone]);
      } else {
        clearInterval(timer);
      }
    }, 3500);
  };

  // Resolve Incident mutation
  const resolveMutation = useMutation({
    mutationFn: ({ id, resolved }: { id: string; resolved: boolean }) =>
      updateIncident(id, resolved),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cc-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["cc-overview"] });
    },
  });

  // Demo Mode incident mutation
  const demoMutation = useMutation({
    mutationFn: createIncident,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["cc-overview"] });
      queryClient.invalidateQueries({ queryKey: ["cc-state"] });
      queryClient.invalidateQueries({ queryKey: ["cc-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["cc-recommendations"] });
      
      setDemoMessage(`Scenario triggered: ${data.incident_type.toUpperCase()} registered!`);
      setTimeout(() => setDemoMessage(null), 5000);
    },
    onError: (err: any) => {
      setDemoMessage(`Error: ${err.message || "Failed to trigger scenario"}`);
      setTimeout(() => setDemoMessage(null), 5000);
    },
  });

  const triggerScenario = (type: string, severity: string, description: string) => {
    const zones = stateQuery.data || [];
    const zoneId = zones[0]?.zone_id || "00000000-0000-0000-0000-000000000000";
    
    demoMutation.mutate({
      incident_type: type,
      severity,
      description,
      latitude: 37.7749,
      longitude: -122.4194,
      reporter_id: "00000000-0000-0000-0000-000000000000",
      zone_id: zoneId,
    });
  };

  const handleApproveRecommendation = (id: string) => {
    setRecApproval(id, true);
  };

  const handleResolveIncident = (id: string) => {
    resolveMutation.mutate({ id, resolved: true });
  };

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, chatThinking]);

  // Digital Twin transforms
  const flowNodes = useMemo(() => {
    const activeZones = playbackActive && simulatedZones ? simulatedZones : (stateQuery.data || []);
    if (activeZones.length === 0) return [];
    
    const labels = [
      "Gate 1 Ingress",
      "Gate 2 Exit",
      "Security Command",
      "Medical Post Alpha",
      "Central Food Plaza",
      "Main Parking Area",
      "Volunteer Base Alpha",
      "Metro Shuttle Plaza",
      "Eastern Restrooms",
      "Operations Center Hub"
    ];
    const types = [
      "Entrance Gate",
      "Exit Gate",
      "Security",
      "Medical",
      "Food Court",
      "Parking",
      "Volunteer Station",
      "Transit",
      "Restrooms",
      "Operations Center"
    ];
    const positions = [
      { x: 40, y: 150 },   // node-0: Gate 1 Ingress
      { x: 920, y: 150 },  // node-1: Gate 2 Exit
      { x: 480, y: 30 },   // node-2: Security Command
      { x: 260, y: 270 },  // node-3: Medical Post Alpha
      { x: 700, y: 270 },  // node-4: Central Food Plaza
      { x: 40, y: 30 },    // node-5: Main Parking Area
      { x: 260, y: 150 },  // node-6: Volunteer Base Alpha
      { x: 920, y: 30 },   // node-7: Metro Shuttle Plaza
      { x: 700, y: 30 },   // node-8: Eastern Restrooms
      { x: 480, y: 150 }   // node-9: Operations Center Hub
    ];

    return labels.map((label, index) => {
      const zone = activeZones[index % activeZones.length] || { density: 0.15, queue_waiting_minutes: 0, zone_id: `zone-${index}` };
      
      let status: "stable" | "warning" | "critical" = "stable";
      if (zone.density > 0.8) status = "critical";
      else if (zone.density > 0.4) status = "warning";

      const isFocused = focusedNodeIndex === index;

      const health = Math.round(100 - (zone.density * 30));
      const capacity = index === 5 ? 4500 : 15000;
      const alerts = status === "critical" ? 2 : status === "warning" ? 1 : 0;
      const recs = status === "critical" ? 3 : status === "warning" ? 1 : 0;
      const resources = index === 6 ? "12 Deployed" : index === 3 ? "2 EMTs" : "Standard";

      let predictionOverlay = null;
      if (showPredictionsOverlay && predictionsQuery.data) {
        const preds = predictionsQuery.data;
        if (index === 0) predictionOverlay = preds.queue_growth;
        else if (index === 1) predictionOverlay = preds.gate_overload;
        else if (index === 3) predictionOverlay = preds.medical_demand;
        else if (index === 4) predictionOverlay = preds.crowd_movement;
        else if (index === 5) predictionOverlay = preds.parking_saturation;
        else if (index === 6) predictionOverlay = preds.volunteer_shortages;
        else if (index === 7) predictionOverlay = preds.transport_congestion;
        else if (index === 9) predictionOverlay = preds.weather_impact;
      }

      return {
        id: `node-${index}`,
        type: "stadiumNode",
        position: positions[index] || { x: 100 + index * 80, y: 100 },
        data: {
          label,
          type: types[index],
          value: `Density: ${Math.round(zone.density * 100)}%`,
          status,
          isFocused,
          health,
          density: Math.round(zone.density * 100),
          queue: zone.queue_waiting_minutes || 0,
          capacity,
          alerts,
          recs,
          resources,
          predictionOverlay
        },
      } as StadiumNode;
    });
  }, [playbackActive, simulatedZones, stateQuery.data, focusedNodeIndex, showPredictionsOverlay, predictionsQuery.data]);

  const flowEdges = useMemo(() => {
    const edges: Edge[] = [];
    if (flowNodes.length < 10) return [];
    
    // Connect Ingress/Parking to central nodes
    edges.push({ id: "e-g1-vol", source: "node-0", target: "node-6", animated: true, style: { stroke: "#10b981" } } as Edge);
    edges.push({ id: "e-prk-sec", source: "node-5", target: "node-2", animated: true, style: { stroke: "#3b82f6" } } as Edge);
    
    // Connect central nodes to ops center
    edges.push({ id: "e-vol-ops", source: "node-6", target: "node-9", animated: true, style: { stroke: "#10b981" } } as Edge);
    edges.push({ id: "e-sec-ops", source: "node-2", target: "node-9", animated: true, style: { stroke: "#ef4444" } } as Edge);
    edges.push({ id: "e-med-ops", source: "node-3", target: "node-9", animated: true, style: { stroke: "#ef4444" } } as Edge);

    // Connect ops center to food plaza / restrooms
    edges.push({ id: "e-ops-fod", source: "node-9", target: "node-4", animated: true, style: { stroke: "#f59e0b" } } as Edge);
    edges.push({ id: "e-ops-rst", source: "node-8", target: "node-9", animated: true, style: { stroke: "#3b82f6" } } as Edge);

    // Connect food plaza / restrooms to Exit/Transit
    edges.push({ id: "e-fod-g2", source: "node-4", target: "node-1", animated: true, style: { stroke: "#ec4899" } } as Edge);
    edges.push({ id: "e-rst-trn", source: "node-8", target: "node-7", animated: true, style: { stroke: "#3b82f6" } } as Edge);
    edges.push({ id: "e-g2-trn", source: "node-1", target: "node-7", animated: true, style: { stroke: "#f59e0b" } } as Edge);

    return edges;
  }, [flowNodes]);

  // Copilot submit message
  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const textToSend = chatInput;
    if (!textToSend.trim()) return;

    const userMsg: ChatMessage = {
      role: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString(),
    };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setChatThinking(true);

    const formattedHistory = chatMessages.map(msg => ({
      role: msg.role,
      text: msg.text
    }));

    postCopilotChat(textToSend, formattedHistory, "en", window.location.pathname)
      .then((responseData) => {
        setChatThinking(false);
        const assistantMsg: ChatMessage = {
          role: "assistant",
          text: responseData.text,
          timestamp: new Date().toLocaleTimeString(),
          citations: responseData.citations || [],
          modelVersion: responseData.model_version || "Gemini 2.5 Flash",
          executionTimeMs: responseData.execution_time_ms || 0,
        };
        setChatMessages((prev) => [...prev, assistantMsg]);
      })
      .catch((err) => {
        setChatThinking(false);
        const assistantMsg: ChatMessage = {
          role: "assistant",
          text: `Error calling Copilot: ${err.message || err}`,
          timestamp: new Date().toLocaleTimeString(),
        };
        setChatMessages((prev) => [...prev, assistantMsg]);
      });
  };

  if (overviewQuery.isLoading || stateQuery.isLoading || incidentsQuery.isLoading) {
    return <LoadingScreen />;
  }

  // Intercept standard data if playback engine is active
  const overview = playbackActive && simulatedOverview ? simulatedOverview : overviewQuery.data;
  const incidents = playbackActive && simulatedIncidents ? simulatedIncidents : (incidentsQuery.data?.items || []);
  const recs = playbackActive && simulatedRecommendations ? simulatedRecommendations : (recommendationsQuery.data?.items || []);

  return (
    <div className="flex flex-col gap-6 text-left h-full">
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Mission Control</h1>
          <p className="text-xs text-muted-foreground mt-1">ATLAS Flagship Workspace: Unified digital twin spatial map, AI Copilot logs, and incident dispatch consoles.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 rounded-full border border-border bg-emerald-500/10 px-3.5 py-1.5 text-xs font-bold text-emerald-400">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span>Real-time link active</span>
          </div>
        </div>
      </div>

      {/* Scenario Playback Controls Bar */}
      <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
            <Zap className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground">Scenario Playback Engine</h3>
            <p className="text-[11px] text-muted-foreground mt-0.5 font-semibold">Replay hypothetical stadium incidents in real-time.</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Selector */}
          <select
            value={playbackScenario || ""}
            onChange={(e) => {
              const val = e.target.value;
              if (val) {
                startSimulation(val);
              } else {
                stopSimulation();
              }
            }}
            className="rounded-xl border border-border bg-card px-3.5 py-2 text-xs font-bold text-foreground outline-none cursor-pointer"
          >
            <option value="">-- Select Scenario Playback --</option>
            <option value="Crowd Surge">Crowd Surge Simulation</option>
            <option value="Medical Emergency">Medical Emergency Simulation</option>
            <option value="Gate Closure">Gate Closure Simulation</option>
            <option value="Heavy Rain">Heavy Rain Simulation</option>
            <option value="Power Failure">Power Failure Simulation</option>
            <option value="VIP Arrival">VIP Arrival Simulation</option>
            <option value="Lost Child">Lost Child Simulation</option>
            <option value="Match End">Match End Simulation</option>
          </select>

          {playbackActive && (
            <>
              {/* Play Pause */}
              <button
                onClick={() => setPlaybackIsPaused(!playbackIsPaused)}
                className="rounded-xl border border-border hover:bg-muted bg-card px-3 py-2 text-xs font-bold transition-colors"
              >
                {playbackIsPaused ? "Resume" : "Pause"}
              </button>

              {/* Scrubber slider */}
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold text-muted-foreground uppercase">Step</span>
                <input
                  type="range"
                  min="0"
                  max={(SCENARIO_STEPS[playbackScenario || ""]?.length || 5) - 1}
                  value={playbackStep}
                  onChange={(e) => {
                    setPlaybackStep(parseInt(e.target.value));
                    setPlaybackIsPaused(true);
                  }}
                  className="w-24 accent-primary cursor-pointer"
                />
                <span className="text-[11px] font-bold text-foreground font-mono">
                  {playbackStep + 1}/{SCENARIO_STEPS[playbackScenario || ""]?.length || 5}
                </span>
              </div>

              {/* Playback speed selector */}
              <div className="flex items-center gap-1.5 border border-border rounded-xl bg-card p-1">
                {[1, 2, 5].map((speed) => (
                  <button
                    key={speed}
                    onClick={() => setPlaybackSpeed(speed)}
                    className={`rounded-lg px-2.5 py-1 text-[10px] font-bold transition-colors ${
                      playbackSpeed === speed ? "bg-primary text-primary-foreground" : "hover:bg-muted text-muted-foreground"
                    }`}
                  >
                    {speed}x
                  </button>
                ))}
              </div>

              {/* Exit Playback */}
              <button
                onClick={() => {
                  stopSimulation();
                  setFocusedNodeIndex(null);
                  setJudgeDemoActive(false);
                }}
                className="rounded-xl bg-destructive px-3.5 py-2 text-xs font-bold text-destructive-foreground hover:opacity-90 transition-opacity"
              >
                Exit
              </button>
            </>
          )}
        </div>
      </div>

      {/* Flagship KPI Matrix */}
      <KpiMatrix overview={overview} />

      {/* Main Grid: Row 1: Digital Twin & AI Copilot */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Digital Twin Widget */}
        <DigitalTwinMap
          flowNodes={flowNodes}
          flowEdges={flowEdges}
          focusedNodeIndex={focusedNodeIndex}
          setFocusedNodeIndex={setFocusedNodeIndex}
          showPredictionsOverlay={showPredictionsOverlay}
          setShowPredictionsOverlay={setShowPredictionsOverlay}
          setToastMessage={setToastMessage}
        />

        {/* Col 3 Sidebar: AI Situation Analysis & Copilot */}
        <div className="flex flex-col gap-6">
          <SituationAnalysisPanel />

          {/* AI Copilot Widget */}
          <AiCopilot
            playbackActive={playbackActive}
            playbackScenario={playbackScenario}
            playbackStep={playbackStep}
            chatMessages={chatMessages}
            chatThinking={chatThinking}
            chatInput={chatInput}
            setChatInput={setChatInput}
            handleChatSubmit={handleChatSubmit}
            chatEndRef={chatEndRef}
          />
        </div>
      </div>

      {/* Row 2: Timeline & Recommendations */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Timeline Widget */}
        <OperationalTimeline incidents={incidents} />

        {/* Recommendations Widget */}
        <ActiveRecommendations
          recs={recs}
          approvedRecs={approvedRecs}
          setSelectedWhyRec={setSelectedWhyRec}
          handleApproveRecommendation={handleApproveRecommendation}
        />
      </div>

      {/* Selected Why Decision Modal */}
      <DecisionIntelModal
        selectedWhyRec={selectedWhyRec}
        onClose={() => setSelectedWhyRec(null)}
      />

      {/* Row 3: Predictive Intelligence (Gemini Predictions) */}
      <PredictiveForecast predictionsQuery={predictionsQuery} />

      {/* Row 4: Live Feed & Active Incidents */}
      <LiveFeedIncidents
        playbackActive={playbackActive}
        localNotifications={localNotifications}
        incidents={incidents}
        handleResolveIncident={handleResolveIncident}
      />

      {/* Floating Demo Control Panel (Judge Demo Mode Console) */}
      <JudgeDemoConsole
        demoOpen={demoOpen}
        setDemoOpen={setDemoOpen}
        demoMessage={demoMessage}
        judgeDemoActive={judgeDemoActive}
        demoStatusMilestone={demoStatusMilestone}
        playbackScenario={playbackScenario}
        playbackStep={playbackStep}
        startJudgeDemo={startJudgeDemo}
      />
    </div>
  );
}
