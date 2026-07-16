import { Search } from "lucide-react";

interface FiltersConsoleProps {
  searchTerm: string;
  setSearchTerm: (val: string) => void;
  filterPriority: string;
  setFilterPriority: (val: string) => void;
  filterSeverity: string;
  setFilterSeverity: (val: string) => void;
  filterStatus: string;
  setFilterStatus: (val: string) => void;
  filterCategory: string;
  setFilterCategory: (val: string) => void;
  selectedIds: Record<string, boolean>;
  handleBulkAction: (status: string) => void;
}

export function FiltersConsole({
  searchTerm,
  setSearchTerm,
  filterPriority,
  setFilterPriority,
  filterSeverity,
  setFilterSeverity,
  filterStatus,
  setFilterStatus,
  filterCategory,
  setFilterCategory,
  selectedIds,
  handleBulkAction,
}: FiltersConsoleProps) {
  const selectedCount = Object.keys(selectedIds).filter((id) => selectedIds[id]).length;

  return (
    <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-5 shadow-lg flex flex-col gap-4">
      <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-5">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search actions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-xl border border-border bg-muted/20 pl-9 pr-3 py-2 text-xs font-bold outline-none placeholder:text-muted-foreground focus-visible:ring-1 focus-visible:ring-primary"
          />
        </div>

        {/* Priority */}
        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value)}
          className="rounded-xl border border-border bg-muted/20 px-3 py-2 text-xs font-bold outline-none cursor-pointer"
        >
          <option value="all">All Priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>

        {/* Severity */}
        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="rounded-xl border border-border bg-muted/20 px-3 py-2 text-xs font-bold outline-none cursor-pointer"
        >
          <option value="all">All Severities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>

        {/* Status */}
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-xl border border-border bg-muted/20 px-3 py-2 text-xs font-bold outline-none cursor-pointer"
        >
          <option value="all">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="completed">Completed</option>
        </select>

        {/* Category */}
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="rounded-xl border border-border bg-muted/20 px-3 py-2 text-xs font-bold outline-none cursor-pointer"
        >
          <option value="all">All Categories</option>
          <option value="reroute">Rerouting</option>
          <option value="dispatch">Dispatching</option>
          <option value="facility">Facility</option>
        </select>
      </div>

      {/* Bulk Action Controls */}
      {selectedCount > 0 && (
        <div className="flex items-center gap-3 bg-muted/30 border border-border rounded-xl p-3 justify-between animate-fadeIn">
          <span className="text-xs font-bold text-muted-foreground">
            Selected: {selectedCount} items
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleBulkAction("approved")}
              className="rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-black text-black uppercase tracking-wider hover:opacity-90"
            >
              Bulk Approve
            </button>
            <button
              onClick={() => handleBulkAction("rejected")}
              className="rounded-lg bg-destructive px-3 py-1.5 text-xs font-black text-destructive-foreground uppercase tracking-wider hover:opacity-90"
            >
              Bulk Reject
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
