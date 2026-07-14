"use client";

import { useResearch, type Subagent } from "@/lib/stream";
import { Panel, Empty } from "./Panel";
import { SubagentCard } from "./SubagentCard";

export function SubagentsPanel() {
  const stream = useResearch();
  const subs = [...stream.subagents.values()] as Subagent[];
  return (
    <Panel title="Subagents" hint={subs.length ? `${subs.length} live` : undefined}>
      {subs.length === 0 ? (
        <Empty>
          No subagents spawned yet. Delegation (the async code-gen agent, or a
          &quot;workflow&quot; fan-out) shows up here.
        </Empty>
      ) : (
        <div className="space-y-2">
          {subs.map((s) => (
            <SubagentCard key={s.id} subagent={s} />
          ))}
        </div>
      )}
    </Panel>
  );
}
