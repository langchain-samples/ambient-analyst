"use client";

import { useAmbientSpecialist, msgToolCalls } from "@/lib/stream";

export function CapabilityChips() {
  const stream = useAmbientSpecialist();
  const subs = [...stream.subagents.values()];

  const toolNames = new Set<string>();
  stream.messages.forEach((m) =>
    msgToolCalls(m).forEach((tc) => toolNames.add(tc.name)),
  );
  const hasFiles = Object.keys(stream.values?.files ?? {}).length > 0;

  const chips = [
    {
      label: "Dynamic subagents",
      on: subs.length > 0 || toolNames.has("task"),
    },
    { label: "Middleware", on: (stream.values?.todos?.length ?? 0) > 0 },
    {
      label: "Sandbox",
      on: hasFiles || [...toolNames].some((n) => /fetch|execute|analysis/.test(n)),
    },
  ];

  return (
    <div className="flex flex-wrap gap-1.5">
      {chips.map((c) => (
        <span
          key={c.label}
          className={`rounded-full border px-2.5 py-0.5 text-xs transition-colors ${
            c.on
              ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-300"
              : "border-zinc-800 text-zinc-500"
          }`}
        >
          <span
            className={`mr-1 inline-block h-1.5 w-1.5 rounded-full ${
              c.on ? "bg-emerald-400" : "bg-zinc-600"
            }`}
          />
          {c.label}
        </span>
      ))}
    </div>
  );
}
