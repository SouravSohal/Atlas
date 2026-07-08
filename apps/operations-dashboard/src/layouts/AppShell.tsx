import { useState, useEffect } from "react";
import { Link } from "@tanstack/react-router";
import {
  Menu,
  Bell,
  User,
  Search,
  LayoutDashboard,
  AlertTriangle,
  Activity,
  Compass,
  Users,
  Brain,
  MapPin,
  TrendingUp,
  Settings,
  Moon,
  Sun,
  X,
  Wifi,
  WifiOff,
  ShieldCheck,
  HelpCircle,
  LogOut,
} from "lucide-react";
import { useTheme } from "../providers/ThemeProvider";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const { theme, setTheme } = useTheme();

  // Listen to network status
  useEffect(() => {
    const goOnline = () => setIsOnline(true);
    const goOffline = () => setIsOnline(false);
    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);
    return () => {
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
    };
  }, []);

  const navigation = [
    { name: "Overview", to: "/", icon: <LayoutDashboard className="h-5 w-5" /> },
    { name: "ATLAS Copilot", to: "/copilot", icon: <Brain className="h-5 w-5 animate-pulse text-primary" /> },
    { name: "Incidents", to: "/incidents", icon: <AlertTriangle className="h-5 w-5" /> },
    { name: "Operational State", to: "/operational-state", icon: <Activity className="h-5 w-5" /> },
    { name: "Recommendations", to: "/recommendations", icon: <Compass className="h-5 w-5" /> },
    { name: "Volunteers", to: "/volunteers", icon: <Users className="h-5 w-5" /> },
    { name: "Crowd Intelligence", to: "/crowd-intelligence", icon: <Brain className="h-5 w-5" /> },
    { name: "Navigation", to: "/navigation", icon: <MapPin className="h-5 w-5" /> },
    { name: "Notifications", to: "/notifications", icon: <Bell className="h-5 w-5" /> },
    { name: "Analytics", to: "/analytics", icon: <TrendingUp className="h-5 w-5" /> },
    { name: "Settings", to: "/settings", icon: <Settings className="h-5 w-5" /> },
  ];

  const mockNotifications = [
    {
      id: 1,
      title: "Queue warning in Zone B",
      description: "Average waiting duration has exceeded 20 minutes.",
      time: "3 mins ago",
    },
    {
      id: 2,
      title: "Task Assigned",
      description: "Volunteer deployed to check broken turnstile at gate A.",
      time: "15 mins ago",
    },
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground transition-colors duration-300">
      {/* LEFT COLLAPSIBLE SIDEBAR */}
      <aside
        aria-label="Sidebar Navigation"
        className={`fixed inset-y-0 left-0 z-20 flex flex-col border-r border-border bg-card transition-all duration-300 ${
          sidebarOpen ? "w-64" : "w-20"
        }`}
      >
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between px-6 border-b border-border">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold text-lg shadow-lg">
              A
            </div>
            {sidebarOpen && (
              <span className="text-md font-bold tracking-wider uppercase text-foreground">
                ATLAS
              </span>
            )}
          </div>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label={sidebarOpen ? "Collapse sidebar navigation" : "Expand sidebar navigation"}
            className="rounded-lg p-1.5 hover:bg-muted text-muted-foreground transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
          >
            <Menu className="h-5 w-5" />
          </button>
        </div>

        {/* Sidebar Nav Links */}
        <nav className="flex-1 space-y-1 p-3 overflow-y-auto" aria-label="Main Navigation Menu">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.to}
              activeProps={{ className: "bg-primary text-primary-foreground shadow-sm" }}
              inactiveProps={{ className: "text-muted-foreground hover:bg-muted hover:text-foreground" }}
              className="flex items-center gap-4 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200 focus-visible:ring-2 focus-visible:ring-primary outline-none"
            >
              <div className="shrink-0">{item.icon}</div>
              {sidebarOpen && <span className="truncate">{item.name}</span>}
            </Link>
          ))}
        </nav>

        {/* Sidebar Footer info */}
        <div className="border-t border-border p-4">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
              <User className="h-5 w-5" />
            </div>
            {sidebarOpen && (
              <div className="flex flex-col text-left">
                <span className="text-xs font-bold truncate text-foreground">Ops Commander</span>
                <span className="text-[10px] text-muted-foreground truncate">commander@atlas.com</span>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* HEADER & MAIN CONTENT WRAPPER */}
      <div className={`flex flex-1 flex-col transition-all duration-300 ${sidebarOpen ? "pl-64" : "pl-20"}`}>
        
        {/* HEADER TOP BAR */}
        <header
          role="banner"
          className="flex h-16 items-center justify-between border-b border-border bg-card/65 px-8 backdrop-blur-md sticky top-0 z-10"
        >
          {/* Left: Search Trigger */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                const event = new KeyboardEvent("keydown", { ctrlKey: true, key: "k" });
                window.dispatchEvent(event);
              }}
              aria-label="Open Command Palette search"
              className="flex items-center gap-2 rounded-xl border border-border bg-muted/50 px-4 py-2.5 text-xs font-semibold text-muted-foreground hover:bg-muted transition-colors w-48 md:w-64 text-left justify-between focus-visible:ring-2 focus-visible:ring-primary outline-none"
            >
              <span className="flex items-center gap-2">
                <Search className="h-4 w-4" />
                Search (Ctrl+K)...
              </span>
              <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-1 rounded bg-card border border-border px-1.5 font-mono text-[9px] font-medium text-muted-foreground">
                Ctrl K
              </kbd>
            </button>
          </div>

          {/* Right: Telemetry & Actions */}
          <div className="flex items-center gap-4">
            
            {/* Global Status Indicator */}
            <div
              aria-label="Global Stadium Health Status"
              className="hidden lg:flex items-center gap-2 rounded-full border border-border bg-muted/30 px-3 py-1 text-xs font-semibold"
            >
              <ShieldCheck className="h-4 w-4 text-emerald-500" />
              <span>System: Healthy</span>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
            </div>

            {/* Connection Status Pill */}
            <div
              aria-label="Network connection status"
              className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${
                isOnline
                  ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-500"
                  : "border-destructive/20 bg-destructive/10 text-destructive animate-pulse"
              }`}
            >
              {isOnline ? (
                <>
                  <Wifi className="h-3.5 w-3.5" />
                  <span>Online</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-3.5 w-3.5" />
                  <span>Offline</span>
                </>
              )}
            </div>

            {/* Theme Switcher Toggle */}
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              aria-label="Toggle visual theme"
              className="rounded-xl p-2 hover:bg-muted text-muted-foreground transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
            >
              {theme === "dark" ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5" />}
            </button>

            {/* Notification Area Trigger */}
            <div className="relative">
              <button
                onClick={() => setNotifOpen(!notifOpen)}
                aria-label="View recent alerts and events"
                aria-expanded={notifOpen}
                aria-haspopup="true"
                className={`rounded-xl p-2 hover:bg-muted text-muted-foreground transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none ${
                  notifOpen ? "bg-muted" : ""
                }`}
              >
                <Bell className="h-5 w-5" />
                <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive animate-pulse" />
              </button>

              {/* Notification Overlay Popover */}
              {notifOpen && (
                <div
                  role="dialog"
                  aria-label="Notifications panel"
                  className="absolute right-0 mt-3 w-80 rounded-2xl border border-border bg-card shadow-2xl p-4 animate-in fade-in slide-in-from-top-2 duration-200"
                >
                  <div className="flex items-center justify-between border-b border-border pb-2 mb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                      Live alerts feed
                    </span>
                    <button
                      onClick={() => setNotifOpen(false)}
                      aria-label="Close alerts panel"
                      className="rounded-full p-1 hover:bg-muted text-muted-foreground transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="space-y-3">
                    {mockNotifications.map((notif) => (
                      <div
                        key={notif.id}
                        className="flex gap-3 items-start p-2.5 rounded-xl bg-muted/30 hover:bg-muted/70 cursor-pointer transition-colors"
                      >
                        <div className="mt-0.5 rounded-full p-1 bg-primary/10 text-primary">
                          <Activity className="h-3.5 w-3.5 animate-pulse" />
                        </div>
                        <div className="flex flex-col text-left">
                          <span className="text-xs font-bold">{notif.title}</span>
                          <span className="text-[10px] text-muted-foreground mt-0.5">
                            {notif.description}
                          </span>
                          <span className="text-[9px] text-primary font-medium mt-1.5">
                            {notif.time}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 border-t border-border pt-2 text-center">
                    <button className="text-xs font-bold text-primary hover:underline focus-visible:ring-2 focus-visible:ring-primary outline-none rounded">
                      Mark all as read
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Profile Selector Menu */}
            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                aria-label="Operations profile menu dropdown"
                aria-expanded={profileOpen}
                aria-haspopup="true"
                className="flex h-10 w-10 items-center justify-center rounded-full bg-muted border border-border hover:bg-muted/70 transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
              >
                <User className="h-5 w-5 text-muted-foreground" />
              </button>

              {/* User Dropdown Options list */}
              {profileOpen && (
                <div
                  role="menu"
                  aria-label="User profile items"
                  className="absolute right-0 mt-3 w-56 rounded-2xl border border-border bg-card shadow-2xl p-2 animate-in fade-in slide-in-from-top-2 duration-200"
                >
                  <div className="px-4 py-3 border-b border-border">
                    <span className="block text-xs font-bold text-foreground">Stadium Director</span>
                    <span className="block text-[10px] text-muted-foreground mt-0.5">director@atlas.com</span>
                  </div>
                  <div className="mt-2 space-y-0.5">
                    <button
                      role="menuitem"
                      className="flex w-full items-center gap-3 rounded-lg px-4 py-2.5 text-xs font-semibold text-muted-foreground hover:bg-muted hover:text-foreground transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
                    >
                      <Settings className="h-4 w-4" />
                      Configuration Settings
                    </button>
                    <button
                      role="menuitem"
                      className="flex w-full items-center gap-3 rounded-lg px-4 py-2.5 text-xs font-semibold text-muted-foreground hover:bg-muted hover:text-foreground transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
                    >
                      <HelpCircle className="h-4 w-4" />
                      Operations Manual
                    </button>
                    <button
                      role="menuitem"
                      className="flex w-full items-center gap-3 rounded-lg px-4 py-2.5 text-xs font-semibold text-destructive hover:bg-destructive/10 transition-colors focus-visible:ring-2 focus-visible:ring-primary outline-none"
                    >
                      <LogOut className="h-4 w-4" />
                      End Operations Session
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* MAIN BODY CONTENT AREA */}
        <main
          id="main-content"
          role="main"
          className="flex-1 overflow-y-auto p-8 focus:outline-none"
        >
          {children}
        </main>
      </div>
    </div>
  );
}
