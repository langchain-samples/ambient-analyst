"use client";

import { useState } from "react";
import { useAmbientSpecialist } from "@/lib/stream";
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
  const stream = useAmbientSpecialist();
  const files = stream.values?.files ?? {};
  const paths = Object.keys(files);
  const [open, setOpen] = useState<string | null>(null);
  const sel = open && files[open] != null ? open : (paths[0] ?? null);

  return (
    <Panel title="Sandbox" hint={paths.length ? `${paths.length} files` : "isolated"}>
      <div className="mb-3 grid grid-cols-2 gap-2">
        <div className="rounded-lg border border-zinc-800 bg-black/30 p-2">
          <p className="text-[10px] uppercase tracking-wider text-zinc-500">Runtime</p>
          <p className="mt-1 flex items-center gap-1.5 text-xs text-emerald-300">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Isolated
          </p>
        </div>
        <div className="rounded-lg border border-zinc-800 bg-black/30 p-2">
          <p className="text-[10px] uppercase tracking-wider text-zinc-500">Workspace</p>
          <p className="mt-1 truncate font-mono text-xs text-sky-300">/analysis</p>
        </div>
      </div>
      {paths.length === 0 ? (
        <Empty>
          Sandbox outputs and files synchronized into agent state appear here.
        </Empty>
      ) : (
        <div className="space-y-2">
          <div className="rounded-lg border border-zinc-800 bg-black/30 p-1">
            {paths.map((p) => (
              <button
                key={p}
                onClick={() => setOpen(p)}
                className={`flex w-full items-center gap-2 rounded px-2 py-1.5 text-left font-mono text-xs ${
                  sel === p
                    ? "bg-sky-500/10 text-sky-300"
                    : "text-zinc-400 hover:bg-zinc-800/60"
                }`}
              >
                <span className="text-zinc-600">▧</span>
                <span className="truncate">{p}</span>
              </button>
            ))}
          </div>
          {sel && <FileView path={sel} content={String(files[sel] ?? "")} />}
        </div>
      )}
    </Panel>
  );
}
