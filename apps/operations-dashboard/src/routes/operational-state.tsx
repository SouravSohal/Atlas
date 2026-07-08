import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  ShieldCheck,
  AlertTriangle,
  Users,
  Clock,
  BarChart3,
} from "lucide-react";
import {
  fetchDashboardOverview,
  fetchOperationalState,
  fetchDashboardIncidents,
  fetchDashboardRecommendations,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/operational-state")({
  component: OperationalStateDashboardPage,
});

function OperationalStateDashboardPage() {
  const overviewQuery = useQuery({
    queryKey: ["overview-ops"],
    queryFn: fetchDashboardOverview,
    refetchInterval: 5000,
  });

  const stateQuery = useQuery({
    queryKey: ["operational-state-ops"],
    queryFn: fetchOperationalState,
    refetchInterval: 5000,
  });

  const incidentsQuery = useQuery({
    queryKey: ["incidents-ops"],
    queryFn: () => fetchDashboardIncidents(1, 5),
    refetchInterval: 5000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["recommendations-ops"],
    queryFn: () => fetchDashboardRecommendations(1, 5),
    refetchInterval: 5000,
  });

  if (overviewQuery.isLoading || stateQuery.isLoading || incidentsQuery.isLoading || recommendationsQuery.isLoading) {
    return <LoadingScreen />;
  }

  if (overviewQuery.isError || stateQuery.isError || incidentsQuery.isError || recommendationsQuery.isError) {
    return (
      <div className="flex h-[50vh] flex-col items-center justify-center text-center p-6 bg-card border border-border rounded-2xl max-w-sm mx-auto mt-10">
        <AlertTriangle className="h-10 w-10 text-destructive mb-3" />
        <h3 className="text-sm font-bold">Failed to connect to API</h3>
        <p className="text-xs text-muted-foreground mt-1">Check backend status and verify connection parameters.</p>
      </div>
    );
  }

  const overview = overviewQuery.data!;
  const zones = stateQuery.data || [];
  const activeIncidents = incidentsQuery.data?.items || [];
  const activeRecs = recommendationsQuery.data?.items || [];

  return (
    <div className="flex flex-col gap-8 text-left">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Operational State</h1>
          <p className="text-xs text-muted-foreground mt-1">Live crowd telemetry, sector throughput, and gate flow metrics.</p>
        </div>
        <div className="text-xs text-muted-foreground">
          Last refreshed: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Stadium Health</span>
            <ShieldCheck className="h-5 w-5 text-emerald-500" />
          </div>
          <div className="mt-4">
            <span className="text-3xl font-black tracking-tight">{Math.round(overview.stadium_health * 100)}%</span>
          </div>
          <p className="mt-2 text-[10px] text-muted-foreground">Global aggregated safety status</p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Crowd Density</span>
            <Activity className="h-5 w-5 text-primary" />
          </div>
          <div className="mt-4">
            <span className="text-3xl font-black tracking-tight">{Math.round(overview.average_crowd_density * 100)}%</span>
          </div>
          <p className="mt-2 text-[10px] text-muted-foreground">Average capacity utilization</p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Volunteer Deployed</span>
            <Users className="h-5 w-5 text-blue-500" />
          </div>
          <div className="mt-4">
            <span className="text-3xl font-black tracking-tight">{overview.allocated_volunteers_count}</span>
          </div>
          <p className="mt-2 text-[10px] text-muted-foreground">Active resources dispatched</p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Active Alerts</span>
            <AlertTriangle className="h-5 w-5 text-destructive" />
          </div>
          <div className="mt-4">
            <span className="text-3xl font-black tracking-tight">{overview.active_incidents_count}</span>
          </div>
          <p className="mt-2 text-[10px] text-muted-foreground">Unresolved safety warnings</p>
        </div>
      </div>

      {/* Main layout grids */}
      <div className="grid gap-8 lg:grid-cols-3">
        
        {/* Heatmap & Density Charts Column */}
        <div className="lg:col-span-2 flex flex-col gap-8">
          
          {/* Heatmap grid placeholder */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-4">
              <h2 className="text-lg font-bold">Stadium Heatmap representation</h2>
              <p className="text-xs text-muted-foreground">Grid matrix representing live sector densities.</p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 border border-border rounded-xl bg-muted/10">
              {zones.map((zone, idx) => (
                <div
                  key={zone.zone_id}
                  className={`flex flex-col justify-between p-4 rounded-xl border text-center transition-all ${
                    zone.density > 0.75
                      ? "bg-destructive/10 border-destructive text-destructive shadow-sm"
                      : zone.density > 0.4
                      ? "bg-amber-500/10 border-amber-500/30 text-amber-500"
                      : "bg-emerald-500/10 border-emerald-500/20 text-emerald-500"
                  }`}
                >
                  <span className="text-[10px] font-bold uppercase tracking-wider opacity-75">Sector {idx + 1}</span>
                  <span className="text-2xl font-black tracking-tight mt-2">{Math.round(zone.density * 100)}%</span>
                  <span className="text-[10px] font-medium mt-1">Wait: {zone.queue_waiting_minutes}m</span>
                </div>
              ))}
            </div>
          </div>

          {/* Density Chart (SVG) */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold">Zone Density comparisons</h2>
                <p className="text-xs text-muted-foreground">Visual bar comparison of sector capacity levels.</p>
              </div>
              <BarChart3 className="h-5 w-5 text-muted-foreground" />
            </div>

            {/* Custom SVG Bar Chart */}
            <div className="h-48 w-full bg-muted/20 border border-border rounded-xl p-4 flex items-end justify-around gap-4">
              {zones.map((zone, idx) => (
                <div key={zone.zone_id} className="flex-1 flex flex-col items-center gap-2 h-full justify-end">
                  <span className="text-[9px] font-bold font-mono">{Math.round(zone.density * 100)}%</span>
                  <div
                    className={`w-full rounded-t-lg transition-all duration-500 ${
                      zone.density > 0.75 ? "bg-destructive animate-pulse" : "bg-primary"
                    }`}
                    style={{ height: `${Math.min(zone.density * 100, 100)}%`, maxHeight: "80%" }}
                  />
                  <span className="text-[9px] font-bold text-muted-foreground truncate max-w-[60px]">Sec {idx + 1}</span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Gate Status & Recommendations Right Column */}
        <div className="flex flex-col gap-8">
          
          {/* Gate status & throughput indicators */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-4">
              <h2 className="text-lg font-bold">Gate Status & Throughput</h2>
              <p className="text-xs text-muted-foreground">Inflow rates and turnstile flow states.</p>
            </div>

            <div className="space-y-4">
              {zones.map((zone, idx) => (
                <div key={zone.zone_id} className="flex items-center justify-between p-3.5 rounded-xl bg-muted/30 border border-border/50">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary font-bold text-xs">
                      G{idx + 1}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs font-bold">Gate {idx + 1} Turnstiles</span>
                      <span className="text-[9px] text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
                        Flow Rate: {zone.queue_waiting_minutes > 15 ? "Heavy" : "Normal"}
                      </span>
                    </div>
                  </div>
                  <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold ${
                    zone.queue_waiting_minutes > 20
                      ? "bg-destructive/10 text-destructive"
                      : "bg-emerald-500/10 text-emerald-500"
                  }`}>
                    <span className={`h-1.5 w-1.5 rounded-full ${zone.queue_waiting_minutes > 20 ? "bg-destructive" : "bg-emerald-500"}`} />
                    {zone.queue_waiting_minutes > 20 ? "Congested" : "Stable"}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Active recommendations timeline log */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-4">
              <h2 className="text-lg font-bold">Mitigation recommendations</h2>
              <p className="text-xs text-muted-foreground">Decision actions based on live flow states.</p>
            </div>

            <div className="space-y-3">
              {activeRecs.length === 0 ? (
                <div className="text-xs text-muted-foreground text-center py-6">No recommendations found. Flow rates normal.</div>
              ) : (
                activeRecs.map((rec) => (
                  <div key={rec.id} className="p-3.5 rounded-xl bg-muted/30 border border-border/50 text-left">
                    <div className="flex justify-between items-center mb-1.5">
                      <span className="text-[10px] font-bold text-primary uppercase tracking-wider">{rec.action_type}</span>
                      <span className="text-[9px] font-bold text-muted-foreground">{Math.round(rec.confidence * 100)}% conf</span>
                    </div>
                    <p className="text-xs font-medium text-foreground">{rec.details}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Operational Timeline log */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-4">
              <h2 className="text-lg font-bold">Operational Timeline</h2>
              <p className="text-xs text-muted-foreground">Shifts logs and state transitions track.</p>
            </div>

            <div className="relative pl-6 border-l border-border space-y-6">
              {activeIncidents.map((inc) => (
                <div key={inc.id} className="relative">
                  <div className="absolute -left-[31px] mt-0.5 rounded-full bg-card border-2 border-border p-1 text-primary">
                    <Clock className="h-3 w-3" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold">{inc.resolved ? "Resolved Status Update" : "Live Alert Registered"}</span>
                    <span className="text-[9px] text-muted-foreground mt-0.5">{inc.description}</span>
                    <span className="text-[9px] text-primary font-bold mt-1">
                      {new Date(inc.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
