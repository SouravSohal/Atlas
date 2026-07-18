import { useState, useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchDashboardOverview } from "../../../services/api";
import { useWebSocket } from "../../../providers/WebSocketProvider";
import { useGlobalStore } from "../../../store/useGlobalStore";

export function useVolunteersState() {
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
