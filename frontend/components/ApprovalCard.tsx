"use client";

import { useState } from "react";
import { useResearch } from "@/lib/stream";

/* eslint-disable @typescript-eslint/no-explicit-any */
type ActionRequest = {
  name?: string;
  action?: string;
  args?: Record<string, unknown>;
  description?: string;
};

export function ApprovalCard() {
  const stream = useResearch();
  const interrupt = stream.interrupt;
  const [busy, setBusy] = useState(false);
  if (!interrupt) return null;

  // Interrupt payload casing differs across HITL middleware versions — accept
  // both snake_case (Python) and camelCase.
  const value: any = interrupt.value ?? {};
  const requests: ActionRequest[] =
    value.action_requests ??
    value.actionRequests ??
    (Array.isArray(value) ? value : [value]);

  async function decide(type: "approve" | "reject") {
    setBusy(true);
    try {
      // Resume maps to Command(resume=…); one decision per pending action.
      await stream.respond({ decisions: requests.map(() => ({ type })) });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="rounded-xl border border-amber-500/40 bg-amber-500/5 p-4">
      <div className="flex items-center gap-2">
        <span className="h-2 w-2 animate-pulse rounded-full bg-amber-400" />
        <h3 className="text-sm font-semibold text-amber-300">Approval required</h3>
      </div>
      <div className="mt-2 space-y-2">
        {requests.map((r, i) => (
          <div
            key={i}
            className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2"
          >
            <p className="text-sm text-zinc-200">
              <span className="font-mono text-amber-300">
                {r.name ?? r.action ?? "action"}
              </span>
              {r.description ? ` — ${r.description}` : ""}
            </p>
            {r.args && (
              <pre className="scroll-thin mt-1 overflow-auto rounded bg-black/40 p-2 text-[11px] text-zinc-400">
                {JSON.stringify(r.args, null, 2)}
              </pre>
            )}
          </div>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <button
          disabled={busy}
          onClick={() => decide("approve")}
          className="rounded-md bg-emerald-500/90 px-3 py-1.5 text-sm font-medium text-black hover:bg-emerald-400 disabled:opacity-50"
        >
          Approve
        </button>
        <button
          disabled={busy}
          onClick={() => decide("reject")}
          className="rounded-md border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 hover:border-red-500 hover:text-red-300 disabled:opacity-50"
        >
          Reject
        </button>
      </div>
    </div>
  );
}
/* eslint-enable @typescript-eslint/no-explicit-any */
