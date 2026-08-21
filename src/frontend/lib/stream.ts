import { useStreamContext } from "@langchain/react";

export type Todo = {
  content: string;
  status: "pending" | "in_progress" | "completed";
};

// Deep agent state we read in the UI. `files` is the StateBackend filesystem
// (path -> contents); `todos` is populated by the planning middleware.
export type AmbientSpecialistState = {
  messages: unknown[];
  todos?: Todo[];
  files?: Record<string, string>;
};

// Structural subset of the SDK's SubagentDiscoverySnapshot — the fields we
// render. `namespace` makes it a valid selector-hook target.
export type Subagent = {
  id: string;
  name: string;
  namespace: readonly string[];
  status: "running" | "complete" | "error";
  taskInput?: string;
  output?: unknown;
  error?: string;
};

/** Shared stream from the nearest <StreamProvider>, typed to our state. */
export const useAmbientSpecialist = () => useStreamContext<AmbientSpecialistState>();

// Messages arrive as @langchain/core BaseMessage instances, but exact accessors
// vary across versions — read defensively so rendering never throws.
/* eslint-disable @typescript-eslint/no-explicit-any */
export function msgRole(m: any): "human" | "ai" | "tool" | "system" {
  const t = m?.getType?.() ?? m?.type ?? m?.role ?? "ai";
  if (t === "human" || t === "user") return "human";
  if (t === "tool") return "tool";
  if (t === "system") return "system";
  return "ai";
}

export function msgText(m: any): string {
  if (typeof m?.text === "string") return m.text;
  if (typeof m?.content === "string") return m.content;
  if (Array.isArray(m?.content)) {
    return m.content
      .map((b: any) => (typeof b === "string" ? b : b?.text ?? ""))
      .join("");
  }
  return "";
}

export function msgToolCalls(m: any): { id?: string; name: string; args: any }[] {
  return m?.tool_calls ?? m?.toolCalls ?? [];
}
/* eslint-enable @typescript-eslint/no-explicit-any */
