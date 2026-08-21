"use client";

import { useAmbientSpecialist, type Subagent } from "@/lib/stream";
import { Panel, Empty } from "./Panel";
import { SubagentCard } from "./SubagentCard";

export function SubagentsPanel() {
  const stream = useAmbientSpecialist();
  const subs = [...stream.subagents.values()] as Subagent[];
  return (
    <Panel title="Subagents" hint={subs.length ? `${subs.length} live` : undefined}>
      {subs.length === 0 ? (
        <Empty>
          No subagents spawned yet. A &quot;workflow&quot; fans macro-analysis workers
          out here.
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
