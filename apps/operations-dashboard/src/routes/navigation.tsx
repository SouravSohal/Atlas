import { useState, useMemo } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  MapPin,
  Compass,
  Sparkles,
} from "lucide-react";
import { motion } from "framer-motion";

export const Route = createFileRoute("/navigation")({
  component: NavigationIntelligencePage,
});

const STADIUM_ZONES = [
  { id: "gate-1", name: "Gate 1 Ingress" },
  { id: "gate-2", name: "Gate 2 Exit" },
  { id: "sec-hq", name: "Security Command" },
  { id: "med-post", name: "Medical Post Alpha" },
  { id: "parking", name: "Main Parking Area" },
  { id: "food-plaza", name: "Central Food Plaza" },
];

function NavigationIntelligencePage() {
  const [origin, setOrigin] = useState("gate-1");
  const [destination, setDestination] = useState("med-post");
  const [navMode, setNavMode] = useState("Volunteers");
  
  // Checkboxes
  const [accessibility, setAccessibility] = useState(false);
  const [crowdAvoidance, setCrowdAvoidance] = useState(true);
  const [fastestRoute, setFastestRoute] = useState(true);
  const [safestRoute, setSafestRoute] = useState(false);

  // Dynamic route rendering logic
  const routeAnalysis = useMemo(() => {
    const origName = STADIUM_ZONES.find((z) => z.id === origin)?.name || "Gate 1";
    const destName = STADIUM_ZONES.find((z) => z.id === destination)?.name || "Medical Post";

    const baseTime = navMode === "Emergency Evacuation" ? 1.5 : 4.0;
    const timeVal = accessibility ? baseTime + 1.5 : baseTime;

    return {
      recommendedRoute: `${origName} ➔ Central Corridor ➔ ${destName}`,
      estimatedTime: `${timeVal.toFixed(1)} minutes`,
      congestionScore: crowdAvoidance ? "18% (Low)" : "68% (High)",
      accessibilityRating: accessibility || navMode === "Wheelchair Accessible" ? "100% - Fully Accessible" : "75% - Standard Stairs",
      crowdDensity: crowdAvoidance ? "Moderate" : "Dense Congestion",
      riskLevel: safestRoute ? "Nominal" : "Medium Warning Index",
      alternatives: [
        `Alt 1: ${origName} ➔ External Perimeter Ring ➔ ${destName} (Est: ${(timeVal + 2.5).toFixed(1)} mins)`,
        `Alt 2: ${origName} ➔ Food Plaza Walkway ➔ ${destName} (Est: ${(timeVal + 1.0).toFixed(1)} mins)`
      ]
    };
  }, [origin, destination, navMode, accessibility, crowdAvoidance, safestRoute]);

  // Coordinate mapping for SVG path visual
  const pathVisual = useMemo(() => {
    const coords: Record<string, string> = {
      "gate-1": "M 80,180",
      "gate-2": "L 480,180",
      "sec-hq": "L 280,70",
      "med-post": "L 280,290",
      "parking": "L 80,70",
      "food-plaza": "L 480,290",
    };

    const start = coords[origin] || "M 80,180";
    const end = coords[destination] || "L 280,290";
    return `${start} ${end}`;
  }, [origin, destination]);

  return (
    <div className="flex flex-col gap-6 text-foreground min-h-[calc(100vh-6rem)] relative">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-border pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <MapPin className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight uppercase">Navigation Intelligence</h1>
            <p className="text-xs text-muted-foreground mt-0.5 uppercase tracking-wider font-semibold">
              AI-Assisted Operational Routing & Egress Path Balancer
            </p>
          </div>
        </div>
      </div>

      {/* Main 3-Column Layout */}
      <div className="grid gap-6 lg:grid-cols-4">
        {/* Left: Route Requests & Form */}
        <div className="rounded-2xl border border-border bg-card/65 backdrop-blur-md p-5 shadow-lg flex flex-col gap-5 text-left h-fit">
          <span className="text-[10px] font-black text-primary uppercase tracking-widest border-b border-border/40 pb-2">
            Configure Route Request
          </span>

          <div className="flex flex-col gap-4 text-xs">
            {/* Origin */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">Origin</label>
              <select
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                className="rounded-xl border border-border bg-muted/20 px-3 py-2 font-bold outline-none cursor-pointer text-foreground"
              >
                {STADIUM_ZONES.map((z) => (
                  <option key={z.id} value={z.id}>{z.name}</option>
                ))}
              </select>
            </div>

            {/* Destination */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">Destination</label>
              <select
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="rounded-xl border border-border bg-muted/20 px-3 py-2 font-bold outline-none cursor-pointer text-foreground"
              >
                {STADIUM_ZONES.map((z) => (
                  <option key={z.id} value={z.id}>{z.name}</option>
                ))}
              </select>
            </div>

            {/* Nav Mode */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-wider">Navigation Mode</label>
              <select
                value={navMode}
                onChange={(e) => setNavMode(e.target.value)}
                className="rounded-xl border border-border bg-muted/20 px-3 py-2 font-bold outline-none cursor-pointer text-foreground"
              >
                {["Spectators", "Staff", "Volunteers", "Security", "Medical", "VIP", "Wheelchair Accessible", "Emergency Evacuation"].map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>

            {/* Checkbox Options */}
            <div className="flex flex-col gap-3.5 border-t border-border/40 pt-4 mt-1.5">
              <label className="flex items-center gap-2 cursor-pointer font-bold select-none">
                <input
                  type="checkbox"
                  checked={accessibility}
                  onChange={(e) => setAccessibility(e.target.checked)}
                  className="rounded border-border accent-primary cursor-pointer w-4.5 h-4.5"
                />
                <span>Wheelchair Accessible</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer font-bold select-none">
                <input
                  type="checkbox"
                  checked={crowdAvoidance}
                  onChange={(e) => setCrowdAvoidance(e.target.checked)}
                  className="rounded border-border accent-primary cursor-pointer w-4.5 h-4.5"
                />
                <span>Crowd Avoidance</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer font-bold select-none">
                <input
                  type="checkbox"
                  checked={fastestRoute}
                  onChange={(e) => setFastestRoute(e.target.checked)}
                  className="rounded border-border accent-primary cursor-pointer w-4.5 h-4.5"
                />
                <span>Fastest Routing path</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer font-bold select-none">
                <input
                  type="checkbox"
                  checked={safestRoute}
                  onChange={(e) => setSafestRoute(e.target.checked)}
                  className="rounded border-border accent-primary cursor-pointer w-4.5 h-4.5"
                />
                <span>Safest Corridor Route</span>
              </label>
            </div>
          </div>
        </div>

        {/* Center: Interactive SVG Map (2 Cols wide) */}
        <div className="lg:col-span-2 rounded-2xl border border-border bg-card/45 backdrop-blur-md p-5 shadow-lg relative flex flex-col justify-between overflow-hidden">
          <div className="flex items-center justify-between border-b border-border/40 pb-3 mb-4">
            <span className="text-xs font-black text-foreground uppercase tracking-widest flex items-center gap-1.5">
              <Compass className="h-4 w-4 text-emerald-400 animate-spin" />
              Live Interactive Stadium Flow Map
            </span>
            <span className="text-[9px] font-mono text-muted-foreground uppercase">Map Scale: Grid Auto</span>
          </div>

          {/* SVG Map Canvas */}
          <div className="flex-1 w-full min-h-[300px] border border-border bg-muted/20 rounded-xl relative overflow-hidden flex items-center justify-center">
            {/* Legend Pins */}
            <div className="absolute top-4 left-4 flex flex-wrap gap-2 text-[8px] font-black uppercase text-muted-foreground tracking-wider pointer-events-none bg-card/60 backdrop-blur border border-border rounded-lg p-2.5">
              <div className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-emerald-500" /> stable</div>
              <div className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" /> warning</div>
              <div className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-destructive animate-pulse" /> restricted</div>
            </div>

            <svg className="w-full h-full min-h-[300px]" viewBox="0 0 560 360">
              {/* Grid Background */}
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255, 255, 255, 0.03)" strokeWidth="1" />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />

              {/* Closed gate restricted area */}
              <circle cx="280" cy="70" r="28" fill="rgba(239, 68, 68, 0.05)" stroke="rgba(239, 68, 68, 0.2)" strokeWidth="1" strokeDasharray="3,3" />

              {/* Stadium Outer Ring layout */}
              <rect x="50" y="30" width="460" height="300" rx="30" fill="none" stroke="rgba(255, 255, 255, 0.06)" strokeWidth="6" />

              {/* Nodes representations */}
              {/* Gate 1 Ingress */}
              <circle cx="80" cy="180" r="16" className="fill-emerald-500/10 stroke-emerald-500/40" strokeWidth="2" />
              <text x="80" y="184" textAnchor="middle" fill="#10b981" fontSize="9" fontWeight="bold">G1</text>

              {/* Gate 2 Exit */}
              <circle cx="480" cy="180" r="16" className="fill-emerald-500/10 stroke-emerald-500/40" strokeWidth="2" />
              <text x="480" y="184" textAnchor="middle" fill="#10b981" fontSize="9" fontWeight="bold">G2</text>

              {/* Security Command */}
              <circle cx="280" cy="70" r="16" className="fill-destructive/10 stroke-destructive/40" strokeWidth="2 animate-pulse" />
              <text x="280" y="74" textAnchor="middle" fill="#ef4444" fontSize="9" fontWeight="bold">SEC</text>

              {/* Medical Post Alpha */}
              <circle cx="280" cy="290" r="16" className="fill-emerald-500/10 stroke-emerald-500/40" strokeWidth="2" />
              <text x="280" y="294" textAnchor="middle" fill="#10b981" fontSize="9" fontWeight="bold">MED</text>

              {/* Main Parking Area */}
              <circle cx="80" cy="70" r="16" className="fill-amber-500/10 stroke-amber-500/40" strokeWidth="2" />
              <text x="80" y="74" textAnchor="middle" fill="#f59e0b" fontSize="9" fontWeight="bold">PRK</text>

              {/* Central Food Plaza */}
              <circle cx="480" cy="290" r="16" className="fill-emerald-500/10 stroke-emerald-500/40" strokeWidth="2" />
              <text x="480" y="294" textAnchor="middle" fill="#10b981" fontSize="9" fontWeight="bold">FOD</text>

              {/* Animated Recommended Route Path */}
              <motion.path
                d={pathVisual}
                fill="none"
                stroke="#3b82f6"
                strokeWidth="4"
                strokeLinecap="round"
                strokeDasharray="8,8"
                animate={{ strokeDashoffset: [0, -40] }}
                transition={{ repeat: Infinity, ease: "linear", duration: 2 }}
              />
            </svg>
          </div>
        </div>

        {/* Right: AI Route Analysis */}
        <div className="rounded-2xl border border-border bg-card/65 backdrop-blur-md p-5 shadow-lg flex flex-col justify-between text-left h-fit gap-5">
          <div>
            <div className="flex items-center gap-2 border-b border-border/40 pb-3 mb-4">
              <Sparkles className="h-4 w-4 text-primary animate-pulse" />
              <span className="text-xs font-black text-foreground uppercase tracking-widest">
                AI Route Analysis
              </span>
            </div>

            <div className="flex flex-col gap-4 text-xs">
              <div className="flex flex-col">
                <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
                  RECOMMENDED PATHWAY
                </span>
                <span className="font-bold text-foreground mt-0.5 text-[11px] font-mono leading-relaxed">
                  {routeAnalysis.recommendedRoute}
                </span>
              </div>

              <div className="flex flex-col">
                <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
                  ESTIMATED TRAVEL TIME
                </span>
                <span className="font-black text-primary text-sm mt-0.5">
                  {routeAnalysis.estimatedTime}
                </span>
              </div>

              <div className="flex flex-col">
                <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
                  CONGESTION INDEX
                </span>
                <span className="font-bold text-foreground mt-0.5 uppercase">
                  {routeAnalysis.congestionScore}
                </span>
              </div>

              <div className="flex flex-col">
                <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
                  ACCESSIBILITY RATING
                </span>
                <span className="font-bold text-foreground mt-0.5 uppercase">
                  {routeAnalysis.accessibilityRating}
                </span>
              </div>

              <div className="flex flex-col">
                <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
                  RISK ASSESSMENT
                </span>
                <span className="font-bold text-foreground mt-0.5 uppercase">
                  {routeAnalysis.riskLevel}
                </span>
              </div>

              <div className="flex flex-col border-t border-border/40 pt-4 mt-1.5">
                <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">
                  Alternative Routes Considered
                </span>
                <div className="flex flex-col gap-2 mt-2">
                  {routeAnalysis.alternatives.map((alt, idx) => (
                    <div key={idx} className="rounded-lg bg-muted/20 border border-border p-2.5 text-[10px] text-muted-foreground font-mono leading-relaxed">
                      {alt}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
