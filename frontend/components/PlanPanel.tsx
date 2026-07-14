"use client";

import { useResearch } from "@/lib/stream";
import { Panel, Empty } from "./Panel";

const MARK = { pending: "○", in_progress: "◐", completed: "●" } as const;
const COLOR = {
  pending: "text-zinc-500",
  in_progress: "text-amber-400",
  completed: "text-emerald-400",
} as const;

export function PlanPanel() {
  const stream = useResearch();
  const todos = stream.values?.todos ?? [];
  const done = todos.filter((t) => t.status === "completed").length;

  return (
    <Panel title="Plan" hint={todos.length ? `${done}/${todos.length}` : undefined}>
      {todos.length === 0 ? (
        <Empty>The planning middleware hasn&apos;t written a plan yet.</Empty>
      ) : (
        <ol className="space-y-1.5">
          {todos.map((t, i) => (
            <li key={i} className="flex gap-2 text-sm">
              <span className={COLOR[t.status]}>{MARK[t.status]}</span>
              <span
                className={
                  t.status === "completed"
                    ? "text-zinc-500 line-through"
                    : "text-zinc-200"
                }
              >
                {t.content}
              </span>
            </li>
          ))}
        </ol>
      )}
    </Panel>
  );
}
