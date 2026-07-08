import { useEffect, useState, useRef } from "react";
import { Search, Sun, Moon, Sparkles, Navigation } from "lucide-react";
import { useTheme } from "../providers/ThemeProvider";

interface CommandItem {
  id: string;
  name: string;
  category: string;
  icon: React.ReactNode;
  action: () => void;
}

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const { theme, setTheme } = useTheme();
  const modalRef = useRef<HTMLDivElement>(null);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const commands: CommandItem[] = [
    {
      id: "theme",
      name: `Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`,
      category: "System",
      icon: theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />,
      action: () => {
        toggleTheme();
        setIsOpen(false);
      },
    },
    {
      id: "nav-dash",
      name: "Go to Operations Overview",
      category: "Navigation",
      icon: <Navigation className="h-4 w-4" />,
      action: () => {
        window.location.hash = "/";
        setIsOpen(false);
      },
    },
    {
      id: "nav-incidents",
      name: "View Live Incidents List",
      category: "Navigation",
      icon: <Navigation className="h-4 w-4" />,
      action: () => {
        window.location.hash = "/incidents";
        setIsOpen(false);
      },
    },
    {
      id: "nav-metrics",
      name: "View Telemetry Metrics",
      category: "Navigation",
      icon: <Navigation className="h-4 w-4" />,
      action: () => {
        window.location.hash = "/metrics";
        setIsOpen(false);
      },
    },
  ];

  const filteredCommands = commands.filter((cmd) =>
    cmd.name.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === "Escape") {
        setIsOpen(false);
      } else if (e.key === "ArrowDown" && isOpen) {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredCommands.length);
      } else if (e.key === "ArrowUp" && isOpen) {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % filteredCommands.length);
      } else if (e.key === "Enter" && isOpen) {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].action();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, filteredCommands, selectedIndex]);

  // Handle clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 pt-[15vh] backdrop-blur-sm transition-opacity duration-300">
      <div
        ref={modalRef}
        className="w-full max-w-lg overflow-hidden rounded-2xl border border-border bg-card shadow-2xl transition-all duration-300 scale-100"
      >
        <div className="flex items-center border-b border-border px-4 py-3">
          <Search className="mr-3 h-5 w-5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Type a command or search..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelectedIndex(0);
            }}
            className="w-full bg-transparent pr-4 text-sm outline-none text-foreground"
            autoFocus
          />
          <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
            ESC
          </kbd>
        </div>

        <div className="max-h-[300px] overflow-y-auto p-2">
          {filteredCommands.length === 0 ? (
            <div className="px-4 py-6 text-center text-sm text-muted-foreground">
              No results found.
            </div>
          ) : (
            filteredCommands.map((cmd, idx) => (
              <div
                key={cmd.id}
                onClick={cmd.action}
                className={`flex cursor-pointer items-center justify-between rounded-xl px-4 py-3 transition-colors ${
                  idx === selectedIndex ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"
                }`}
              >
                <div className="flex items-center gap-3">
                  {cmd.icon}
                  <span className="text-sm font-medium">{cmd.name}</span>
                </div>
                <span className="text-xs uppercase tracking-wider opacity-65 font-semibold">
                  {cmd.category}
                </span>
              </div>
            ))
          )}
        </div>

        <div className="flex items-center justify-between border-t border-border px-4 py-2 bg-muted/30">
          <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
            <Sparkles className="h-3 w-3 text-primary animate-pulse" />
            <span>Use Arrow keys and Enter to execute</span>
          </div>
          <span className="text-[10px] text-muted-foreground">ATLAS Terminal v1.0</span>
        </div>
      </div>
    </div>
  );
}
