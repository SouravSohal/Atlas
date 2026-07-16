import { useState, useEffect } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useGlobalStore } from "../store/useGlobalStore";
import { envConfig } from "../config/env";
import {
  auth,
  googleProvider,
  signInWithEmailAndPassword,
  signInWithPopup,
} from "../services/firebase";
import {
  Shield,
  Activity,
  Cloud,
  Lock,
  Mail,
  ArrowRight,
  Terminal,
  Info,
} from "lucide-react";

export const Route = createFileRoute("/login")({
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDemoLoading, setIsDemoLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  const showDemoAccess =
    envConfig.defaultDemoMode || envConfig.environment === "development";

  // Check backend status on page load
  useEffect(() => {
    fetch(`${envConfig.apiUrl}/health`)
      .then((res) => setBackendOnline(res.ok))
      .catch(() => setBackendOnline(false));
  }, []);

  const handleFetchUserProfile = async (idToken: string, userCredential: any, isDemo: boolean) => {
    // Call backend /auth/me with the Firebase ID Token to retrieve or register user profile
    const profileRes = await fetch(`${envConfig.apiUrl}/auth/me`, {
      headers: {
        Authorization: `Bearer ${idToken}`,
      },
    });

    if (!profileRes.ok) {
      const errorPayload = await profileRes.json().catch(() => ({}));
      throw new Error(errorPayload.error || "Failed to retrieve user profile from ATLAS backend.");
    }

    const profileData = await profileRes.json();
    const dbUser = profileData.data;

    // Save session credentials in localStorage
    localStorage.setItem("atlas_access_token", idToken);
    localStorage.setItem("atlas_refresh_token", userCredential.user.refreshToken);
    localStorage.setItem("atlas_user", JSON.stringify(dbUser));
    localStorage.setItem("atlas_is_demo", isDemo ? "true" : "false");

    // Update global state store
    useGlobalStore.setState({
      accessToken: idToken,
      refreshToken: userCredential.user.refreshToken,
      user: dbUser,
      userRole: dbUser.role,
      isDemoSession: isDemo,
    });

    navigate({ to: "/" });
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please fill in all fields.");
      return;
    }
    setError(null);
    setIsLoading(true);

    try {
      // 1. Authenticate with Firebase Web SDK
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();

      const isDemo = email.trim().toLowerCase() === envConfig.demoEmail.trim().toLowerCase();

      // 2. Fetch profile from Backend
      await handleFetchUserProfile(idToken, userCredential, isDemo);
    } catch (err: any) {
      setError(err.message || "Failed to sign in. Please verify credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError(null);
    setIsLoading(true);

    try {
      // 1. Google Sign-In with Firebase Web SDK
      const userCredential = await signInWithPopup(auth, googleProvider);
      const idToken = await userCredential.user.getIdToken();

      const emailVal = userCredential.user.email || "";
      const isDemo = emailVal.trim().toLowerCase() === envConfig.demoEmail.trim().toLowerCase();

      // 2. Fetch profile from Backend
      await handleFetchUserProfile(idToken, userCredential, isDemo);
    } catch (err: any) {
      setError(err.message || "Google Sign-In failed or cancelled.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLaunchDemo = async () => {
    setError(null);
    setIsDemoLoading(true);

    try {
      const demoEmail = envConfig.demoEmail;
      const demoPassword = envConfig.demoPassword;

      // 1. Authenticate demo user with Firebase Web SDK using environment variables
      const userCredential = await signInWithEmailAndPassword(auth, demoEmail, demoPassword);
      const idToken = await userCredential.user.getIdToken();

      // 2. Fetch profile from Backend
      await handleFetchUserProfile(idToken, userCredential, true);
    } catch (err: any) {
      setError(err.message || "Failed to authenticate demo environment.");
    } finally {
      setIsDemoLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 w-screen h-screen flex flex-col md:flex-row bg-[#08070d] text-foreground font-sans overflow-hidden">
      {/* LEFT PANEL: ATLAS BRANDING */}
      <div className="relative w-full md:w-1/2 h-1/3 md:h-full border-b md:border-b-0 md:border-r border-border/30 bg-[#0c0a17]/90 p-8 md:p-16 flex flex-col justify-between overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(139,92,246,0.1)_0%,transparent_70%)] pointer-events-none" />
        <div className="absolute inset-0 opacity-15 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />
        
        {/* Top Header */}
        <div className="flex items-center gap-3.5 relative z-10">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 font-black text-xl shadow-lg shadow-purple-500/20 text-white">
            A
          </div>
          <div className="text-left">
            <span className="text-xl font-black tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400">
              ATLAS
            </span>
            <span className="block text-[9px] font-black uppercase tracking-wider text-muted-foreground/80 mt-0.5">
              Stadium Intelligence System
            </span>
          </div>
        </div>

        {/* Center Pitch description */}
        <div className="my-auto text-left relative z-10 max-w-md hidden md:block">
          <h1 className="text-3xl font-black leading-tight uppercase tracking-tight text-foreground">
            AI-Powered Stadium <br />
            Operations Platform
          </h1>
          <p className="text-sm font-medium text-muted-foreground mt-4 leading-relaxed">
            Unified Operational Intelligence for FIFA Tournament Operations. Complete situation awareness, crowd dynamics forecasting, and real-time incident resolution.
          </p>
        </div>

        {/* System telemetry & environment markers */}
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3 border-t border-border/20 pt-5 relative z-10 text-[10px] font-mono text-muted-foreground uppercase">
          <div className="flex flex-col text-left">
            <span>VERSION</span>
            <span className="font-bold text-foreground mt-0.5">{envConfig.appVersion}</span>
          </div>
          <div className="flex flex-col text-left">
            <span>IDENTITY PROVIDER</span>
            <span className="font-bold text-purple-400 mt-0.5">FIREBASE AUTH</span>
          </div>
          <div className="flex flex-col text-left">
            <span>CONNECTED BACKEND</span>
            <span className={`font-bold mt-0.5 flex items-center gap-1 ${
              backendOnline === true
                ? "text-emerald-400"
                : backendOnline === false
                ? "text-destructive animate-pulse"
                : "text-amber-500 animate-pulse"
            }`}>
              <span className={`h-1.5 w-1.5 rounded-full ${
                backendOnline === true ? "bg-emerald-400" : "bg-destructive animate-pulse"
              }`} />
              {backendOnline === true ? "ONLINE" : backendOnline === false ? "OFFLINE" : "CHECKING..."}
            </span>
          </div>
          <div className="flex flex-col text-left">
            <span>AI COGNITIVE ENGINE</span>
            <span className="font-bold text-purple-400 mt-0.5 flex items-center gap-1">
              <Activity className="h-3 w-3 animate-pulse" />
              ACTIVE
            </span>
          </div>
          <div className="flex flex-col text-left">
            <span>FIRESTORE CLOUD</span>
            <span className="font-bold text-emerald-400 mt-0.5 flex items-center gap-1">
              <Cloud className="h-3 w-3" />
              CONNECTED
            </span>
          </div>
        </div>
      </div>

      {/* RIGHT PANEL: CREDENTIALS & DEMO ACCESS */}
      <div className="w-full md:w-1/2 h-2/3 md:h-full bg-[#08070d] p-8 md:p-16 flex flex-col justify-center overflow-y-auto">
        <div className="w-full max-w-sm mx-auto space-y-6 text-left">
          {/* Welcome back */}
          <div>
            <h2 className="text-2xl font-black uppercase tracking-tight">Welcome Back</h2>
            <p className="text-xs text-muted-foreground mt-1">
              Enter operations credentials to access the command console.
            </p>
          </div>

          {error && (
            <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-3 flex items-start gap-2.5 text-xs text-destructive">
              <Info className="h-4 w-4 shrink-0 mt-0.5" />
              <p className="font-medium leading-normal">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSignIn} className="space-y-4">
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  id="email"
                  type="email"
                  placeholder="name@atlas.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading || isDemoLoading}
                  className="w-full rounded-xl border border-border bg-card/45 pl-10 pr-4 py-2.5 text-xs text-foreground placeholder:text-muted-foreground outline-none focus:border-purple-500 transition-colors"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="pass" className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">
                Security Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  id="pass"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading || isDemoLoading}
                  className="w-full rounded-xl border border-border bg-card/45 pl-10 pr-4 py-2.5 text-xs text-foreground placeholder:text-muted-foreground outline-none focus:border-purple-500 transition-colors"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-[11px] font-medium">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  disabled={isLoading || isDemoLoading}
                  className="rounded border-border accent-purple-500"
                />
                <span className="text-muted-foreground">Remember Me</span>
              </label>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                type="submit"
                disabled={isLoading || isDemoLoading}
                className="w-full rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 py-3 text-xs font-black uppercase tracking-wider text-white shadow-lg shadow-purple-950/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {isLoading ? (
                  <div className="h-4 w-4 border-2 border-white border-t-transparent animate-spin rounded-full" />
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleGoogleSignIn}
                disabled={isLoading || isDemoLoading}
                className="w-full rounded-xl border border-border bg-card hover:bg-muted py-3 text-xs font-black uppercase tracking-wider text-foreground flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                Sign In with Google
              </button>
            </div>
          </form>

          {/* Demo Mode section */}
          {showDemoAccess && (
            <div className="space-y-4 pt-4 border-t border-border/25">
              <div className="flex items-start gap-2.5 p-3 rounded-xl border border-purple-500/10 bg-purple-500/5 text-[10px] leading-relaxed text-purple-300">
                <Terminal className="h-4 w-4 shrink-0 text-purple-400 mt-0.5 animate-pulse" />
                <p>
                  For hackathon evaluation and testing purposes, ATLAS includes a preconfigured demonstration environment. This authenticates using a dedicated Firebase demo account with full role capabilities.
                </p>
              </div>

              <button
                type="button"
                onClick={handleLaunchDemo}
                disabled={isLoading || isDemoLoading}
                className="w-full rounded-xl border border-purple-500/30 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 py-3 text-xs font-black uppercase tracking-wider flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {isDemoLoading ? (
                  <div className="h-4 w-4 border-2 border-purple-400 border-t-transparent animate-spin rounded-full" />
                ) : (
                  <>
                    Launch Demo Mode
                    <Shield className="h-4 w-4 animate-pulse" />
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
