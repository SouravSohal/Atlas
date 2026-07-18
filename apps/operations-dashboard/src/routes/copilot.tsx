import { useEffect, useRef, useState, useCallback } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useWebSocket } from "../providers/WebSocketProvider";
import {
  Brain,
  Send,
  CheckCircle,
  Terminal,
} from "lucide-react";
import { postCopilotChat } from "../services/api";
import { useGlobalStore } from "../store/useGlobalStore";
import type { ChatMessage } from "../store/useGlobalStore";

const CO_THINKING_STAGES = [
  "Analyzing user request...",
  "Querying live operational telemetry...",
  "Formatting prompt constraints...",
  "Invoking Gemini 2.5 Flash model...",
  "Structuring response payload..."
];

export const Route = createFileRoute("/copilot")({
  component: CopilotChatPage,
});

function CopilotChatPage() {
  const { subscribe, unsubscribe } = useWebSocket();
  const {
    chatMessages: messages,
    setChatMessages: setMessages,
    chatInput: input,
    setChatInput: setInput,
    chatThinking: isThinking,
    setChatThinking: setIsThinking,
  } = useGlobalStore();

  useEffect(() => {
    subscribe("telemetry");
    subscribe("incidents");
    subscribe("recommendations");
    return () => {
      unsubscribe("telemetry");
      unsubscribe("incidents");
      unsubscribe("recommendations");
    };
  }, [subscribe, unsubscribe]);

  const [thinkingStage, setThinkingStage] = useState(0);
  const chatEndRef = useRef<HTMLDivElement>(null);



  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  const handleClearChat = useCallback(() => {
    setMessages([
      {
        role: "assistant",
        text: "Conversation cleared. Ready for new operational inquiries.",
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
  }, [setMessages]);

  // Keyboard Shortcuts (Ctrl+L to clear chat)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "l") {
        e.preventDefault();
        handleClearChat();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleClearChat]);

  const handleSendMessage = (textToSend: string) => {
    if (!textToSend.trim()) return;

    // Add user message
    const userMsg: ChatMessage = {
      role: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsThinking(true);
    setThinkingStage(0);

    const defaultThinking = [
      "Analyzing user request...",
      "Querying live operational telemetry...",
      "Formatting prompt constraints...",
      "Invoking Gemini 2.5 Flash model...",
      "Structuring response payload..."
    ];

    // Cycle through local placeholder thinking steps every 800ms while loading
    let stageIndex = 0;
    const placeholderInterval = setInterval(() => {
      if (stageIndex < defaultThinking.length - 1) {
        stageIndex++;
        setThinkingStage(stageIndex);
      }
    }, 800);

    const formattedHistory = messages.map(msg => ({
      role: msg.role,
      text: msg.text
    }));

    postCopilotChat(textToSend, formattedHistory, "en", window.location.pathname)
      .then((responseData) => {
        clearInterval(placeholderInterval);
        setIsThinking(false);

        const assistantMsg: ChatMessage = {
          role: "assistant",
          text: "",
          timestamp: new Date().toLocaleTimeString(),
          thinkingSteps: responseData.thinking || defaultThinking,
          citations: responseData.citations || [],
          modelVersion: responseData.model_version || "Gemini 2.5 Flash",
          executionTimeMs: responseData.execution_time_ms || 0,
        };

        setMessages((prev) => [...prev, assistantMsg]);

        let charIndex = 0;
        const streamInterval = setInterval(() => {
          if (charIndex < responseData.text.length) {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === "assistant") {
                last.text = responseData.text.slice(0, charIndex + 1);
              }
              return updated;
            });
            charIndex += 2;
          } else {
            clearInterval(streamInterval);
          }
        }, 10);
      })
      .catch((err) => {
        console.error("Copilot Chat API Error:", err);
        clearInterval(placeholderInterval);
        setIsThinking(false);
        const errorMsg: ChatMessage = {
          role: "assistant",
          text: "⚠️ Failed to establish connection with Gemini API. Please check the browser console for details or verify your backend logs.",
          timestamp: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, errorMsg]);
      });
  };



  const quickActions = [
    { label: "Summarize Incidents", prompt: "Summarize active incidents" },
    { label: "Analyze Congestion", prompt: "Analyze crowd congestion and densities" },
    { label: "Show Recommendations", prompt: "List active recommendations" },
  ];

  return (
    <div className="flex flex-col gap-6 text-left max-w-5xl mx-auto h-[80vh]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-border pb-4 gap-4">
        <div className="flex items-center gap-3">
          <Brain className="h-8 w-8 text-primary animate-pulse" />
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">ATLAS Copilot</h1>
            <p className="text-xs text-muted-foreground mt-1">
              Natural language decision assistant powered by cognitive agents.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono bg-muted/40 px-3.5 py-1.5 rounded-full border border-border">
          <Terminal className="h-3.5 w-3.5" />
          <span>Model: Gemini 2.5 Flash (Active)</span>
        </div>
      </div>

      {/* Main split: Chat Area / Help Guidelines */}
      <div className="grid gap-6 md:grid-cols-4 flex-1 overflow-hidden min-h-[400px]">
        
        {/* Left Side: Conversation window */}
        <div className="md:col-span-3 rounded-2xl border border-border bg-card flex flex-col justify-between overflow-hidden shadow-sm h-full">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-4 items-start ${msg.role === "user" ? "justify-end text-right" : "justify-start text-left"}`}
              >
                {msg.role === "assistant" && (
                  <div className="rounded-xl p-2 bg-primary/10 border border-primary/20 text-primary shrink-0">
                    <Brain className="h-4 w-4" />
                  </div>
                )}
                
                <div className={`flex flex-col max-w-[80%] gap-1.5 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                  <div className={`rounded-2xl p-4 text-xs leading-relaxed border ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-muted/30 border-border/80 text-foreground"
                  }`}>
                    {/* Render basic markdown headers / lists */}
                    <div className="space-y-2">
                      {msg.text.split("\n").map((line, lIdx) => {
                        if (line.startsWith("### ")) {
                          return <h3 key={lIdx} className="font-bold text-sm text-foreground mt-1">{line.slice(4)}</h3>;
                        }
                        if (line.startsWith("* ")) {
                          return <div key={lIdx} className="flex gap-2 items-start pl-2"><span>&bull;</span><span>{line.slice(2)}</span></div>;
                        }
                        return <p key={lIdx}>{line}</p>;
                      })}
                    </div>

                    {/* Citations panel */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-border/60 space-y-1.5 text-[9px] text-muted-foreground font-mono">
                        <span className="font-bold block">CITATIONS:</span>
                        {msg.citations.map((c, cIdx) => (
                          <div key={cIdx} className="flex gap-1.5 items-start">
                            <span className="text-primary font-bold">{c.label}</span>
                            <span>{c.text}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <span className="text-[9px] text-muted-foreground font-semibold px-2">
                    {msg.timestamp}
                  </span>
                </div>
              </div>
            ))}

            {/* Thinking status */}
            {isThinking && (
              <div className="flex gap-4 items-start justify-start text-left">
                <div className="rounded-xl p-2 bg-primary/10 border border-primary/20 text-primary shrink-0 animate-spin">
                  <RotateCcw className="h-4 w-4" />
                </div>
                <div className="flex flex-col gap-1.5 items-start">
                  <div className="rounded-2xl p-4 bg-muted/30 border border-border/80 text-xs text-muted-foreground font-medium space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                      <span>Thinking...</span>
                    </div>
                    <div className="pl-5 text-[10px] space-y-1 text-muted-foreground">
                      {CO_THINKING_STAGES.slice(0, thinkingStage + 1).map((step: string, idx: number) => (
                        <div key={idx} className="flex items-center gap-1.5">
                          <CheckCircle className="h-3 w-3 text-primary shrink-0" />
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* User Input bar */}
          <div className="border-t border-border p-4 bg-muted/20 flex flex-col gap-3">
            {/* Quick Actions */}
            <div className="flex flex-wrap gap-2">
              {quickActions.map((action) => (
                <button
                  key={action.label}
                  onClick={() => handleSendMessage(action.prompt)}
                  className="rounded-lg border border-border bg-card hover:bg-muted transition-colors px-3 py-1.5 text-[10px] font-bold text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-primary outline-none"
                >
                  {action.label}
                </button>
              ))}
            </div>

            {/* Message input */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage(input);
              }}
              className="flex gap-3 items-center"
            >
              <input
                type="text"
                placeholder="Ask Copilot a question (e.g. 'Show active incidents')..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-1 rounded-xl border border-border bg-card px-4 py-3 text-xs outline-none text-foreground focus-visible:ring-2 focus-visible:ring-primary"
              />
              <button
                type="submit"
                aria-label="Send message"
                className="rounded-xl bg-primary p-3 text-primary-foreground hover:opacity-90 transition-opacity focus-visible:ring-2 focus-visible:ring-primary outline-none"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>

        {/* Right Side: Keyboard & Info Panel */}
        <div className="flex flex-col gap-6">
          <div className="rounded-2xl border border-border bg-card p-6">
            <h2 className="text-base font-bold mb-4">Command Guide</h2>
            <div className="space-y-4 text-xs">
              <div className="space-y-1">
                <span className="font-bold text-muted-foreground block uppercase text-[10px]">Shortcuts</span>
                <div className="flex justify-between items-center text-[11px] font-mono border-b border-border/40 py-1.5">
                  <span>Clear Chat</span>
                  <kbd className="bg-muted px-1.5 py-0.5 rounded border border-border font-bold">Ctrl L</kbd>
                </div>
                <div className="flex justify-between items-center text-[11px] font-mono py-1.5">
                  <span>Send Message</span>
                  <kbd className="bg-muted px-1.5 py-0.5 rounded border border-border font-bold">Enter</kbd>
                </div>
              </div>

              <div className="space-y-2.5 pt-4 border-t border-border">
                <span className="font-bold text-muted-foreground block uppercase text-[10px]">Try asking:</span>
                <ul className="space-y-2 list-disc pl-4 text-muted-foreground font-medium">
                  <li>"Is there any congestion at the gates?"</li>
                  <li>"Show active recommendations"</li>
                  <li>"List unresolved incidents"</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

// Inline fallback rotation icon
function RotateCcw(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
    </svg>
  );
}
