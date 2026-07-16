import { Brain, Sparkles, Send } from "lucide-react";
import { SCENARIO_STEPS } from "../../../store/scenarioSteps";
import type { ChatMessage } from "../../../store/useGlobalStore";

interface AiCopilotProps {
  playbackActive: boolean;
  playbackScenario: string | null;
  playbackStep: number;
  chatMessages: ChatMessage[];
  chatThinking: boolean;
  chatInput: string;
  setChatInput: (val: string) => void;
  handleChatSubmit: (e: React.FormEvent) => void;
  chatEndRef: React.RefObject<HTMLDivElement | null>;
}

export function AiCopilot({
  playbackActive,
  playbackScenario,
  playbackStep,
  chatMessages,
  chatThinking,
  chatInput,
  setChatInput,
  handleChatSubmit,
  chatEndRef,
}: AiCopilotProps) {
  return (
    <div className="rounded-2xl border border-border bg-card/45 backdrop-blur-md overflow-hidden h-[400px] flex flex-col justify-between shadow-sm text-left">
      <div className="p-4 border-b border-border bg-muted/20 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Brain className="h-4 w-4 text-primary animate-pulse" />
          <span className="text-xs font-bold text-foreground">ATLAS Copilot</span>
        </div>
        <span className="text-xs text-muted-foreground font-mono">Gemini 2.5 Flash</span>
      </div>

      {/* Conversation history */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {playbackActive && (
          <div className="p-3 rounded-xl border border-primary/30 bg-primary/5 flex items-start gap-2 text-left">
            <Sparkles className="h-4 w-4 text-primary shrink-0 mt-0.5 animate-pulse" />
            <div>
              <span className="font-bold block text-primary text-xs uppercase">AI Situation Summary:</span>
              <p className="text-foreground mt-0.5">
                {SCENARIO_STEPS[playbackScenario || ""]?.[playbackStep]?.summary}
              </p>
            </div>
          </div>
        )}

        {chatMessages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col gap-1 ${msg.role === "user" ? "items-end" : "items-start"}`}>
            <div
              className={`p-3 rounded-2xl border ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-muted/30 border-border"
              } max-w-[85%] text-left`}
            >
              {msg.text.split("\n").map((line, iIdx) => (
                <p key={iIdx}>{line}</p>
              ))}
            </div>
            <span className="text-xs text-muted-foreground px-1">{msg.timestamp}</span>
          </div>
        ))}
        {chatThinking && (
          <div className="flex items-center gap-1.5 text-muted-foreground italic">
            <div className="h-3 w-3 rounded-full border border-primary border-t-transparent animate-spin" />
            <span>Copilot is thinking...</span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Form input */}
      <form onSubmit={handleChatSubmit} className="p-3 border-t border-border bg-muted/10 flex gap-2">
        <input
          type="text"
          placeholder="Ask Copilot a question..."
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          className="flex-1 rounded-lg border border-border bg-card px-3 py-2 text-xs outline-none text-foreground"
        />
        <button
          type="submit"
          className="rounded-lg bg-primary p-2 text-primary-foreground hover:opacity-90 transition-opacity"
        >
          <Send className="h-3.5 w-3.5" />
        </button>
      </form>
    </div>
  );
}
