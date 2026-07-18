import { useMemo, useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useWebSocket } from "../providers/WebSocketProvider";
import { Tv } from "lucide-react";
import {
  fetchDashboardOverview,
  fetchDashboardIncidents,
  fetchOperationalState,
  fetchDashboardRecommendations,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";
import { SituationAnalysisPanel } from "../components/SituationAnalysisPanel";
import { useGlobalStore } from "../store/useGlobalStore";
import {
  ExecutiveKpiCards,
  DecisionsCenter,
  WhyDecisionModal,
  ConfidenceIndex,
  SectorDensities,
} from "../features/executive-situation-room/components/SituationRoomSubComponents";

export const Route = createFileRoute("/executive-situation-room")({
  component: ExecutiveSituationRoomPage,
});

const EMPTY_ARRAY: any[] = [];

function ExecutiveSituationRoomPage() {
  const { subscribe, unsubscribe } = useWebSocket();
  const {
    approvedRecs: approvedDecisions,
    setRecApproval,
    playbackActive,
    simulatedOverview,
    simulatedZones,
    simulatedIncidents,
    simulatedRecommendations,
  } = useGlobalStore();

  const [selectedWhyRec, setSelectedWhyRec] = useState<any | null>(null);

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

  const overview = playbackActive && simulatedOverview ? simulatedOverview : overviewQuery.data;
  const states = playbackActive && simulatedZones ? simulatedZones : (stateQuery.data || EMPTY_ARRAY);
  const incidents = playbackActive && simulatedIncidents ? simulatedIncidents : (incidentsQuery.data?.items || EMPTY_ARRAY);
  const rawRecs = playbackActive && simulatedRecommendations ? simulatedRecommendations : (recommendationsQuery.data?.items || EMPTY_ARRAY);

  const recs = useMemo(() => {
    return rawRecs.map((item) => ({
      ...item,
      priority: item.priority || "high",
      confidence: item.confidence || 0.95,
    }));
  }, [rawRecs]);

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

  const activeIncidents = useMemo(() => {
    return incidents.filter((inc) => !inc.resolved);
  }, [incidents]);

  const majorRisks = useMemo(() => {
    return activeIncidents.filter((inc) => inc.severity === "critical" || inc.severity === "high");
  }, [activeIncidents]);

  const healthScore = overview?.stadium_health ?? 0.98;
  const isHealthy = healthScore >= 0.92;

  if (overviewQuery.isLoading || stateQuery.isLoading || incidentsQuery.isLoading || recommendationsQuery.isLoading) {
    return <LoadingScreen />;
  }

  const handleApprove = (id: string) => {
    setRecApproval(id, true);
  };

  return (
    <div className="flex flex-col gap-6 text-foreground">
      {/* Upper Status Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-border pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500 animate-pulse">
            <Tv className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight uppercase">EXECUTIVE SITUATION ROOM</h1>
            <p className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
              Strategic Stadium Operations & Decision Control Console
            </p>
          </div>
        </div>

        {/* Live Mission Status Banner */}
        <div className="flex items-center gap-2 px-4 py-2 rounded-full border border-border bg-card/65 backdrop-blur-md shadow-inner">
          <span className={`h-2.5 w-2.5 rounded-full ${isHealthy ? "bg-emerald-500 animate-pulse" : "bg-amber-500 animate-pulse"}`} />
          <span className="text-[10px] font-black uppercase tracking-widest font-mono">
            {isHealthy ? "MISSION STATUS: NOMINAL" : "MISSION STATUS: ESCALATED"}
          </span>
        </div>
      </div>

      {/* Grid of 4 Key Executive Indicators component */}
      <ExecutiveKpiCards
        healthScore={healthScore}
        isHealthy={isHealthy}
        majorRisksCount={majorRisks.length}
      />

      {/* Main Multi-Column Content Area */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Col 1 & 2: Briefing and Active Decisions */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <SituationAnalysisPanel />

          {/* Active Decisions / Actions Center Review component */}
          <DecisionsCenter
            recs={recs}
            approvedDecisions={approvedDecisions}
            handleApprove={handleApprove}
            setSelectedWhyRec={setSelectedWhyRec}
            parseDetails={parseDetails}
          />
        </div>

        {/* Col 3: Crowd Intelligence, Risk Assessment & Confidence */}
        <div className="flex flex-col gap-6">
          {/* AI Confidence Meter component */}
          <ConfidenceIndex />

          {/* Crowd Intelligence Sector Densities component */}
          <SectorDensities states={states} />
        </div>
      </div>

      {/* Selected Why Decision Modal component */}
      <WhyDecisionModal
        selectedWhyRec={selectedWhyRec}
        setSelectedWhyRec={setSelectedWhyRec}
        parseDetails={parseDetails}
      />
    </div>
  );
}
export { ExecutiveSituationRoomPage };
