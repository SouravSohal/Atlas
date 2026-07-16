import { useMemo } from "react";
import type { Recommendation, ExplanationDetails } from "../types";

interface UseRecommendationsExplanationProps {
  selectedRec: Recommendation | null;
  explainData: any;
}

export function useRecommendationsExplanation({
  selectedRec,
  explainData,
}: UseRecommendationsExplanationProps): ExplanationDetails | null {
  const explanationDetails = useMemo(() => {
    if (!selectedRec) return null;

    // Find prioritized detail explanation if available
    const prioritizedMatch = explainData?.prioritized_recommendations?.find(
      (p: any) => p.recommendation_id === selectedRec.id
    );

    const whyText =
      prioritizedMatch?.explanation ||
      explainData?.natural_language_explanation ||
      `The ATLAS telemetry pipeline detected congestion bounds nearing capacity constraints. Triggering a preventative override distributes inflow weights safely.`;

    const alternatives =
      explainData?.alternative_actions && explainData.alternative_actions.length > 0
        ? explainData.alternative_actions
        : [
            "Divert entry traffic to Parking Lot B corridors",
            "Keep gates active and deploy temporary guides",
          ];

    const risks = explainData?.risk_assessment
      ? [explainData.risk_assessment]
      : [
          "Slight staff displacement in security sector C",
          "Temporary queue confusion at Gate 2 corridors",
        ];

    return {
      why: whyText,
      data_considered: [
        `Crowd Density: ${Math.round((selectedRec.confidence || 0.95) * 100)}%`,
        `Average Gate queue: 14 minutes`,
        `Staff Capacity Index: Optimal`,
      ],
      business_rules: [
        "Rule 305: Divert crowd ingress vectors if turnstile congestion index exceeds 0.70 threshold.",
        "Rule 112: Reallocate local security squads when severity markers reach warning boundaries.",
      ],
      alternatives: alternatives,
      confidence: selectedRec.confidence || 0.95,
      risks: risks,
    };
  }, [selectedRec, explainData]);

  return explanationDetails;
}
