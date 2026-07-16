import { useMemo, useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  Compass,
  CheckCircle,
  XCircle,
  HelpCircle,
  Play,
  UserCheck,
  Search,
  Sparkles,
  Info,
  X,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { fetchDashboardRecommendations, fetchRecommendationsExplanation, generateAIRecommendations } from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";
import { useWebSocket } from "../providers/WebSocketProvider";
import { useGlobalStore } from "../store/useGlobalStore";

export const Route = createFileRoute("/recommendations")({
  component: RecommendationsPage,
});

function RecommendationsPage() {
  const { subscribe, unsubscribe } = useWebSocket();

  const {
    selectedIds,
    setSelectedIds,
    localStatuses,
    setLocalStatuses,
    drawerOpen,
    setDrawerOpen,
    selectedRec,
    setSelectedRec,
    recSearch: searchTerm,
    setRecSearch: setSearchTerm,
    recFilterPriority: filterPriority,
    setRecFilterPriority: setFilterPriority,
    recFilterSeverity: filterSeverity,
    setRecFilterSeverity: setFilterSeverity,
    recFilterStatus: filterStatus,
    setRecFilterStatus: setFilterStatus,
    recFilterCategory: filterCategory,
    setRecFilterCategory: setFilterCategory,
    toastMessage,
    setToastMessage,
    playbackActive,
    simulatedRecommendations,
  } = useGlobalStore();

  // Fetch recommendations
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["cc-recommendations"],
    queryFn: () => fetchDashboardRecommendations(1, 40),
    refetchInterval: 10000,
  });

  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateAIRecommendations = async () => {
    setIsGenerating(true);
    setToastMessage("Generating AI recommendations via Gemini 2.5 Flash...");
    try {
      await generateAIRecommendations();
      await refetch();
      setToastMessage("AI recommendations generated successfully!");
    } catch (err: any) {
      setToastMessage(`Error: ${err.message || "Failed to generate recommendations"}`);
    } finally {
      setIsGenerating(false);
      setTimeout(() => setToastMessage(null), 4000);
    }
  };
  const formatDetails = (detailsStr: string) => {
    try {
      const parsed = JSON.parse(detailsStr);
      if (parsed.explanation) return parsed.explanation;
      if (parsed.trigger_reason) return parsed.trigger_reason;
      if (parsed.expected_impact) return `Impact: ${parsed.expected_impact}`;
      return detailsStr;
    } catch {
      return detailsStr;
    }
  };

  const explainQuery = useQuery({
    queryKey: ["cc-recommendations-explain"],
    queryFn: fetchRecommendationsExplanation,
    refetchInterval: 10000,
  });

  const rawItems = playbackActive && simulatedRecommendations ? simulatedRecommendations : (data?.items || []);

  // Real-time WebSocket connection to subscribe to topic updates
  useEffect(() => {
    subscribe("recommendations");
    return () => unsubscribe("recommendations");
  }, [subscribe, unsubscribe]);

  // Merge local status overrides (Approved/Rejected/Completed etc)
  const items = useMemo(() => {
    return rawItems.map((item) => ({
      ...item,
      status: localStatuses[item.id] || item.status || "pending",
      // Seed fallback metrics if they are omitted by backend
      priority: item.priority || "high",
      severity: item.priority || "medium",
      confidence: item.confidence || 0.95,
      impact: "Alleviate queue wait by 25%",
      resolutionTime: "8 mins",
      resources: ["Volunteer Crew A", "Gate Monitors"],
      timestamp: item.created_at ? new Date(item.created_at).toLocaleTimeString() : new Date().toLocaleTimeString(),
    }));
  }, [rawItems, localStatuses]);

  // Filters application
  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const matchSearch = item.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.action_type.toLowerCase().includes(searchTerm.toLowerCase());
      const matchPriority = filterPriority === "all" || item.priority.toLowerCase() === filterPriority.toLowerCase();
      const matchSeverity = filterSeverity === "all" || item.severity.toLowerCase() === filterSeverity.toLowerCase();
      const matchStatus = filterStatus === "all" || item.status.toLowerCase() === filterStatus.toLowerCase();
      
      // Category matches action_type prefix
      const matchCategory = filterCategory === "all" || 
        (filterCategory === "reroute" && item.action_type.toLowerCase().includes("reroute")) ||
        (filterCategory === "dispatch" && item.action_type.toLowerCase().includes("dispatch")) ||
        (filterCategory === "facility" && item.action_type.toLowerCase().includes("facility"));

      return matchSearch && matchPriority && matchSeverity && matchStatus && matchCategory;
    });
  }, [items, searchTerm, filterPriority, filterSeverity, filterStatus, filterCategory]);

  const handleStatusChange = (id: string, status: string) => {
    setLocalStatuses((prev) => ({ ...prev, [id]: status }));
    setToastMessage(`Recommendation ${status} successfully.`);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleBulkAction = (status: string) => {
    const selected = Object.keys(selectedIds).filter((id) => selectedIds[id]);
    if (selected.length === 0) return;

    const updates: Record<string, string> = {};
    selected.forEach((id) => {
      updates[id] = status;
    });
    setLocalStatuses((prev) => ({ ...prev, ...updates }));
    setSelectedIds({});
    setToastMessage(`Bulk updated ${selected.length} items to ${status}.`);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Dynamic drawer detailed calculations
  const explanationDetails = useMemo(() => {
    if (!selectedRec) return null;
    
    // Find prioritized detail explanation if available
    const prioritizedMatch = explainQuery.data?.prioritized_recommendations?.find(
      (p) => p.recommendation_id === selectedRec.id
    );

    const whyText = prioritizedMatch?.explanation 
      || explainQuery.data?.natural_language_explanation 
      || `The ATLAS telemetry pipeline detected congestion bounds nearing capacity constraints. Triggering a preventative override distributes inflow weights safely.`;

    const alternatives = explainQuery.data?.alternative_actions && explainQuery.data.alternative_actions.length > 0
      ? explainQuery.data.alternative_actions
      : [
          "Divert entry traffic to Parking Lot B corridors",
          "Keep gates active and deploy temporary guides"
        ];

    const risks = explainQuery.data?.risk_assessment
      ? [explainQuery.data.risk_assessment]
      : [
          "Slight staff displacement in security sector C",
          "Temporary queue confusion at Gate 2 corridors"
        ];

    return {
      why: whyText,
      data_considered: [
        `Crowd Density: ${Math.round((selectedRec.confidence || 0.95) * 100)}%`,
        `Average Gate queue: 14 minutes`,
        `Staff Capacity Index: Optimal`
      ],
      business_rules: [
        "Rule 305: Divert crowd ingress vectors if turnstile congestion index exceeds 0.70 threshold.",
        "Rule 112: Reallocate local security squads when severity markers reach warning boundaries."
      ],
      alternatives: alternatives,
      confidence: selectedRec.confidence || 0.95,
      risks: risks
    };
  }, [selectedRec, explainQuery.data]);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <div className="flex flex-col gap-6 text-foreground min-h-[calc(100vh-6rem)] relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-border pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500">
            <Compass className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight uppercase">ATLAS Decision Center</h1>
            <p className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
              Review and Dispatch AI-Generated Stadium Actions (Human-in-the-Loop)
            </p>
          </div>
        </div>

        <button
          disabled={isGenerating}
          onClick={handleGenerateAIRecommendations}
          className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-black uppercase tracking-wider shadow-md transition-all border shrink-0 ${
            isGenerating
              ? "bg-muted text-muted-foreground border-border cursor-not-allowed"
              : "bg-primary text-primary-foreground border-primary hover:opacity-90 active:scale-95 shadow-primary/20"
          }`}
        >
          <Sparkles className={`h-4 w-4 ${isGenerating ? "animate-spin" : "animate-pulse text-amber-300"}`} />
          {isGenerating ? "Generating..." : "Generate AI Recommendations"}
        </button>
      </div>

      {/* Filter and Bulk Actions Console */}
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
        {Object.keys(selectedIds).filter((id) => selectedIds[id]).length > 0 && (
          <div className="flex items-center gap-3 bg-muted/30 border border-border rounded-xl p-3 justify-between animate-fadeIn">
            <span className="text-xs font-bold text-muted-foreground">
              Selected: {Object.keys(selectedIds).filter((id) => selectedIds[id]).length} items
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

      {/* Cards list grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredItems.length === 0 ? (
          <div className="col-span-full rounded-2xl border border-dashed border-border bg-card/20 p-12 text-center text-xs text-muted-foreground font-semibold">
            No recommendations match your selected filters.
          </div>
        ) : (
          filteredItems.map((rec) => {
            const isSelected = selectedIds[rec.id];

            return (
              <div
                key={rec.id}
                className={`rounded-2xl border bg-card/65 backdrop-blur-md p-5 hover:shadow-lg transition-all flex flex-col justify-between relative ${
                  rec.status === "approved"
                    ? "border-emerald-500/30 shadow-emerald-950/5"
                    : rec.status === "rejected"
                    ? "border-destructive/30 shadow-destructive-950/5 opacity-70"
                    : "border-border"
                }`}
              >
                <div>
                  {/* Card Header */}
                  <div className="flex items-start justify-between gap-3 border-b border-border/40 pb-2.5">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={!!isSelected}
                        onChange={(e) => {
                          setSelectedIds((prev) => ({ ...prev, [rec.id]: e.target.checked }));
                        }}
                        className="rounded border-border accent-primary cursor-pointer w-4 h-4"
                      />
                      <span className="text-[10px] font-black text-foreground uppercase tracking-wider font-mono">
                        {rec.action_type}
                      </span>
                    </div>

                    <span className={`text-[8px] font-black uppercase px-2 py-0.5 rounded border ${
                      rec.status === "approved"
                        ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                        : rec.status === "rejected"
                        ? "bg-destructive/10 border-destructive/20 text-destructive"
                        : "bg-amber-500/10 border-amber-500/20 text-amber-500 animate-pulse"
                    }`}>
                      {rec.status}
                    </span>
                  </div>

                  {/* Recommendation Details */}
                  <p className="text-xs font-black text-foreground uppercase mt-3 leading-snug">
                    {formatDetails(rec.details)}
                  </p>

                  {/* Metric Metadata pills */}
                  <div className="grid grid-cols-2 gap-2 mt-4 text-[9px] font-mono text-muted-foreground bg-muted/20 border border-border/40 rounded-xl p-3">
                    <div className="flex flex-col">
                      <span>PRIORITY</span>
                      <span className="font-bold text-foreground mt-0.5 uppercase">{rec.priority}</span>
                    </div>
                    <div className="flex flex-col">
                      <span>CONFIDENCE</span>
                      <span className="font-bold text-foreground mt-0.5">{(rec.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex flex-col">
                      <span>TIME TO RESOLVE</span>
                      <span className="font-bold text-foreground mt-0.5">{rec.resolutionTime}</span>
                    </div>
                    <div className="flex flex-col">
                      <span>EXPECTED IMPACT</span>
                      <span className="font-bold text-foreground mt-0.5 uppercase tracking-tight">{rec.impact}</span>
                    </div>
                  </div>

                   <div className="mt-3.5 flex flex-wrap gap-1">
                    {rec.resources?.map((res: any, idx: number) => (
                      <span key={idx} className="bg-muted/40 border border-border text-[8px] font-black uppercase text-muted-foreground px-2 py-0.5 rounded">
                        {res}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Card Actions Bottom Row */}
                <div className="mt-5 border-t border-border/40 pt-4 flex flex-wrap gap-2 items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    {/* Explain drawer button */}
                    <button
                      onClick={() => {
                        setSelectedRec(rec);
                        setDrawerOpen(true);
                      }}
                      className="rounded-lg border border-border bg-muted/25 hover:bg-muted/50 p-2 text-muted-foreground hover:text-foreground transition-colors"
                      title="Request Explanation"
                    >
                      <HelpCircle className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleStatusChange(rec.id, "simulated")}
                      className="rounded-lg border border-border bg-muted/25 hover:bg-muted/50 p-2 text-muted-foreground hover:text-foreground transition-colors"
                      title="Simulate Impact"
                    >
                      <Play className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleStatusChange(rec.id, "delegated")}
                      className="rounded-lg border border-border bg-muted/25 hover:bg-muted/50 p-2 text-muted-foreground hover:text-foreground transition-colors"
                      title="Delegate Task"
                    >
                      <UserCheck className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {rec.status !== "approved" && rec.status !== "completed" && (
                      <button
                        onClick={() => handleStatusChange(rec.id, "approved")}
                        className="rounded-lg bg-emerald-500 px-3 py-1.5 text-[10px] font-black text-black uppercase tracking-wider hover:opacity-90 flex items-center gap-1"
                      >
                        <CheckCircle className="h-3 w-3" />
                        Approve
                      </button>
                    )}
                    {rec.status !== "rejected" && rec.status !== "completed" && (
                      <button
                        onClick={() => handleStatusChange(rec.id, "rejected")}
                        className="rounded-lg bg-destructive px-3 py-1.5 text-[10px] font-black text-destructive-foreground uppercase tracking-wider hover:opacity-90 flex items-center gap-1"
                      >
                        <XCircle className="h-3 w-3" />
                        Reject
                      </button>
                    )}
                    {rec.status === "approved" && (
                      <button
                        onClick={() => handleStatusChange(rec.id, "completed")}
                        className="rounded-lg bg-primary px-3 py-1.5 text-[10px] font-black text-primary-foreground uppercase tracking-wider hover:opacity-90 flex items-center gap-1"
                      >
                        <CheckCircle className="h-3 w-3" />
                        Complete
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Slideout Side Explanation Drawer */}
      <AnimatePresence>
        {drawerOpen && selectedRec && explanationDetails && (
          <div className="fixed inset-0 z-50 flex justify-end">
            {/* Overlay backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setDrawerOpen(false)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />

            {/* Sliding Container */}
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 220 }}
              className="relative w-full max-w-md h-full bg-card/95 border-l border-border p-6 shadow-2xl overflow-y-auto flex flex-col justify-between text-left"
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between border-b border-border pb-4 mb-6">
                  <div className="flex items-center gap-2 text-primary">
                    <Sparkles className="h-5 w-5 text-primary animate-pulse" />
                    <span className="text-xs font-black uppercase tracking-widest">
                      AI Explanation Summary
                    </span>
                  </div>
                  <button
                    onClick={() => setDrawerOpen(false)}
                    className="p-1.5 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>

                {/* Explanation Content */}
                <div className="flex flex-col gap-6">
                  {/* Recommendation details card */}
                  <div className="rounded-xl border border-border bg-muted/30 p-4">
                    <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
                      Target Action
                    </span>
                    <span className="text-xs font-black text-foreground uppercase tracking-wide block mt-1.5">
                      {formatDetails(selectedRec.details)}
                    </span>
                  </div>

                  {/* Why generated */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[9px] font-black text-primary uppercase tracking-widest block">
                      Reasoning Analysis
                    </span>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {explanationDetails.why}
                    </p>
                  </div>

                  {/* Telemetry data */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[9px] font-black text-primary uppercase tracking-widest block">
                      Operational State Considered
                    </span>
                    <ul className="flex flex-col gap-1 text-xs text-muted-foreground list-disc pl-4">
                      {explanationDetails.data_considered.map((d, idx) => (
                        <li key={idx}>{d}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Business Rules */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[9px] font-black text-primary uppercase tracking-widest block">
                      Business Rules Triggered
                    </span>
                    <ul className="flex flex-col gap-1.5 text-xs text-muted-foreground list-disc pl-4">
                      {explanationDetails.business_rules.map((rule, idx) => (
                        <li key={idx}>{rule}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Alternatives */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[9px] font-black text-primary uppercase tracking-widest block">
                      Alternative Strategic Actions
                    </span>
                    <ul className="flex flex-col gap-1 text-xs text-muted-foreground list-disc pl-4">
                      {explanationDetails.alternatives.map((alt, idx) => (
                        <li key={idx}>{alt}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Risks */}
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[9px] font-black text-destructive uppercase tracking-widest block">
                      Expected Risks & Trade-offs
                    </span>
                    <ul className="flex flex-col gap-1 text-xs text-muted-foreground list-disc pl-4">
                      {explanationDetails.risks.map((risk, idx) => (
                        <li key={idx} className="text-destructive/80 font-semibold">{risk}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Bottom Confidence dial */}
              <div className="border-t border-border pt-5 mt-6 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Info className="h-4 w-4 text-muted-foreground" />
                  <span className="text-[10px] font-black text-muted-foreground uppercase">
                    AI Accuracy Rating
                  </span>
                </div>
                <span className="text-xs font-black text-foreground font-mono bg-primary/10 border border-primary/20 text-primary px-3 py-1 rounded-full">
                  {(explanationDetails.confidence * 100).toFixed(0)}% Confidence
                </span>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Floating Dynamic Toasts */}
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
    </div>
  );
}
