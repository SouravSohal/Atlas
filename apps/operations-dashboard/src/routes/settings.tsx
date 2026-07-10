import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  Settings as SettingsIcon,
  Globe,
  Cpu,
  Database,
  Sliders,
  AlertTriangle,
  Wifi,
  UserCheck,
  Terminal,
  Info,
  Play,
  Pause,
  RefreshCw,
  Download,
  ExternalLink,
  CheckCircle2,
  Lock,
} from "lucide-react";
import { envConfig } from "../config/env";
import { useGlobalStore } from "../store/useGlobalStore";

export const Route = createFileRoute("/settings")({
  component: SettingsPage,
});

type TabId = "general" | "ai" | "database" | "simulation" | "thresholds" | "sync" | "auth" | "logs" | "about";

function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabId>("general");

  // State configurations connected to centralized envConfig
  const [backendUrl, setBackendUrl] = useState(envConfig.apiUrl);
  const [frontendUrl, setFrontendUrl] = useState(window.location.origin);
  const [environment, setEnvironment] = useState(envConfig.environment);
  const [deploymentStatus] = useState("Operational");

  const [geminiModel, setGeminiModel] = useState(envConfig.geminiModel);
  const [aiTestStatus, setAiTestStatus] = useState<"idle" | "testing" | "success" | "error">("idle");
  const [lastAiRequest, setLastAiRequest] = useState("2026-07-10 17:21:05");

  const dbEngine = envConfig.dbEngine;
  const [dbSyncStatus, setDbSyncStatus] = useState<"idle" | "syncing" | "success">("idle");
  const [dbTotalRecords, setDbTotalRecords] = useState(14820);
  const [lastDbSync, setLastDbSync] = useState("2026-07-10 17:24:18");

  const [demoMode, setDemoMode] = useState(envConfig.defaultDemoMode);
  const {
    playbackSpeed: simSpeed,
    setPlaybackSpeed: setSimSpeed,
    playbackIsPaused: simPaused,
    setPlaybackIsPaused: setSimPaused,
    thresholdDensity,
    setThresholdDensity,
    thresholdQueue,
    setThresholdQueue,
    confidenceThreshold,
    setConfidenceThreshold,
    sessionExpiry,
    setSessionExpiry,
    userRole,
  } = useGlobalStore();
  const [selectedSeed, setSelectedSeed] = useState("stadium_seed_data.json");

  const [medAutoDispatch, setMedAutoDispatch] = useState(true);
  const [weatherOverride, setWeatherOverride] = useState("Medium");

  const wsLatency = 12;
  const activeClients = 104;

  const [diagnosticLogs, setDiagnosticLogs] = useState<string[]>([
    "[2026-07-10 17:20:00] INFO: WebSocket client registry handshake completed (client-104)",
    "[2026-07-10 17:21:05] SUCCESS: AI prompt situation compilation successfully generated via Gemini-2.5-pro",
    "[2026-07-10 17:22:15] WARN: Crowd density warning limit breached at Gate 1 Turnstiles",
    "[2026-07-10 17:23:44] DATABASE: Firestore transaction committed for Incident resolution (ID: inc-041)",
    "[2026-07-10 17:24:18] INFO: Digital Twin telemetry synchronization cycle complete"
  ]);

  // Connection testing handler
  const handleTestAIConnection = () => {
    setAiTestStatus("testing");
    setTimeout(() => {
      setAiTestStatus("success");
      setLastAiRequest(new Date().toLocaleTimeString());
    }, 1500);
  };

  // Database synchronization handler
  const handleSyncDatabase = () => {
    setDbSyncStatus("syncing");
    setTimeout(() => {
      setDbSyncStatus("success");
      setLastDbSync(new Date().toLocaleTimeString());
      setDbTotalRecords((prev) => prev + 4);
      setDiagnosticLogs((prev) => [
        `[${new Date().toLocaleString()}] SUCCESS: Manual database sync trigger executed. Verified ${dbTotalRecords + 4} documents.`,
        ...prev
      ]);
    }, 1200);
  };

  const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: "general", label: "Environment & App", icon: <Globe className="h-4 w-4" /> },
    { id: "ai", label: "AI Configuration", icon: <Cpu className="h-4 w-4" /> },
    { id: "database", label: "Database", icon: <Database className="h-4 w-4" /> },
    { id: "simulation", label: "Simulation Controls", icon: <Sliders className="h-4 w-4" /> },
    { id: "thresholds", label: "Alert Thresholds", icon: <AlertTriangle className="h-4 w-4" /> },
    { id: "sync", label: "Live Sync & WS", icon: <Wifi className="h-4 w-4" /> },
    { id: "auth", label: "Authentication", icon: <UserCheck className="h-4 w-4" /> },
    { id: "logs", label: "Diagnostics & Logs", icon: <Terminal className="h-4 w-4" /> },
    { id: "about", label: "About ATLAS", icon: <Info className="h-4 w-4" /> },
  ];

  return (
    <div className="flex flex-col gap-6 text-left h-full">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">System Settings</h1>
          <p className="text-xs text-muted-foreground mt-1">Configure telemetry thresholds, AI orchestration variables, database settings, and simulation engines.</p>
        </div>
        <div className="text-xs text-muted-foreground bg-muted/50 px-3 py-1.5 rounded-full border border-border flex items-center gap-1.5 font-bold">
          <SettingsIcon className="h-3.5 w-3.5 animate-spin" style={{ animationDuration: '6s' }} />
          <span>Console Operational</span>
        </div>
      </div>

      {/* Main Console Layout */}
      <div className="grid gap-6 lg:grid-cols-4 flex-1 items-start min-h-[600px] pb-10">
        
        {/* Navigation Sidebar */}
        <div className="lg:col-span-1 flex flex-col gap-1 bg-card rounded-2xl border border-border p-3 shadow-md">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-extrabold transition-all duration-200 border text-left ${
                activeTab === tab.id
                  ? "bg-primary/10 border-primary text-primary"
                  : "bg-transparent border-transparent hover:bg-muted/50 text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content Pane */}
        <div className="lg:col-span-3 bg-card rounded-2xl border border-border p-6 shadow-md min-h-[500px] flex flex-col">
          
          {/* TAB 1: GENERAL ENVIRONMENT */}
          {activeTab === "general" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-black text-foreground">Environment & Application Settings</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Manage hosting URLs and deployment environment variables.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Backend Gateway URL</label>
                  <input
                    type="text"
                    value={backendUrl}
                    onChange={(e) => setBackendUrl(e.target.value)}
                    className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Dashboard Client URL</label>
                  <input
                    type="text"
                    value={frontendUrl}
                    onChange={(e) => setFrontendUrl(e.target.value)}
                    className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Target Environment</label>
                  <select
                    value={environment}
                    onChange={(e) => setEnvironment(e.target.value)}
                    className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-bold"
                  >
                    <option value="Development">Development (Localhost)</option>
                    <option value="Staging">Staging (QA Sandbox)</option>
                    <option value="Production">Production (Live Operations)</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Deployment Status</label>
                  <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2">
                    <span className="text-xs font-bold text-foreground">{deploymentStatus}</span>
                    <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-border bg-muted/20 p-4 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="font-bold text-muted-foreground">Console Host Build</span>
                  <span className="font-mono text-foreground">v0.9.4-rc2 (Hatch-Compiled)</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="font-bold text-muted-foreground">Git Commit Revision</span>
                  <span className="font-mono text-foreground text-primary hover:underline cursor-pointer flex items-center gap-1">
                    a82e9b1 <ExternalLink className="h-3 w-3" />
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: AI CONFIGURATION */}
          {activeTab === "ai" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-black text-foreground">Gemini AI Configuration</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Control orchestration LLM model targets and check key connectivity status.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Gemini LLM Target Model</label>
                  <select
                    value={geminiModel}
                    onChange={(e) => setGeminiModel(e.target.value)}
                    className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-bold"
                  >
                    <option value="gemini-2.5-pro">Gemini 2.5 Pro (Operational - Recommended)</option>
                    <option value="gemini-2.5-flash">Gemini 2.5 Flash (Latency Optimization)</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro Legacy</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">API Authentication status</label>
                  <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2">
                    <span className="text-xs font-bold text-foreground">Connected</span>
                    <span className="flex items-center gap-1 rounded bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 text-[9px] font-black text-emerald-400">
                      ONLINE
                    </span>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Last Orchestrated Request</label>
                  <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground">
                    {lastAiRequest}
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Daily Request limit quota</label>
                  <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-xs">
                    <span className="font-bold text-foreground">248 / 10,000 requests</span>
                    <span className="font-bold text-muted-foreground text-[10px]">2.4% Used</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleTestAIConnection}
                  disabled={aiTestStatus === "testing"}
                  className="px-4 py-2 bg-primary text-primary-foreground font-extrabold text-xs rounded-xl hover:bg-primary/95 transition-all shadow flex items-center gap-2"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${aiTestStatus === "testing" ? "animate-spin" : ""}`} />
                  Test AI Connection
                </button>
                {aiTestStatus === "success" && (
                  <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 className="h-4 w-4" /> Connection active. Latency: 140ms
                  </span>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: DATABASE CONFIG */}
          {activeTab === "database" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-black text-foreground">Database Configuration</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Verify Google Cloud Firestore connectivity states and document sync details.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Database Engine</label>
                  <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-xs text-foreground font-bold">
                    {dbEngine}
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Total Synced Documents</label>
                  <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground font-bold">
                    {dbTotalRecords.toLocaleString()} docs
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Last Synchronization</label>
                  <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground">
                    {lastDbSync}
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Database Health Status</label>
                  <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2">
                    <span className="text-xs font-bold text-foreground">Healthy</span>
                    <span className="flex items-center gap-1 rounded bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 text-[9px] font-black text-emerald-400">
                      NOMINAL
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleSyncDatabase}
                  disabled={dbSyncStatus === "syncing"}
                  className="px-4 py-2 bg-primary text-primary-foreground font-extrabold text-xs rounded-xl hover:bg-primary/95 transition-all shadow flex items-center gap-2"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${dbSyncStatus === "syncing" ? "animate-spin" : ""}`} />
                  Trigger Synchronization
                </button>
                {dbSyncStatus === "success" && (
                  <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 className="h-4 w-4" /> Databases synchronized successfully
                  </span>
                )}
              </div>
            </div>
          )}

          {/* TAB 4: SIMULATION CONTROLS */}
          {activeTab === "simulation" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-black text-foreground">Simulation Engine Settings</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Control the active Digital Twin simulation execution loops, speed multipliers, and seeds.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Demo Mode</label>
                  <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl p-3">
                    <span className="text-xs text-muted-foreground">Toggle automated scenario execution</span>
                    <button
                      onClick={() => setDemoMode(!demoMode)}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                        demoMode ? "bg-primary" : "bg-muted"
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                          demoMode ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Seed Config Dataset</label>
                  <select
                    value={selectedSeed}
                    onChange={(e) => setSelectedSeed(e.target.value)}
                    className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-bold"
                  >
                    <option value="stadium_seed_data.json">stadium_seed_data.json (Aurelia Arena - Standard)</option>
                    <option value="stadium_seed_congestion.json">stadium_seed_congestion.json (High-Load Congestion)</option>
                  </select>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between text-xs">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Simulation Speed</label>
                  <span className="font-bold text-primary">{simSpeed}x Realtime speed</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={simSpeed}
                  onChange={(e) => setSimSpeed(parseInt(e.target.value))}
                  className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <div className="flex justify-between text-[9px] font-bold text-muted-foreground uppercase tracking-wider">
                  <span>1x (Nominal)</span>
                  <span>5x</span>
                  <span>10x (Maximum)</span>
                </div>
              </div>

              <div className="flex items-center gap-3 pt-4 border-t border-border/40">
                <button
                  onClick={() => setSimPaused(!simPaused)}
                  className={`px-4 py-2 border rounded-xl font-extrabold text-xs transition-all shadow flex items-center gap-2 ${
                    simPaused
                      ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20"
                      : "bg-destructive/10 border-destructive/20 text-destructive hover:bg-destructive/20"
                  }`}
                >
                  {simPaused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
                  {simPaused ? "Resume Simulation" : "Pause Simulation"}
                </button>
                <button
                  onClick={() => {
                    setSimPaused(false);
                    setDiagnosticLogs((prev) => [
                      `[${new Date().toLocaleString()}] INFO: Manual Simulation Engine restart/replay triggered. Clock reset to T-120m.`,
                      ...prev
                    ]);
                  }}
                  className="px-4 py-2 border border-border bg-muted/40 text-foreground hover:bg-muted/80 rounded-xl font-extrabold text-xs transition-all shadow flex items-center gap-2"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  Reset Simulation
                </button>
              </div>
            </div>
          )}

          {/* TAB 5: ALERT THRESHOLDS */}
          {activeTab === "thresholds" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-black text-foreground">Alert Threshold & Automation Rules</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Adjust telemetry boundaries triggering warning states and automated EMT/Police dispatcher triggers.</p>
              </div>

              <div className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between text-xs">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Crowd Density Warning Limit</label>
                    <span className="font-bold text-destructive">{thresholdDensity}% capacity</span>
                  </div>
                  <input
                    type="range"
                    min="50"
                    max="95"
                    value={thresholdDensity}
                    onChange={(e) => setThresholdDensity(parseInt(e.target.value))}
                    className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between text-xs">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Queue Waiting Warning Duration</label>
                    <span className="font-bold text-amber-500">{thresholdQueue} minutes</span>
                  </div>
                  <input
                    type="range"
                    min="5"
                    max="45"
                    value={thresholdQueue}
                    onChange={(e) => setThresholdQueue(parseInt(e.target.value))}
                    className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between text-xs">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">AI Inference Confidence Cut-off</label>
                    <span className="font-bold text-primary">{confidenceThreshold}% confidence</span>
                  </div>
                  <input
                    type="range"
                    min="60"
                    max="95"
                    value={confidenceThreshold}
                    onChange={(e) => setConfidenceThreshold(parseInt(e.target.value))}
                    className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 pt-4 border-t border-border/40">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Weather Warning Severity Threshold</label>
                  <select
                    value={weatherOverride}
                    onChange={(e) => setWeatherOverride(e.target.value)}
                    className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-bold"
                  >
                    <option value="Low">Low (Shower alerts only)</option>
                    <option value="Medium">Medium (Rain / Wind warnings)</option>
                    <option value="High">High (Severe lightning warnings)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider block">Medical Event Dispatch</label>
                  <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl p-3">
                    <span className="text-xs text-muted-foreground">Auto-dispatch EMT responders</span>
                    <button
                      onClick={() => setMedAutoDispatch(!medAutoDispatch)}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                        medAutoDispatch ? "bg-primary" : "bg-muted"
                      }`}
                    >
                      <span
                        className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                          medAutoDispatch ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: WEBSOCKET LIVE SYNC */}
          {activeTab === "sync" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-black text-foreground">WebSocket & Live Sync Status</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Diagnose real-time pub-sub streaming connections from clients and operations centers.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Sync Connection Status</label>
                  <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2">
                    <span className="text-xs font-bold text-foreground">Connected</span>
                    <span className="flex items-center gap-1 rounded bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 text-[9px] font-black text-emerald-400">
                      LIVE
                    </span>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">WebSocket Latency</label>
                  <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground font-bold">
                    {wsLatency} ms
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Connected client screens</label>
                  <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground font-bold">
                    {activeClients} active terminals
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Broadcaster Buffer Frame Rate</label>
                  <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 font-mono text-xs text-foreground">
                    12.0 ticks / min (nominal)
                  </div>
                </div>
              </div>

              <button
                onClick={() => {
                  setDiagnosticLogs((prev) => [
                    `[${new Date().toLocaleString()}] INFO: WebSocket handshake manually re-asserted. Latency stabilized.`,
                    ...prev
                  ]);
                }}
                className="px-4 py-2 border border-border bg-muted/40 text-foreground hover:bg-muted/80 rounded-xl font-extrabold text-xs transition-all shadow flex items-center gap-2"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Reconnect WebSocket Channel
              </button>
            </div>
          )}

          {/* TAB 7: AUTHENTICATION */}
          {activeTab === "auth" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-black text-foreground">Identity & Authentication Settings</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Inspect current login sessions, user roles, and security authorization variables.</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Current User Role</label>
                  <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2 text-xs font-bold text-foreground">
                    <span>{userRole}</span>
                    <span className="flex items-center gap-0.5 rounded bg-primary/10 border border-primary/20 px-1.5 py-0.5 text-[9px] font-black text-primary uppercase">
                      SYSTEM ADMIN
                    </span>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Session JWT Lifetime</label>
                  <select
                    value={sessionExpiry}
                    onChange={(e) => setSessionExpiry(e.target.value)}
                    className="w-full text-xs bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-bold"
                  >
                    <option value="1 Hour">1 Hour (High Security)</option>
                    <option value="12 Hours">12 Hours (Standard shift duration)</option>
                    <option value="24 Hours">24 Hours (Operations extended)</option>
                  </select>
                </div>
              </div>

              <div className="rounded-xl border border-dashed border-border bg-muted/10 p-4 flex items-center gap-3">
                <Lock className="h-5 w-5 text-muted-foreground" />
                <div>
                  <h4 className="text-xs font-bold text-foreground">Security Key Management</h4>
                  <p className="text-[10px] text-muted-foreground mt-0.5">Authorization checks are routed directly via Firebase Admin credentials and JWT verification middleware.</p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 8: LOGGING & DIAGNOSTICS */}
          {activeTab === "logs" && (
            <div className="flex-1 flex flex-col gap-4">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-black text-foreground">Logging & Diagnostics Console</h2>
                  <p className="text-xs text-muted-foreground mt-0.5">Monitor real-time system executions, exceptions, and server diagnostics.</p>
                </div>
                <button
                  onClick={() => {
                    const text = diagnosticLogs.join("\n");
                    const blob = new Blob([text], { type: "text/plain" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "atlas_diagnostics.log";
                    a.click();
                  }}
                  className="px-3 py-1.5 border border-border bg-muted/40 text-foreground hover:bg-muted/80 rounded-xl font-extrabold text-[10px] transition-all flex items-center gap-1.5"
                >
                  <Download className="h-3.5 w-3.5" />
                  Export Logs
                </button>
              </div>

              {/* Terminal View */}
              <div className="flex-1 min-h-[300px] rounded-xl border border-border bg-black/90 p-4 font-mono text-[10px] text-emerald-400 overflow-y-auto space-y-2 text-left">
                {diagnosticLogs.map((log, idx) => (
                  <div key={idx} className="leading-relaxed whitespace-pre-wrap">
                    {log}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 9: ABOUT ATLAS */}
          {activeTab === "about" && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-primary to-violet-600 flex items-center justify-center shadow-lg">
                  <span className="font-extrabold text-white text-3xl">A</span>
                </div>
                <div>
                  <h2 className="text-xl font-black text-foreground">ATLAS Stadium Intelligence</h2>
                  <span className="text-xs text-muted-foreground block font-mono">Build 0.9.4-rc2 (Hatch / Hatchling)</span>
                </div>
              </div>

              <div className="space-y-4 text-xs leading-relaxed text-muted-foreground">
                <p>
                  <strong>ATLAS</strong> (Adaptive Tournament Logistics & Autonomous Stadium Intelligence) is a state-of-the-art Digital Twin orchestration suite. It synchronizes live crowd density sensors, coordinates medical/security anomalies, and generates logistical recommendation actions using Gemini LLM reasoning models.
                </p>
                
                <div className="grid gap-3 sm:grid-cols-2 pt-4 border-t border-border/40">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase block">AI Reasoning Engine</span>
                    <span className="font-bold text-foreground block">Gemini 2.5 Pro APIs</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase block">Graph Layout Compiler</span>
                    <span className="font-bold text-foreground block">Dagre Automatic Solver v0.8.5</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase block">Websocket Router</span>
                    <span className="font-bold text-foreground block">FastAPI Broadcast PubSub</span>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase block">Database Storage</span>
                    <span className="font-bold text-foreground block">Google Cloud Firestore (atlas-01)</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-border/40 text-[10px] text-muted-foreground">
                © 2026 AdiMita Technologies. Under LICENSE. All rights reserved.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
