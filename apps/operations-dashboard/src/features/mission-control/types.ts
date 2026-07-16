import type { Node } from "@xyflow/react";

export type StadiumNodeData = {
  label: string;
  value: string;
  status: "stable" | "warning" | "critical";
  type: string;
  isFocused?: boolean;
  health: number;
  density: number;
  queue: number;
  capacity: number;
  alerts: number;
  recs: number;
  resources: string;
  predictionOverlay?: any;
};

export type StadiumNode = Node<StadiumNodeData, "stadiumNode">;
