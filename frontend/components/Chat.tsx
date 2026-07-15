"use client";

import { useEffect, useRef, useState } from "react";
import { useAmbientSpecialist, msgRole, msgText, msgToolCalls } from "@/lib/stream";
import { OrchestrationCanvas } from "./OrchestrationCanvas";

const EXAMPLES = [
  {
    label: "Macro outlook",
    text: "What are the most important macroeconomic forces shaping enterprise software spending over the next 12 months? Give me a base case, upside case, and downside case.",
  },
  {
    label: "Run a workflow",
    text: "Run a workflow with one macro-analysis-worker per company to compare the growth drivers, competitive position, and key risks for Microsoft, Amazon, and Google.",
  },
  {
    label: "Analyze data",
    text: "Use the analysis sandbox to build a scenario table for US GDP growth, inflation, and interest rates, then save the CSV and a chart under /analysis/.",
  },
];

/* eslint-disable @typescript-eslint/no-explicit-any */
function ToolUpdates({ tools }: { tools: { id?: string; name: string }[] }) {
  const signature = tools.map((tool) => tool.id ?? tool.name).join(":");
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    setVisible(true);
    const timeout = window.setTimeout(() => setVisible(false), 6000);
    return () => window.clearTimeout(timeout);
  }, [signature]);

  if (!visible) return null;
  return (
    <div className="flex items-center gap-1 overflow-hidden text-[10px] text-zinc-500">
      <span className="shrink-0 uppercase tracking-wider">Tools</span>
      {tools.slice(0, 3).map((tool, index) => (
        <span
          key={tool.id ?? index}
          className="max-w-32 truncate rounded border border-emerald-900/70 bg-emerald-950/30 px-1.5 py-0.5 font-mono text-emerald-400"
        >
          {tool.name}
        </span>
      ))}
      {tools.length > 3 && <span className="shrink-0">+{tools.length - 3}</span>}
    </div>
  );
}

function Bubble({ m, showTools }: { m: any; showTools: boolean }) {
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
        {showTools && tools.length > 0 && <ToolUpdates tools={tools} />}
      </div>
    </div>
  );
}
/* eslint-enable @typescript-eslint/no-explicit-any */

export function Chat() {
  const stream = useAmbientSpecialist();
  const [input, setInput] = useState("");
  const [topologyExpanded, setTopologyExpanded] = useState(true);
  const endRef = useRef<HTMLDivElement>(null);
  const wasLoading = useRef(false);
  const responseCount = stream.messages.filter(
    (message) => msgRole(message) === "ai" && msgText(message).trim(),
  ).length;
  const completedResponseCount = useRef(responseCount);
  const lastToolMessage = stream.messages.findLastIndex(
    (message) => msgToolCalls(message).length > 0,
  );

  useEffect(() => {
    if (stream.isLoading) {
      setTopologyExpanded(true);
    } else if (
      wasLoading.current &&
      responseCount > completedResponseCount.current
    ) {
      setTopologyExpanded(false);
    } else if (stream.messages.length === 0) {
      setTopologyExpanded(true);
    }
    if (!stream.isLoading) completedResponseCount.current = responseCount;
    wasLoading.current = stream.isLoading;
  }, [stream.isLoading, stream.messages.length, responseCount]);

  useEffect(() => {
    if (topologyExpanded) return;
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [stream.messages, stream.interrupt, topologyExpanded]);

  function send(text: string) {
    const t = text.trim();
    if (!t || stream.isLoading) return;
    setInput("");
    setTopologyExpanded(true);
    void stream
      .submit({ messages: [{ type: "human", content: t }] } as never)
      .catch(() => undefined);
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="scroll-thin flex-1 space-y-3 overflow-y-auto px-6 py-4">
        <OrchestrationCanvas
          expanded={topologyExpanded}
          onToggle={() => setTopologyExpanded((value) => !value)}
        />
        {stream.messages.length === 0 && (
          <div className="mx-auto max-w-md pt-16 text-center text-sm text-zinc-500">
            Ask Ambient Analyst something — or pick a prompt below to light up
            subagents, planning, and sandbox activity.
          </div>
        )}
        {stream.messages.map((m, i) => (
          <Bubble
            key={(m as { id?: string }).id ?? i}
            m={m}
            showTools={i === lastToolMessage}
          />
        ))}
        {stream.error != null && (
          <div className="rounded-lg border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-300">
            {stream.error instanceof Error
              ? stream.error.message
              : "Could not connect to the agent server."}
          </div>
        )}
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
            placeholder="Message Ambient Analyst…"
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
