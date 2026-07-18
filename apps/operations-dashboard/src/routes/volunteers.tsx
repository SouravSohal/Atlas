import { useState, useMemo, useEffect, Fragment } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  Users,
  Search,
  CheckCircle,
  Sparkles,
  Battery,
  AlertOctagon,
  UserCheck,
  UserX,
  MessageSquare,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { fetchDashboardOverview } from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";
import { useWebSocket } from "../providers/WebSocketProvider";
import { useGlobalStore } from "../store/useGlobalStore";
import type { Volunteer } from "../store/useGlobalStore";

export const Route = createFileRoute("/volunteers")({
  component: VolunteersIntelligencePage,
});

// Custom hook to extract all state, API calling, and logic
function useVolunteersState() {
  const { subscribe, unsubscribe } = useWebSocket();
  const {
    volunteers,
    setVolunteers,
    toastMessage,
    setToastMessage,
  } = useGlobalStore();
  const [selectedVolId, setSelectedVolId] = useState<string>("vol-1");
  const [bulkSelected, setBulkSelected] = useState<Record<string, boolean>>({});
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});

  // Filters
  const [searchTerm, setSearchTerm] = useState("");
  const [filterTeam, setFilterTeam] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");

  const overviewQuery = useQuery({
    queryKey: ["cc-overview"],
    queryFn: fetchDashboardOverview,
    refetchInterval: 5000,
  });

  // Real-time WebSocket connection to subscribe to updates
  useEffect(() => {
    subscribe("telemetry");
    return () => unsubscribe("telemetry");
  }, [subscribe, unsubscribe]);

  const selectedVolunteer = useMemo(() => {
    return volunteers.find((v) => v.id === selectedVolId) || volunteers[0];
  }, [volunteers, selectedVolId]);

  // Filters application
  const filteredVolunteers = useMemo(() => {
    return volunteers.filter((v) => {
      const matchSearch = v.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.currentAssignment.toLowerCase().includes(searchTerm.toLowerCase());
      const matchTeam = filterTeam === "all" || v.team.toLowerCase() === filterTeam.toLowerCase();
      const matchStatus = filterStatus === "all" || v.status.toLowerCase() === filterStatus.toLowerCase();
      return matchSearch && matchTeam && matchStatus;
    });
  }, [volunteers, searchTerm, filterTeam, filterStatus]);

  const handleAction = (action: string) => {
    if (!selectedVolunteer) return;
    
    // Perform state changes based on action
    if (action === "available") {
      setVolunteers((prev) =>
        prev.map((v) => (v.id === selectedVolunteer.id ? { ...v, status: "Available", currentAssignment: "Idle / Standing by" } : v))
      );
      setToastMessage(`Volunteer ${selectedVolunteer.name} is now Available.`);
    } else if (action === "recall") {
      setVolunteers((prev) =>
        prev.map((v) => (v.id === selectedVolunteer.id ? { ...v, status: "Off Duty", currentAssignment: "Stood down" } : v))
      );
      setToastMessage(`Recalled Volunteer ${selectedVolunteer.name}.`);
    } else if (action === "emergency") {
      setVolunteers((prev) =>
        prev.map((v) => (v.id === selectedVolunteer.id ? { ...v, status: "Emergency", currentAssignment: "Emergency dispatch active" } : v))
      );
      setToastMessage(`EMERGENCY: Dispatch alert sent to ${selectedVolunteer.name}!`);
    }
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleAssign = () => {
    const task = prompt("Enter assignment details:");
    if (!task) return;
    setVolunteers((prev) =>
      prev.map((v) => (v.id === selectedVolunteer.id ? { ...v, status: "Assigned", currentAssignment: task } : v))
    );
    setToastMessage(`Assigned task to ${selectedVolunteer.name}.`);
    setTimeout(() => setToastMessage(null), 3500);
  };

  return {
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
  };
}

// Presentational Component: KPI Row
interface VolunteerKpiRowProps {
  volunteers: Volunteer[];
}
function VolunteerKpiRow({ volunteers }: VolunteerKpiRowProps) {
  const kpis = useMemo(() => [
    { title: "Total Staff", value: volunteers.length, desc: "Active registry" },
    { title: "Available", value: volunteers.filter((v) => v.status === "Available").length, desc: "Ready to deploy", highlight: "text-emerald-400" },
    { title: "Assigned", value: volunteers.filter((v) => v.status === "Assigned").length, desc: "On active task" },
    { title: "Off Duty", value: volunteers.filter((v) => v.status === "Off Duty").length, desc: "Shift ended" },
    { title: "Active Missions", value: volunteers.filter((v) => v.status === "Emergency" || v.status === "Assigned").length, desc: "Missions in progress" },
    { title: "Avg Response", value: "3.5m", desc: "Dispatch speed" }
  ], [volunteers]);

  return (
    <div className="grid gap-4 grid-cols-2 md:grid-cols-6">
      {kpis.map((kpi, idx) => (
        <div key={idx} className="rounded-xl border border-border bg-card/45 backdrop-blur-md p-4 shadow">
          <span className="text-[8px] font-black text-muted-foreground uppercase tracking-widest block">{kpi.title}</span>
          <span className={`text-2xl font-black mt-2 block ${kpi.highlight || "text-foreground"}`}>{kpi.value}</span>
          <span className="text-[8px] font-bold text-muted-foreground uppercase mt-1 block">{kpi.desc}</span>
        </div>
      ))}
    </div>
  );
}

// Presentational Component: Filter & Search Bar + AI Staffing Recommendations
interface VolunteerFilterBarProps {
  searchTerm: string;
  setSearchTerm: (val: string) => void;
  filterTeam: string;
  setFilterTeam: (val: string) => void;
  filterStatus: string;
  setFilterStatus: (val: string) => void;
  setToastMessage: (msg: string | null) => void;
}
function VolunteerFilterBar({
  searchTerm,
  setSearchTerm,
  filterTeam,
  setFilterTeam,
  filterStatus,
  setFilterStatus,
  setToastMessage,
}: VolunteerFilterBarProps) {
  return (
    <>
      {/* Controls */}
      <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-4 flex flex-wrap items-center gap-4 justify-between">
        <div className="flex items-center gap-2">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search staff..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none placeholder:text-muted-foreground w-48 focus-visible:ring-1 focus-visible:ring-primary"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={filterTeam}
            onChange={(e) => setFilterTeam(e.target.value)}
            className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer"
          >
            <option value="all">All Teams</option>
            <option value="Medical">Medical</option>
            <option value="Crowd Control">Crowd Control</option>
            <option value="Gate Ops">Gate Ops</option>
            <option value="Security">Security</option>
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="rounded-xl border border-border bg-muted/20 px-3 py-1.5 text-xs font-bold outline-none cursor-pointer"
          >
            <option value="all">All Statuses</option>
            <option value="Available">Available</option>
            <option value="Assigned">Assigned</option>
            <option value="Off Duty">Off Duty</option>
            <option value="Emergency">Emergency</option>
          </select>
        </div>
      </div>

      {/* AI recommendations bar */}
      <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-amber-400 shrink-0" />
          <span className="text-[10px] font-black text-amber-400 uppercase tracking-widest">
            AI Staffing Recommendation:
          </span>
          <p className="text-xs font-bold text-foreground">
            Move 6 volunteers from Food Court to Gate B. Expected congestion improvement: 30%.
          </p>
        </div>
        <button
          onClick={() => {
            setToastMessage("AI recommendation applied to dispatcher.");
            setTimeout(() => setToastMessage(null), 3000);
          }}
          className="rounded-lg bg-amber-500 text-black text-[9px] font-black uppercase tracking-wider px-3 py-1 hover:opacity-90"
        >
          Apply
        </button>
      </div>
    </>
  );
}

// Presentational Component: Volunteers Data Grid
interface VolunteerTableProps {
  filteredVolunteers: Volunteer[];
  selectedVolId: string;
  setSelectedVolId: (id: string) => void;
  bulkSelected: Record<string, boolean>;
  setBulkSelected: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  expandedRows: Record<string, boolean>;
  setExpandedRows: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
}
function VolunteerTable({
  filteredVolunteers,
  selectedVolId,
  setSelectedVolId,
  bulkSelected,
  setBulkSelected,
  expandedRows,
  setExpandedRows,
}: VolunteerTableProps) {
  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md overflow-hidden shadow-lg">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-border/40 bg-muted/25 text-[10px] font-black uppercase tracking-widest text-muted-foreground">
            <th className="p-4 w-12 text-center">
              <input
                type="checkbox"
                onChange={(e) => {
                  const checked = e.target.checked;
                  const ids: Record<string, boolean> = {};
                  filteredVolunteers.forEach((v) => (ids[v.id] = checked));
                  setBulkSelected(ids);
                }}
                className="rounded accent-primary cursor-pointer w-4 h-4"
              />
            </th>
            <th className="p-4">Name</th>
            <th className="p-4">Team</th>
            <th className="p-4">Current Zone</th>
            <th className="p-4">Status</th>
            <th className="p-4">Assignment</th>
            <th className="p-4">Battery</th>
            <th className="p-4">ETA</th>
          </tr>
        </thead>
        <tbody>
          {filteredVolunteers.map((vol) => {
            const isSelected = selectedVolId === vol.id;
            const isBulkSelected = bulkSelected[vol.id];
            const isExpanded = expandedRows[vol.id];

            return (
              <Fragment key={vol.id}>
                <tr
                  onClick={() => setSelectedVolId(vol.id)}
                  className={`border-b border-border/40 text-xs font-bold cursor-pointer hover:bg-muted/15 transition-colors ${
                    isSelected ? "bg-primary/5" : ""
                  }`}
                >
                  <td className="p-4 text-center" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={!!isBulkSelected}
                      onChange={(e) => {
                        setBulkSelected((prev) => ({ ...prev, [vol.id]: e.target.checked }));
                      }}
                      className="rounded accent-primary cursor-pointer w-4 h-4"
                    />
                  </td>
                  <td className="p-4 flex flex-col justify-center">
                    <span className="font-black text-foreground uppercase">{vol.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedRows((prev) => ({ ...prev, [vol.id]: !isExpanded }));
                      }}
                      className="text-[9px] text-primary hover:underline self-start uppercase font-bold mt-1"
                    >
                      {isExpanded ? "Collapse logs" : "Expand logs"}
                    </button>
                  </td>
                  <td className="p-4 uppercase">{vol.team}</td>
                  <td className="p-4 uppercase text-muted-foreground">{vol.zone}</td>
                  <td className="p-4">
                    <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded border ${
                      vol.status === "Available"
                        ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                        : vol.status === "Emergency"
                        ? "bg-destructive/10 border-destructive/20 text-destructive animate-pulse"
                        : vol.status === "Off Duty"
                        ? "bg-muted/30 border-border text-muted-foreground"
                        : "bg-amber-500/10 border-amber-500/20 text-amber-500"
                    }`}>
                      {vol.status}
                    </span>
                  </td>
                  <td className="p-4 text-muted-foreground">{vol.currentAssignment}</td>
                  <td className="p-4 flex items-center gap-1.5">
                    <Battery className={`h-4 w-4 ${vol.battery < 20 ? "text-destructive animate-pulse" : "text-muted-foreground"}`} />
                    <span className={vol.battery < 20 ? "text-destructive font-bold" : ""}>{vol.battery}%</span>
                  </td>
                  <td className="p-4 font-mono font-bold">{vol.eta}</td>
                </tr>

                {/* Expanded Row Content */}
                {isExpanded && (
                  <tr className="bg-muted/10 border-b border-border/40">
                    <td colSpan={8} className="p-4 text-left text-xs">
                      <div className="flex flex-col gap-2 pl-12">
                        <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
                          Assignment History Logs:
                        </span>
                        <ul className="list-disc pl-4 text-muted-foreground">
                          {vol.history.map((h, i) => (
                            <li key={i}>{h}</li>
                          ))}
                        </ul>
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// Presentational Component: Details & Dispatch Control Sidebar
interface VolunteerDetailsSidebarProps {
  selectedVolunteer: Volunteer;
  handleAssign: () => void;
  handleAction: (action: string) => void;
  setToastMessage: (msg: string | null) => void;
}
function VolunteerDetailsSidebar({
  selectedVolunteer,
  handleAssign,
  handleAction,
  setToastMessage,
}: VolunteerDetailsSidebarProps) {
  if (!selectedVolunteer) return null;

  return (
    <div className="rounded-2xl border border-border bg-card/65 backdrop-blur-md p-5 shadow-lg flex flex-col justify-between h-fit gap-6 text-left">
      <div>
        <div className="flex items-center gap-2.5 border-b border-border/40 pb-3.5 mb-4">
          <div className="p-2 rounded-xl bg-primary/10 text-primary">
            <Users className="h-4 w-4" />
          </div>
          <div>
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
              SELECTED STAFF
            </span>
            <span className="text-xs font-black text-foreground uppercase mt-0.5 block">
              {selectedVolunteer.name}
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-4 text-xs">
          <div className="flex flex-col">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
              Current Location
            </span>
            <span className="font-bold text-foreground mt-0.5 uppercase">
              {selectedVolunteer.zone}
            </span>
          </div>

          <div className="flex flex-col">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
              Skill Matrix
            </span>
            <div className="flex flex-wrap gap-1 mt-1.5">
              {selectedVolunteer.skills.map((s, i) => (
                <span key={i} className="bg-muted/40 border border-border text-[8px] font-black uppercase text-muted-foreground px-2 py-0.5 rounded">
                  {s}
                </span>
              ))}
            </div>
          </div>

          <div className="flex flex-col">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
              Certifications
            </span>
            <span className="font-bold text-foreground mt-0.5 uppercase">
              {selectedVolunteer.certifications.join(", ")}
            </span>
          </div>

          <div className="flex flex-col">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
              Shift Duration
            </span>
            <span className="font-bold text-foreground mt-0.5">
              {selectedVolunteer.shiftDuration}
            </span>
          </div>

          <div className="flex flex-col">
            <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
              Active Routing Path
            </span>
            <span className="font-bold text-foreground mt-0.5 text-[11px] font-mono">
              {selectedVolunteer.route}
            </span>
          </div>
        </div>
      </div>

      {/* Action Dispatch Buttons */}
      <div className="flex flex-col gap-2.5 border-t border-border/40 pt-5">
        <button
          onClick={handleAssign}
          className="w-full rounded-xl bg-primary text-primary-foreground hover:opacity-90 py-2.5 text-xs font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-opacity"
        >
          <UserCheck className="h-4 w-4" />
          Assign Task
        </button>

        <button
          onClick={() => handleAction("available")}
          className="w-full rounded-xl border border-border bg-muted/20 hover:bg-muted/40 py-2.5 text-xs font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors text-foreground"
        >
          <CheckCircle className="h-4 w-4 text-emerald-400" />
          Mark Available
        </button>

        <button
          onClick={() => handleAction("recall")}
          className="w-full rounded-xl border border-border bg-muted/20 hover:bg-muted/40 py-2.5 text-xs font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors text-foreground"
        >
          <UserX className="h-4 w-4 text-muted-foreground" />
          Recall Shift
        </button>

        <button
          onClick={() => {
            const msg = prompt("Enter message text:");
            if (msg) {
              setToastMessage(`Radio Message sent to ${selectedVolunteer.name}: "${msg}"`);
              setTimeout(() => setToastMessage(null), 3000);
            }
          }}
          className="w-full rounded-xl border border-border bg-muted/20 hover:bg-muted/40 py-2.5 text-xs font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-colors text-foreground"
        >
          <MessageSquare className="h-4 w-4" />
          Send Message
        </button>

        {/* Glowing Emergency Dispatch */}
        <button
          onClick={() => handleAction("emergency")}
          className="w-full rounded-xl bg-destructive text-destructive-foreground hover:opacity-90 py-3 text-xs font-black uppercase tracking-wider flex items-center justify-center gap-1.5 transition-opacity shadow-lg shadow-destructive/10 animate-pulse border border-destructive/20"
        >
          <AlertOctagon className="h-4 w-4" />
          Emergency Dispatch
        </button>
      </div>
    </div>
  );
}

// Presentational Component: Toast Notifications
interface VolunteerToastProps {
  toastMessage: string | null;
}
function VolunteerToast({ toastMessage }: VolunteerToastProps) {
  return (
    <AnimatePresence>
      {toastMessage && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          className="fixed bottom-6 right-6 z-50 rounded-xl border border-primary/30 bg-card/95 backdrop-blur-md px-4 py-3 shadow-xl text-xs font-bold text-primary flex items-center gap-2 uppercase tracking-wide"
        >
          <Sparkles className="h-4 w-4 animate-spin text-primary" />
          {toastMessage}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Main Page Orchestrator Component
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
    <div className="flex flex-col gap-6 text-foreground min-h-[calc(100vh-6rem)] relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-border pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500">
            <Users className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight uppercase">VOLUNTEER INTELLIGENCE CENTER</h1>
            <p className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
              Real-time Operations Workforce Command & Dispatch Console
            </p>
          </div>
        </div>
      </div>

      {/* Top KPIs Row */}
      <VolunteerKpiRow volunteers={volunteers} />

      {/* Main Grid Area */}
      <div className="grid gap-6 lg:grid-cols-4">
        {/* Col 1, 2, 3: Filter & Data Grid */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <VolunteerFilterBar
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            filterTeam={filterTeam}
            setFilterTeam={setFilterTeam}
            filterStatus={filterStatus}
            setFilterStatus={setFilterStatus}
            setToastMessage={setToastMessage}
          />
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

        {/* Col 4: Right Selected Volunteer Details & Dispatch Controls */}
        <VolunteerDetailsSidebar
          selectedVolunteer={selectedVolunteer}
          handleAssign={handleAssign}
          handleAction={handleAction}
          setToastMessage={setToastMessage}
        />
      </div>

      {/* Floating Dynamic Toasts */}
      <VolunteerToast toastMessage={toastMessage} />
    </div>
  );
}
