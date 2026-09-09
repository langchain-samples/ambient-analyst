"use client";

import { useMessages } from "@langchain/react";
import { ASSISTANT_ID } from "@/lib/config";
import { msgText, useAmbientSpecialist, type Subagent } from "@/lib/stream";

const STATUS = {
  running: "bg-amber-400 shadow-[0_0_12px_rgb(251_191_36)] animate-pulse",
  complete: "bg-emerald-400 shadow-[0_0_10px_rgb(52_211_153)]",
  error: "bg-red-400 shadow-[0_0_10px_rgb(248_113_113)]",
} as const;

function AgentNode({ agent }: { agent: Subagent }) {
  const stream = useAmbientSpecialist();
  const messages = useMessages(stream, agent);
  const last = [...messages].reverse().find((message) => msgText(message).trim());
  const dynamic = agent.name === "source-analyst" || agent.name.startsWith("dynamic");
  const detail = msgText(last) || agent.taskInput || "Waiting for agent output…";

  return (
    <div className="agent-node relative min-w-0 rounded-2xl border border-zinc-700/80 bg-zinc-950/90 p-3 shadow-xl shadow-black/30">
      <div className="flex items-start gap-3">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-violet-500/15 text-violet-300 ring-1 ring-violet-400/30">
          <span className="text-sm">◇</span>
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${STATUS[agent.status] ?? STATUS.running}`} />
            <h3 className="truncate text-sm font-semibold capitalize text-zinc-100">
              {agent.name}
            </h3>
          </div>
          <p className="mt-0.5 text-[10px] font-medium uppercase tracking-[0.16em] text-violet-300">
            {dynamic ? "Dynamic specialist" : "Delegated specialist"}
          </p>
        </div>
      </div>
      <p className="mt-3 line-clamp-3 min-h-12 text-xs leading-4 text-zinc-400">
        {detail}
      </p>
      <div className="mt-3 flex items-center justify-between border-t border-zinc-800 pt-2 text-[10px] text-zinc-500">
        <span>{messages.length} events</span>
        <span className="uppercase tracking-wider">{agent.status}</span>
      </div>
    </div>
  );
}

export function OrchestrationCanvas({
  expanded,
  onToggle,
}: {
  expanded: boolean;
  onToggle: () => void;
}) {
  const stream = useAmbientSpecialist();
  const agents = [...stream.subagents.values()] as Subagent[];
  const running = agents.filter((agent) => agent.status === "running").length;

  return (
    <section className={`orchestration-grid flex shrink-0 flex-col overflow-hidden rounded-2xl border border-zinc-800 bg-[#09090b] transition-[height] duration-300 ${expanded ? "h-[calc(100%-0.75rem)] min-h-96" : "h-16"}`}>
      <header className="flex items-center border-b border-zinc-800/80 px-4 py-3">
        <button
          type="button"
          onClick={onToggle}
          className="flex min-w-0 items-center gap-3 text-left"
          aria-expanded={expanded}
        >
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-sky-400/15 text-sky-300 ring-1 ring-sky-300/30">
            ◎
          </span>
          <span className="min-w-0">
            <span className="block text-[10px] font-semibold uppercase tracking-[0.18em] text-sky-300">
              Supervisor agent
            </span>
            <span className="block truncate text-xs font-medium text-zinc-200">
              {ASSISTANT_ID} · {agents.length} delegations
            </span>
          </span>
          <span className="text-xs text-zinc-500">{expanded ? "⌃" : "⌄"}</span>
        </button>
        <div className="ml-auto flex items-center gap-2 rounded-full border border-zinc-800 bg-black/40 px-2.5 py-1 text-[10px] text-zinc-400">
          <span className={`h-1.5 w-1.5 rounded-full ${stream.isLoading ? "animate-pulse bg-emerald-400" : "bg-zinc-600"}`} />
          {stream.isLoading ? `${running || 1} active` : "ready"}
        </div>
      </header>

      {expanded && <div className="scroll-thin flex-1 overflow-auto p-5">
        <div className="mx-auto flex min-h-full max-w-5xl flex-col items-center">
          <button type="button" onClick={onToggle} className={`relative w-full max-w-sm rounded-2xl border p-4 text-left shadow-2xl transition-colors ${stream.isLoading ? "border-emerald-400/50 bg-emerald-400/10 shadow-emerald-950/40" : "border-sky-400/30 bg-sky-400/5 shadow-black/30"}`}>
            <div className="flex items-center gap-3">
              <div className="relative grid h-12 w-12 place-items-center rounded-2xl bg-sky-400/15 text-xl text-sky-300 ring-1 ring-sky-300/30">
                ◎
                {stream.isLoading && <span className="absolute inset-0 animate-ping rounded-2xl ring-1 ring-emerald-400/40" />}
              </div>
              <div className="min-w-0">
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-sky-300">
                  Orchestrator
                </p>
                <h3 className="truncate text-base font-semibold text-white">{ASSISTANT_ID}</h3>
                <p className="text-xs text-zinc-500">
                  {stream.messages.length} events · {agents.length} delegations
                </p>
              </div>
            </div>
          </button>

          {agents.length === 0 ? (
            <div className="flex flex-1 flex-col items-center justify-center py-16 text-center">
              <div className="mb-4 h-16 w-px bg-gradient-to-b from-sky-400/60 to-zinc-800" />
              <div className="grid h-12 w-12 place-items-center rounded-full border border-dashed border-zinc-700 text-zinc-600">＋</div>
              <p className="mt-3 text-sm text-zinc-400">Delegated agents appear here</p>
              <p className="mt-1 max-w-xs text-xs text-zinc-600">
                Run a workflow to watch dynamic specialists fan out from the orchestrator.
              </p>
            </div>
          ) : (
            <div className="agent-tree w-full">
              <div className="agent-tree-stem mx-auto h-10 w-px bg-gradient-to-b from-sky-400 to-violet-500" />
              <div className="agent-tree-branches grid gap-4" style={{ gridTemplateColumns: `repeat(${Math.min(agents.length, 3)}, minmax(0, 1fr))` }}>
                {agents.length > 1 && (
                  <div
                    className="absolute top-0 h-px bg-violet-500/60"
                    style={{
                      left: `${50 / Math.min(agents.length, 3)}%`,
                      right: `${50 / Math.min(agents.length, 3)}%`,
                    }}
                  />
                )}
                {agents.map((agent) => (
                  <div key={agent.id} className="relative pt-6">
                    <div className="absolute left-1/2 top-0 h-6 w-px bg-violet-500/60" />
                    <AgentNode agent={agent} />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>}
    </section>
  );
}
