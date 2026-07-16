import type { RecommendationItem } from "../../services/api";

export interface Recommendation extends RecommendationItem {
  severity?: string;
  impact?: string;
  resolutionTime?: string;
  resources?: string[];
  timestamp?: string;
}

export interface ExplanationDetails {
  why: string;
  data_considered: string[];
  business_rules: string[];
  alternatives: string[];
  confidence: number;
  risks: string[];
}
