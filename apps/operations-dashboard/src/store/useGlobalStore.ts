import { create } from "zustand";
import { envConfig } from "../config/env";

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

  // Active Simulation Controls
  playbackActive: boolean;
  playbackScenario: string | null;
  playbackStep: number;
  playbackSpeed: number;
  playbackIsPaused: boolean;
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

export const useGlobalStore = create<GlobalState>((set) => ({
  // Authentication & Security Context
  userRole: "Administrator",
  sessionExpiry: "12 Hours",
  setUserRole: (role) => set({ userRole: role }),
  setSessionExpiry: (expiry) => set({ sessionExpiry: expiry }),

  // Active Simulation Controls
  playbackActive: false,
  playbackScenario: null,
  playbackStep: 0,
  playbackSpeed: 1,
  playbackIsPaused: false,
  setPlaybackActive: (active) => set({ playbackActive: active }),
  setPlaybackScenario: (scenario) => set({ playbackScenario: scenario, playbackStep: 0 }),
  setPlaybackStep: (step) =>
    set((state) => ({
      playbackStep: typeof step === "function" ? step(state.playbackStep) : step,
    })),
  setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),
  setPlaybackIsPaused: (paused) => set({ playbackIsPaused: paused }),

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
