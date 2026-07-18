import { useMemo, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useWebSocket } from "../providers/WebSocketProvider";
import { TrendingUp, Download, Filter } from "lucide-react";
import { fetchDashboardOverview, fetchDashboardIncidents } from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";
import { useGlobalStore } from "../store/useGlobalStore";
import { SCENARIO_STEPS } from "../store/scenarioSteps";
import {
  AnalyticsKpiCards,
  QueueWaitTimeChart,
  SpectatorFlowChart,
  IncidentSeverityChart,
  CrowdDensityHeatmap,
  AiExecutiveSummary,
  AnalyticsToast,
} from "../features/analytics/components/AnalyticsSubComponents";

export const Route = createFileRoute("/analytics")({
  component: AnalyticsPage,
});

function AnalyticsPage() {
  const { subscribe, unsubscribe } = useWebSocket();
  const {
    timeRange,
    setTimeRange,
    filterZone,
    setFilterZone,
    filterType,
    setFilterType,
    toastMessage,
    setToastMessage,
    playbackActive,
    playbackScenario,
    playbackStep,
    simulatedIncidents,
  } = useGlobalStore();

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
    queryKey: ["cc-incidents-analytics"],
    queryFn: () => fetchDashboardIncidents(1, 40),
    refetchInterval: 5000,
  });

  const handleExport = (format: "CSV" | "PDF") => {
    setToastMessage(`Exporting operations report as ${format}...`);
    setTimeout(() => {
      setToastMessage(`Export completed: ATLAS_Operational_Report.${format.toLowerCase()}`);
      setTimeout(() => setToastMessage(null), 3000);
    }, 1500);
  };

  const waitTimes = useMemo(() => {
    if (playbackActive && playbackScenario) {
      const steps = SCENARIO_STEPS[playbackScenario] || [];
      return steps.map(step => {
        const zones = step.zones || [];
        if (zones.length === 0) return 4;
        return zones[0].queue_waiting_minutes || 0;
      });
    }
    return [5, 12, 18, 8, 4, 2];
  }, [playbackActive, playbackScenario]);

  const arrivals = useMemo(() => {
    if (playbackActive && playbackScenario) {
      const steps = SCENARIO_STEPS[playbackScenario] || [];
      return steps.map(step => {
        return Math.round((step.overview?.average_crowd_density || 0.45) * 100);
      });
    }
    return [10, 45, 85, 30, 10, 5];
  }, [playbackActive, playbackScenario]);

  const stepSize = useMemo(() => {
    return 500 / Math.max(1, waitTimes.length - 1);
  }, [waitTimes]);

  const chartPoints = useMemo(() => {
    const coordinates = waitTimes.map((time, idx) => `${idx * stepSize + 40},${220 - time * 6}`);
    return coordinates.join(" ");
  }, [waitTimes, stepSize]);

  const areaPoints = useMemo(() => {
    const path = arrivals.map((arr, idx) => `${idx * stepSize + 40},${220 - arr * 1.8}`);
    return `40,240 ${path.join(" ")} 540,240`;
  }, [arrivals, stepSize]);

  const incidents = useMemo(() => {
    return playbackActive && simulatedIncidents ? simulatedIncidents : (incidentsQuery.data?.items || []);
  }, [playbackActive, simulatedIncidents, incidentsQuery.data]);

  const { criticalCount, highCount, mediumCount, lowCount, maxCount, critHeight, highHeight, medHeight, lowHeight } = useMemo(() => {
    const criticalCount = incidents.filter((i: any) => i.severity === "critical" && !i.resolved).length;
    const highCount = incidents.filter((i: any) => i.severity === "high" && !i.resolved).length;
    const mediumCount = incidents.filter((i: any) => i.severity === "medium" && !i.resolved).length;
    const lowCount = incidents.filter((i: any) => i.severity === "low" && !i.resolved).length;

    const maxCount = Math.max(1, criticalCount, highCount, mediumCount, lowCount);
    const critHeight = criticalCount > 0 ? (criticalCount / maxCount) * 160 : 0;
    const highHeight = highCount > 0 ? (highCount / maxCount) * 160 : 0;
    const medHeight = mediumCount > 0 ? (mediumCount / maxCount) * 160 : 0;
    const lowHeight = lowCount > 0 ? (lowCount / maxCount) * 160 : 0;

    return { criticalCount, highCount, mediumCount, lowCount, maxCount, critHeight, highHeight, medHeight, lowHeight };
  }, [incidents]);

  if (overviewQuery.isLoading || incidentsQuery.isLoading) {
    return <LoadingScreen />;
  }

  return (
    <div className="flex flex-col gap-6 text-foreground min-h-[calc(100vh-6rem)] relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-border pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500">
            <TrendingUp className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight uppercase">Stadium Operational Intelligence</h1>
            <p className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
              Stadium Operational Metrics, Performance Intelligence & AI Accuracy Audits
            </p>
          </div>
        </div>

        {/* Export buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport("CSV")}
            className="rounded-xl border border-border bg-card hover:bg-muted px-4 py-2.5 text-xs font-black uppercase tracking-wider flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </button>
          <button
            onClick={() => handleExport("PDF")}
            className="rounded-xl bg-primary text-primary-foreground hover:opacity-90 px-4 py-2.5 text-xs font-black uppercase tracking-wider flex items-center gap-1.5 shadow-lg shadow-primary/10 transition-opacity cursor-pointer"
          >
            <Download className="h-4 w-4" />
            Export PDF
          </button>
        </div>
      </div>

      {/* Analytics Filter Toolbar */}
      <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-4 flex flex-wrap items-center gap-4 justify-between">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Filter className="h-4 w-4" />
          <span className="text-[10px] font-black uppercase tracking-wider">Configure Filters</span>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer text-foreground"
          >
            <option value="hour" className="bg-card">Last 1 Hour</option>
            <option value="6hours" className="bg-card">Last 6 Hours</option>
            <option value="match" className="bg-card">Full Match Duration</option>
          </select>

          <select
            value={filterZone}
            onChange={(e) => setFilterZone(e.target.value)}
            className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer text-foreground"
          >
            <option value="all" className="bg-card">All Zones</option>
            <option value="gate1" className="bg-card">Gate 1 Ingress</option>
            <option value="gate2" className="bg-card">Gate 2 Exit</option>
            <option value="med" className="bg-card">Medical Post Alpha</option>
          </select>

          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer text-foreground"
          >
            <option value="all" className="bg-card">All Incidents</option>
            <option value="crowd" className="bg-card">Crowd Surge</option>
            <option value="medical" className="bg-card">Medical emergency</option>
            <option value="weather" className="bg-card">Heavy Rain</option>
          </select>
        </div>
      </div>

      {/* Grid of Key Performance Indicators */}
      <AnalyticsKpiCards />

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Chart 1: Queue Wait Time Trends */}
        <QueueWaitTimeChart
          chartPoints={chartPoints}
          playbackActive={playbackActive}
          playbackStep={playbackStep}
          stepSize={stepSize}
          waitTimes={waitTimes}
        />

        {/* Chart 2: Spectator Flow Rate */}
        <SpectatorFlowChart
          areaPoints={areaPoints}
          playbackActive={playbackActive}
          playbackStep={playbackStep}
          stepSize={stepSize}
          arrivals={arrivals}
        />

        {/* Chart 3: Incident Severity Distributions */}
        <IncidentSeverityChart
          maxCount={maxCount}
          criticalCount={criticalCount}
          highCount={highCount}
          mediumCount={mediumCount}
          lowCount={lowCount}
          critHeight={critHeight}
          highHeight={highHeight}
          medHeight={medHeight}
          lowHeight={lowHeight}
        />

        {/* Chart 4: Crowd Density Grid */}
        <CrowdDensityHeatmap />
      </div>

      {/* Executive Summary Narrative */}
      <AiExecutiveSummary />

      {/* Floating Dynamic Toasts */}
      <AnalyticsToast toastMessage={toastMessage} />
    </div>
  );
}
export { AnalyticsPage };
