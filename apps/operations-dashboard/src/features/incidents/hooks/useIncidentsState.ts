import { useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchDashboardIncidents, updateIncident, type IncidentItem } from "../../../services/api";
import { useWebSocket } from "../../../providers/WebSocketProvider";
import { useGlobalStore } from "../../../store/useGlobalStore";

export function useIncidentsState() {
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
  }, [setSelectedIncident]);

  return {
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
    setVolunteerMessage,
    page,
    setPage,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
    playbackActive,
    simulatedIncidents,
    data,
    isLoading,
    isError,
    refetch,
    handleToggleResolve,
    handleAssignVolunteer,
    updateMutation,
  };
}
