import { create } from "zustand";
import { envConfig } from "../config/env";
import { SCENARIO_STEPS } from "./scenarioSteps";

export interface ChatMessage {
  role: "user" | "assistant";
  text: string;
  timestamp: string;
  thinkingSteps?: string[];
  citations?: { label: string; text: string }[];
}

export interface IncidentItem {
  id: string;
  incident_type: string;
  severity: string;
  description: string;
  latitude: number;
  longitude: number;
  reporter_id: string;
  resolved: boolean;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
  zoneId?: string;
}

export interface RecommendationItem {
  id: string;
  action_type: string;
  priority: string;
  confidence: number;
  details: string;
  status: string;
  approved_by_id: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
  zoneId?: string;
}

interface GlobalState {
  // Authentication & Security Context
  userRole: string;
  sessionExpiry: string;
  setUserRole: (role: string) => void;
  setSessionExpiry: (expiry: string) => void;

  // Active Simulation Controls & State
  playbackActive: boolean;
  playbackScenario: string | null;
  playbackStep: number;
  playbackSpeed: number;
  playbackIsPaused: boolean;
  simulationClock: string;
  simulatedOverview: any | null;
  simulatedZones: any[] | null;
  simulatedIncidents: any[] | null;
  simulatedRecommendations: any[] | null;

  startSimulation: (scenario: string) => void;
  pauseSimulation: () => void;
  resumeSimulation: () => void;
  resetSimulation: () => void;
  stopSimulation: () => void;
  updateSimulationStep: (scenario: string, step: number) => void;
  setPlaybackActive: (active: boolean) => void;
  setPlaybackScenario: (scenario: string | null) => void;
  setPlaybackStep: (step: number | ((prev: number) => number)) => void;
  setPlaybackSpeed: (speed: number) => void;
  setPlaybackIsPaused: (paused: boolean) => void;

  // Incidents State & UI Filters
  selectedIncident: IncidentItem | null;
  incidentSearch: string;
  incidentFilterSeverity: string;
  incidentFilterStatus: string;
  incidentPage: number;
  incidentSortBy: "created_at" | "severity";
  incidentSortOrder: "asc" | "desc";
  assignedVolunteer: string;
  volunteerMessage: string;
  setSelectedIncident: (incident: IncidentItem | null) => void;
  setIncidentSearch: (search: string | ((prev: string) => string)) => void;
  setIncidentFilterSeverity: (severity: string | ((prev: string) => string)) => void;
  setIncidentFilterStatus: (status: string | ((prev: string) => string)) => void;
  setIncidentPage: (page: number | ((prev: number) => number)) => void;
  setIncidentSortBy: (sortBy: "created_at" | "severity" | ((prev: "created_at" | "severity") => "created_at" | "severity")) => void;
  setIncidentSortOrder: (order: "asc" | "desc" | ((prev: "asc" | "desc") => "asc" | "desc")) => void;
  setAssignedVolunteer: (volunteer: string) => void;
  setVolunteerMessage: (msg: string) => void;

  // Recommendations State & Approvals
  approvedRecs: Record<string, boolean>;
  recSearch: string;
  recFilterPriority: string;
  recFilterSeverity: string;
  recFilterStatus: string;
  recFilterCategory: string;
  selectedRec: RecommendationItem | null;
  drawerOpen: boolean;
  selectedIds: Record<string, boolean>;
  localStatuses: Record<string, string>;
  toggleRecApproval: (recId: string) => void;
  setRecApproval: (recId: string, approved: boolean) => void;
  setRecSearch: (search: string) => void;
  setRecFilterPriority: (priority: string) => void;
  setRecFilterSeverity: (severity: string) => void;
  setRecFilterStatus: (status: string) => void;
  setRecFilterCategory: (category: string) => void;
  setSelectedRec: (rec: RecommendationItem | null) => void;
  setDrawerOpen: (open: boolean) => void;
  setSelectedIds: (ids: Record<string, boolean> | ((prev: Record<string, boolean>) => Record<string, boolean>)) => void;
  setLocalStatuses: (statuses: Record<string, string> | ((prev: Record<string, string>) => Record<string, string>)) => void;

  // Telemetry & Digital Twin State
  focusedNodeIndex: number | null;
  selectedNodeId: string | null;
  setFocusedNodeIndex: (idx: number | null) => void;
  setSelectedNodeId: (id: string | null) => void;

  // AI Assistant (Copilot) Chat History
  chatMessages: ChatMessage[];
  chatInput: string;
  chatThinking: boolean;
  setChatMessages: (msgs: ChatMessage[] | ((prev: ChatMessage[]) => ChatMessage[])) => void;
  setChatInput: (input: string) => void;
  setChatThinking: (thinking: boolean) => void;

  // Notification Feed Logs & UI Indicators
  localNotifications: any[];
  toastMessage: string | null;
  demoOpen: boolean;
  demoMessage: string | null;
  judgeDemoActive: boolean;
  demoStatusMilestone: string;
  notificationFilterCategory: string;
  notificationFilterSeverity: string;
  notificationGroupBySeverity: boolean;
  notificationLocalReadState: Record<string, boolean>;
  setLocalNotifications: (notifs: any[] | ((prev: any[]) => any[])) => void;
  setToastMessage: (msg: string | null) => void;
  setDemoOpen: (open: boolean) => void;
  setDemoMessage: (msg: string | null) => void;
  setJudgeDemoActive: (active: boolean) => void;
  setDemoStatusMilestone: (milestone: string) => void;
  setNotificationFilterCategory: (category: string) => void;
  setNotificationFilterSeverity: (severity: string) => void;
  setNotificationGroupBySeverity: (group: boolean) => void;
  setNotificationLocalReadState: (state: Record<string, boolean> | ((prev: Record<string, boolean>) => Record<string, boolean>)) => void;

  // Timeline States
  timelinePlaybackActive: boolean;
  timelinePlaybackStep: number;
  timelinePlaybackSpeed: number;
  timelineFilterType: string;
  timelineFilterSeverity: string;
  setTimelinePlaybackActive: (active: boolean) => void;
  setTimelinePlaybackStep: (step: number | ((prev: number) => number)) => void;
  setTimelinePlaybackSpeed: (speed: number) => void;
  setTimelineFilterType: (type: string) => void;
  setTimelineFilterSeverity: (severity: string) => void;

  // Global Thresholds
  thresholdDensity: number;
  thresholdQueue: number;
  confidenceThreshold: number;
  setThresholdDensity: (density: number) => void;
  setThresholdQueue: (queue: number) => void;
  setConfidenceThreshold: (confidence: number) => void;

  // Analytics UI Filters
  timeRange: string;
  filterZone: string;
  filterType: string;
  setTimeRange: (range: string) => void;
  setFilterZone: (zone: string) => void;
  setFilterType: (type: string) => void;
}

let simInterval: any = null;

const runSimulationTick = (get: any) => {
  const state = get();
  if (!state.playbackActive || state.playbackIsPaused || !state.playbackScenario) return;

  const scenario = state.playbackScenario;
  const currentStep = state.playbackStep;
  const steps = SCENARIO_STEPS[scenario] || [];

  if (currentStep < steps.length - 1) {
    const nextStep = currentStep + 1;
    state.updateSimulationStep(scenario, nextStep);
  } else {
    // Loop simulation
    state.updateSimulationStep(scenario, 0);
  }
};

const startTimer = (get: any) => {
  if (simInterval) {
    clearInterval(simInterval);
  }
  const state = get();
  const delay = 4000 / state.playbackSpeed;
  simInterval = setInterval(() => {
    runSimulationTick(get);
  }, delay);
};

const stopTimer = () => {
  if (simInterval) {
    clearInterval(simInterval);
    simInterval = null;
  }
};

export const useGlobalStore = create<GlobalState>((set, get) => ({
  // Authentication & Security Context
  userRole: "Administrator",
  sessionExpiry: "12 Hours",
  setUserRole: (role) => set({ userRole: role }),
  setSessionExpiry: (expiry) => set({ sessionExpiry: expiry }),

  // Active Simulation Controls & State
  playbackActive: false,
  playbackScenario: null,
  playbackStep: 0,
  playbackSpeed: 1,
  playbackIsPaused: false,
  simulationClock: "18:00",
  simulatedOverview: null,
  simulatedZones: null,
  simulatedIncidents: null,
  simulatedRecommendations: null,

  startSimulation: (scenario) => {
    set({
      playbackActive: true,
      playbackScenario: scenario,
      playbackStep: 0,
      playbackIsPaused: false,
    });
    get().updateSimulationStep(scenario, 0);
    startTimer(get);
  },
  pauseSimulation: () => {
    set({ playbackIsPaused: true });
    stopTimer();
  },
  resumeSimulation: () => {
    set({ playbackIsPaused: false });
    startTimer(get);
  },
  resetSimulation: () => {
    const scenario = get().playbackScenario || "Crowd Surge";
    set({
      playbackStep: 0,
      playbackIsPaused: false,
    });
    get().updateSimulationStep(scenario, 0);
    startTimer(get);
  },
  stopSimulation: () => {
    set({
      playbackActive: false,
      playbackScenario: null,
      playbackStep: 0,
      playbackIsPaused: false,
      simulatedOverview: null,
      simulatedZones: null,
      simulatedIncidents: null,
      simulatedRecommendations: null,
      simulationClock: "18:00",
    });
    stopTimer();
  },
  updateSimulationStep: (scenario, step) => {
    const stepData = SCENARIO_STEPS[scenario]?.[step];
    if (!stepData) return;

    const getZoneId = (scen: string, idx: number): string => {
      if (scen === "Crowd Surge") {
        if (idx === 0) return "gate-1";
        if (idx === 1) return "food-court";
        if (idx === 2) return "restrooms";
      }
      if (scen === "Medical Emergency") {
        if (idx === 0) return "med-post";
        if (idx === 1) return "sec-cmd";
      }
      if (scen === "Gate Closure") {
        if (idx === 0) return "gate-1";
        if (idx === 1) return "transit-hub";
      }
      if (scen === "Heavy Rain") {
        if (idx === 0) return "food-court";
        if (idx === 1) return "restrooms";
      }
      if (scen === "Power Failure") {
        if (idx === 0) return "food-court";
        if (idx === 1) return "sec-cmd";
      }
      if (scen === "VIP Arrival") {
        if (idx === 0) return "park-vip";
        if (idx === 1) return "gate-1";
      }
      if (scen === "Lost Child") {
        if (idx === 0) return "sec-cmd";
        if (idx === 1) return "vol-depot";
      }
      if (scen === "Match End") {
        if (idx === 0) return "gate-1";
        if (idx === 1) return "transit-hub";
      }
      return `zone-${idx}`;
    };

    const zoneMetadata = [
      { zone_id: "gate-1" },
      { zone_id: "sec-cmd" },
      { zone_id: "med-post" },
      { zone_id: "park-vip" },
      { zone_id: "food-court" },
      { zone_id: "restrooms" },
      { zone_id: "transit-hub" },
      { zone_id: "vol-depot" },
    ];

    const simulatedZones = zoneMetadata.map((meta) => {
      const stepZoneIndex = (stepData.zones || []).findIndex(
        (_: any, idx: number) => getZoneId(scenario, idx) === meta.zone_id
      );
      if (stepZoneIndex !== -1) {
        const sz = stepData.zones[stepZoneIndex];
        return {
          zone_id: meta.zone_id,
          density: sz.density,
          queue_waiting_minutes: sz.queue_waiting_minutes,
          last_updated: new Date().toISOString(),
        };
      }
      return {
        zone_id: meta.zone_id,
        density: 0.15,
        queue_waiting_minutes: 2,
        last_updated: new Date().toISOString(),
      };
    });

    const simulatedOverview = {
      stadium_health: stepData.overview.stadium_health,
      active_incidents_count: stepData.overview.active_incidents_count,
      average_crowd_density: stepData.overview.average_crowd_density,
      allocated_volunteers_count: stepData.overview.allocated_volunteers_count,
      last_updated: new Date().toISOString(),
    };

    const simulatedIncidents = (stepData.incidents || []).map((inc: any) => {
      let zoneId = "gate-1";
      if (inc.id === "inc-2") zoneId = "med-post";
      else if (inc.id === "inc-4") zoneId = "food-court";
      else if (inc.id === "inc-5") zoneId = "sec-cmd";
      return {
        ...inc,
        zoneId,
        created_at: inc.created_at || new Date().toISOString(),
      };
    });

    const simulatedRecommendations = (stepData.recs || []).map((rec: any) => {
      let zoneId = "gate-1";
      if (rec.id === "rec-3" || rec.id === "rec-4") zoneId = "med-post";
      else if (rec.id === "rec-7" || rec.id === "rec-8" || rec.id === "rec-9" || rec.id === "rec-10") zoneId = "food-court";
      else if (rec.id === "rec-11" || rec.id === "rec-12") zoneId = "park-vip";
      else if (rec.id === "rec-13" || rec.id === "rec-14") zoneId = "sec-cmd";
      return {
        ...rec,
        zoneId,
        confidence: rec.confidence || 0.85,
        status: rec.status || "pending",
        created_at: new Date().toISOString(),
      };
    });

    // Clock calculation
    const hours = 18 + Math.floor((step * 15) / 60);
    const minutes = (step * 15) % 60;
    const timeString = `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;

    // New notification object
    const notifId = `notif-${scenario}-${step}-${Date.now()}`;
    const newNotification = {
      id: notifId,
      category: "AI" as const,
      severity: (stepData.overview.stadium_health < 0.8 ? "critical" : "warning") as any,
      title: `${scenario} Update (Step ${step + 1})`,
      description: stepData.notification,
      timestamp: new Date().toLocaleTimeString(),
      read: false,
      referenceId: stepData.incidents?.[0]?.id || `step-${step}`,
      type: (stepData.incidents && stepData.incidents.length > 0 ? "incident" : "recommendation") as any,
    };

    set((state) => {
      const isAlreadyPresent = state.chatMessages.some((msg) => msg.text.includes(stepData.summary));
      const chatMessages = isAlreadyPresent
        ? state.chatMessages
        : [
            ...state.chatMessages,
            {
              role: "assistant" as const,
              text: `### [Simulation Engine Update] ${scenario} (Step ${step + 1})\n\n${stepData.summary}`,
              timestamp: new Date().toLocaleTimeString(),
            },
          ];

      return {
        playbackStep: step,
        simulationClock: timeString,
        simulatedOverview,
        simulatedZones,
        simulatedIncidents,
        simulatedRecommendations,
        toastMessage: stepData.notification,
        localNotifications: [newNotification, ...state.localNotifications],
        chatMessages,
      };
    });
  },
  setPlaybackActive: (active) => {
    if (active) {
      get().startSimulation(get().playbackScenario || "Crowd Surge");
    } else {
      get().stopSimulation();
    }
  },
  setPlaybackScenario: (scenario) => {
    if (scenario) {
      get().startSimulation(scenario);
    } else {
      get().stopSimulation();
    }
  },
  setPlaybackStep: (step) => {
    const nextStep = typeof step === "function" ? step(get().playbackStep) : step;
    get().updateSimulationStep(get().playbackScenario || "Crowd Surge", nextStep);
  },
  setPlaybackSpeed: (speed) => {
    set({ playbackSpeed: speed });
    if (get().playbackActive && !get().playbackIsPaused) {
      startTimer(get);
    }
  },
  setPlaybackIsPaused: (paused) => {
    if (paused) {
      get().pauseSimulation();
    } else {
      get().resumeSimulation();
    }
  },

  // Incidents State & UI Filters
  selectedIncident: null,
  incidentSearch: "",
  incidentFilterSeverity: "all",
  incidentFilterStatus: "all",
  incidentPage: 1,
  incidentSortBy: "created_at",
  incidentSortOrder: "desc",
  assignedVolunteer: "",
  volunteerMessage: "",
  setSelectedIncident: (incident) => set({ selectedIncident: incident }),
  setIncidentSearch: (search) =>
    set((state) => ({
      incidentSearch: typeof search === "function" ? search(state.incidentSearch) : search,
      incidentPage: 1,
    })),
  setIncidentFilterSeverity: (severity) =>
    set((state) => ({
      incidentFilterSeverity: typeof severity === "function" ? severity(state.incidentFilterSeverity) : severity,
      incidentPage: 1,
    })),
  setIncidentFilterStatus: (status) =>
    set((state) => ({
      incidentFilterStatus: typeof status === "function" ? status(state.incidentFilterStatus) : status,
      incidentPage: 1,
    })),
  setIncidentPage: (page) =>
    set((state) => ({
      incidentPage: typeof page === "function" ? page(state.incidentPage) : page,
    })),
  setIncidentSortBy: (sortBy) =>
    set((state) => ({
      incidentSortBy: typeof sortBy === "function" ? sortBy(state.incidentSortBy) : sortBy,
    })),
  setIncidentSortOrder: (order) =>
    set((state) => ({
      incidentSortOrder: typeof order === "function" ? order(state.incidentSortOrder) : order,
    })),
  setAssignedVolunteer: (volunteer) => set({ assignedVolunteer: volunteer }),
  setVolunteerMessage: (msg) => set({ volunteerMessage: msg }),

  // Recommendations State & Approvals
  approvedRecs: {},
  recSearch: "",
  recFilterPriority: "all",
  recFilterSeverity: "all",
  recFilterStatus: "all",
  recFilterCategory: "all",
  selectedRec: null,
  drawerOpen: false,
  selectedIds: {},
  localStatuses: {},
  toggleRecApproval: (recId) =>
    set((state) => ({
      approvedRecs: {
        ...state.approvedRecs,
        [recId]: !state.approvedRecs[recId],
      },
    })),
  setRecApproval: (recId, approved) =>
    set((state) => ({
      approvedRecs: {
        ...state.approvedRecs,
        [recId]: approved,
      },
    })),
  setRecSearch: (search) => set({ recSearch: search }),
  setRecFilterPriority: (priority) => set({ recFilterPriority: priority }),
  setRecFilterSeverity: (severity) => set({ recFilterSeverity: severity }),
  setRecFilterStatus: (status) => set({ recFilterStatus: status }),
  setRecFilterCategory: (category) => set({ recFilterCategory: category }),
  setSelectedRec: (rec) => set({ selectedRec: rec }),
  setDrawerOpen: (open) => set({ drawerOpen: open }),
  setSelectedIds: (ids) =>
    set((state) => ({
      selectedIds: typeof ids === "function" ? ids(state.selectedIds) : ids,
    })),
  setLocalStatuses: (statuses) =>
    set((state) => ({
      localStatuses: typeof statuses === "function" ? statuses(state.localStatuses) : statuses,
    })),

  // Telemetry & Digital Twin State
  focusedNodeIndex: null,
  selectedNodeId: null,
  setFocusedNodeIndex: (idx) => set({ focusedNodeIndex: idx }),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),

  // AI Assistant (Copilot) Chat History
  chatMessages: [
    {
      role: "assistant",
      text: "Hello! I am your **ATLAS Copilot** operations assistant. Ask me anything about stadium health, volunteer distribution, or active recommendations.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ],
  chatInput: "",
  chatThinking: false,
  setChatMessages: (msgs) =>
    set((state) => ({
      chatMessages: typeof msgs === "function" ? msgs(state.chatMessages) : msgs,
    })),
  setChatInput: (input) => set({ chatInput: input }),
  setChatThinking: (thinking) => set({ chatThinking: thinking }),

  // Notification Feed Logs & UI Indicators
  localNotifications: [],
  toastMessage: null,
  demoOpen: false,
  demoMessage: null,
  judgeDemoActive: false,
  demoStatusMilestone: "",
  setLocalNotifications: (notifs) =>
    set((state) => ({
      localNotifications: typeof notifs === "function" ? notifs(state.localNotifications) : notifs,
    })),
  setToastMessage: (msg) => set({ toastMessage: msg }),
  setDemoOpen: (open) => set({ demoOpen: open }),
  setDemoMessage: (msg) => set({ demoMessage: msg }),
  setJudgeDemoActive: (active) => set({ judgeDemoActive: active }),
  setDemoStatusMilestone: (milestone) => set({ demoStatusMilestone: milestone }),
  notificationFilterCategory: "all",
  notificationFilterSeverity: "all",
  notificationGroupBySeverity: false,
  notificationLocalReadState: {},
  setNotificationFilterCategory: (category) => set({ notificationFilterCategory: category }),
  setNotificationFilterSeverity: (severity) => set({ notificationFilterSeverity: severity }),
  setNotificationGroupBySeverity: (group) => set({ notificationGroupBySeverity: group }),
  setNotificationLocalReadState: (state) =>
    set((s) => ({
      notificationLocalReadState: typeof state === "function" ? state(s.notificationLocalReadState) : state,
    })),

  // Timeline States
  timelinePlaybackActive: false,
  timelinePlaybackStep: 4, // Defaults to HISTORICAL_EVENTS.length - 1 (which is 5 elements, i.e., index 4)
  timelinePlaybackSpeed: 1,
  timelineFilterType: "all",
  timelineFilterSeverity: "all",
  setTimelinePlaybackActive: (active) => set({ timelinePlaybackActive: active }),
  setTimelinePlaybackStep: (step) =>
    set((state) => ({
      timelinePlaybackStep: typeof step === "function" ? step(state.timelinePlaybackStep) : step,
    })),
  setTimelinePlaybackSpeed: (speed) => set({ timelinePlaybackSpeed: speed }),
  setTimelineFilterType: (type) => set({ timelineFilterType: type }),
  setTimelineFilterSeverity: (severity) => set({ timelineFilterSeverity: severity }),

  // Global Thresholds
  thresholdDensity: envConfig.defaultCrowdDensityThreshold,
  thresholdQueue: envConfig.defaultQueueTimeThreshold,
  confidenceThreshold: envConfig.defaultAiConfidenceThreshold,
  setThresholdDensity: (density) => set({ thresholdDensity: density }),
  setThresholdQueue: (queue) => set({ thresholdQueue: queue }),
  setConfidenceThreshold: (confidence) => set({ confidenceThreshold: confidence }),

  // Analytics UI Filters
  timeRange: "match",
  filterZone: "all",
  filterType: "all",
  setTimeRange: (range) => set({ timeRange: range }),
  setFilterZone: (zone) => set({ filterZone: zone }),
  setFilterType: (type) => set({ filterType: type }),
}));
