import { ShieldCheck, AlertTriangle, Users, Brain, Clock } from "lucide-react";
import { motion } from "framer-motion";

interface KpiMatrixProps {
  overview: any;
}

export function KpiMatrix({ overview }: KpiMatrixProps) {
  const metrics = [
    {
      title: "Stadium Health",
      value: `${Math.round((overview?.stadium_health || 0.98) * 100)}%`,
      status: "Optimal",
      icon: <ShieldCheck className="h-4 w-4 text-emerald-400" />,
    },
    {
      title: "Active Incidents",
      value: overview?.active_incidents_count ?? 0,
      status: "Urgent",
      icon: <AlertTriangle className="h-4 w-4 text-destructive" />,
    },
    {
      title: "Crowd Density",
      value: `${Math.round((overview?.average_crowd_density || 0.45) * 100)}%`,
      status: "Moderate",
      icon: <Users className="h-4 w-4 text-primary" />,
    },
    {
      title: "Volunteers Allocated",
      value: overview?.allocated_volunteers_count ?? 0,
      status: "Active",
      icon: <Users className="h-4 w-4 text-primary" />,
    },
    {
      title: "AI Confidence",
      value: "96.4%",
      status: "Optimal",
      icon: <Brain className="h-4 w-4 text-emerald-400" />,
    },
    {
      title: "Avg Queue Time",
      value: "8 min",
      status: "Optimal",
      icon: <Clock className="h-4 w-4 text-emerald-400" />,
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
      {metrics.map((m) => (
        <motion.div
          key={`${m.title}-${m.value}`}
          initial={{ scale: 0.95, opacity: 0.8 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className="rounded-xl border border-border bg-card/45 backdrop-blur-md p-4 hover:shadow-md transition-shadow text-left"
        >
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-[10px] font-bold uppercase tracking-wider">{m.title}</span>
            {m.icon}
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-black tracking-tight">{m.value}</span>
            <span className="text-[9px] font-bold text-muted-foreground uppercase">{m.status}</span>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
