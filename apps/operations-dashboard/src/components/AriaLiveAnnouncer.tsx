import { useEffect, useRef, useState } from "react";
import { useGlobalStore } from "../store/useGlobalStore";

export function AriaLiveAnnouncer() {
  const [announcement, setAnnouncement] = useState("");
  const toastMessage = useGlobalStore((state) => state.toastMessage);
  const chatMessages = useGlobalStore((state) => state.chatMessages);
  const localNotifications = useGlobalStore((state) => state.localNotifications);
  const playbackStep = useGlobalStore((state) => state.playbackStep);
  const playbackScenario = useGlobalStore((state) => state.playbackScenario);

  const prevChatCount = useRef(chatMessages.length);
  const prevNotifCount = useRef(localNotifications.length);
  const prevStep = useRef(playbackStep);
  const prevScenario = useRef(playbackScenario);

  // 1. Monitor toast / system alerts
  useEffect(() => {
    if (toastMessage) {
      setAnnouncement(`System status update: ${toastMessage}`);
    }
  }, [toastMessage]);

  // 2. Monitor AI Responses
  useEffect(() => {
    if (chatMessages.length > prevChatCount.current) {
      const lastMsg = chatMessages[chatMessages.length - 1];
      if (lastMsg && lastMsg.role === "assistant") {
        setAnnouncement(`AI Response received: ${lastMsg.text.slice(0, 150)}...`);
      }
    }
    prevChatCount.current = chatMessages.length;
  }, [chatMessages]);

  // 3. Monitor notifications list growth
  useEffect(() => {
    if (localNotifications.length > prevNotifCount.current) {
      const lastNotif = localNotifications[localNotifications.length - 1];
      if (lastNotif) {
        setAnnouncement(`New alert notification: ${lastNotif.text || lastNotif.title}`);
      }
    }
    prevNotifCount.current = localNotifications.length;
  }, [localNotifications]);

  // 4. Monitor simulation ticks
  useEffect(() => {
    if (playbackScenario && (playbackStep !== prevStep.current || playbackScenario !== prevScenario.current)) {
      setAnnouncement(`Simulation event: ${playbackScenario} is active at step ${playbackStep + 1}.`);
    }
    prevStep.current = playbackStep;
    prevScenario.current = playbackScenario;
  }, [playbackStep, playbackScenario]);

  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="sr-only absolute w-[1px] h-[1px] p-0 -m-[1px] overflow-hidden clip-[rect(0,0,0,0)] border-0"
    >
      {announcement}
    </div>
  );
}
