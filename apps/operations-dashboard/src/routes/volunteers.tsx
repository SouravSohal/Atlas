import { createFileRoute } from "@tanstack/react-router";
import { Users } from "lucide-react";
import { useVolunteersState } from "../features/volunteers/hooks/useVolunteersState";
import {
  VolunteerKpiRow,
  VolunteerFilterBar,
  VolunteerTable,
  VolunteerDetailsSidebar,
  VolunteerToast,
} from "../features/volunteers/components/VolunteerSubComponents";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/volunteers")({
  component: VolunteersIntelligencePage,
});

function VolunteersIntelligencePage() {
  const {
    volunteers,
    selectedVolunteer,
    filteredVolunteers,
    searchTerm,
    setSearchTerm,
    filterTeam,
    setFilterTeam,
    filterStatus,
    setFilterStatus,
    bulkSelected,
    setBulkSelected,
    expandedRows,
    setExpandedRows,
    selectedVolId,
    setSelectedVolId,
    toastMessage,
    setToastMessage,
    overviewQuery,
    handleAction,
    handleAssign,
  } = useVolunteersState();

  if (overviewQuery.isLoading) {
    return <LoadingScreen />;
  }

  return (
    <div className="space-y-6 text-left">
      {/* Title Header */}
      <div className="flex items-center gap-3.5">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary to-indigo-600 shadow-lg shadow-primary/20 text-white">
          <Users className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-xl font-black text-foreground uppercase tracking-tight">
            Volunteer Intelligence Center
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Real-time staff allocation, performance metrics, and emergency dispatch console.
          </p>
        </div>
      </div>

      {/* KPI Row presentational component */}
      <VolunteerKpiRow volunteers={volunteers} />

      {/* Filter Bar presentational component */}
      <VolunteerFilterBar
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        filterTeam={filterTeam}
        setFilterTeam={setFilterTeam}
        filterStatus={filterStatus}
        setFilterStatus={setFilterStatus}
        setToastMessage={setToastMessage}
      />

      {/* Main Grid: Data table on left, Details sidebar on right */}
      <div className="grid gap-6 lg:grid-cols-4">
        <div className="lg:col-span-3">
          <VolunteerTable
            filteredVolunteers={filteredVolunteers}
            selectedVolId={selectedVolId}
            setSelectedVolId={setSelectedVolId}
            bulkSelected={bulkSelected}
            setBulkSelected={setBulkSelected}
            expandedRows={expandedRows}
            setExpandedRows={setExpandedRows}
          />
        </div>
        <div className="lg:col-span-1">
          <VolunteerDetailsSidebar
            selectedVolunteer={selectedVolunteer}
            handleAssign={handleAssign}
            handleAction={handleAction}
            setToastMessage={setToastMessage}
          />
        </div>
      </div>

      {/* Toast component */}
      <VolunteerToast toastMessage={toastMessage} />
    </div>
  );
}
export { VolunteersIntelligencePage };
