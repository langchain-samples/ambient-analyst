"use client";

import { useAmbientSpecialist, msgRole } from "@/lib/stream";
import { Panel } from "./Panel";

// The agent's middleware stack (see ambient_analyst/agent.py). Middleware is
// cross-cutting and has no single stream projection, so this shows the stack +
// the live effects we can observe (turn budget, planning activity).
const STACK = [
  { name: "PII redaction", desc: "Redacts SSN / email / phone / card / MRN from everything the model sees." },
  { name: "Recursion floor", desc: "Guarantees ≥25 steps of headroom before the recursion limit." },
  { name: "Step budget", desc: "Forces a clean final answer as the turn limit approaches." },
  { name: "Planning (todos)", desc: "Writes and updates the plan shown in the Plan panel." },
  { name: "Code interpreter", desc: "Runs JS to dispatch subagents dynamically on a “workflow” request." },
];

export function MiddlewarePanel() {
  const stream = useAmbientSpecialist();
  const turns = stream.messages.filter((m) => msgRole(m) === "ai").length;

  return (
    <Panel title="Middleware stack" hint={`${turns}/25 model turns`}>
      <ul className="space-y-2">
        {STACK.map((m) => (
          <li key={m.name} className="flex gap-2">
            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
            <div>
              <p className="text-sm text-zinc-200">{m.name}</p>
              <p className="text-xs text-zinc-500">{m.desc}</p>
            </div>
          </li>
        ))}
      </ul>
    </Panel>
  );
}
