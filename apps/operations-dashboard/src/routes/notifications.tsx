import { useState, useMemo, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useWebSocket } from "../providers/WebSocketProvider";
import {
  Bell,
  Filter,
  Trash2,
  Shield,
  HeartPulse,
  Brain,
  CloudRain,
  Bus,
  CheckCircle,
  Clock,
  Activity,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  fetchDashboardIncidents,
  fetchDashboardRecommendations,
  updateIncident,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/notifications")({
  component: NotificationCenterPage,
});

type NotificationCategory = "Security" | "Medical" | "Operations" | "AI" | "Weather" | "Transport";
type NotificationSeverity = "info" | "warning" | "critical";

interface NotificationItem {
  id: string;
  category: NotificationCategory;
  severity: NotificationSeverity;
  title: string;
  description: string;
  timestamp: string;
  read: boolean;
  referenceId: string;
  type: "incident" | "recommendation";
}

function NotificationCenterPage() {
  const queryClient = useQueryClient();
  const { subscribe, unsubscribe } = useWebSocket();

  useEffect(() => {
    subscribe("incidents");
    subscribe("recommendations");
    return () => {
      unsubscribe("incidents");
      unsubscribe("recommendations");
    };
  }, [subscribe, unsubscribe]);

  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [groupBySeverity, setGroupBySeverity] = useState(false);
  const [localReadState, setLocalReadState] = useState<Record<string, boolean>>({});

  // Query backend data
  const incidentsQuery = useQuery({
    queryKey: ["notifications-incidents"],
    queryFn: () => fetchDashboardIncidents(1, 100),
    refetchInterval: 5000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["notifications-recs"],
    queryFn: () => fetchDashboardRecommendations(1, 100),
    refetchInterval: 5000,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, resolved }: { id: string; resolved: boolean }) =>
      updateIncident(id, resolved),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["cc-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["cc-overview"] });
    },
  });

  const handleResolveIncident = (incidentId: string) => {
    updateMutation.mutate({ id: incidentId, resolved: true });
  };

  const handleMarkAsRead = (id: string) => {
    setLocalReadState((prev) => ({ ...prev, [id]: true }));
  };

  const handleMarkAllAsRead = (notifs: NotificationItem[]) => {
    const updates = notifs.reduce((acc, n) => ({ ...acc, [n.id]: true }), {});
    setLocalReadState((prev) => ({ ...prev, ...updates }));
  };

  // Convert raw API models into standardized notifications
  const notificationsList = useMemo(() => {
    const list: NotificationItem[] = [];

    // Map Incidents
    const incidents = incidentsQuery.data?.items || [];
    incidents.forEach((inc) => {
      let category: NotificationCategory = "Operations";
      if (inc.incident_type === "security") category = "Security";
      else if (inc.incident_type === "medical") category = "Medical";
      else if (inc.incident_type === "weather") category = "Weather";

      let severity: NotificationSeverity = "info";
      if (inc.severity === "critical") severity = "critical";
      else if (inc.severity === "high" || inc.severity === "medium") severity = "warning";

      list.push({
        id: `incident-${inc.id}`,
        category,
        severity,
        title: `${category} Dispatch Alert`,
        description: inc.description,
        timestamp: inc.created_at,
        read: inc.resolved || localReadState[`incident-${inc.id}`] || false,
        referenceId: inc.id,
        type: "incident",
      });
    });

    // Map AI Recommendations
    const recs = recommendationsQuery.data?.items || [];
    recs.forEach((rec) => {
      let severity: NotificationSeverity = "info";
      if (rec.priority === "high") severity = "warning";

      list.push({
        id: `rec-${rec.id}`,
        category: "AI",
        severity,
        title: `AI Optimization: ${rec.action_type}`,
        description: rec.details,
        timestamp: rec.created_at,
        read: localReadState[`rec-${rec.id}`] || false,
        referenceId: rec.id,
        type: "recommendation",
      });
    });

    // Add a couple of simulated static Transport notifications
    list.push({
      id: "transport-static-1",
      category: "Transport",
      severity: "info",
      title: "Shuttle Circulator Frequency",
      description: "Subway connector shuttles running at 3-minute intervals. Traffic flowing normally.",
      timestamp: new Date(Date.now() - 300000).toISOString(),
      read: localReadState["transport-static-1"] || false,
      referenceId: "static-1",
      type: "incident",
    });

    return list.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [incidentsQuery.data, recommendationsQuery.data, localReadState]);

  // Compute unread count
  const unreadCount = useMemo(() => {
    return notificationsList.filter((n) => !n.read).length;
  }, [notificationsList]);

  // Filters
  const filteredNotifications = useMemo(() => {
    return notificationsList.filter((n) => {
      const matchesCategory = filterCategory === "all" || n.category === filterCategory;
      const matchesSeverity = filterSeverity === "all" || n.severity === filterSeverity;
      return matchesCategory && matchesSeverity;
    });
  }, [notificationsList, filterCategory, filterSeverity]);

  // Grouping
  const groupedNotifications = useMemo(() => {
    if (!groupBySeverity) return { list: filteredNotifications };

    return filteredNotifications.reduce<Record<string, NotificationItem[]>>((acc, item) => {
      const key = item.severity.toUpperCase();
      if (!acc[key]) acc[key] = [];
      acc[key].push(item);
      return acc;
    }, {});
  }, [filteredNotifications, groupBySeverity]);

  if (incidentsQuery.isLoading || recommendationsQuery.isLoading) {
    return <LoadingScreen />;
  }

  const categoryIcons: Record<NotificationCategory, React.ReactNode> = {
    Security: <Shield className="h-4 w-4" />,
    Medical: <HeartPulse className="h-4 w-4" />,
    Operations: <Activity className="h-4 w-4" />,
    AI: <Brain className="h-4 w-4" />,
    Weather: <CloudRain className="h-4 w-4" />,
    Transport: <Bus className="h-4 w-4" />,
  };

  const severityColors = {
    info: "border-blue-500/20 bg-blue-500/5 text-blue-400",
    warning: "border-amber-500/20 bg-amber-500/5 text-amber-400",
    critical: "border-destructive/30 bg-destructive/5 text-destructive animate-pulse",
  };

  return (
    <div className="flex flex-col gap-6 text-left max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Bell className="h-8 w-8 text-primary" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-destructive text-[10px] font-black text-white flex items-center justify-center animate-pulse">
                {unreadCount}
              </span>
            )}
          </div>
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">Notification Center</h1>
            <p className="text-xs text-muted-foreground mt-1">Live broadcast alerts, dispatcher coordination notes, and AI logs.</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleMarkAllAsRead(filteredNotifications)}
            className="rounded-xl border border-border bg-card px-4 py-2 text-xs font-semibold hover:bg-muted transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
          >
            Mark Page as Read
          </button>
        </div>
      </div>

      {/* Control bar */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-stretch bg-muted/20 p-4 border border-border rounded-2xl shadow-sm">
        <div className="flex flex-wrap items-center gap-3 text-xs">
          
          {/* Category Filter */}
          <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2">
            <Filter className="h-3.5 w-3.5 text-muted-foreground" />
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="bg-transparent font-semibold outline-none cursor-pointer"
            >
              <option value="all">All Categories</option>
              <option value="Security">Security</option>
              <option value="Medical">Medical</option>
              <option value="Operations">Operations</option>
              <option value="AI">AI Agent</option>
              <option value="Weather">Weather</option>
              <option value="Transport">Transport</option>
            </select>
          </div>

          {/* Severity Filter */}
          <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2">
            <Filter className="h-3.5 w-3.5 text-muted-foreground" />
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="bg-transparent font-semibold outline-none cursor-pointer"
            >
              <option value="all">All Severities</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs font-bold cursor-pointer text-muted-foreground hover:text-foreground select-none">
            <input
              type="checkbox"
              checked={groupBySeverity}
              onChange={(e) => setGroupBySeverity(e.target.checked)}
              className="rounded border-border bg-card text-primary focus:ring-primary"
            />
            Group by Severity
          </label>
        </div>
      </div>

      {/* Notifications list layout */}
      <div className="space-y-6">
        <AnimatePresence mode="popLayout">
          {groupBySeverity ? (
            Object.entries(groupedNotifications).map(([groupName, list]) => (
              <div key={groupName} className="space-y-3">
                <h3 className="text-xs font-black tracking-widest text-muted-foreground uppercase pl-1">{groupName} ALERTS</h3>
                <div className="space-y-3">
                  {list.map((notif) => (
                    <NotificationCard
                      key={notif.id}
                      notif={notif}
                      categoryIcons={categoryIcons}
                      severityColors={severityColors}
                      onRead={handleMarkAsRead}
                      onResolve={handleResolveIncident}
                    />
                  ))}
                </div>
              </div>
            ))
          ) : filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center border border-dashed border-border rounded-2xl bg-card">
              <CheckCircle className="h-10 w-10 text-emerald-500 mb-3" />
              <span className="text-sm font-bold text-foreground">Inbox Clear</span>
              <p className="text-xs text-muted-foreground mt-1 max-w-xs">
                No active notifications match your current category and severity filters.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredNotifications.map((notif) => (
                <NotificationCard
                  key={notif.id}
                  notif={notif}
                  categoryIcons={categoryIcons}
                  severityColors={severityColors}
                  onRead={handleMarkAsRead}
                  onResolve={handleResolveIncident}
                />
              ))}
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// Sub-component: Notification Card
interface NotificationCardProps {
  notif: NotificationItem;
  categoryIcons: Record<NotificationCategory, React.ReactNode>;
  severityColors: Record<NotificationSeverity, string>;
  onRead: (id: string) => void;
  onResolve: (id: string) => void;
}

function NotificationCard({ notif, categoryIcons, severityColors, onRead, onResolve }: NotificationCardProps) {
  const formattedTime = (dateStr: string) => {
    const diffMs = Date.now() - new Date(dateStr).getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return new Date(dateStr).toLocaleDateString();
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={`rounded-2xl border bg-card p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 transition-all duration-200 ${
        notif.read ? "opacity-60 border-border" : "shadow-md border-border/80 border-l-4 border-l-primary"
      }`}
    >
      <div className="flex gap-4 items-start text-left">
        <div className={`rounded-xl p-2.5 border shrink-0 ${severityColors[notif.severity]}`}>
          {categoryIcons[notif.category]}
        </div>
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-black text-foreground">{notif.title}</span>
            <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${severityColors[notif.severity]}`}>
              {notif.severity}
            </span>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed max-w-xl">{notif.description}</p>
          <div className="flex items-center gap-1.5 text-[9px] text-muted-foreground font-semibold mt-1">
            <Clock className="h-3 w-3" />
            <span>{formattedTime(notif.timestamp)}</span>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-2 shrink-0 self-end sm:self-center">
        {!notif.read && (
          <button
            onClick={() => onRead(notif.id)}
            className="rounded-lg border border-border px-3 py-1.5 text-[10px] font-bold hover:bg-muted transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
          >
            Mark as Read
          </button>
        )}

        {notif.type === "incident" && !notif.read && (
          <button
            onClick={() => onResolve(notif.referenceId)}
            className="rounded-lg bg-emerald-600 px-3 py-1.5 text-[10px] font-bold text-white hover:opacity-90 transition-all focus-visible:ring-2 focus-visible:ring-primary outline-none"
          >
            Resolve
          </button>
        )}

        <button
          onClick={() => onRead(notif.id)}
          aria-label="Delete notification"
          className="rounded-lg p-2 border border-border text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
    </motion.div>
  );
}
