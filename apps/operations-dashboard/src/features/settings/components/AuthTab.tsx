import { Lock } from "lucide-react";
import { envConfig } from "../../../config/env";
import { auth } from "../../../services/firebase";

interface AuthTabProps {
  userRole: string;
  sessionExpiry: string;
}

export function AuthTab({ userRole, sessionExpiry }: AuthTabProps) {
  const currentUser = auth.currentUser;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-black text-foreground">Identity & Authentication Settings</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Inspect current login sessions, user roles, and security authorization variables.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Authentication Provider</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2 text-xs font-bold text-foreground">
            Firebase Authentication
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Current Firebase Project</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2 text-xs font-bold text-foreground font-mono">
            {envConfig.firebaseProjectId}
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Current User UID</label>
          <div
            className="bg-muted/40 border border-border rounded-xl px-3.5 py-2 text-xs font-bold text-foreground font-mono truncate"
            title={currentUser?.uid || "N/A"}
          >
            {currentUser?.uid || "N/A"}
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Current User Email</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2 text-xs font-bold text-foreground truncate">
            {currentUser?.email || "N/A"}
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Authentication Status</label>
          <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2 text-xs font-bold text-foreground">
            <span>{currentUser ? "Session Active" : "Unauthenticated"}</span>
            <span
              className={`flex items-center gap-0.5 rounded border px-1.5 py-0.5 text-[9px] font-black uppercase ${
                currentUser
                  ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                  : "bg-destructive/10 border-destructive/20 text-destructive"
              }`}
            >
              {currentUser ? "CONNECTED" : "DISCONNECTED"}
            </span>
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Current User Role</label>
          <div className="flex items-center justify-between bg-muted/40 border border-border rounded-xl px-3.5 py-2 text-xs font-bold text-foreground">
            <span>{userRole}</span>
            <span className="flex items-center gap-0.5 rounded bg-primary/10 border border-primary/20 px-1.5 py-0.5 text-[9px] font-black text-primary uppercase">
              SYSTEM USER
            </span>
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Last Authentication Time</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-xs text-foreground font-bold">
            {currentUser?.metadata.lastSignInTime
              ? new Date(currentUser.metadata.lastSignInTime).toLocaleString()
              : "N/A"}
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Token Expiration (Configured)</label>
          <div className="bg-muted/40 border border-border rounded-xl px-3.5 py-2.5 text-xs text-foreground font-bold">
            {sessionExpiry} (Standard Firebase Session)
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-dashed border-border bg-muted/10 p-4 flex items-center gap-3">
        <Lock className="h-5 w-5 text-muted-foreground" />
        <div>
          <h4 className="text-xs font-bold text-foreground">Security Key Management</h4>
          <p className="text-[10px] text-muted-foreground mt-0.5 font-semibold">
            Authorization checks are routed directly via Firebase Admin credentials and ID token verification middleware.
          </p>
        </div>
      </div>
    </div>
  );
}
