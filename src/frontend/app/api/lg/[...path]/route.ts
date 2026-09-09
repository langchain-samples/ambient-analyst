import { NextRequest } from "next/server";

// Same-origin passthrough to the LangGraph agent server. Keeps the LangSmith
// key server-side and avoids CORS. Point LANGGRAPH_DEPLOYMENT_URL at a local
// `langgraph dev` (default) or the LangSmith deployment URL.
export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const BASE = (
  process.env.LANGGRAPH_DEPLOYMENT_URL ?? "http://127.0.0.1:2024"
).replace(/\/$/, "");
const API_KEY = process.env.LANGSMITH_API_KEY ?? process.env.LANGGRAPH_API_KEY;

async function handler(
  req: NextRequest,
  ctx: { params: Promise<{ path?: string[] }> },
) {
  const { path = [] } = await ctx.params;
  const target = `${BASE}/${path.join("/")}${req.nextUrl.search}`;

  const headers = new Headers(req.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");
  if (API_KEY) headers.set("x-api-key", API_KEY);

  const hasBody = !["GET", "HEAD"].includes(req.method);
  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method: req.method,
      headers,
      body: hasBody ? req.body : undefined,
      // Required by Node's fetch when streaming a request body.
      ...(hasBody ? { duplex: "half" } : {}),
      redirect: "manual",
    } as RequestInit);
  } catch {
    return Response.json(
      { error: "LangGraph agent unavailable", retryable: true },
      { status: 502 },
    );
  }

  // Pass the (possibly streaming/SSE) body straight through. Drop encoding/
  // length headers — fetch has already decoded the upstream response.
  const resHeaders = new Headers(upstream.headers);
  resHeaders.delete("content-encoding");
  resHeaders.delete("content-length");
  return new Response(upstream.body, {
    status: upstream.status,
    headers: resHeaders,
  });
}

export {
  handler as GET,
  handler as POST,
  handler as PUT,
  handler as PATCH,
  handler as DELETE,
  handler as OPTIONS,
};
