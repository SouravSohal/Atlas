import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  ShieldCheck,
  AlertTriangle,
  Compass,
  Users,
  Brain,
  Clock,
  RefreshCw,
  TrendingUp,
} from "lucide-react";
import {
  fetchDashboardOverview,
  fetchDashboardIncidents,
  fetchDashboardRecommendations,
  fetchOperationalState,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/")({
  component: DashboardOverviewPage,
});

function DashboardOverviewPage() {
  const overviewQuery = useQuery({
    queryKey: ["overview"],
    queryFn: fetchDashboardOverview,
    refetchInterval: 5000, // Poll every 5s for real-time overview updates
  });

  const incidentsQuery = useQuery({
    queryKey: ["incidents"],
    queryFn: () => fetchDashboardIncidents(1, 5),
    refetchInterval: 5000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["recommendations"],
    queryFn: () => fetchDashboardRecommendations(1, 5),
    refetchInterval: 5000,
  });

  const stateQuery = useQuery({
    queryKey: ["operational-state"],
    queryFn: fetchOperationalState,
    refetchInterval: 5000,
  });

  // Handle loading
  if (overviewQuery.isLoading || incidentsQuery.isLoading || recommendationsQuery.isLoading || stateQuery.isLoading) {
    return <LoadingScreen />;
  }

  // Handle errors / API failures
  if (overviewQuery.isError || incidentsQuery.isError || recommendationsQuery.isError || stateQuery.isError) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center text-center p-6 bg-card border border-border rounded-2xl max-w-md mx-auto mt-10 shadow-lg">
        <AlertTriangle className="h-12 w-12 text-destructive mb-4 animate-bounce" />
        <h2 className="text-lg font-bold tracking-tight">API Connection Offline</h2>
        <p className="text-xs text-muted-foreground mt-2 max-w-xs">
          Unable to establish connection to the ATLAS API Service. Check that the backend server is running and try again.
        </p>
        <button
          onClick={() => {
            overviewQuery.refetch();
            incidentsQuery.refetch();
            recommendationsQuery.refetch();
            stateQuery.refetch();
          }}
          className="mt-6 flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-xs font-semibold text-primary-foreground hover:opacity-90 transition-opacity focus-visible:ring-2 focus-visible:ring-primary outline-none"
        >
          <RefreshCw className="h-4 w-4" />
          Retry Connection
        </button>
      </div>
    );
  }

  const overview = overviewQuery.data!;
  const incidents = incidentsQuery.data?.items || [];
  const recommendations = recommendationsQuery.data?.items || [];
  const zones = stateQuery.data || [];

  const kpis = [
    {
      title: "Stadium Health",
      value: `${Math.round(overview.stadium_health * 100)}%`,
      desc: "Live aggregated safety score",
      icon: <ShieldCheck className="h-5 w-5 text-emerald-500" />,
    },
    {
      title: "Active Incidents",
      value: String(overview.active_incidents_count),
      desc: "Unresolved issues in zones",
      icon: <AlertTriangle className="h-5 w-5 text-destructive" />,
    },
    {
      title: "Pending Recommendations",
      value: String(overview.pending_recommendations_count),
      desc: "Actions requiring confirmation",
      icon: <Compass className="h-5 w-5 text-amber-500 animate-pulse" />,
    },
    {
      title: "Active Volunteers",
      value: String(overview.allocated_volunteers_count),
      desc: "Deployed staff members",
      icon: <Users className="h-5 w-5 text-blue-500" />,
    },
    {
      title: "Crowd Flow Density",
      value: `${Math.round(overview.average_crowd_density * 100)}%`,
      desc: "Avg capacity density rate",
      icon: <Brain className="h-5 w-5 text-purple-500" />,
    },
  ];

  return (
    <div className="flex flex-col gap-8 text-left">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Operations Dashboard</h1>
          <p className="text-xs text-muted-foreground mt-1">Real-time stadium management and decision support systems.</p>
        </div>
        <div className="text-xs text-muted-foreground">
          Last updated: {new Date(overview.timestamp).toLocaleTimeString()}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
        {kpis.map((kpi) => (
          <div key={kpi.title} className="rounded-2xl border border-border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{kpi.title}</span>
              {kpi.icon}
            </div>
            <div className="mt-4">
              <span className="text-3xl font-black tracking-tight">{kpi.value}</span>
            </div>
            <p className="mt-2 text-[10px] text-muted-foreground">{kpi.desc}</p>
          </div>
        ))}
      </div>

      {/* Main Grid Widgets */}
      <div className="grid gap-8 lg:grid-cols-3">
        
        {/* Left Column (Incidents & Recommendations) */}
        <div className="lg:col-span-2 flex flex-col gap-8">
          
          {/* Recent Incidents */}
          <div className="rounded-2xl border border-border bg-card p-6 flex flex-col justify-between">
            <div className="mb-4">
              <h2 className="text-lg font-bold">Recent Incidents</h2>
              <p className="text-xs text-muted-foreground">Latest reported security, medical, and crowd issues.</p>
            </div>

            {incidents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 border border-dashed border-border rounded-xl bg-muted/10">
                <ShieldCheck className="h-8 w-8 text-emerald-500 mb-2" />
                <span className="text-xs font-semibold">Stadium Secure</span>
                <p className="text-[10px] text-muted-foreground mt-0.5">No active incidents reported at this time.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {incidents.map((inc) => (
                  <div key={inc.id} className="flex items-center justify-between p-4 rounded-xl bg-muted/30 border border-border/50 hover:bg-muted/50 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className={`rounded-full p-2 ${inc.severity === "critical" || inc.severity === "high" ? "bg-destructive/10 text-destructive" : "bg-primary/10 text-primary"}`}>
                        <AlertTriangle className="h-4 w-4" />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs font-bold">{inc.description}</span>
                        <span className="text-[10px] text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
                          {inc.incident_type} &bull; {inc.severity} priority
                        </span>
                      </div>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-1 rounded bg-muted text-muted-foreground">
                      {new Date(inc.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active Recommendations */}
          <div className="rounded-2xl border border-border bg-card p-6 flex flex-col justify-between">
            <div className="mb-4">
              <h2 className="text-lg font-bold">Active Recommendations</h2>
              <p className="text-xs text-muted-foreground">Routing actions and flow mitigations suggested by logic engine.</p>
            </div>

            {recommendations.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 border border-dashed border-border rounded-xl bg-muted/10">
                <Compass className="h-8 w-8 text-muted-foreground/60 mb-2" />
                <span className="text-xs font-semibold">Zones Flow Stable</span>
                <p className="text-[10px] text-muted-foreground mt-0.5">No active recommendations generated.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recommendations.map((rec) => (
                  <div key={rec.id} className="flex items-center justify-between p-4 rounded-xl bg-muted/30 border border-border/50 hover:bg-muted/50 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="rounded-full p-2 bg-amber-500/10 text-amber-500">
                        <Compass className="h-4 w-4 animate-spin-slow" />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs font-bold">{rec.details}</span>
                        <span className="text-[10px] text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
                          {rec.action_type} &bull; {Math.round(rec.confidence * 100)}% confidence
                        </span>
                      </div>
                    </div>
                    <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${rec.status === "pending" ? "bg-amber-500/10 text-amber-500" : "bg-primary/10 text-primary"}`}>
                      {rec.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

        {/* Right Column (Heat Summary, Timeline, Activity Feed) */}
        <div className="flex flex-col gap-8">
          
          {/* Crowd Heat Summary */}
          <div className="rounded-2xl border border-border bg-card p-6 flex flex-col justify-between">
            <div className="mb-4">
              <h2 className="text-lg font-bold">Crowd Heat Summary</h2>
              <p className="text-xs text-muted-foreground">Crowd capacity ratios and queue statuses per sector.</p>
            </div>

            {zones.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 border border-dashed border-border rounded-xl bg-muted/10">
                <Brain className="h-8 w-8 text-muted-foreground/60 mb-2" />
                <span className="text-xs font-semibold">No Zone States</span>
                <p className="text-[10px] text-muted-foreground mt-0.5">Operational states lists are empty.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {zones.slice(0, 4).map((zone) => (
                  <div key={zone.zone_id} className="space-y-2">
                    <div className="flex items-center justify-between text-xs font-bold">
                      <span className="truncate max-w-[150px]">Zone {zone.zone_id.slice(0, 8)}</span>
                      <span className={`${zone.density > 0.75 ? "text-destructive" : "text-muted-foreground"}`}>
                        {Math.round(zone.density * 100)}% density ({zone.queue_waiting_minutes}m wait)
                      </span>
                    </div>
                    <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${zone.density > 0.75 ? "bg-destructive animate-pulse" : "bg-primary"}`}
                        style={{ width: `${Math.min(zone.density * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Operational Timeline / Live Activity Feed */}
          <div className="rounded-2xl border border-border bg-card p-6 flex flex-col justify-between">
            <div className="mb-4">
              <h2 className="text-lg font-bold">Operational Timeline</h2>
              <p className="text-xs text-muted-foreground">Chronological log trace of system and incident event cycles.</p>
            </div>

            <div className="relative pl-6 border-l border-border space-y-6">
              {incidents.length === 0 ? (
                <div className="text-xs text-muted-foreground py-4">No events logged in the current operational shift.</div>
              ) : (
                incidents.map((inc) => (
                  <div key={inc.id} className="relative">
                    <div className="absolute -left-[31px] mt-0.5 rounded-full bg-card border-2 border-border p-1 text-primary">
                      <Clock className="h-3 w-3" />
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs font-bold">{inc.resolved ? "Incident Resolved" : "Incident Reported"}</span>
                      <span className="text-[10px] text-muted-foreground mt-0.5">{inc.description}</span>
                      <span className="text-[9px] text-primary font-bold mt-1">
                        {new Date(inc.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Live Activity Feed */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold">Live Activity Feed</h2>
                <p className="text-xs text-muted-foreground">Audit logs feed from stadium monitors.</p>
              </div>
              <TrendingUp className="h-4 w-4 text-primary animate-pulse" />
            </div>
            <div className="space-y-3 font-mono text-[10px] text-muted-foreground">
              <div className="flex gap-2 items-start">
                <span className="text-primary font-bold">[SYS]</span>
                <span>Audit logger initialized. Connected.</span>
              </div>
              <div className="flex gap-2 items-start">
                <span className="text-primary font-bold">[SYS]</span>
                <span>Active volunteers count: {overview.allocated_volunteers_count}.</span>
              </div>
              <div className="flex gap-2 items-start">
                <span className="text-amber-500 font-bold">[WARN]</span>
                <span>Average wait times currently at {zones[0]?.queue_waiting_minutes || 0}m.</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
