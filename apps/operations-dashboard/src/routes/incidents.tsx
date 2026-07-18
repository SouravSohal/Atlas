import { createFileRoute } from "@tanstack/react-router";
import { Clock } from "lucide-react";
import { useIncidentsState } from "../features/incidents/hooks/useIncidentsState";
import {
  IncidentsFilterBar,
  IncidentsTable,
  IncidentDetailDrawer,
} from "../features/incidents/components/IncidentSubComponents";

export const Route = createFileRoute("/incidents")({
  component: IncidentsPage,
});

function IncidentsPage() {
  const {
    search,
    setSearch,
    filterSeverity,
    setFilterSeverity,
    filterStatus,
    setFilterStatus,
    selectedIncident,
    setSelectedIncident,
    assignedVolunteer,
    setAssignedVolunteer,
    volunteerMessage,
    page,
    setPage,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
    playbackActive,
    simulatedIncidents,
    data,
    handleToggleResolve,
    handleAssignVolunteer,
    updateMutation,
  } = useIncidentsState();

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

      {/* Filters & Search Header presentational component */}
      <IncidentsFilterBar
        search={search}
        setSearch={setSearch}
        filterSeverity={filterSeverity}
        setFilterSeverity={setFilterSeverity}
        filterStatus={filterStatus}
        setFilterStatus={setFilterStatus}
        sortBy={sortBy}
        setSortBy={setSortBy}
        sortOrder={sortOrder}
        setSortOrder={setSortOrder}
      />

      {/* Incident List Table presentational component */}
      <IncidentsTable
        filteredItems={filteredItems}
        setSelectedIncident={setSelectedIncident}
        page={page}
        setPage={setPage}
        totalPages={totalPages}
        totalCount={totalCount}
      />

      {/* Detail slide-over drawer presentational component */}
      {selectedIncident && (
        <IncidentDetailDrawer
          selectedIncident={selectedIncident}
          setSelectedIncident={setSelectedIncident}
          handleToggleResolve={handleToggleResolve}
          updateMutationIsPending={updateMutation.isPending}
          assignedVolunteer={assignedVolunteer}
          setAssignedVolunteer={setAssignedVolunteer}
          handleAssignVolunteer={handleAssignVolunteer}
          volunteerMessage={volunteerMessage}
        />
      )}
    </div>
  );
}
export { IncidentsPage };
