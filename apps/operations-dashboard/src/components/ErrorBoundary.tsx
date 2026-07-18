import React from "react";
import type { ErrorInfo, ReactNode } from "react";
import { AlertOctagon } from "lucide-react";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-background px-4 text-foreground">
          <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-xl text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive">
              <AlertOctagon className="h-6 w-6" />
            </div>
            <h2 className="mt-4 text-lg font-semibold">Something went wrong</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              An unexpected error occurred in the Operations Command Center. Please reload the page or contact operations support.
            </p>
            {this.state.error && (
              <pre className="mt-4 max-h-40 overflow-auto rounded-lg bg-muted p-3 text-left text-xs font-mono text-muted-foreground">
                {this.state.error.message}
              </pre>
            )}
            <button
              onClick={() => window.location.reload()}
              className="mt-6 w-full rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity"
            >
              Reload Operations Command Center
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
