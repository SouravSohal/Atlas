import { createFileRoute } from "@tanstack/react-router";
import { LayoutDashboard, Users, AlertCircle, TrendingUp } from "lucide-react";

export const Route = createFileRoute("/")({
  component: DashboardOverviewPage,
});

function DashboardOverviewPage() {
  const cards = [
    { title: "Active Incidents", value: "3", icon: <AlertCircle className="h-5 w-5 text-red-500" />, desc: "Critical security/medical alerts" },
    { title: "Crowd Flow Rate", value: "1.2k / min", icon: <Users className="h-5 w-5 text-blue-500" />, desc: "Total stadium visitor entries" },
    { title: "Average Wait Time", value: "14 mins", icon: <TrendingUp className="h-5 w-5 text-green-500" />, desc: "Queue wait duration estimate" },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <LayoutDashboard className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold tracking-tight">Operations Overview</h1>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <div key={card.title} className="rounded-2xl border border-border bg-card p-6 shadow-sm transition-all hover:shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-muted-foreground">{card.title}</span>
              {card.icon}
            </div>
            <div className="mt-4">
              <span className="text-3xl font-bold tracking-tight">{card.value}</span>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">{card.desc}</p>
          </div>
        ))}
      </div>

      {/* Main Grid Mock Section */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-border bg-card p-6 min-h-[300px] flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold">Operational Health Telemetry</h2>
            <p className="text-xs text-muted-foreground mt-1">Live health monitoring status across all zones.</p>
          </div>
          <div className="flex flex-1 items-center justify-center border-2 border-dashed border-border rounded-xl mt-4 bg-muted/20">
            <span className="text-xs text-muted-foreground">Visualization Canvas Placeholder</span>
          </div>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6 min-h-[300px] flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold">Resource Allocation status</h2>
            <p className="text-xs text-muted-foreground mt-1">Volunteers assignment and task list details.</p>
          </div>
          <div className="flex flex-1 items-center justify-center border-2 border-dashed border-border rounded-xl mt-4 bg-muted/20">
            <span className="text-xs text-muted-foreground">Task Flow Diagram Placeholder</span>
          </div>
        </div>
      </div>
    </div>
  );
}
