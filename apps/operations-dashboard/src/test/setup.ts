import "@testing-library/jest-dom";
import { beforeAll, afterEach, afterAll, vi } from "vitest";
import { server } from "./mocks/server";

// Start server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: "bypass" }));

// Reset handlers after each test
afterEach(() => {
  server.resetHandlers();
});

// Close server after all tests
afterAll(() => server.close());

// Mock window.scrollTo
vi.stubGlobal("scrollTo", vi.fn());

// Mock ResizeObserver
class MockResizeObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
vi.stubGlobal("ResizeObserver", MockResizeObserver);

// Mock @xyflow/react to avoid jsdom layout measurement exceptions
vi.mock("@xyflow/react", () => {
  const ReactFlow = ({ children }: any) => children;
  const Background = () => null;
  const Controls = () => null;
  const MiniMap = () => null;
  const Handle = () => null;
  const Position = {
    Left: "left",
    Right: "right",
  };
  return {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    Handle,
    Position,
  };
});
