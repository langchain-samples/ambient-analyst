"use client";

import { useMessages } from "@langchain/react";
import { useResearch, msgText, type Subagent } from "@/lib/stream";

const STATUS = {
  running: { dot: "bg-amber-400 animate-pulse", label: "running" },
  complete: { dot: "bg-emerald-400", label: "complete" },
  error: { dot: "bg-red-400", label: "error" },
} as const;

export function SubagentCard({ subagent }: { subagent: Subagent }) {
  const stream = useResearch();
  // Mount = subscribe to this subagent's namespaced message stream.
  const messages = useMessages(stream, subagent);
  const last = [...messages].reverse().find((m) => msgText(m).trim());
  const body =
    msgText(last) ||
    (typeof subagent.output === "string" ? subagent.output : "");
  const s = STATUS[subagent.status] ?? STATUS.running;

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3">
      <div className="flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full ${s.dot}`} />
        <span className="text-sm font-medium capitalize">{subagent.name}</span>
        <span className="ml-auto text-[10px] uppercase tracking-wide text-zinc-500">
          {s.label}
        </span>
      </div>
      {subagent.taskInput && (
        <p className="mt-1 line-clamp-2 text-xs text-zinc-400">
          {subagent.taskInput}
        </p>
      )}
      {body && (
        <p className="mt-2 line-clamp-4 whitespace-pre-wrap text-xs text-zinc-300">
          {body}
        </p>
      )}
    </div>
  );
}
