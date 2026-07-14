"use client";

import { useEffect, useRef, useState } from "react";
import { useResearch, msgRole, msgText, msgToolCalls } from "@/lib/stream";
import { ApprovalCard } from "./ApprovalCard";

const EXAMPLES = [
  {
    label: "Research",
    text: "Which open-weight model currently leads on coding benchmarks, and how trustworthy are those benchmarks?",
  },
  {
    label: "Run a workflow",
    text: "Run a workflow that analyzes each of these sources and summarizes the top risks, one source-analyst per source: https://openai.com/research, https://www.anthropic.com/research, https://ai.meta.com/research/",
  },
  {
    label: "Generate code",
    text: "Generate a Python matplotlib chart comparing MMLU scores for the top 5 models and save it to /shared/chart.py.",
  },
];

/* eslint-disable @typescript-eslint/no-explicit-any */
function Bubble({ m }: { m: any }) {
  const role = msgRole(m);
  const text = msgText(m);
  const tools = msgToolCalls(m);

  if (role === "human") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl bg-sky-500/90 px-4 py-2 text-sm text-black">
          {text}
        </div>
      </div>
    );
  }
  if (role === "tool") return null; // tool output surfaces via the side panels

  if (!text && tools.length === 0) return null;
  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] space-y-2">
        {text && (
          <div className="whitespace-pre-wrap rounded-2xl bg-zinc-800 px-4 py-2 text-sm text-zinc-100">
            {text}
          </div>
        )}
        {tools.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {tools.map((tc: any, i: number) => (
              <span
                key={tc.id ?? i}
                className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-0.5 font-mono text-[11px] text-emerald-300"
              >
                {tc.name}()
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
/* eslint-enable @typescript-eslint/no-explicit-any */

export function Chat() {
  const stream = useResearch();
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [stream.messages, stream.interrupt]);

  function send(text: string) {
    const t = text.trim();
    if (!t || stream.isLoading) return;
    setInput("");
    void stream.submit({ messages: [{ type: "human", content: t }] } as never);
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="scroll-thin flex-1 space-y-3 overflow-y-auto px-6 py-4">
        {stream.messages.length === 0 && (
          <div className="mx-auto max-w-md pt-16 text-center text-sm text-zinc-500">
            Ask the research agent something — or pick a prompt below to light up
            subagents, planning, and human-in-the-loop.
          </div>
        )}
        {stream.messages.map((m, i) => (
          <Bubble key={(m as { id?: string }).id ?? i} m={m} />
        ))}
        {stream.interrupt && <ApprovalCard />}
        <div ref={endRef} />
      </div>

      <div className="border-t border-zinc-800 px-6 py-3">
        <div className="mb-2 flex flex-wrap gap-1.5">
          {EXAMPLES.map((e) => (
            <button
              key={e.label}
              onClick={() => send(e.text)}
              disabled={stream.isLoading}
              className="rounded-full border border-zinc-700 px-3 py-1 text-xs text-zinc-300 hover:border-sky-500 hover:text-sky-300 disabled:opacity-40"
            >
              {e.label}
            </button>
          ))}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="flex gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Message the research agent…"
            className="flex-1 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm outline-none focus:border-sky-500"
          />
          <button
            type="submit"
            disabled={stream.isLoading || !input.trim()}
            className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-black hover:bg-sky-400 disabled:opacity-40"
          >
            {stream.isLoading ? "…" : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}
