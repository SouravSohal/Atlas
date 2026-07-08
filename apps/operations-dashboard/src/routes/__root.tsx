import { createRootRoute, Outlet } from "@tanstack/react-router";
import { ThemeProvider } from "../providers/ThemeProvider";
import { AppShell } from "../layouts/AppShell";
import { CommandPalette } from "../components/CommandPalette";
import { ErrorBoundary } from "../components/ErrorBoundary";

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <AppShell>
          <Outlet />
        </AppShell>
        <CommandPalette />
      </ThemeProvider>
    </ErrorBoundary>
  );
}
