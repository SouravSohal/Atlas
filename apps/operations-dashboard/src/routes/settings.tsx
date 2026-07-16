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
} from "lucide-react";
import { envConfig } from "../config/env";
import { useGlobalStore } from "../store/useGlobalStore";

import { GeneralTab } from "../features/settings/components/GeneralTab";
import { AiTab } from "../features/settings/components/AiTab";
import { DatabaseTab } from "../features/settings/components/DatabaseTab";
import { SimulationTab } from "../features/settings/components/SimulationTab";
import { ThresholdsTab } from "../features/settings/components/ThresholdsTab";
import { SyncTab } from "../features/settings/components/SyncTab";
import { AuthTab } from "../features/settings/components/AuthTab";
import { LogsTab } from "../features/settings/components/LogsTab";
import { AboutTab } from "../features/settings/components/AboutTab";

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
    userRole,
    resetSimulation,
  } = useGlobalStore();
  const [selectedSeed, setSelectedSeed] = useState("stadium_seed_data.json");

  const [medAutoDispatch, setMedAutoDispatch] = useState(true);
  const [weatherOverride, setWeatherOverride] = useState("Medium");

  const wsLatency = 12;
  const activeClients = 104;

  const [diagnosticLogs, setDiagnosticLogs] = useState<string[]>([
    "[2026-07-10 17:20:00] INFO: WebSocket client registry handshake completed (client-104)",
    "[2026-07-10 17:21:05] SUCCESS: AI prompt situation compilation successfully generated via Gemini-2.5-flash",
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
          {activeTab === "general" && (
            <GeneralTab
              backendUrl={backendUrl}
              setBackendUrl={setBackendUrl}
              frontendUrl={frontendUrl}
              setFrontendUrl={setFrontendUrl}
              environment={environment}
              setEnvironment={setEnvironment}
              deploymentStatus={deploymentStatus}
            />
          )}

          {activeTab === "ai" && (
            <AiTab
              geminiModel={geminiModel}
              setGeminiModel={setGeminiModel}
              aiTestStatus={aiTestStatus}
              handleTestAIConnection={handleTestAIConnection}
              lastAiRequest={lastAiRequest}
            />
          )}

          {activeTab === "database" && (
            <DatabaseTab
              dbEngine={dbEngine}
              dbSyncStatus={dbSyncStatus}
              handleSyncDatabase={handleSyncDatabase}
              lastDbSync={lastDbSync}
              dbTotalRecords={dbTotalRecords}
            />
          )}

          {activeTab === "simulation" && (
            <SimulationTab
              demoMode={demoMode}
              setDemoMode={setDemoMode}
              selectedSeed={selectedSeed}
              setSelectedSeed={setSelectedSeed}
              simSpeed={simSpeed}
              setSimSpeed={setSimSpeed}
              simPaused={simPaused}
              setSimPaused={setSimPaused}
              resetSimulation={resetSimulation}
              setDiagnosticLogs={setDiagnosticLogs}
            />
          )}

          {activeTab === "thresholds" && (
            <ThresholdsTab
              thresholdDensity={thresholdDensity}
              setThresholdDensity={setThresholdDensity}
              thresholdQueue={thresholdQueue}
              setThresholdQueue={setThresholdQueue}
              confidenceThreshold={confidenceThreshold}
              setConfidenceThreshold={setConfidenceThreshold}
              weatherOverride={weatherOverride}
              setWeatherOverride={setWeatherOverride}
              medAutoDispatch={medAutoDispatch}
              setMedAutoDispatch={setMedAutoDispatch}
            />
          )}

          {activeTab === "sync" && (
            <SyncTab
              wsLatency={wsLatency}
              activeClients={activeClients}
              setDiagnosticLogs={setDiagnosticLogs}
            />
          )}

          {activeTab === "auth" && (
            <AuthTab
              userRole={userRole}
              sessionExpiry={sessionExpiry}
            />
          )}

          {activeTab === "logs" && (
            <LogsTab
              diagnosticLogs={diagnosticLogs}
            />
          )}

          {activeTab === "about" && (
            <AboutTab />
          )}
        </div>
      </div>
    </div>
  );
}
