import { useState } from "react";
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
  BarChart3,
  Moon,
  Sun,
  X,
  HelpCircle,
  LogOut,
  Settings,
} from "lucide-react";
import { useTheme } from "../providers/ThemeProvider";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const { theme, setTheme } = useTheme();

  const navigation = [
    { name: "Overview", to: "/", icon: <LayoutDashboard className="h-5 w-5" /> },
    { name: "Incidents", to: "/incidents", icon: <AlertTriangle className="h-5 w-5" /> },
    { name: "Operational State", to: "/operational-state", icon: <Activity className="h-5 w-5" /> },
    { name: "Recommendations", to: "/recommendations", icon: <Compass className="h-5 w-5" /> },
    { name: "Metrics", to: "/metrics", icon: <BarChart3 className="h-5 w-5" /> },
  ];

  const mockNotifications = [
    {
      id: 1,
      title: "High Density in Zone A",
      description: "Crowd density has reached 0.85 in Sector 2.",
      time: "2 mins ago",
      type: "alert",
    },
    {
      id: 2,
      title: "Incident Resolved",
      description: "Medical emergency at Gate C has been marked resolved.",
      time: "10 mins ago",
      type: "info",
    },
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground transition-colors duration-300">
      {/* LEFT SIDEBAR */}
      <aside
        className={`fixed inset-y-0 left-0 z-20 flex flex-col border-r border-border bg-card transition-all duration-300 ${
          sidebarOpen ? "w-64" : "w-20"
        }`}
      >
        {/* Brand */}
        <div className="flex h-16 items-center justify-between px-6 border-b border-border">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold text-lg shadow-lg">
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
            className="rounded-lg p-1.5 hover:bg-muted text-muted-foreground transition-colors"
          >
            <Menu className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 space-y-1.5 p-4">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.to}
              activeProps={{ className: "bg-primary text-primary-foreground shadow-md" }}
              inactiveProps={{ className: "text-muted-foreground hover:bg-muted hover:text-foreground" }}
              className="flex items-center gap-4 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200"
            >
              {item.icon}
              {sidebarOpen && <span>{item.name}</span>}
            </Link>
          ))}
        </nav>

        {/* User Footer info (optional preview) */}
        <div className="border-t border-border p-4">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
              <User className="h-5 w-5" />
            </div>
            {sidebarOpen && (
              <div className="flex flex-col text-left">
                <span className="text-xs font-bold truncate">Ops Commander</span>
                <span className="text-[10px] text-muted-foreground truncate">commander@atlas.com</span>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* MAIN LAYOUT WRAPPER */}
      <div className={`flex flex-1 flex-col transition-all duration-300 ${sidebarOpen ? "pl-64" : "pl-20"}`}>
        {/* TOP NAVIGATION HEADER */}
        <header className="flex h-16 items-center justify-between border-b border-border bg-card/65 px-8 backdrop-blur-md sticky top-0 z-10">
          {/* Left: Search Trigger */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                const event = new KeyboardEvent("keydown", { ctrlKey: true, key: "k" });
                window.dispatchEvent(event);
              }}
              className="flex items-center gap-2 rounded-xl border border-border bg-muted/50 px-4 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted transition-colors w-48 md:w-64 text-left justify-between"
            >
              <span className="flex items-center gap-2">
                <Search className="h-4 w-4" />
                Quick Search...
              </span>
              <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-1 rounded bg-card border border-border px-1.5 font-mono text-[9px] font-medium text-muted-foreground">
                Ctrl K
              </kbd>
            </button>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-4">
            {/* Theme Toggle */}
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="rounded-xl p-2 hover:bg-muted text-muted-foreground transition-colors"
            >
              {theme === "dark" ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5" />}
            </button>

            {/* Notification Trigger */}
            <div className="relative">
              <button
                onClick={() => setNotifOpen(!notifOpen)}
                className={`rounded-xl p-2 hover:bg-muted text-muted-foreground transition-colors ${
                  notifOpen ? "bg-muted" : ""
                }`}
              >
                <Bell className="h-5 w-5" />
                <span className="absolute top-1.5 right-1.5 h-2.5 w-2.5 rounded-full bg-destructive animate-pulse" />
              </button>

              {/* NOTIFICATION PANEL (Dropdown) */}
              {notifOpen && (
                <div className="absolute right-0 mt-3 w-80 rounded-2xl border border-border bg-card shadow-2xl p-4 animate-in fade-in slide-in-from-top-2 duration-200">
                  <div className="flex items-center justify-between border-b border-border pb-2 mb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                      Operational Alerts
                    </span>
                    <button
                      onClick={() => setNotifOpen(false)}
                      className="rounded-full p-1 hover:bg-muted text-muted-foreground transition-colors"
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
                        <div className="mt-0.5 rounded-full p-1 bg-destructive/10 text-destructive">
                          <AlertTriangle className="h-3.5 w-3.5" />
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
                    <button className="text-xs font-bold text-primary hover:underline">
                      Mark all as read
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex h-10 w-10 items-center justify-center rounded-full bg-muted border border-border hover:bg-muted/70 transition-colors"
              >
                <User className="h-5 w-5 text-muted-foreground" />
              </button>

              {/* USER PROFILE MENU */}
              {profileOpen && (
                <div className="absolute right-0 mt-3 w-56 rounded-2xl border border-border bg-card shadow-2xl p-2 animate-in fade-in slide-in-from-top-2 duration-200">
                  <div className="px-4 py-3 border-b border-border">
                    <span className="block text-xs font-bold text-foreground">Stadium Director</span>
                    <span className="block text-[10px] text-muted-foreground mt-0.5">director@atlas.com</span>
                  </div>
                  <div className="mt-2 space-y-0.5">
                    <button className="flex w-full items-center gap-3 rounded-lg px-4 py-2.5 text-xs font-semibold text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
                      <Settings className="h-4 w-4" />
                      Configuration Settings
                    </button>
                    <button className="flex w-full items-center gap-3 rounded-lg px-4 py-2.5 text-xs font-semibold text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
                      <HelpCircle className="h-4 w-4" />
                      Help & Support Documentation
                    </button>
                    <button className="flex w-full items-center gap-3 rounded-lg px-4 py-2.5 text-xs font-semibold text-destructive hover:bg-destructive/10 transition-colors">
                      <LogOut className="h-4 w-4" />
                      Logout Session
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* MAIN CONTENT AREA */}
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}
