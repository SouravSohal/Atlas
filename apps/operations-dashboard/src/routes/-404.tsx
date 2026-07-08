import { Link } from "@tanstack/react-router";
import { Compass } from "lucide-react";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 text-foreground">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-xl text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Compass className="h-6 w-6" />
        </div>
        <h2 className="mt-4 text-lg font-semibold">404 - Page Not Found</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          The operations module you are looking for does not exist or has not been initialized.
        </p>
        <Link
          to="/"
          className="mt-6 inline-block w-full text-center rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity"
        >
          Return to Overview
        </Link>
      </div>
    </div>
  );
}
