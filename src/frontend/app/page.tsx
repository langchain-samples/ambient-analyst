"use client";

import { useAmbientSpecialist } from "@/lib/stream";
import { API_URL, ASSISTANT_ID } from "@/lib/config";
import { CapabilityChips } from "@/components/CapabilityChips";
import { Chat } from "@/components/Chat";
import { PlanPanel } from "@/components/PlanPanel";
import { ArtifactsPanel } from "@/components/ArtifactsPanel";
import { MiddlewarePanel } from "@/components/MiddlewarePanel";
import { useNewConversation } from "./providers";

export default function Home() {
  const stream = useAmbientSpecialist();
  const newConversation = useNewConversation();
  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <header className="flex items-center gap-4 border-b border-zinc-800 px-6 py-3">
        <div>
          <h1 className="text-sm font-semibold">Ambient Analyst</h1>
          <p className="text-[11px] text-zinc-500">
            {ASSISTANT_ID} · {API_URL}
            {stream.isLoading ? " · running…" : ""}
          </p>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <button
            type="button"
            onClick={newConversation}
            disabled={stream.isLoading || stream.threadId == null}
            className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-200 transition-colors hover:border-sky-500 hover:text-sky-300 disabled:cursor-not-allowed disabled:opacity-40"
          >
            ＋ New conversation
          </button>
          <CapabilityChips />
        </div>
      </header>

      <div className="dashboard-grid grid min-h-0 flex-1 grid-cols-[minmax(560px,1fr)_360px] gap-3 p-3">
        <div className="flex min-h-0 flex-col overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-950/60">
          <Chat />
        </div>
        <aside className="scroll-thin min-h-0 space-y-3 overflow-y-auto">
          <PlanPanel />
          <ArtifactsPanel />
          <MiddlewarePanel />
        </aside>
      </div>
    </div>
  );
}
