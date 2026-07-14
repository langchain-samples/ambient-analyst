"use client";

import { StreamProvider } from "@langchain/react";
import { API_URL, ASSISTANT_ID } from "@/lib/config";
import type { ResearchState } from "@/lib/stream";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <StreamProvider<ResearchState> apiUrl={API_URL} assistantId={ASSISTANT_ID}>
      {children}
    </StreamProvider>
  );
}
