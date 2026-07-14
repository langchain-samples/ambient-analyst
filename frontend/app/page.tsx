"use client";

import { useResearch } from "@/lib/stream";
import { API_URL, ASSISTANT_ID } from "@/lib/config";
import { CapabilityChips } from "@/components/CapabilityChips";
import { Chat } from "@/components/Chat";
import { PlanPanel } from "@/components/PlanPanel";
import { SubagentsPanel } from "@/components/SubagentsPanel";
import { ArtifactsPanel } from "@/components/ArtifactsPanel";
import { MiddlewarePanel } from "@/components/MiddlewarePanel";

export default function Home() {
  const stream = useResearch();
  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <header className="flex items-center gap-4 border-b border-zinc-800 px-6 py-3">
        <div>
          <h1 className="text-sm font-semibold">Deep Agents Capability Visualizer</h1>
          <p className="text-[11px] text-zinc-500">
            {ASSISTANT_ID} · {API_URL}
            {stream.isLoading ? " · running…" : ""}
          </p>
        </div>
        <div className="ml-auto">
          <CapabilityChips />
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <div className="flex flex-1 flex-col border-r border-zinc-800">
          <Chat />
        </div>
        <aside className="scroll-thin w-96 shrink-0 space-y-4 overflow-y-auto p-4">
          <PlanPanel />
          <SubagentsPanel />
          <ArtifactsPanel />
          <MiddlewarePanel />
        </aside>
      </div>
    </div>
  );
}
