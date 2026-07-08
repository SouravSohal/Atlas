import { Loader2 } from "lucide-react";

export function LoadingScreen() {
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center bg-background text-foreground transition-colors duration-300">
      <div className="relative flex flex-col items-center gap-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <span className="text-sm font-medium tracking-wider text-muted-foreground uppercase animate-pulse">
          ATLAS Stadium Ops
        </span>
      </div>
    </div>
  );
}
