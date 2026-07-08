import { useState, useMemo, useEffect, useRef } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
} from "@xyflow/react";
import type { Node, Edge, NodeProps } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  ShieldCheck,
  AlertTriangle,
  Users,
  Brain,
  Clock,
  Activity,
  Sparkles,
  Send,
  CheckCircle,
  Zap,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import {
  fetchDashboardOverview,
  fetchDashboardIncidents,
  fetchDashboardRecommendations,
  fetchOperationalState,
  createIncident,
  updateIncident,
} from "../services/api";
import { LoadingScreen } from "../components/LoadingScreen";

export const Route = createFileRoute("/")({
  component: MissionControlPage,
});

type StadiumNodeData = {
  label: string;
  value: string;
  status: "stable" | "warning" | "critical";
  type: string;
  isFocused?: boolean;
};

type StadiumNode = Node<StadiumNodeData, "stadiumNode">;

// Custom React flow nodes configuration
const CustomNode = ({ data }: NodeProps<StadiumNode>) => {
  const borderColors = {
    stable: data.isFocused ? "border-amber-400 ring-2 ring-amber-400/50" : "border-emerald-500/50 shadow-emerald-500/5",
    warning: data.isFocused ? "border-amber-400 ring-2 ring-amber-400/50" : "border-amber-500/50 shadow-amber-500/5",
    critical: data.isFocused ? "border-amber-400 ring-2 ring-amber-400/50" : "border-destructive/60 shadow-destructive/5",
  };

  const bgColors = {
    stable: "bg-emerald-500/5",
    warning: "bg-amber-500/5",
    critical: "bg-destructive/5 animate-pulse",
  };

  const indicatorColors = {
    stable: "bg-emerald-500",
    warning: "bg-amber-500",
    critical: "bg-destructive",
  };

  return (
    <motion.div
      animate={data.isFocused ? { scale: [1, 1.05, 1], y: [0, -3, 0] } : {}}
      transition={{ repeat: Infinity, duration: 1.5 }}
      className={`rounded-xl border ${borderColors[data.status]} ${bgColors[data.status]} p-3 text-left w-40 backdrop-blur-md shadow-lg relative`}
    >
      {data.isFocused && (
        <span className="absolute -top-2.5 -right-2 bg-amber-500 text-black text-[7px] font-black px-1 py-0.5 rounded border border-black shadow uppercase animate-pulse">
          🎯 focus
        </span>
      )}
      <Handle type="target" position={Position.Left} className="w-1.5 h-1.5 bg-border" />
      <div className="flex items-center gap-1.5">
        <span className={`h-1.5 w-1.5 rounded-full ${indicatorColors[data.status]}`} />
        <span className="text-[10px] font-black tracking-wide text-foreground uppercase">{data.label}</span>
      </div>
      <div className="mt-1">
        <span className="text-xs font-bold text-muted-foreground block">{data.type}</span>
        <span className="text-xs font-black text-foreground mt-0.5 block">{data.value}</span>
      </div>
      <Handle type="source" position={Position.Right} className="w-1.5 h-1.5 bg-border" />
    </motion.div>
  );
};

const nodeTypes = {
  stadiumNode: CustomNode,
};

// Playback scenario database definitions
const SCENARIO_STEPS: Record<string, any[]> = {
  "Crowd Surge": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }, { density: 0.35, queue_waiting_minutes: 3 }],
      incidents: [],
      recs: [],
      summary: "Stadium ingress gates reporting normal spectator arrivals. Staff deployed at check-points.",
      notification: "System initialized. Operations nominal."
    },
    {
      overview: { stadium_health: 0.92, active_incidents_count: 0, average_crowd_density: 0.65, allocated_volunteers_count: 20 },
      zones: [{ density: 0.75, queue_waiting_minutes: 12 }, { density: 0.50, queue_waiting_minutes: 6 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [{ id: "rec-1", action_type: "dispatch", priority: "medium", details: "Deploy 2 additional volunteers to Gate 1 check-points.", age: 60000 }],
      summary: "Spectator density rising rapidly at Gate 1 turnstiles. Queue wait time now at 12 minutes.",
      notification: "Warning: High crowd density detected at Gate 1 Sector."
    },
    {
      overview: { stadium_health: 0.75, active_incidents_count: 1, average_crowd_density: 0.85, allocated_volunteers_count: 20 },
      zones: [{ density: 0.95, queue_waiting_minutes: 25 }, { density: 0.65, queue_waiting_minutes: 15 }, { density: 0.45, queue_waiting_minutes: 5 }],
      incidents: [{ id: "inc-1", incident_type: "crowd_control", severity: "high", description: "Ingress bottleneck alert at Gate 1 check-points.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [
        { id: "rec-1", action_type: "dispatch", priority: "medium", details: "Deploy 2 additional volunteers to Gate 1 check-points.", age: 120000 },
        { id: "rec-2", action_type: "reroute", priority: "high", details: "Reroute incoming flows from Gate 1 to Gate 2.", age: 60000 }
      ],
      summary: "Ingress bottleneck alert at Gate 1 turnstiles. System recommends active flow rerouting.",
      notification: "High Alert: Sector congestion bottleneck active."
    },
    {
      overview: { stadium_health: 0.70, active_incidents_count: 1, average_crowd_density: 0.90, allocated_volunteers_count: 24 },
      zones: [{ density: 0.98, queue_waiting_minutes: 32 }, { density: 0.70, queue_waiting_minutes: 18 }, { density: 0.50, queue_waiting_minutes: 6 }],
      incidents: [{ id: "inc-1", incident_type: "crowd_control", severity: "high", description: "Ingress bottleneck alert at Gate 1 check-points.", resolved: false, created_at: new Date().toISOString(), age: 180000 }],
      recs: [
        { id: "rec-2", action_type: "reroute", priority: "high", details: "Reroute incoming flows from Gate 1 to Gate 2.", age: 120000 }
      ],
      summary: "Rerouting active. Volunteer teams are directing crowd flow to empty Gate 2 corridors.",
      notification: "Rerouting protocol: Gate 2 backup ingress channels active."
    },
    {
      overview: { stadium_health: 0.95, active_incidents_count: 0, average_crowd_density: 0.55, allocated_volunteers_count: 24 },
      zones: [{ density: 0.50, queue_waiting_minutes: 6 }, { density: 0.55, queue_waiting_minutes: 8 }, { density: 0.45, queue_waiting_minutes: 5 }],
      incidents: [],
      recs: [],
      summary: "Bottleneck dispersed successfully. Ingress flow stabilized under recommended routing.",
      notification: "Clear: Gate 1 turnstiles returned to safe operational levels."
    }
  ],
  "Medical Emergency": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Operations normal. Medical responder units placed on standby at Post Alpha.",
      notification: "Medical status check complete. Ready."
    },
    {
      overview: { stadium_health: 0.83, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.55, queue_waiting_minutes: 8 }],
      incidents: [{ id: "inc-2", incident_type: "medical", severity: "critical", description: "Spectator collapse reported in Section 104. Dispatching post units.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-3", action_type: "dispatch", priority: "high", details: "Dispatch First-Aid Team Alpha to Section 104.", age: 60000 }],
      summary: "Spectator collapse reported in Section 104. First Aid responders dispatched.",
      notification: "Emergency: Medical alert registered in Section 104."
    },
    {
      overview: { stadium_health: 0.83, active_incidents_count: 1, average_crowd_density: 0.50, allocated_volunteers_count: 22 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.60, queue_waiting_minutes: 10 }],
      incidents: [{ id: "inc-2", incident_type: "medical", severity: "critical", description: "Spectator collapse reported in Section 104. Dispatching post units.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [{ id: "rec-4", action_type: "reroute", priority: "medium", details: "Clear security corridor near Section 104 exit.", age: 60000 }],
      summary: "Responders arrived on scene. Administering first aid. Corridor cleared for transit.",
      notification: "Update: Responders arrived. Scene secured."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 22 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Patient evacuated and stable. Incident resolved. Corridor reopened.",
      notification: "Resolve: Emergency cleared. Sector nominal."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Medical responders returned to standby. Ready.",
      notification: "System initialized. Standby."
    }
  ],
  "Gate Closure": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "All gates active and operating. Flow rate nominal.",
      notification: "All check-points online."
    },
    {
      overview: { stadium_health: 0.83, active_incidents_count: 1, average_crowd_density: 0.50, allocated_volunteers_count: 20 },
      zones: [{ density: 0.0, queue_waiting_minutes: 0 }, { density: 0.65, queue_waiting_minutes: 12 }],
      incidents: [{ id: "inc-3", incident_type: "facility", severity: "high", description: "Gate 1 Turnstile malfunction. Structural block.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-5", action_type: "dispatch", priority: "medium", details: "Dispatch maintenance engineers to Gate 1.", age: 60000 }],
      summary: "Turnstile malfunction at Gate 1. Ingress flow halted. Diverting spectators.",
      notification: "Warning: Gate 1 turnstile malfunction."
    },
    {
      overview: { stadium_health: 0.65, active_incidents_count: 1, average_crowd_density: 0.70, allocated_volunteers_count: 20 },
      zones: [{ density: 0.0, queue_waiting_minutes: 0 }, { density: 0.90, queue_waiting_minutes: 25 }],
      incidents: [{ id: "inc-3", incident_type: "facility", severity: "high", description: "Gate 1 Turnstile malfunction. Structural block.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [
        { id: "rec-5", action_type: "dispatch", priority: "medium", details: "Dispatch maintenance engineers to Gate 1.", age: 120000 },
        { id: "rec-6", action_type: "reroute", priority: "high", details: "Divert crowd flow to Gate 2.", age: 60000 }
      ],
      summary: "Engineers on site. Spectators diverted. Gate 2 experiencing heavy load.",
      notification: "Alert: Gate 2 queue times rising."
    },
    {
      overview: { stadium_health: 0.95, active_incidents_count: 0, average_crowd_density: 0.55, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 6 }, { density: 0.55, queue_waiting_minutes: 8 }],
      incidents: [],
      recs: [],
      summary: "Turnstile repaired. Gate 1 reopened. Flow rates normalized.",
      notification: "Clear: Gate 1 turnstile repaired."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Gate operations returned to default presets.",
      notification: "System initialized. Normal."
    }
  ],
  "Heavy Rain": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Weather forecast: Clear sky operations.",
      notification: "System initialized."
    },
    {
      overview: { stadium_health: 0.93, active_incidents_count: 0, average_crowd_density: 0.55, allocated_volunteers_count: 20 },
      zones: [{ density: 0.55, queue_waiting_minutes: 10 }, { density: 0.50, queue_waiting_minutes: 8 }],
      incidents: [],
      recs: [{ id: "rec-7", action_type: "dispatch", priority: "medium", details: "Distribute rain covers and clear open plaza paths.", age: 60000 }],
      summary: "Rain initiated. Open plaza areas cleared. Queue speeds slowing down.",
      notification: "Warning: Rain shower starting."
    },
    {
      overview: { stadium_health: 0.88, active_incidents_count: 0, average_crowd_density: 0.65, allocated_volunteers_count: 20 },
      zones: [{ density: 0.65, queue_waiting_minutes: 15 }, { density: 0.60, queue_waiting_minutes: 12 }],
      incidents: [],
      recs: [{ id: "rec-8", action_type: "reroute", priority: "high", details: "Evacuate open parking lots to covered corridors.", age: 60000 }],
      summary: "Spectators moving to covered sectors. Plaza density rising.",
      notification: "Alert: Spectators seeking cover."
    },
    {
      overview: { stadium_health: 0.95, active_incidents_count: 0, average_crowd_density: 0.55, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 6 }, { density: 0.50, queue_waiting_minutes: 7 }],
      incidents: [],
      recs: [],
      summary: "Rain cleared. Operations returning to default layout.",
      notification: "Clear: Rain stopped."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Clear sky operations restored.",
      notification: "System initialized. Normal."
    }
  ],
  "Power Failure": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Power grid stable. All systems operating on main source.",
      notification: "Power systems normal."
    },
    {
      overview: { stadium_health: 0.68, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 15 }, { density: 0.50, queue_waiting_minutes: 14 }],
      incidents: [{ id: "inc-4", incident_type: "facility", severity: "critical", description: "Food Plaza sector power grid blackout.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-9", action_type: "dispatch", priority: "critical", details: "Dispatch emergency engineering crew and activate backup generator.", age: 60000 }],
      summary: "Power outage in Food Plaza sector. Backup generators initiated.",
      notification: "Critical: Food Plaza blackout reported."
    },
    {
      overview: { stadium_health: 0.78, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 22 },
      zones: [{ density: 0.45, queue_waiting_minutes: 10 }, { density: 0.45, queue_waiting_minutes: 8 }],
      incidents: [{ id: "inc-4", incident_type: "facility", severity: "critical", description: "Food Plaza sector power grid blackout.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [{ id: "rec-10", action_type: "dispatch", priority: "medium", details: "Verify main system security loops.", age: 60000 }],
      summary: "Engineers working on restoration. Backup power keeping systems active.",
      notification: "Update: Engineers on scene. Backup power active."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 22 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Main grid restored. Blackout cleared.",
      notification: "Clear: Power restored to Food Plaza."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Operations returned to default grid source.",
      notification: "System initialized. Grid normal."
    }
  ],
  "VIP Arrival": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Gate corridors operating on default ingress flow.",
      notification: "System initialized."
    },
    {
      overview: { stadium_health: 0.93, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 10 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [{ id: "rec-11", action_type: "dispatch", priority: "medium", details: "Secure Gate 2 arrival corridor.", age: 60000 }],
      summary: "VIP motorcade approaching Gate 2. Corridor secure loops initiated.",
      notification: "VIP Warning: Motorcade approaching."
    },
    {
      overview: { stadium_health: 0.88, active_incidents_count: 0, average_crowd_density: 0.50, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 15 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [{ id: "rec-12", action_type: "reroute", priority: "high", details: "Divert public flow from Gate 2 to Gate 1.", age: 60000 }],
      summary: "VIP arrival corridor secured. Public flow diverted to Gate 1.",
      notification: "VIP Alert: Ingress diversion active."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "VIP transit complete. Gate 2 corridors returned to normal.",
      notification: "Clear: VIP escort finished."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "VIP transit completed. Operations returned to default.",
      notification: "System initialized. Normal."
    }
  ],
  "Lost Child": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Security patrols reporting all clear at Sections 200-220.",
      notification: "System initialized. Security nominal."
    },
    {
      overview: { stadium_health: 0.88, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.50, queue_waiting_minutes: 6 }],
      incidents: [{ id: "inc-5", incident_type: "security", severity: "medium", description: "7-year-old child separated from guardians near Section 208.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-13", action_type: "dispatch", priority: "high", details: "Deploy Gate 2 volunteers to support perimeter search.", age: 60000 }],
      summary: "Lost child reported near Section 208. Dispatching nearest search volunteers.",
      notification: "Warning: Lost child alert in Section 208."
    },
    {
      overview: { stadium_health: 0.85, active_incidents_count: 1, average_crowd_density: 0.45, allocated_volunteers_count: 24 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.45, queue_waiting_minutes: 5 }],
      incidents: [{ id: "inc-5", incident_type: "security", severity: "medium", description: "7-year-old child separated from guardians near Section 208.", resolved: false, created_at: new Date().toISOString(), age: 120000 }],
      recs: [{ id: "rec-14", action_type: "dispatch", priority: "medium", details: "Broadcast alert description to exit gate turnstiles.", age: 60000 }],
      summary: "Search in progress. Security checkpoints verified. Parent matched details.",
      notification: "Update: Security perimeter sweep in progress."
    },
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 24 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Child reunited with guardians. Search stood down.",
      notification: "Clear: Family reunited successfully."
    }
  ],
  "Match End": [
    {
      overview: { stadium_health: 0.98, active_incidents_count: 0, average_crowd_density: 0.45, allocated_volunteers_count: 20 },
      zones: [{ density: 0.45, queue_waiting_minutes: 5 }, { density: 0.40, queue_waiting_minutes: 4 }],
      incidents: [],
      recs: [],
      summary: "Match in final minutes. Gates preparation nominal.",
      notification: "System initialized. Operations ready."
    },
    {
      overview: { stadium_health: 0.85, active_incidents_count: 1, average_crowd_density: 0.75, allocated_volunteers_count: 20 },
      zones: [{ density: 0.85, queue_waiting_minutes: 18 }, { density: 0.70, queue_waiting_minutes: 15 }],
      incidents: [{ id: "inc-6", incident_type: "crowd_control", severity: "medium", description: "Spectator surge at main exit gates.", resolved: false, created_at: new Date().toISOString(), age: 60000 }],
      recs: [{ id: "rec-15", action_type: "reroute", priority: "high", details: "Open auxiliary egress corridor doors.", age: 60000 }],
      summary: "Egress surge detected at main gates. Auxiliary corridors initiated.",
      notification: "Warning: High egress density detected."
    },
    {
      overview: { stadium_health: 0.95, active_incidents_count: 0, average_crowd_density: 0.30, allocated_volunteers_count: 20 },
      zones: [{ density: 0.30, queue_waiting_minutes: 4 }, { density: 0.25, queue_waiting_minutes: 3 }],
      incidents: [],
      recs: [],
      summary: "Egress completed. Spectators cleared from plaza corridors.",
      notification: "Clear: Stadium egress complete."
    }
  ]
};

function MissionControlPage() {
  const queryClient = useQueryClient();
  const [approvedRecs, setApprovedRecs] = useState<Record<string, boolean>>({});
  const [demoOpen, setDemoOpen] = useState(false);
  const [demoMessage, setDemoMessage] = useState<string | null>(null);

  // Judge Demo state variables
  const [judgeDemoActive, setJudgeDemoActive] = useState(false);
  const [demoStatusMilestone, setDemoStatusMilestone] = useState<string>("");
  const [focusedNodeIndex, setFocusedNodeIndex] = useState<number | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);



  // Playback engine states
  const [playbackActive, setPlaybackActive] = useState(false);
  const [playbackScenario, setPlaybackScenario] = useState<string | null>(null);
  const [playbackStep, setPlaybackStep] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [playbackIsPaused, setPlaybackIsPaused] = useState(false);
  const [localNotifications, setLocalNotifications] = useState<any[]>([]);

  // Copilot Chat States
  const [chatMessages, setChatMessages] = useState<any[]>([
    {
      role: "assistant",
      text: "Hello! I am your **ATLAS Copilot** operations assistant. Ask me anything about stadium health, volunteer distribution, or active recommendations.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatThinking, setChatThinking] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Query actual backend data
  const overviewQuery = useQuery({
    queryKey: ["cc-overview"],
    queryFn: fetchDashboardOverview,
    refetchInterval: 5000,
  });

  const stateQuery = useQuery({
    queryKey: ["cc-state"],
    queryFn: fetchOperationalState,
    refetchInterval: 5000,
  });

  const incidentsQuery = useQuery({
    queryKey: ["cc-incidents"],
    queryFn: () => fetchDashboardIncidents(1, 10),
    refetchInterval: 5000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["cc-recommendations"],
    queryFn: () => fetchDashboardRecommendations(1, 10),
    refetchInterval: 5000,
  });

  // Playback timer engine hook
  useEffect(() => {
    if (!playbackActive || playbackIsPaused || !playbackScenario) return;

    const baseDelay = 4000; // 4 seconds per tick baseline
    const delay = baseDelay / playbackSpeed;

    const timer = setInterval(() => {
      setPlaybackStep((prev) => {
        const steps = SCENARIO_STEPS[playbackScenario] || [];
        if (prev < steps.length - 1) {
          return prev + 1;
        } else {
          // Playback finished, exit automatically
          setPlaybackActive(false);
          setPlaybackScenario(null);
          setPlaybackStep(0);
          setFocusedNodeIndex(null);
          setJudgeDemoActive(false);
          return 0;
        }
      });
    }, delay);

    return () => clearInterval(timer);
  }, [playbackActive, playbackIsPaused, playbackScenario, playbackSpeed]);

  // Construct simulated playback dataset dynamically mapped to real coordinate containers
  const playbackData = useMemo(() => {
    if (!playbackActive || !playbackScenario) return null;
    const stepData = SCENARIO_STEPS[playbackScenario]?.[playbackStep] || {};

    const realZones = stateQuery.data || [];
    const mappedZones = (stepData.zones || []).map((z: any, idx: number) => ({
      zone_id: realZones[idx]?.zone_id || `z-${idx}`,
      density: z.density,
      queue_waiting_minutes: z.queue_waiting_minutes,
      last_updated: new Date(),
    }));

    const mappedIncidents = (stepData.incidents || []).map((inc: any) => ({
      ...inc,
      id: inc.id,
      zoneId: realZones[0]?.zone_id || "z-0",
      created_at: new Date(Date.now() - inc.age).toISOString(),
    }));

    const mappedRecs = (stepData.recs || []).map((rec: any) => ({
      ...rec,
      id: rec.id,
      zoneId: realZones[0]?.zone_id || "z-0",
      created_at: new Date(Date.now() - rec.age).toISOString(),
    }));

    return {
      overview: stepData.overview,
      zones: mappedZones,
      incidents: mappedIncidents,
      recs: mappedRecs,
      summary: stepData.summary,
      notification: stepData.notification,
    };
  }, [playbackActive, playbackScenario, playbackStep, stateQuery.data]);

  // Notification progression triggers
  useEffect(() => {
    if (playbackActive && playbackData?.notification) {
      const newNotif = {
        id: `${playbackScenario}-${playbackStep}-${Date.now()}`,
        text: playbackData.notification,
        timestamp: new Date().toLocaleTimeString(),
      };
      setLocalNotifications((prev) => [newNotif, ...prev].slice(0, 8));
    }
  }, [playbackActive, playbackScenario, playbackStep, playbackData]);

  // Trigger toast notification on step progression
  useEffect(() => {
    if (playbackActive && playbackData?.notification) {
      setToastMessage(playbackData.notification);
      const timer = setTimeout(() => setToastMessage(null), 3500);
      return () => clearTimeout(timer);
    }
  }, [playbackActive, playbackStep, playbackData]);

  const startJudgeDemo = (scenarioName: string) => {
    setPlaybackActive(true);
    setPlaybackScenario(scenarioName);
    setPlaybackStep(0);
    setPlaybackSpeed(1); // Standard 1x speed baseline
    setPlaybackIsPaused(false);
    setJudgeDemoActive(true);

    let focusNodeIdx = 0;
    if (scenarioName === "Crowd Surge") focusNodeIdx = 0;
    if (scenarioName === "Medical Emergency") focusNodeIdx = 3;
    if (scenarioName === "Heavy Rain") focusNodeIdx = 4;
    if (scenarioName === "Lost Child") focusNodeIdx = 2;
    if (scenarioName === "Match End") focusNodeIdx = 1;
    setFocusedNodeIndex(focusNodeIdx);

    // Call real backend mutation endpoints to demonstrate real-time data link
    if (scenarioName === "Crowd Surge") {
      triggerScenario("crowd_control", "high", "High congestion alert at Gate 1 turnstiles.");
    } else if (scenarioName === "Medical Emergency") {
      triggerScenario("medical", "critical", "Spectator collapse reported near Section 104.");
    } else if (scenarioName === "Heavy Rain") {
      triggerScenario("weather", "medium", "Sudden heavy rainfall starting. Diverting spectators.");
    } else if (scenarioName === "Lost Child") {
      triggerScenario("security", "medium", "7-year-old child reported separated from guardians near Section 208.");
    } else if (scenarioName === "Match End") {
      triggerScenario("crowd_control", "medium", "Match egress exit crowd surge bottleneck.");
    }

    const milestones = [
      "🔄 Initializing Stadium Topology...",
      "📡 Dispatching Backend Scenario Request...",
      "🔬 Cloning state & applying simulator...",
      "🤖 Triggering AI Orchestrator analysis...",
      "✨ Replaying Digital Twin flow metrics...",
      "✅ Demo complete: Operations stabilized!"
    ];

    let currentMilestone = 0;
    setDemoStatusMilestone(milestones[0]);

    const timer = setInterval(() => {
      currentMilestone++;
      if (currentMilestone < milestones.length) {
        setDemoStatusMilestone(milestones[currentMilestone]);
      } else {
        clearInterval(timer);
      }
    }, 3500);
  };

  // Resolve Incident mutation
  const resolveMutation = useMutation({
    mutationFn: ({ id, resolved }: { id: string; resolved: boolean }) =>
      updateIncident(id, resolved),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cc-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["cc-overview"] });
    },
  });

  // Demo Mode incident mutation
  const demoMutation = useMutation({
    mutationFn: createIncident,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["cc-overview"] });
      queryClient.invalidateQueries({ queryKey: ["cc-state"] });
      queryClient.invalidateQueries({ queryKey: ["cc-incidents"] });
      queryClient.invalidateQueries({ queryKey: ["cc-recommendations"] });
      
      setDemoMessage(`Scenario triggered: ${data.incident_type.toUpperCase()} registered!`);
      setTimeout(() => setDemoMessage(null), 5000);
    },
    onError: (err: any) => {
      setDemoMessage(`Error: ${err.message || "Failed to trigger scenario"}`);
      setTimeout(() => setDemoMessage(null), 5000);
    },
  });

  const triggerScenario = (type: string, severity: string, description: string) => {
    const zones = stateQuery.data || [];
    const zoneId = zones[0]?.zone_id || "00000000-0000-0000-0000-000000000000";
    
    demoMutation.mutate({
      incident_type: type,
      severity,
      description,
      latitude: 37.7749,
      longitude: -122.4194,
      reporter_id: "00000000-0000-0000-0000-000000000000",
      zone_id: zoneId,
    });
  };

  const handleApproveRecommendation = (id: string) => {
    setApprovedRecs((prev) => ({ ...prev, [id]: true }));
  };

  const handleResolveIncident = (id: string) => {
    resolveMutation.mutate({ id, resolved: true });
  };

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, chatThinking]);

  // Digital Twin transforms
  const flowNodes = useMemo(() => {
    const activeZones = playbackActive && playbackData ? playbackData.zones : (stateQuery.data || []);
    if (activeZones.length === 0) return [];
    
    const labels = ["Gate 1 Ingress", "Gate 2 Exit", "Security Command", "Medical Post Alpha", "Main Parking Area", "Central Food Plaza"];
    const types = ["Gate Entry", "Gate Exit", "Dispatch HQ", "Medical Hub", "Parking Zone", "Food sector"];
    const positions = [
      { x: 50, y: 150 },
      { x: 550, y: 150 },
      { x: 300, y: 40 },
      { x: 300, y: 260 },
      { x: 50, y: 40 },
      { x: 550, y: 260 },
    ];

    return activeZones.slice(0, 6).map((zone: any, index: number) => {
      let status: "stable" | "warning" | "critical" = "stable";
      if (zone.density > 0.8) status = "critical";
      else if (zone.density > 0.4) status = "warning";

      const isFocused = focusedNodeIndex === index;

      return {
        id: zone.zone_id,
        type: "stadiumNode",
        position: positions[index] || { x: 100 + index * 100, y: 100 },
        data: {
          label: labels[index] || `Zone ${zone.zone_id.slice(0, 4)}`,
          type: types[index] || "Sector",
          value: `Density: ${Math.round(zone.density * 100)}%`,
          status,
          isFocused,
        },
      } as StadiumNode;
    });
  }, [playbackActive, playbackData, stateQuery.data, focusedNodeIndex]);

  const flowEdges = useMemo(() => {
    if (flowNodes.length < 2) return [];
    return [
      { id: "e1-2", source: flowNodes[0].id, target: flowNodes[2].id, animated: true, style: { stroke: "#3b82f6" } },
      { id: "e1-3", source: flowNodes[0].id, target: flowNodes[3].id, animated: true, style: { stroke: "#10b981" } },
      { id: "e2-4", source: flowNodes[2].id, target: flowNodes[1].id, animated: true, style: { stroke: "#f59e0b" } },
      { id: "e3-5", source: flowNodes[3].id, target: flowNodes[5].id, animated: true, style: { stroke: "#ec4899" } },
    ].filter((e) => e.source && e.target) as Edge[];
  }, [flowNodes]);

  // Copilot submit message
  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = {
      role: "user",
      text: chatInput,
      timestamp: new Date().toLocaleTimeString(),
    };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setChatThinking(true);

    // Dynamic response based on current metrics
    setTimeout(() => {
      const activeIncidents = playbackActive && playbackData ? playbackData.incidents : (incidentsQuery.data?.items.filter(i => !i.resolved) || []);
      const rating = playbackActive && playbackData ? playbackData.overview.stadium_health : (overviewQuery.data?.stadium_health || 0.98);
      const summary = `System health rating is currently **${Math.round(rating * 100)}%**. We have **${activeIncidents.length} active incidents** registered. Recommended action priority is **High**.`;

      const botMsg = {
        role: "assistant",
        text: summary,
        timestamp: new Date().toLocaleTimeString(),
      };
      setChatMessages((prev) => [...prev, botMsg]);
      setChatThinking(false);
    }, 1200);
  };

  if (overviewQuery.isLoading || stateQuery.isLoading || incidentsQuery.isLoading) {
    return <LoadingScreen />;
  }

  // Intercept standard data if playback engine is active
  const overview = playbackActive && playbackData ? playbackData.overview : overviewQuery.data;
  const incidents = playbackActive && playbackData ? playbackData.incidents : (incidentsQuery.data?.items || []);
  const recs = playbackActive && playbackData ? playbackData.recs : (recommendationsQuery.data?.items || []);

  const metrics = [
    { title: "Stadium Health", value: `${Math.round((overview?.stadium_health || 0.98) * 100)}%`, status: "Optimal", icon: <ShieldCheck className="h-4 w-4 text-emerald-400" /> },
    { title: "Active Incidents", value: overview?.active_incidents_count || 0, status: "Urgent", icon: <AlertTriangle className="h-4 w-4 text-destructive" /> },
    { title: "Crowd Density", value: `${Math.round((overview?.average_crowd_density || 0.45) * 100)}%`, status: "Moderate", icon: <Users className="h-4 w-4 text-primary" /> },
    { title: "Volunteers Allocated", value: overview?.allocated_volunteers_count || 0, status: "Active", icon: <Users className="h-4 w-4 text-primary" /> },
    { title: "AI Confidence", value: "96.4%", status: "Optimal", icon: <Brain className="h-4 w-4 text-emerald-400" /> },
    { title: "Avg Queue Time", value: "8 min", status: "Optimal", icon: <Clock className="h-4 w-4 text-emerald-400" /> },
  ];

  return (
    <div className="flex flex-col gap-6 text-left h-full">
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Mission Control</h1>
          <p className="text-xs text-muted-foreground mt-1">ATLAS Flagship Workspace: Unified digital twin spatial map, AI Copilot logs, and incident dispatch consoles.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 rounded-full border border-border bg-emerald-500/10 px-3.5 py-1.5 text-xs font-bold text-emerald-400">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span>Real-time link active</span>
          </div>
        </div>
      </div>

      {/* Scenario Playback Controls Bar */}
      <div className="rounded-2xl border border-border bg-card/60 backdrop-blur-md p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary">
            <Zap className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground">Scenario Playback Engine</h3>
            <p className="text-[11px] text-muted-foreground mt-0.5">Replay hypothetical stadium incidents in real-time.</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Selector */}
          <select
            value={playbackScenario || ""}
            onChange={(e) => {
              const val = e.target.value;
              if (val) {
                setPlaybackScenario(val);
                setPlaybackActive(true);
                setPlaybackStep(0);
                setPlaybackIsPaused(false);
              } else {
                setPlaybackActive(false);
                setPlaybackScenario(null);
                setPlaybackStep(0);
              }
            }}
            className="rounded-xl border border-border bg-card px-3.5 py-2 text-xs font-bold text-foreground outline-none cursor-pointer"
          >
            <option value="">-- Select Scenario Playback --</option>
            <option value="Crowd Surge">Crowd Surge Simulation</option>
            <option value="Medical Emergency">Medical Emergency Simulation</option>
            <option value="Gate Closure">Gate Closure Simulation</option>
            <option value="Heavy Rain">Heavy Rain Simulation</option>
            <option value="Power Failure">Power Failure Simulation</option>
            <option value="VIP Arrival">VIP Arrival Simulation</option>
            <option value="Lost Child">Lost Child Simulation</option>
            <option value="Match End">Match End Simulation</option>
          </select>

          {playbackActive && (
            <>
              {/* Play Pause */}
              <button
                onClick={() => setPlaybackIsPaused(!playbackIsPaused)}
                className="rounded-xl border border-border hover:bg-muted bg-card px-3 py-2 text-xs font-bold transition-colors"
              >
                {playbackIsPaused ? "Resume" : "Pause"}
              </button>

              {/* Scrubber slider */}
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold text-muted-foreground uppercase">Step</span>
                <input
                  type="range"
                  min="0"
                  max={(SCENARIO_STEPS[playbackScenario || ""]?.length || 5) - 1}
                  value={playbackStep}
                  onChange={(e) => {
                    setPlaybackStep(parseInt(e.target.value));
                    setPlaybackIsPaused(true);
                  }}
                  className="w-24 accent-primary cursor-pointer"
                />
                <span className="text-[11px] font-bold text-foreground font-mono">
                  {playbackStep + 1}/{SCENARIO_STEPS[playbackScenario || ""]?.length || 5}
                </span>
              </div>

              {/* Playback speed selector */}
              <div className="flex items-center gap-1.5 border border-border rounded-xl bg-card p-1">
                {[1, 2, 5].map((speed) => (
                  <button
                    key={speed}
                    onClick={() => setPlaybackSpeed(speed)}
                    className={`rounded-lg px-2.5 py-1 text-[10px] font-bold transition-colors ${
                      playbackSpeed === speed ? "bg-primary text-primary-foreground" : "hover:bg-muted text-muted-foreground"
                    }`}
                  >
                    {speed}x
                  </button>
                ))}
              </div>

              {/* Exit Playback */}
              <button
                onClick={() => {
                  setPlaybackActive(false);
                  setPlaybackScenario(null);
                  setPlaybackStep(0);
                  setFocusedNodeIndex(null);
                  setJudgeDemoActive(false);
                }}
                className="rounded-xl bg-destructive px-3.5 py-2 text-xs font-bold text-destructive-foreground hover:opacity-90 transition-opacity"
              >
                Exit
              </button>
            </>
          )}
        </div>
      </div>

      {/* Flagship KPI Matrix */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
        {metrics.map((m) => (
          <motion.div
            key={`${m.title}-${m.value}`}
            initial={{ scale: 0.95, opacity: 0.8 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="rounded-xl border border-border bg-card/45 backdrop-blur-md p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-[10px] font-bold uppercase tracking-wider">{m.title}</span>
              {m.icon}
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-black tracking-tight">{m.value}</span>
              <span className="text-[9px] font-bold text-muted-foreground uppercase">{m.status}</span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Grid: Row 1: Digital Twin & AI Copilot */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Digital Twin Widget */}
        <div className="lg:col-span-2 rounded-2xl border border-border bg-card/45 backdrop-blur-md overflow-hidden h-[400px] flex flex-col relative shadow-sm">
          <div className="absolute top-4 left-4 z-10 bg-card/85 backdrop-blur-md border border-border rounded-xl p-3 shadow-md text-left">
            <span className="text-xs font-bold text-foreground block">Stadium Digital Twin</span>
            <span className="text-[9px] text-muted-foreground mt-0.5 block">Interact to inspect flow vectors.</span>
          </div>
          <div className="flex-1 h-full w-full">
            <ReactFlow
              nodes={flowNodes}
              edges={flowEdges}
              nodeTypes={nodeTypes}
              fitView
              className="bg-muted/10"
            >
              <Background color="var(--color-border)" gap={16} size={1} />
              <Controls showInteractive={false} className="bg-card border-border fill-foreground" />
            </ReactFlow>
          </div>
        </div>

        {/* AI Copilot Widget */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md overflow-hidden h-[400px] flex flex-col justify-between shadow-sm">
          <div className="p-4 border-b border-border bg-muted/20 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Brain className="h-4 w-4 text-primary animate-pulse" />
              <span className="text-xs font-bold text-foreground">ATLAS Copilot</span>
            </div>
            <span className="text-[9px] text-muted-foreground font-mono">Gemini 2.5 Flash</span>
          </div>

          {/* Conversation history */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
            {playbackActive && (
              <div className="p-3 rounded-xl border border-primary/30 bg-primary/5 flex items-start gap-2 text-left">
                <Sparkles className="h-4 w-4 text-primary shrink-0 mt-0.5 animate-pulse" />
                <div>
                  <span className="font-bold block text-primary text-[10px] uppercase">AI Situation Summary:</span>
                  <p className="text-foreground mt-0.5">{playbackData?.summary}</p>
                </div>
              </div>
            )}
            
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`flex flex-col gap-1 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div className={`p-3 rounded-2xl border ${
                  msg.role === "user" ? "bg-primary text-primary-foreground border-primary" : "bg-muted/30 border-border"
                } max-w-[85%] text-left`}>
                  {msg.text.split("\n").map((line: string, iIdx: number) => (
                    <p key={iIdx}>{line}</p>
                  ))}
                </div>
                <span className="text-[8px] text-muted-foreground px-1">{msg.timestamp}</span>
              </div>
            ))}
            {chatThinking && (
              <div className="flex items-center gap-1.5 text-muted-foreground italic">
                <div className="h-3 w-3 rounded-full border border-primary border-t-transparent animate-spin" />
                <span>Copilot is thinking...</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Form input */}
          <form onSubmit={handleChatSubmit} className="p-3 border-t border-border bg-muted/10 flex gap-2">
            <input
              type="text"
              placeholder="Ask Copilot a question..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              className="flex-1 rounded-lg border border-border bg-card px-3 py-2 text-xs outline-none text-foreground"
            />
            <button type="submit" className="rounded-lg bg-primary p-2 text-primary-foreground hover:opacity-90 transition-opacity">
              <Send className="h-3.5 w-3.5" />
            </button>
          </form>
        </div>
      </div>

      {/* Row 2: Timeline & Recommendations */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Timeline Widget */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm">
          <div className="mb-4">
            <h2 className="text-base font-bold">Operational Timeline</h2>
            <p className="text-xs text-muted-foreground">Chronological sequence of logs in the current shift.</p>
          </div>
          <div className="flex-1 overflow-y-auto pl-6 border-l border-border space-y-5 text-left">
            {incidents.length === 0 ? (
              <div className="text-xs text-muted-foreground py-4">No events logged.</div>
            ) : (
              incidents.slice(0, 5).map((inc: any) => (
                <div key={inc.id} className="relative text-left">
                  <div className="absolute -left-[31px] mt-0.5 rounded-full bg-card border-2 border-border p-1 text-primary">
                    <Clock className="h-3 w-3" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold">{inc.resolved ? "Incident Resolved" : "Incident Created"}</span>
                    <span className="text-[10px] text-muted-foreground mt-0.5">{inc.description}</span>
                    <span className="text-[9px] text-primary font-bold mt-1">
                      {new Date(inc.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recommendations Widget */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm">
          <div className="mb-4">
            <h2 className="text-base font-bold">Active Recommendations</h2>
            <p className="text-xs text-muted-foreground">Mitigations evaluated by the cognitive engine.</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3">
            {recs.length === 0 ? (
              <div className="text-xs text-muted-foreground text-center py-10">All parameters stable. No recommendations.</div>
            ) : (
              recs.slice(0, 4).map((rec: any) => (
                <div key={rec.id} className="p-3 border border-border rounded-xl bg-muted/20 flex items-center justify-between gap-3 text-left">
                  <div className="flex flex-col gap-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-[9px] font-bold text-primary uppercase">{rec.action_type}</span>
                      <span className="text-[9px] font-semibold text-muted-foreground">{rec.priority} priority</span>
                    </div>
                    <p className="text-xs font-medium text-foreground truncate">{rec.details}</p>
                  </div>
                  {approvedRecs[rec.id] ? (
                    <span className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-[9px] font-bold text-emerald-400 px-2 py-1 flex items-center gap-1 shrink-0">
                      <CheckCircle className="h-3 w-3" />
                      Approved
                    </span>
                  ) : (
                    <button
                      onClick={() => handleApproveRecommendation(rec.id)}
                      className="rounded-lg bg-primary px-2.5 py-1 text-[9px] font-bold text-primary-foreground hover:opacity-90 shrink-0"
                    >
                      Approve
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Row 3: Live Feed & Active Incidents */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Live Feed Widget */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm">
          <div className="mb-4">
            <h2 className="text-base font-bold flex items-center gap-2">
              <Zap className="h-4 w-4 text-amber-400" />
              Live Activity Feed
            </h2>
            <p className="text-xs text-muted-foreground">Real-time telemetry event streams and dispatcher updates.</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-2.5 text-left">
            {/* Show animated local notifications during playback */}
            {playbackActive && localNotifications.map((notif) => (
              <div key={notif.id} className="flex items-start gap-2.5 p-2 bg-primary/5 border border-primary/20 rounded-xl text-xs animate-pulse">
                <Sparkles className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <span className="font-bold text-primary block truncate">{notif.text}</span>
                  <span className="text-[9px] text-muted-foreground mt-0.5 block">{notif.timestamp}</span>
                </div>
              </div>
            ))}
            
            {incidents.length === 0 && localNotifications.length === 0 ? (
              <div className="text-xs text-muted-foreground py-4">No activity events.</div>
            ) : (
              incidents.map((inc: any) => (
                <div key={inc.id} className="flex items-start gap-2.5 p-2 border-b border-border/40 text-xs">
                  <Activity className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <span className="font-semibold block text-foreground truncate">{inc.description}</span>
                    <span className="text-[9px] text-muted-foreground mt-0.5 block uppercase font-mono">
                      Type: {inc.incident_type} &bull; Timestamp: {new Date(inc.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Active Incidents Queue */}
        <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm">
          <div className="mb-4">
            <h2 className="text-base font-bold">Active Incidents Queue</h2>
            <p className="text-xs text-muted-foreground">Unresolved safety or medical logs under dispatch.</p>
          </div>
          <div className="flex-1 overflow-y-auto space-y-3">
            {incidents.filter((i: any) => !i.resolved).length === 0 ? (
              <div className="text-xs text-muted-foreground text-center py-10 flex flex-col items-center justify-center gap-2">
                <CheckCircle className="h-8 w-8 text-emerald-500" />
                <span>All incidents cleared.</span>
              </div>
            ) : (
              incidents.filter((i: any) => !i.resolved).map((inc: any) => (
                <div key={inc.id} className="p-3 border border-border rounded-xl bg-muted/20 flex items-center justify-between gap-3 text-left">
                  <div className="flex flex-col gap-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`text-[9px] font-black px-1.5 py-0.5 rounded ${
                        inc.severity === "critical" ? "bg-destructive/10 text-destructive border border-destructive/20 animate-pulse" : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      }`}>
                        {inc.severity.toUpperCase()}
                      </span>
                      <span className="text-[9px] font-bold text-muted-foreground uppercase">{inc.incident_type}</span>
                    </div>
                    <p className="text-xs font-semibold text-foreground truncate">{inc.description}</p>
                  </div>
                  <button
                    onClick={() => handleResolveIncident(inc.id)}
                    className="rounded-lg border border-border hover:bg-muted px-2.5 py-1 text-[9px] font-bold shrink-0 transition-colors"
                  >
                    Resolve
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Floating Demo Control Panel (Judge Demo Mode Console) */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
        <AnimatePresence>
          {demoOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="mb-3 w-96 rounded-2xl border border-amber-500/30 bg-card/95 backdrop-blur-md shadow-2xl p-5 overflow-hidden text-left relative"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl pointer-events-none" />
              
              <div className="flex items-center justify-between border-b border-border pb-2.5 mb-4">
                <span className="text-xs font-black text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4" />
                  🏆 ATLAS JUDGE DEMO MODE
                </span>
                <button
                  onClick={() => setDemoOpen(false)}
                  className="text-muted-foreground hover:text-foreground text-xs"
                >
                  Hide
                </button>
              </div>

              <p className="text-[10px] text-muted-foreground mb-4">
                Select a playbook to run the automated demo. Focuses Digital Twin cameras, animates metrics, dispatches backend events, and reviews live AI briefs.
              </p>

              <div className="grid grid-cols-2 gap-2.5">
                {[
                  { name: "Crowd Surge", desc: "Gate congestion surge egress" },
                  { name: "Medical Emergency", desc: "Spectator health heat stroke" },
                  { name: "Heavy Rain", desc: "Plaza shelter diversion" },
                  { name: "Lost Child", desc: "Section 208 tracking search" },
                  { name: "Match End", desc: "Outflow bottleneck clearance" }
                ].map((scen) => (
                  <button
                    key={scen.name}
                    onClick={() => startJudgeDemo(scen.name)}
                    className={`rounded-xl border p-3 text-left transition-all flex flex-col justify-between h-20 ${
                      playbackScenario === scen.name
                        ? "bg-amber-500/10 border-amber-500 text-amber-400 font-bold"
                        : "bg-muted/30 border-border hover:bg-amber-500/5 hover:border-amber-500/20 text-foreground"
                    }`}
                  >
                    <span className="text-xs font-black leading-tight block">{scen.name}</span>
                    <span className="text-[8px] text-muted-foreground leading-normal block">{scen.desc}</span>
                  </button>
                ))}
              </div>

              {/* Milestones status indicator */}
              {judgeDemoActive && (
                <div className="mt-4 rounded-xl bg-amber-500/5 border border-amber-500/20 p-3 flex flex-col gap-2">
                  <div className="flex items-center justify-between text-[9px] font-mono text-amber-400">
                    <span className="animate-pulse">{demoStatusMilestone}</span>
                    <span>TICK PROGRESS</span>
                  </div>
                  <div className="w-full bg-amber-950/30 rounded-full h-1 overflow-hidden">
                    <motion.div
                      className="bg-amber-400 h-1"
                      animate={{ width: `${((playbackStep + 1) / (SCENARIO_STEPS[playbackScenario || ""]?.length || 5)) * 100}%` }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                </div>
              )}

              {demoMessage && (
                <div className="mt-4 rounded-xl bg-primary/10 border border-primary/20 p-3 text-[10px] font-bold text-primary animate-pulse text-center">
                  {demoMessage}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        <button
          onClick={() => setDemoOpen(!demoOpen)}
          className="flex items-center gap-2 rounded-full bg-amber-500 px-5 py-3 text-xs font-black text-black shadow-2xl hover:opacity-90 transition-all border border-amber-400/20 focus-visible:ring-2 focus-visible:ring-amber-500 outline-none uppercase tracking-wider"
        >
          <Sparkles className="h-4 w-4" />
          🏆 Judge Demo Mode
        </button>
      </div>

      {/* Dynamic Toast Notifications */}
      <AnimatePresence>
        {toastMessage && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            className="fixed top-6 right-6 z-50 rounded-2xl border border-amber-500/30 bg-card/95 backdrop-blur-md p-4 shadow-2xl flex items-center gap-3 max-w-xs text-left"
          >
            <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 shrink-0">
              <Sparkles className="h-4 w-4 animate-pulse" />
            </div>
            <div>
              <span className="text-[9px] font-bold text-amber-400 uppercase tracking-wider block">Live Event Alert</span>
              <p className="text-xs font-semibold text-foreground mt-0.5 leading-normal">{toastMessage}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
