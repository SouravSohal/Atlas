import { HelpCircle, CheckCircle } from "lucide-react";

interface ActiveRecommendationsProps {
  recs: any[];
  approvedRecs: Record<string, boolean>;
  setSelectedWhyRec: (rec: any | null) => void;
  handleApproveRecommendation: (id: string) => void;
}

export function ActiveRecommendations({
  recs,
  approvedRecs,
  setSelectedWhyRec,
  handleApproveRecommendation,
}: ActiveRecommendationsProps) {
  const parseDetails = (detailsStr: string) => {
    try {
      const parsed = JSON.parse(detailsStr);
      return parsed.explanation || detailsStr;
    } catch {
      return detailsStr;
    }
  };

  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md p-6 flex flex-col h-[320px] shadow-sm text-left">
      <div className="mb-4">
        <h2 className="text-base font-bold">Active Recommendations</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Mitigations evaluated by the cognitive engine.</p>
      </div>
      <div className="flex-1 overflow-y-auto space-y-3">
        {recs.length === 0 ? (
          <div className="text-xs text-muted-foreground text-center py-10 font-medium">
            All parameters stable. No recommendations.
          </div>
        ) : (
          recs.slice(0, 4).map((rec: any) => {
            const explanationText = parseDetails(rec.details);
            return (
              <div
                key={rec.id}
                className="p-3 border border-border rounded-xl bg-muted/20 flex items-center justify-between gap-3 text-left animate-fadeIn"
              >
                <div className="flex flex-col gap-1 min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-primary uppercase truncate max-w-[120px]">
                      {rec.action_type}
                    </span>
                    <span className="text-xs font-semibold text-muted-foreground">{rec.priority} priority</span>
                    <span className="text-xs font-mono bg-purple-500/10 border border-purple-500/20 text-purple-400 px-1 rounded">
                      {((rec.confidence || 0.95) * 100).toFixed(0)}% Conf
                    </span>
                  </div>
                  <p className="text-xs font-medium text-foreground truncate">{explanationText}</p>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  <button
                    onClick={() => setSelectedWhyRec(rec)}
                    className="rounded-lg border border-purple-500/30 bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 px-2 py-1 text-xs font-bold uppercase tracking-wider flex items-center gap-0.5 transition-colors focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 outline-none"
                  >
                    <HelpCircle className="h-3 w-3" />
                    Why?
                  </button>

                  {approvedRecs[rec.id] ? (
                    <span className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs font-bold text-emerald-400 px-2 py-1 flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" />
                      Approved
                    </span>
                  ) : (
                    <button
                      onClick={() => handleApproveRecommendation(rec.id)}
                      className="rounded-lg bg-primary px-2.5 py-1 text-xs font-bold text-primary-foreground hover:opacity-90 transition-opacity focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 outline-none"
                    >
                      Approve
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
