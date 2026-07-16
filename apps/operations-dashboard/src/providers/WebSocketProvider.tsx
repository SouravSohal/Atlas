import { createContext, useContext, useEffect, useState, useRef, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { envConfig } from "../config/env";

type WebSocketContextState = {
  connected: boolean;
  subscribe: (topic: string) => void;
  unsubscribe: (topic: string) => void;
  send: (payload: any) => void;
};

const WebSocketContext = createContext<WebSocketContextState | undefined>(undefined);

// List of all cache keys corresponding to dashboard widgets, timeline, incidents, and twin views
const QUERY_KEYS_TO_INVALIDATE = [
  "cc-overview",
  "cc-state",
  "cc-incidents",
  "cc-recommendations",
  "twin-state",
  "twin-incidents",
  "twin-recs",
  "copilot-overview",
  "copilot-state",
  "copilot-incidents",
  "copilot-recs",
  "dashboard-incidents",
  "notifications-incidents",
  "notifications-recs",
  "overview"
];

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [connected, setConnected] = useState(false);
  const queryClient = useQueryClient();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);
  const activeSubscriptionsRef = useRef<Set<string>>(new Set());
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    const wsUrl = envConfig.wsUrl;

    if (socketRef.current) {
      socketRef.current.onclose = null;
      socketRef.current.onerror = null;
      socketRef.current.close();
    }

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      setConnected(true);
      reconnectAttemptsRef.current = 0;
      // Resubscribe to all previous topics upon reconnection
      activeSubscriptionsRef.current.forEach((topic) => {
        socket.send(JSON.stringify({ type: "subscribe", topic }));
      });
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);

        // Broad invalidation of all related query keys on simulation updates or ticks
        if (payload.type === "update" || payload.type === "broadcast" || payload.event === "action_center_update") {
          QUERY_KEYS_TO_INVALIDATE.forEach((key) => {
            queryClient.invalidateQueries({ queryKey: [key] });
          });
        }
      } catch (err) {
        console.warn("WebSocket message parse warning", err);
      }
    };

    socket.onclose = () => {
      setConnected(false);
      // Exponential backoff reconnect
      const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 16000);
      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectAttemptsRef.current += 1;
        connect();
      }, delay);
    };

    socket.onerror = (err) => {
      console.error("WebSocket connection error:", err);
      socket.close();
    };
  }, [queryClient]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, [connect]);

  const subscribe = useCallback((topic: string) => {
    activeSubscriptionsRef.current.add(topic);
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "subscribe", topic }));
    }
  }, []);

  const unsubscribe = useCallback((topic: string) => {
    activeSubscriptionsRef.current.delete(topic);
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "unsubscribe", topic }));
    }
  }, []);

  const send = useCallback((payload: any) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
    }
  }, []);

  return (
    <WebSocketContext.Provider value={{ connected, subscribe, unsubscribe, send }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
};
