"use client";

import { useState } from "react";
import { useResearch } from "@/lib/stream";
import { Panel, Empty } from "./Panel";

function FileView({ path, content }: { path: string; content: string }) {
  const ext = path.split(".").pop()?.toLowerCase();
  if (ext === "html" || /^\s*<!doctype html|^\s*<html/i.test(content)) {
    return (
      <iframe
        title={path}
        srcDoc={content}
        sandbox="allow-scripts"
        className="h-64 w-full rounded border border-zinc-800 bg-white"
      />
    );
  }
  if (ext === "svg") {
    // ponytail: agent-authored SVG only; not user input, so raw render is fine.
    return (
      <div
        className="rounded border border-zinc-800 bg-white p-2"
        dangerouslySetInnerHTML={{ __html: content }}
      />
    );
  }
  return (
    <pre className="scroll-thin max-h-64 overflow-auto whitespace-pre-wrap rounded border border-zinc-800 bg-black/40 p-2 text-[11px] text-zinc-300">
      {content}
    </pre>
  );
}

export function ArtifactsPanel() {
  const stream = useResearch();
  const files = stream.values?.files ?? {};
  const paths = Object.keys(files);
  const [open, setOpen] = useState<string | null>(null);
  const sel = open && files[open] != null ? open : (paths[0] ?? null);

  return (
    <Panel title="Artifacts" hint={paths.length ? `${paths.length} files` : undefined}>
      {paths.length === 0 ? (
        <Empty>
          No files yet. Files the agent writes to state (and outputs it pulls
          back from the sandbox) appear here.
        </Empty>
      ) : (
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1">
            {paths.map((p) => (
              <button
                key={p}
                onClick={() => setOpen(p)}
                className={`rounded border px-2 py-0.5 text-xs ${
                  sel === p
                    ? "border-sky-500 bg-sky-500/10 text-sky-300"
                    : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
                }`}
              >
                {p.split("/").pop()}
              </button>
            ))}
          </div>
          {sel && <FileView path={sel} content={String(files[sel] ?? "")} />}
        </div>
      )}
    </Panel>
  );
}
