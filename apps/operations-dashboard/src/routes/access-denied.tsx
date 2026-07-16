import { createFileRoute, Link } from "@tanstack/react-router";
import { ShieldAlert } from "lucide-react";
import { useGlobalStore } from "../store/useGlobalStore";

export const Route = createFileRoute("/access-denied")({
  component: AccessDeniedPage,
});

export function AccessDeniedPage() {
  const { user, userRole } = useGlobalStore();

  return (
    <div className="flex min-h-[80vh] items-center justify-center bg-background px-4 text-foreground">
      <div className="w-full max-w-md rounded-2xl border border-destructive/30 bg-card p-8 shadow-xl text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-destructive/10 text-destructive">
          <ShieldAlert className="h-8 w-8" />
        </div>
        <h2 className="mt-6 text-xl font-bold tracking-tight">403 - Access Denied</h2>
        <p className="mt-3 text-sm text-muted-foreground">
          You do not have the required permissions to access this operations module.
        </p>

        <div className="mt-6 rounded-xl bg-muted/30 p-4 text-left border border-border">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Logged in as:</span>
            <span className="font-semibold text-foreground">{user?.email || "N/A"}</span>
          </div>
          <div className="flex justify-between text-xs mt-2">
            <span className="text-muted-foreground">Your Role:</span>
            <span className="font-semibold uppercase tracking-wider text-destructive bg-destructive/10 px-2 py-0.5 rounded-md">
              {userRole || "N/A"}
            </span>
          </div>
        </div>

        <div className="mt-8 flex flex-col gap-3">
          <Link
            to="/"
            className="inline-block w-full text-center rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity"
          >
            Return to Dashboard
          </Link>
          <Link
            to="/login"
            className="inline-block w-full text-center rounded-xl border border-border px-4 py-2.5 text-sm font-semibold text-foreground hover:bg-muted/40 transition-colors"
          >
            Sign In with Different Account
          </Link>
        </div>
      </div>
    </div>
  );
}
