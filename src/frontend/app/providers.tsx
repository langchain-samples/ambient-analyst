"use client";

import { StreamProvider } from "@langchain/react";
import { createContext, useContext, useEffect, useState } from "react";
import { API_URL, ASSISTANT_ID } from "@/lib/config";
import type { AmbientSpecialistState } from "@/lib/stream";

const NewConversationContext = createContext<() => void>(() => undefined);

export const useNewConversation = () => useContext(NewConversationContext);

export function Providers({ children }: { children: React.ReactNode }) {
  const [apiUrl, setApiUrl] = useState(
    API_URL.startsWith("/") ? null : API_URL,
  );
  const [threadId, setThreadId] = useState<string | null>(null);

  useEffect(() => {
    setApiUrl(new URL(API_URL, window.location.origin).href.replace(/\/$/, ""));
  }, []);

  if (!apiUrl) return null;

  return (
    <NewConversationContext.Provider value={() => setThreadId(null)}>
      <StreamProvider<AmbientSpecialistState>
        apiUrl={apiUrl}
        assistantId={ASSISTANT_ID}
        threadId={threadId}
        onThreadId={setThreadId}
      >
        {children}
      </StreamProvider>
    </NewConversationContext.Provider>
  );
}
