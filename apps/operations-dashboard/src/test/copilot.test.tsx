import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AiCopilot } from "../features/mission-control/components/AiCopilot";
import type { ChatMessage } from "../store/useGlobalStore";

describe("AiCopilot Component tests", () => {
  const mockMessages: ChatMessage[] = [
    {
      role: "user",
      text: "How is Gate 1 traffic?",
      timestamp: "12:00:00",
    },
    {
      role: "assistant",
      text: "Gate 1 is currently operating at nominal 30% load.",
      timestamp: "12:00:05",
    },
  ];

  it("should render history messages correctly", () => {
    const setInput = vi.fn();
    const handleSubmit = vi.fn((e) => e.preventDefault());
    const chatEndRef = { current: null };

    render(
      <AiCopilot
        playbackActive={false}
        playbackScenario={null}
        playbackStep={0}
        chatMessages={mockMessages}
        chatThinking={false}
        chatInput="testing query"
        setChatInput={setInput}
        handleChatSubmit={handleSubmit}
        chatEndRef={chatEndRef}
      />
    );

    expect(screen.getByText("How is Gate 1 traffic?")).toBeInTheDocument();
    expect(screen.getByText("Gate 1 is currently operating at nominal 30% load.")).toBeInTheDocument();
  });

  it("should trigger input changes on typing", () => {
    const setInput = vi.fn();
    const handleSubmit = vi.fn((e) => e.preventDefault());
    const chatEndRef = { current: null };

    render(
      <AiCopilot
        playbackActive={false}
        playbackScenario={null}
        playbackStep={0}
        chatMessages={[]}
        chatThinking={false}
        chatInput=""
        setChatInput={setInput}
        handleChatSubmit={handleSubmit}
        chatEndRef={chatEndRef}
      />
    );

    const inputEl = screen.getByPlaceholderText("Ask Copilot a question...");
    fireEvent.change(inputEl, { target: { value: "Hello Copilot" } });

    expect(setInput).toHaveBeenCalledWith("Hello Copilot");
  });

  it("should trigger submit handler on submit button click", () => {
    const setInput = vi.fn();
    const handleSubmit = vi.fn((e) => e.preventDefault());
    const chatEndRef = { current: null };

    render(
      <AiCopilot
        playbackActive={false}
        playbackScenario={null}
        playbackStep={0}
        chatMessages={[]}
        chatThinking={false}
        chatInput="Help me reroute"
        setChatInput={setInput}
        handleChatSubmit={handleSubmit}
        chatEndRef={chatEndRef}
      />
    );

    const submitBtn = screen.getByRole("button");
    fireEvent.click(submitBtn);

    expect(handleSubmit).toHaveBeenCalled();
  });

  it("should render thinking indicator when chatThinking is true", () => {
    const setInput = vi.fn();
    const handleSubmit = vi.fn((e) => e.preventDefault());
    const chatEndRef = { current: null };

    render(
      <AiCopilot
        playbackActive={false}
        playbackScenario={null}
        playbackStep={0}
        chatMessages={[]}
        chatThinking={true}
        chatInput=""
        setChatInput={setInput}
        handleChatSubmit={handleSubmit}
        chatEndRef={chatEndRef}
      />
    );

    expect(screen.getByText("Copilot is thinking...")).toBeInTheDocument();
  });
});
