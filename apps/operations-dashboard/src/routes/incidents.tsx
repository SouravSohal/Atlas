import { useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  Search,
  Filter,
  X,
  CheckCircle,
  Clock,
  UserCheck,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
} from "lucide-react";
import { fetchDashboardIncidents, updateIncident, type IncidentItem } from "../services/api";
import { useWebSocket } from "../providers/WebSocketProvider";
import { useGlobalStore } from "../store/useGlobalStore";

export const Route = createFileRoute("/incidents")({
  component: IncidentsPage,
});

function IncidentsPage() {
  const queryClient = useQueryClient();
  const { subscribe, unsubscribe } = useWebSocket();

  useEffect(() => {
    subscribe("incidents");
    return () => unsubscribe("incidents");
  }, [subscribe, unsubscribe]);
  const {
    incidentSearch: search,
    setIncidentSearch: setSearch,
    incidentFilterSeverity: filterSeverity,
    setIncidentFilterSeverity: setFilterSeverity,
    incidentFilterStatus: filterStatus,
    setIncidentFilterStatus: setFilterStatus,
    selectedIncident,
    setSelectedIncident,
    assignedVolunteer,
    setAssignedVolunteer,
    volunteerMessage,
    setVolunteerMessage,
    incidentPage: page,
    setIncidentPage: setPage,
    incidentSortBy: sortBy,
    setIncidentSortBy: setSortBy,
    incidentSortOrder: sortOrder,
    setIncidentSortOrder: setSortOrder,
    playbackActive,
    simulatedIncidents,
  } = useGlobalStore();

  // Query - refresh every 15 seconds
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["dashboard-incidents", page, sortBy, sortOrder],
    queryFn: () => fetchDashboardIncidents(page, 10, sortBy, sortOrder),
    refetchInterval: 15000,
  });

  // Mutation for updating status
  const updateMutation = useMutation({
    mutationFn: ({ id, resolved }: { id: string; resolved: boolean }) =>
      updateIncident(id, resolved),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["dashboard-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["overview"] });
      // Update selected incident details
      if (selectedIncident && selectedIncident.id === updated.id) {
        setSelectedIncident(updated);
      }
    },
  });

  const handleToggleResolve = (incident: IncidentItem) => {
    updateMutation.mutate({ id: incident.id, resolved: !incident.resolved });
  };

  const handleAssignVolunteer = (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignedVolunteer.trim()) return;
    setVolunteerMessage(`Volunteer "${assignedVolunteer}" successfully assigned to task.`);
    setAssignedVolunteer("");
    setTimeout(() => setVolunteerMessage(""), 5000);
  };

  // Close drawer on ESC
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setSelectedIncident(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-[40vh] items-center justify-center">
        <div className="animate-spin text-primary">
          <Clock className="h-8 w-8" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-6 bg-destructive/10 border border-destructive/20 text-destructive rounded-xl text-center">
        <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
        <h3 className="text-sm font-bold">Failed to load incidents</h3>
        <button onClick={() => refetch()} className="mt-4 rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground hover:opacity-90 transition-opacity">
          Retry
        </button>
      </div>
    );
  }

  const items = playbackActive && simulatedIncidents ? simulatedIncidents : (data?.items || []);
  const totalCount = playbackActive && simulatedIncidents ? simulatedIncidents.length : (data?.total_count || 0);
  const totalPages = Math.ceil(totalCount / 10) || 1;

  // Client-side local filtering (search on description)
  const filteredItems = items.filter((item) => {
    const matchesSearch = item.description.toLowerCase().includes(search.toLowerCase());
    const matchesSeverity = filterSeverity === "all" || item.severity === filterSeverity;
    const matchesStatus =
      filterStatus === "all" ||
      (filterStatus === "resolved" && item.resolved) ||
      (filterStatus === "active" && !item.resolved);
    return matchesSearch && matchesSeverity && matchesStatus;
  });

  return (
    <div className="flex flex-col gap-6 text-left relative min-h-[80vh]">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Incident Console</h1>
          <p className="text-xs text-muted-foreground mt-1">Live dispatch control center for security and emergency management.</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted/40 px-3 py-1.5 rounded-full border border-border">
          <Clock className="h-3.5 w-3.5" />
          <span>Polled every 15s</span>
        </div>
      </div>

      {/* Filters & Search Header */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-stretch">
        <div className="flex flex-1 items-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5">
          <Search className="h-4 w-4 text-muted-foreground shrink-0" />
          <input
            type="text"
            placeholder="Search incident logs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-transparent text-sm outline-none text-foreground"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Severity filter */}
          <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-xs">
            <Filter className="h-3.5 w-3.5 text-muted-foreground" />
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="bg-transparent font-semibold outline-none cursor-pointer"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          {/* Status filter */}
          <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-xs">
            <Filter className="h-3.5 w-3.5 text-muted-foreground" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-transparent font-semibold outline-none cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          {/* Sort field selector */}
          <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-xs">
            <ArrowUpDown className="h-3.5 w-3.5 text-muted-foreground" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "created_at" | "severity")}
              className="bg-transparent font-semibold outline-none cursor-pointer"
            >
              <option value="created_at">Date</option>
              <option value="severity">Severity</option>
            </select>
          </div>

          {/* Sort order button */}
          <button
            onClick={() => {
              setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
            }}
            className="flex items-center gap-2 rounded-xl border border-border bg-card px-3.5 py-2 text-xs font-semibold hover:bg-muted transition-colors"
          >
            Sort Order: {sortOrder.toUpperCase()}
          </button>
        </div>
      </div>

      {/* Incident List Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm" role="grid" aria-label="Incidents register table">
            <thead className="bg-muted/50 border-b border-border text-xs font-bold uppercase text-muted-foreground">
              <tr>
                <th className="px-6 py-4">Incident Log ID</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Severity</th>
                <th className="px-6 py-4">Description</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Time</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-sm text-muted-foreground">
                    No matching incidents found.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-muted/35 cursor-pointer transition-colors"
                    onClick={() => setSelectedIncident(item)}
                  >
                    <td className="px-6 py-4 font-mono text-xs">{item.id.slice(0, 8)}</td>
                    <td className="px-6 py-4 font-semibold text-foreground uppercase tracking-wider text-xs">
                      {item.incident_type}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex rounded px-2.5 py-1 text-[10px] font-bold uppercase ${
                          item.severity === "critical" || item.severity === "high"
                            ? "bg-destructive/10 text-destructive"
                            : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {item.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-foreground truncate max-w-xs">{item.description}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-[10px] font-bold ${
                          item.resolved ? "bg-emerald-500/10 text-emerald-500" : "bg-destructive/10 text-destructive animate-pulse"
                        }`}
                      >
                        {item.resolved ? "Resolved" : "Active"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-muted-foreground">
                      {new Date(item.created_at).toLocaleTimeString()}
                    </td>
                    <td className="px-6 py-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => setSelectedIncident(item)}
                        className="rounded-xl border border-border px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination footer */}
        <div className="flex items-center justify-between border-t border-border px-6 py-4 bg-muted/20">
          <span className="text-xs text-muted-foreground">
            Page {page} of {totalPages} ({totalCount} total entries)
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
              disabled={page === 1}
              aria-label="Previous page"
              className="rounded-xl border border-border p-2 hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              onClick={() => setPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={page === totalPages}
              aria-label="Next page"
              className="rounded-xl border border-border p-2 hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* DETAIL SLIDE-OVER DRAWER */}
      {selectedIncident && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Incident details"
          className="fixed inset-y-0 right-0 z-50 flex max-w-full pl-10"
        >
          {/* Overlay backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity duration-300"
            onClick={() => setSelectedIncident(null)}
          />

          <div className="relative w-screen max-w-md transform bg-card border-l border-border shadow-2xl p-6 transition-transform duration-300 translate-x-0 overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-border pb-4 mb-6">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground font-mono">
                  Incident ID {selectedIncident.id.slice(0, 8)}
                </span>
                <h2 className="text-lg font-bold mt-1 text-foreground">Incident Record Details</h2>
              </div>
              <button
                onClick={() => setSelectedIncident(null)}
                aria-label="Close details panel"
                className="rounded-full p-1.5 hover:bg-muted text-muted-foreground transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Information Grid */}
            <div className="space-y-6">
              <div className="rounded-xl border border-border bg-muted/20 p-4 space-y-3">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground font-medium">Type Classification</span>
                  <span className="font-bold uppercase tracking-wider text-foreground">
                    {selectedIncident.incident_type}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground font-medium">Severity Tier</span>
                  <span className="font-bold uppercase tracking-wider text-foreground">
                    {selectedIncident.severity}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground font-medium">Resolution Status</span>
                  <span className={`font-bold px-2 py-0.5 rounded-full ${selectedIncident.resolved ? "bg-emerald-500/10 text-emerald-500" : "bg-destructive/10 text-destructive animate-pulse"}`}>
                    {selectedIncident.resolved ? "Resolved" : "Active Dispatch"}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground font-medium">Report Time</span>
                  <span className="font-semibold text-foreground">
                    {new Date(selectedIncident.created_at).toLocaleString()}
                  </span>
                </div>
                {selectedIncident.resolved_at && (
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground font-medium">Resolved Time</span>
                    <span className="font-semibold text-foreground">
                      {new Date(selectedIncident.resolved_at).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>

              {/* Description */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-muted-foreground">Description</span>
                <p className="text-sm border border-border rounded-xl p-3 bg-muted/10 leading-relaxed text-foreground">
                  {selectedIncident.description}
                </p>
              </div>

              {/* Coordinates Map coordinates */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-muted-foreground">Geographical coordinates</span>
                <div className="flex justify-between text-xs border border-border rounded-xl p-3 bg-muted/10 font-mono">
                  <span>Lat: {selectedIncident.latitude}</span>
                  <span>Long: {selectedIncident.longitude}</span>
                </div>
              </div>

              {/* Actions segment */}
              <div className="space-y-4 pt-4 border-t border-border">
                <span className="text-xs font-bold text-muted-foreground">Console Dispatch Actions</span>
                
                <div className="flex gap-4">
                  <button
                    onClick={() => handleToggleResolve(selectedIncident)}
                    disabled={updateMutation.isPending}
                    className={`flex-1 rounded-xl px-4 py-3 text-xs font-semibold shadow-sm transition-all focus-visible:ring-2 focus-visible:ring-primary outline-none ${
                      selectedIncident.resolved
                        ? "border border-border bg-card text-foreground hover:bg-muted"
                        : "bg-emerald-600 text-white hover:opacity-90"
                    }`}
                  >
                    {selectedIncident.resolved ? "Mark Incident as Active" : "Mark as Resolved"}
                  </button>
                </div>

                {/* Volunteer Assignment Form */}
                <form onSubmit={handleAssignVolunteer} className="space-y-3 pt-3 border-t border-border">
                  <label htmlFor="volunteer-input" className="block text-xs font-bold text-muted-foreground">
                    Deploy Volunteer Staff
                  </label>
                  <div className="flex gap-2">
                    <input
                      id="volunteer-input"
                      type="text"
                      placeholder="Enter volunteer name..."
                      value={assignedVolunteer}
                      onChange={(e) => setAssignedVolunteer(e.target.value)}
                      className="flex-1 rounded-xl border border-border bg-muted/20 px-3 py-2.5 text-xs outline-none text-foreground focus-visible:ring-2 focus-visible:ring-primary"
                    />
                    <button
                      type="submit"
                      className="flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:opacity-90 transition-all focus-visible:ring-2 focus-visible:ring-primary outline-none"
                    >
                      <UserCheck className="h-4 w-4" />
                      Deploy
                    </button>
                  </div>
                  {volunteerMessage && (
                    <div className="flex items-center gap-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 px-3.5 py-2 text-[10px] font-bold text-emerald-500">
                      <CheckCircle className="h-3.5 w-3.5 shrink-0" />
                      <span>{volunteerMessage}</span>
                    </div>
                  )}
                </form>
              </div>

            </div>
          </div>
        </div>
      )}
    </div>
  );
}
