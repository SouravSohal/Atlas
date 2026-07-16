import { useMemo } from "react";
import type { Recommendation } from "../types";

interface UseRecommendationsFilterProps {
  items: Recommendation[];
  searchTerm: string;
  filterPriority: string;
  filterSeverity: string;
  filterStatus: string;
  filterCategory: string;
}

export function useRecommendationsFilter({
  items,
  searchTerm,
  filterPriority,
  filterSeverity,
  filterStatus,
  filterCategory,
}: UseRecommendationsFilterProps) {
  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const matchSearch =
        item.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.action_type.toLowerCase().includes(searchTerm.toLowerCase());
      const matchPriority =
        filterPriority === "all" ||
        item.priority.toLowerCase() === filterPriority.toLowerCase();
      const matchSeverity =
        filterSeverity === "all" ||
        (item.severity || "").toLowerCase() === filterSeverity.toLowerCase();
      const matchStatus =
        filterStatus === "all" ||
        item.status.toLowerCase() === filterStatus.toLowerCase();

      // Category matches action_type prefix
      const matchCategory =
        filterCategory === "all" ||
        (filterCategory === "reroute" &&
          item.action_type.toLowerCase().includes("reroute")) ||
        (filterCategory === "dispatch" &&
          item.action_type.toLowerCase().includes("dispatch")) ||
        (filterCategory === "facility" &&
          item.action_type.toLowerCase().includes("facility"));

      return matchSearch && matchPriority && matchSeverity && matchStatus && matchCategory;
    });
  }, [items, searchTerm, filterPriority, filterSeverity, filterStatus, filterCategory]);

  return filteredItems;
}
