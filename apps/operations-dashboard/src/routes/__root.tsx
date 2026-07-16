import { useEffect, useState } from "react";
import { createRootRoute, Outlet, useLocation, useNavigate } from "@tanstack/react-router";
import { ThemeProvider } from "../providers/ThemeProvider";
import { AppShell } from "../layouts/AppShell";
import { CommandPalette } from "../components/CommandPalette";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { useGlobalStore } from "../store/useGlobalStore";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X } from "lucide-react";
import { auth } from "../services/firebase";
import { onAuthStateChanged } from "firebase/auth";
import { envConfig } from "../config/env";
import { AriaLiveAnnouncer } from "../components/AriaLiveAnnouncer";

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  const location = useLocation();
  const navigate = useNavigate();
  const { accessToken } = useGlobalStore();

  const [showWelcome, setShowWelcome] = useState(false);

  const isLoginPage = location.pathname === "/login";

  // 1. Session Recovery & Navigation Guards
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          const idToken = await firebaseUser.getIdToken();
          const storedUser = localStorage.getItem("atlas_user");
          let dbUser = storedUser ? JSON.parse(storedUser) : null;

          if (!dbUser || dbUser.email !== firebaseUser.email) {
            const profileRes = await fetch(`${envConfig.apiUrl}/auth/me`, {
              headers: {
                Authorization: `Bearer ${idToken}`,
              },
            });
            if (profileRes.ok) {
              const profileData = await profileRes.json();
              dbUser = profileData?.data;
            }
          }

          if (dbUser) {
            const isDemo = firebaseUser.email === envConfig.demoEmail;
            localStorage.setItem("atlas_access_token", idToken);
            localStorage.setItem("atlas_user", JSON.stringify(dbUser));
            localStorage.setItem("atlas_is_demo", isDemo ? "true" : "false");

            useGlobalStore.setState({
              accessToken: idToken,
              refreshToken: firebaseUser.refreshToken,
              user: dbUser,
              userRole: dbUser.role,
              isDemoSession: isDemo,
            });

            if (location.pathname === "/login") {
              navigate({ to: "/" });
            }
          }
        } catch (err) {
          console.error("Failed to restore Firebase session", err);
        }
      } else {
        localStorage.removeItem("atlas_access_token");
        localStorage.removeItem("atlas_refresh_token");
        localStorage.removeItem("atlas_user");
        localStorage.removeItem("atlas_is_demo");
        useGlobalStore.setState({
          accessToken: null,
          refreshToken: null,
          user: null,
          userRole: "Administrator",
          isDemoSession: false,
        });
        if (location.pathname !== "/login") {
          navigate({ to: "/login" });
        }
      }
    });

    return () => unsubscribe();
  }, [navigate]);

  useEffect(() => {
    const storedAccess = localStorage.getItem("atlas_access_token") || accessToken;
    if (!storedAccess && location.pathname !== "/login") {
      navigate({ to: "/login" });
    } else if (storedAccess && location.pathname === "/login") {
      navigate({ to: "/" });
    }
  }, [location.pathname]);

  // 2. Welcome Experience Trigger on First Login
  useEffect(() => {
    const storedAccess = localStorage.getItem("atlas_access_token") || accessToken;
    if (storedAccess) {
      const hasSeen = localStorage.getItem("atlas_seen_welcome") === "true";
      if (!hasSeen) {
        // Delay slightly for premium visual entrance
        const timer = setTimeout(() => setShowWelcome(true), 1200);
        return () => clearTimeout(timer);
      }
    }
  }, [accessToken]);

  const handleDismissWelcome = () => {
    localStorage.setItem("atlas_seen_welcome", "true");
    setShowWelcome(false);
  };

  const handleStartGuidedDemo = () => {
    localStorage.setItem("atlas_seen_welcome", "true");
    setShowWelcome(false);
    // Guide them to the Simulation Dashboard page or Reroute
    navigate({ to: "/final-demo" });
  };

  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        {isLoginPage ? (
          <Outlet />
        ) : (
          <AppShell>
            <Outlet />
          </AppShell>
        )}
        <CommandPalette />
        <AriaLiveAnnouncer />

        {/* Welcome Dialog Modal */}
        <AnimatePresence>
          {showWelcome && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
            >
              <motion.div
                initial={{ scale: 0.95, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.95, y: 20 }}
                className="relative w-full max-w-md overflow-hidden rounded-3xl border border-primary/20 bg-card p-6 md:p-8 shadow-2xl text-left"
              >
                {/* Glowing aesthetic backgrounds */}
                <div className="absolute top-0 right-0 w-36 h-36 bg-primary/5 rounded-full blur-3xl pointer-events-none" />

                {/* Close Trigger */}
                <button
                  onClick={handleDismissWelcome}
                  className="absolute top-4 right-4 rounded-full p-1.5 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>

                {/* Header Icon */}
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 border border-primary/20 text-primary mb-6 animate-bounce">
                  <Sparkles className="h-6 w-6" />
                </div>

                {/* Title */}
                <h3 className="text-lg font-black text-foreground uppercase tracking-tight">
                  Welcome to ATLAS Mission Control
                </h3>

                {/* Body */}
                <p className="text-xs text-muted-foreground mt-3.5 leading-relaxed">
                  This demonstration showcases an AI-powered operational command platform designed for large sporting events.
                  <br /><br />
                  Every simulation, recommendation and operational insight is generated through the same event-driven architecture used throughout the platform.
                </p>

                {/* Action Controls */}
                <div className="flex items-center justify-end gap-3 border-t border-border/40 pt-5 mt-6">
                  <button
                    onClick={handleDismissWelcome}
                    className="rounded-xl border border-border bg-card hover:bg-muted px-4.5 py-2.5 text-xs font-black uppercase tracking-wider transition-all"
                  >
                    Dismiss
                  </button>
                  <button
                    onClick={handleStartGuidedDemo}
                    className="rounded-xl bg-primary text-primary-foreground hover:opacity-90 px-4.5 py-2.5 text-xs font-black uppercase tracking-wider flex items-center gap-1.5 shadow-md shadow-primary/10 transition-all"
                  >
                    Start Guided Demo
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

// Inline replacement for missing lucide arrow
function ArrowRight(props: any) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={2.5}
      stroke="currentColor"
      {...props}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
    </svg>
  );
}
