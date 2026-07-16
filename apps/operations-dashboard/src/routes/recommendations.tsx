import { useEffect, useState, useMemo } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Compass, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { fetchDashboardRecommendations, fetchRecommendationsExplanation, generateAIRecommendations } from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";
import { useWebSocket } from "../providers/WebSocketProvider";
import { useGlobalStore } from "../store/useGlobalStore";

import type { Recommendation } from "../features/recommendations/types";
import { FiltersConsole } from "../features/recommendations/components/FiltersConsole";
import { RecommendationCard } from "../features/recommendations/components/RecommendationCard";
import { ExplanationDrawer } from "../features/recommendations/components/ExplanationDrawer";
import { useRecommendationsFilter } from "../features/recommendations/hooks/useRecommendationsFilter";
import { useRecommendationsExplanation } from "../features/recommendations/hooks/useRecommendationsExplanation";

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

  // Filters application via custom hook
  const filteredItems = useRecommendationsFilter({
    items: items as Recommendation[],
    searchTerm,
    filterPriority,
    filterSeverity,
    filterStatus,
    filterCategory,
  });

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

  // Explanation Drawer details mapping via custom hook
  const explanationDetails = useRecommendationsExplanation({
    selectedRec: selectedRec as Recommendation | null,
    explainData: explainQuery.data,
  });

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
      <FiltersConsole
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        filterPriority={filterPriority}
        setFilterPriority={setFilterPriority}
        filterSeverity={filterSeverity}
        setFilterSeverity={setFilterSeverity}
        filterStatus={filterStatus}
        setFilterStatus={setFilterStatus}
        filterCategory={filterCategory}
        setFilterCategory={setFilterCategory}
        selectedIds={selectedIds}
        handleBulkAction={handleBulkAction}
      />

      {/* Cards list grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredItems.length === 0 ? (
          <div className="col-span-full rounded-2xl border border-dashed border-border bg-card/20 p-12 text-center text-xs text-muted-foreground font-semibold">
            No recommendations match your selected filters.
          </div>
        ) : (
          filteredItems.map((rec) => (
            <RecommendationCard
              key={rec.id}
              rec={rec}
              isSelected={!!selectedIds[rec.id]}
              onSelectedChange={(checked) => {
                setSelectedIds((prev) => ({ ...prev, [rec.id]: checked }));
              }}
              onExplainRequest={() => {
                setSelectedRec(rec);
                setDrawerOpen(true);
              }}
              onSimulateRequest={() => handleStatusChange(rec.id, "simulated")}
              onDelegateRequest={() => handleStatusChange(rec.id, "delegated")}
              onStatusChange={(newStatus) => handleStatusChange(rec.id, newStatus)}
            />
          ))
        )}
      </div>

      {/* Slideout Side Explanation Drawer */}
      <ExplanationDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        selectedRec={selectedRec as Recommendation | null}
        explanationDetails={explanationDetails}
      />

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
