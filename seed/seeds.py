#!/usr/bin/env python3
"""
Seed LangSmith traces for the "ambient analyst" macro business/strategy agent.

Runs selected conversation batches against a LangGraph Platform deployment concurrently.
Some conversations are one-off questions; others are multi-turn (each follow-up
runs on the SAME thread so the trace shows a real back-and-forth).

Docs this is based on:
  - https://docs.langchain.com/langsmith/deployment-quickstart  (runs.stream, "agent" assistant)
  - https://docs.langchain.com/langsmith/same-thread            (multi-turn on one thread)
  - https://docs.langchain.com/langsmith/agent-server-api/thread-runs/create-run-stream-output

Usage:
    export LANGSMITH_API_KEY=lsv2_...        # or LANGCHAIN_API_KEY
    uv run python seed/seeds.py                     # run batch 1
    uv run python seed/seeds.py --batches 1 2       # run both batches
    uv run python seed/seeds.py --concurrency 10    # cap in-flight conversations
    uv run python seed/seeds.py --limit 5 --dry-run # preview without calling the API

Set the deployment URL with --url or the DEPLOYMENT_URL env var. The assistant defaults to
ambient-analyst, not the lighter ambient-analyst-simple graph.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
import uuid
import dotenv

dotenv.load_dotenv()

DEFAULT_ASSISTANT = "ambient-analyst"

# ---------------------------------------------------------------------------
# Batch 1: 50 seed conversations.
# Each conversation is a list of user turns:
#   - length 1  -> a one-off question
#   - length >1 -> initial question + follow-ups (all on the same thread)
# ---------------------------------------------------------------------------
BATCH_1: list[dict] = [
    # ---- One-off questions --------------------------------------------------
    {"title": "USD strength drivers", "turns": [
        "What's driving the recent strength in the US dollar, and which sectors benefit most? Include a simple visual comparing the main drivers and sector beneficiaries.",
    ]},
    {"title": "Semis bull/bear", "turns": [
        "Give me the bull and bear case for semiconductors heading into next year.",
    ]},
    {"title": "China property", "turns": [
        "How exposed is the global economy to a prolonged slowdown in Chinese property?",
    ]},
    {"title": "Oil price outlook", "turns": [
        "Summarize the key supply and demand factors that will shape oil prices over the next 12 months. Build and share a visual showing the main supply and demand forces.",
    ]},
    {"title": "Fed rate path", "turns": [
        "What does the current rate environment imply for growth vs. value equity positioning? Include a visual comparing the implications for growth and value under the main rate scenarios.",
    ]},
    {"title": "AI capex", "turns": [
        "Is hyperscaler AI capex sustainable, or are we heading toward a digestion phase? Lay out the debate.",
    ]},
    {"title": "EU energy", "turns": [
        "How structurally competitive is European manufacturing given current energy costs?",
    ]},
    {"title": "Reshoring", "turns": [
        "What are the second-order economic effects of supply-chain reshoring to North America?",
    ]},
    {"title": "Commercial real estate", "turns": [
        "Where are the biggest systemic risks in US commercial real estate right now?",
    ]},
    {"title": "India growth", "turns": [
        "Make the case for and against India as the top emerging-market growth story this decade.",
    ]},
    {"title": "Gold thesis", "turns": [
        "Why has gold been resilient despite high real rates? Walk me through the competing explanations.",
    ]},
    {"title": "Labor market", "turns": [
        "How should I read a labor market that's cooling on hiring but not on wages?",
    ]},
    {"title": "Credit spreads", "turns": [
        "What are tight credit spreads telling us, and when have they been misleading in the past?",
    ]},
    {"title": "Yen carry", "turns": [
        "Explain the yen carry trade unwind risk and who is most exposed.",
    ]},
    {"title": "Defense spending", "turns": [
        "How does rising global defense spending flow through to industrial and tech supply chains?",
    ]},
    {"title": "Consumer health", "turns": [
        "Is the US consumer as strong as headline spending suggests? Break down the divergences by income cohort and include a visual comparing the cohorts.",
    ]},
    {"title": "Copper demand", "turns": [
        "Why do people call copper the 'metal of electrification,' and is the demand story overhyped?",
    ]},
    {"title": "Sovereign debt", "turns": [
        "Which developed-market sovereign debt trajectories worry you most and why?",
    ]},
    {"title": "Productivity", "turns": [
        "Could AI actually move the needle on aggregate productivity, or is that wishful thinking?",
    ]},
    {"title": "Deglobalization", "turns": [
        "Is 'deglobalization' real in the trade data, or is it a narrative? Show me both sides.",
    ]},
    {"title": "Housing affordability", "turns": [
        "What structural factors are keeping US housing unaffordable even as rates fluctuate?",
    ]},
    {"title": "Bank sector", "turns": [
        "What should I be watching in regional bank balance sheets over the next few quarters?",
    ]},

    # ---- Multi-turn conversations (with follow-ups) ------------------------
    {"title": "Recession odds deep-dive", "turns": [
        "What's your read on US recession odds over the next 12 months?",
        "Which two indicators would most change that view if they turned?",
        "If a recession does hit, which sectors historically bottom first?",
    ]},
    {"title": "Nvidia concentration", "turns": [
        "How concerned should investors be about market concentration in a handful of AI names?",
        "How does today compare to the dot-com concentration in 2000?",
        "What would a healthy broadening of the rally actually look like?",
    ]},
    {"title": "Rate cuts to portfolio", "turns": [
        "If the Fed cuts three times next year, what's the likely impact on bonds vs. equities?",
        "How would that change if inflation reaccelerates instead?",
        "Given both scenarios, how would you barbell a portfolio?",
    ]},
    {"title": "China stimulus", "turns": [
        "Break down China's latest stimulus measures and whether they're big enough.",
        "Which global exporters benefit most if it works?",
        "And what's the risk to commodities if it doesn't?",
    ]},
    {"title": "Energy transition economics", "turns": [
        "What's the realistic timeline for solar and storage to dominate new power generation?",
        "Where does that leave natural gas demand over the same period?",
        "Which parts of the value chain have the most durable margins?",
    ]},
    {"title": "Inflation regime", "turns": [
        "Are we in a structurally higher-inflation regime than the 2010s? Make the argument.",
        "Now give me the counterargument that disinflation resumes.",
        "What single data series would settle the debate for you?",
    ]},
    {"title": "EM debt opportunity", "turns": [
        "Is emerging-market local-currency debt an attractive entry point right now?",
        "Which countries screen best on fundamentals vs. valuation?",
        "What's the main way this trade goes wrong?",
    ]},
    {"title": "Japan reflation", "turns": [
        "Explain the structural bull case for Japanese equities after decades of stagnation.",
        "How central is corporate governance reform to that thesis?",
        "What could derail it in the next two years?",
    ]},
    {"title": "Software margins", "turns": [
        "How is AI changing the unit economics of enterprise software companies?",
        "Does that help or hurt incumbents vs. startups?",
        "Where should I expect margin compression first?",
    ]},
    {"title": "Commodities supercycle", "turns": [
        "Is there a credible case for a new commodities supercycle this decade?",
        "How does underinvestment in supply factor in?",
        "Which commodities have the tightest structural supply picture?",
    ]},
    {"title": "US fiscal path", "turns": [
        "How sustainable is the US fiscal trajectory given current deficits?",
        "At what point do bond markets start to push back meaningfully?",
        "What are the realistic off-ramps politically and economically?",
    ]},
    {"title": "Private credit growth", "turns": [
        "Why has private credit grown so fast, and is it a systemic risk?",
        "How would it behave in a real default cycle we haven't tested it through?",
        "Who are the ultimate holders of that risk?",
    ]},
    {"title": "Europe vs US equities", "turns": [
        "Why have European equities structurally underperformed US equities?",
        "Is any of that gap cyclical rather than structural?",
        "What would need to change for European outperformance to persist?",
    ]},
    {"title": "Aging demographics", "turns": [
        "How will aging demographics reshape growth and inflation in developed markets? Create and share a visual mapping the main demographic effects on growth and inflation.",
        "Which sectors are structural winners from that shift?",
        "Does immigration realistically offset the drag?",
    ]},
    {"title": "Crypto as macro asset", "turns": [
        "Has bitcoin earned a place as a legitimate macro asset in a diversified portfolio?",
        "How correlated is it really to risk assets vs. gold?",
        "What would falsify the 'digital gold' thesis?",
    ]},
    {"title": "Trade policy shocks", "turns": [
        "Walk me through how a new round of tariffs would ripple through inflation and growth.",
        "Which industries are most and least insulated?",
        "How should a multinational CFO be hedging that risk?",
    ]},
    {"title": "Healthcare disruption", "turns": [
        "How are GLP-1 drugs reshaping the economics of food, retail, and healthcare?",
        "Which second-order effects are the market underpricing?",
        "Who are the clearest structural losers?",
    ]},
    {"title": "Data center power", "turns": [
        "Is power availability the real bottleneck for AI data center buildout? Build and share a visual showing the bottleneck chain from data-center demand to grid capacity.",
        "What does that mean for utilities and grid investment?",
        "Which regions are best positioned to capture that demand?",
    ]},
    {"title": "Small caps", "turns": [
        "What would it take for US small caps to sustainably outperform large caps again?",
        "How does their debt structure make them rate-sensitive?",
        "Is now historically a good entry point on valuation?",
    ]},
    {"title": "Supply chain resilience", "turns": [
        "How should a global manufacturer think about resilience vs. cost after the last few years of shocks?",
        "What does 'China plus one' actually look like in practice?",
        "Where are firms overcorrecting?",
    ]},
    {"title": "Volatility regime", "turns": [
        "Are we entering a structurally higher-volatility macro regime?",
        "What are the main drivers if so?",
        "How does that change the value of holding cash and optionality?",
    ]},
    {"title": "Corporate earnings", "turns": [
        "How resilient are corporate margins if revenue growth slows from here?",
        "Which cost levers have companies already pulled?",
        "Where's the biggest gap between guidance and reality?",
    ]},
    {"title": "Emerging tech themes", "turns": [
        "Beyond AI, which emerging technology themes have the strongest macro tailwinds?",
        "Which are most exposed to a funding slowdown?",
        "How would you separate durable themes from hype?",
    ]},
    {"title": "Global liquidity", "turns": [
        "How should I think about global liquidity as a driver of asset prices right now?",
        "Which central bank actions matter most for that?",
        "What's the lag between liquidity shifts and market impact?",
    ]},
    {"title": "Manufacturing PMIs", "turns": [
        "Global manufacturing PMIs have been soft — is that signal or noise?",
        "How does it square with resilient services activity?",
        "What would confirm a genuine industrial recovery?",
    ]},
    {"title": "Insurance and climate", "turns": [
        "How is climate risk reshaping the economics of the insurance industry?",
        "What are the knock-on effects for real estate and mortgages?",
        "Where does the uninsurable-risk problem land politically?",
    ]},
    {"title": "Wage-price dynamics", "turns": [
        "Is there still a wage-price spiral risk, or has that faded?",
        "How much of recent wage growth is catch-up vs. structural?",
        "Which industries are the bellwethers to watch?",
    ]},
    {"title": "Frontier markets", "turns": [
        "Which frontier markets offer the most compelling risk-adjusted growth stories?",
        "What governance and liquidity risks come with them?",
        "How would you size that in a diversified allocation?",
    ]},
]

# Batch 2: 100 additional conversations.
BATCH_2: list[dict] = [
    {"title": row[0], "turns": list(row[1:])}
    for row in [
        ("Central bank divergence", "How will diverging Fed, ECB, and BOJ policy paths affect currencies, rates, and global equities over the next year?"),
        ("Treasury term premium", "What is driving the US Treasury term premium, and which assets are most sensitive to a sustained increase?"),
        ("Quantitative tightening", "Is quantitative tightening materially tightening financial conditions, or is private liquidity offsetting it?"),
        ("Inflation expectations", "Which market and survey measures best reveal whether inflation expectations are becoming unanchored?"),
        ("Services inflation", "Why is services inflation sticky, and what evidence would show that it is finally normalizing?"),
        ("Food inflation", "Map the main weather, energy, fertilizer, and trade-policy risks to global food inflation."),
        ("Container shipping", "Are elevated container shipping rates temporary disruption or evidence of structurally higher logistics costs?"),
        ("Red Sea trade routes", "Quantify the economic effects of persistent Red Sea shipping disruption by industry and region."),
        ("Panama Canal constraints", "How do Panama Canal capacity constraints affect commodity flows, freight rates, and US supply chains?"),
        ("Global LNG market", "How will new LNG capacity change regional gas prices and the bargaining power of producers and buyers?"),
        ("Uranium cycle", "Assess the uranium supply-demand balance and the strongest risks to the nuclear fuel investment thesis."),
        ("Lithium reset", "Has the lithium market completed its downcycle, and what would signal a durable recovery?"),
        ("Rare earth security", "Which rare-earth supply chains are most vulnerable to geopolitical disruption, and where can substitution work?"),
        ("Steel cycle", "What do steel prices and capacity utilization imply for global manufacturing and construction demand?"),
        ("Fertilizer economics", "How sensitive are fertilizer producers and farm economics to natural-gas prices and export restrictions?"),
        ("Water scarcity", "Which industries and regions face the largest economic exposure to water scarcity over the next decade?"),
        ("Grid modernization", "Where will grid modernization spending create bottlenecks, pricing power, and investment opportunities?"),
        ("Nuclear renaissance", "Is the nuclear renaissance economically credible once financing, construction risk, and fuel supply are included?"),
        ("Carbon markets", "Compare the effectiveness and investability of major compliance and voluntary carbon markets."),
        ("Airline economics", "Can airlines sustain improved margins, or will capacity growth and labor costs restore the old cycle?"),
        ("Auto affordability", "How are financing costs, incentives, and used-car prices reshaping vehicle affordability and demand?"),
        ("EV price war", "Who can survive the global EV price war, and which suppliers carry the greatest volume and margin risk?"),
        ("Battery supply chain", "Identify the tightest links in the battery supply chain and how chemistry changes could shift them."),
        ("Industrial automation", "Which industries have the clearest economic case for accelerated automation over the next five years?"),
        ("Robotics and labor", "How quickly can robotics relieve labor shortages without destroying the productivity gains through excess capex?"),
        ("Pharma patent cliff", "Which pharmaceutical patent expirations matter most, and which companies have credible replacement pipelines?"),
        ("Obesity drug economics", "Trace how obesity drugs could change healthcare spending, food demand, and employer benefit costs."),
        ("Biotech funding", "Is the biotech funding cycle reopening, and which indicators distinguish durable recovery from a short rally?"),
        ("Hospital margins", "What is driving hospital margin recovery, and which labor or reimbursement pressures could reverse it?"),
        ("Medtech demand", "How durable is procedure-volume growth for medtech companies as healthcare utilization normalizes?"),
        ("Cybersecurity budgets", "Which cybersecurity categories retain budget priority in a slowdown, and where is vendor consolidation likely?"),
        ("SaaS consolidation", "What would a mature consolidation cycle look like across enterprise SaaS, and who has acquisition capacity?"),
        ("Cloud margins", "How much additional margin expansion can cloud platforms achieve without slowing product investment?"),
        ("AI inference economics", "Compare the cost curves and competitive moats in AI training versus inference infrastructure."),
        ("Foundry competition", "How should investors evaluate foundry competition across process leadership, yield, subsidies, and geopolitics?"),
        ("Memory chip cycle", "Where are DRAM and NAND in the cycle, and how does AI demand alter the usual inventory pattern?"),
        ("Telecom capex", "When will telecom capex recover, and which equipment categories benefit first?"),
        ("Satellite economics", "Which satellite business models can support attractive returns after launch costs and constellation replacement?"),
        ("Quantum commercialization", "Which quantum-computing applications have a credible path to commercial value before fault tolerance?"),
        ("Advertising cycle", "What do digital and traditional advertising trends reveal about consumer demand and business confidence?"),
        ("Streaming profitability", "Have streaming economics structurally improved, or are current profits mostly the result of temporary cost cuts?"),
        ("Creator economy", "Where does durable pricing power sit in the creator economy: platforms, tools, agencies, or creators?"),
        ("Luxury demand", "How exposed is global luxury demand to China, tourism flows, and aspirational-consumer weakness?"),
        ("Retail shrink", "Separate the evidence from the narrative on retail shrink and quantify its real margin impact."),
        ("Restaurant margins", "Can restaurants preserve margins as traffic slows and wage inflation remains elevated?"),
        ("Travel normalization", "Which travel segments still have structural growth after the post-pandemic normalization ends?"),
        ("Logistics real estate", "Is logistics real estate oversupplied, or do e-commerce and supply-chain redesign support another growth leg?"),
        ("Office conversion", "Where are office-to-residential conversions economically viable, and why do most proposed projects fail?"),
        ("Homebuilder advantage", "Why have large homebuilders gained share, and how durable is their financing and land advantage?"),
        ("Mortgage banking", "How would changing rates affect mortgage originators, servicers, and mortgage insurers differently?"),
        ("Municipal finance", "Which US municipal issuers face the greatest fiscal pressure from pensions, migration, and commercial property?"),
        ("Insurance pricing cycle", "Where is property-and-casualty insurance pricing still hard, and which lines are beginning to soften?"),
        ("Reinsurance capacity", "How are catastrophe losses and alternative capital reshaping reinsurance pricing and capacity?"),
        ("Asset manager margins", "Which asset-management models are best positioned for fee compression and the shift toward private markets?"),
        ("ETF market structure", "How is ETF growth changing price discovery, liquidity, and competition among asset managers?"),
        ("Pension funded status", "How should improved pension funded ratios change corporate allocation and fixed-income demand?"),
        ("Endowment alternatives", "Are endowments overallocated to illiquid alternatives given slower distributions and higher cash needs?"),
        ("Venture reset", "What evidence would show that venture valuations, exits, and fund sizes have fully reset?"),
        ("Private equity exits", "What will unlock the private-equity exit backlog, and which strategies face the greatest pressure?"),
        ("M&A cycle", "Is the M&A cycle turning, and which sectors have the strongest strategic and financing setup?"),
        ("IPO reopening", "What conditions are required for a durable IPO reopening rather than a few isolated deals?"),
        ("Activist investing", "Which balance-sheet and governance conditions make companies most vulnerable to activist campaigns?"),
        ("Corporate buybacks", "How sensitive are corporate buybacks to earnings, taxes, rates, and executive confidence?"),
        ("Dividend resilience", "Which sectors have the most resilient dividends under a mild recession and why?"),
        ("Earnings quality", "Build a practical framework for separating high-quality earnings from accrual-driven or cyclical profits."),
        ("Accounting red flags", "Which accounting signals most reliably flag deteriorating business quality before headline earnings fall?"),
        ("Small business credit", "What do small-business credit conditions imply for hiring, investment, and local-bank losses?"),
        ("Emerging-market dollarization", "When does informal dollarization stabilize an emerging economy, and when does it deepen fragility?"),
        ("African sovereign debt", "Which African sovereign debt restructurings offer durable recovery versus repeated default risk?"),
        ("Latin America nearshoring", "Which Latin American economies can capture nearshoring investment beyond Mexico, and what blocks them?"),
        ("Mexico manufacturing", "Can Mexico convert nearshoring interest into sustained productivity and wage growth?"),
        ("Brazil rate cycle", "How does Brazil's rate cycle affect its currency, banks, domestic equities, and fiscal outlook?"),
        ("Argentina stabilization", "What would distinguish durable stabilization in Argentina from another temporary adjustment?"),
        ("Turkey inflation", "Evaluate Turkey's disinflation path and the risks to policy credibility, banks, and the currency."),
        ("Gulf diversification", "Which Gulf diversification programs are producing self-sustaining private activity rather than state-led demand?"),
        ("ASEAN supply chains", "Which ASEAN countries are gaining most from supply-chain diversification, and where are capacity limits emerging?"),
        ("Korea governance", "How much value could corporate-governance reform unlock in South Korea, and what could prevent it?"),
        ("Taiwan risk premium", "How should investors quantify Taiwan geopolitical risk across semiconductors, shipping, and global portfolios?"),
        ("Australia China exposure", "How vulnerable is Australia to a Chinese slowdown once commodities, education, tourism, and housing are included?"),
        ("Canada household debt", "How does high Canadian household debt change the transmission of rates into housing and consumption?"),
        ("UK productivity", "Why has UK productivity lagged, and which reforms could plausibly improve it?"),
        ("German industry", "Can German industry restore competitiveness amid energy, China, labor, and regulatory pressures?"),
        ("French fiscal outlook", "What adjustment path could stabilize France's public finances without causing a deep slowdown?"),
        ("Nordic housing", "Compare housing and bank risks across Sweden, Norway, Denmark, and Finland."),
        ("Defense industrial capacity", "Can Western defense manufacturers expand capacity fast enough, and where are the binding bottlenecks?"),
        ("Sanctions effectiveness", "Under what conditions do financial and trade sanctions meaningfully alter state behavior?"),
        ("Tariff pass-through", "Who ultimately bears tariffs across importers, consumers, workers, and foreign producers?"),
        ("Election fiscal cycles", "How do election cycles change fiscal policy, inflation risk, and sovereign bond performance?"),
        ("Immigration economics", "Separate the near-term and long-term effects of immigration on wages, housing, inflation, and fiscal balances."),
        ("Labor participation", "Which policies or demographic shifts could materially raise labor-force participation?"),
        ("Remote work equilibrium", "Where is remote work settling by industry, and what are the second-order effects on cities and productivity?"),
        ("Education ROI", "How is the return on higher education changing across fields, institutions, and financing models?"),
        ("Climate adaptation", "Which climate-adaptation investments offer the highest economic returns, and who will finance them?"),
        ("Disaster reconstruction", "How do major disasters affect regional growth, inflation, insurance, and migration over time?"),
        ("Prediction markets", "When do prediction markets outperform surveys and expert forecasts, and where do they systematically fail?"),
        ("Global soft landing", "Build the case for a synchronized global soft landing.", "Now identify the weakest link in that case.", "Which three indicators would invalidate the base case first?"),
        ("Stagflation portfolio", "Construct a stagflation scenario for the next two years.", "Which industries gain or lose pricing power?", "How would you stress-test a diversified portfolio against it?"),
        ("Debt refinancing wall", "Map the corporate debt refinancing wall by sector.", "Which borrowers can absorb higher coupons?", "What would turn a refinancing problem into a default cycle?"),
        ("AI labor transition", "Estimate how AI adoption could reshape white-collar labor demand.", "Which roles are complemented rather than displaced?", "What macro data would reveal the transition earliest?"),
        ("Energy security", "Compare US, European, and Asian energy-security strategies.", "Where do cost and resilience objectives conflict?", "Which strategy looks most durable under a supply shock?"),
    ]
]

BATCHES = {1: BATCH_1, 2: BATCH_2}
CONVERSATIONS = BATCH_1


def conversations_for_batches(batch_numbers: list[int]) -> list[dict]:
    return [conversation for number in batch_numbers for conversation in BATCHES[number]]


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------
async def run_conversation(client, assistant_id, convo, sem, batch_id, dry_run):
    """Run one conversation (1+ turns) on a single thread."""
    title = convo["title"]
    turns = convo["turns"]
    kind = "multi-turn" if len(turns) > 1 else "one-off"

    async with sem:
        if dry_run:
            print(f"[dry-run] {title} ({kind}, {len(turns)} turn(s))")
            return {"title": title, "ok": True, "turns": len(turns)}

        try:
            thread = await client.threads.create(
                metadata={"seed_batch": batch_id, "seed_title": title, "seed": True}
            )
            thread_id = thread["thread_id"]

            for i, content in enumerate(turns, start=1):
                # Stream the run so it completes and produces a full trace.
                async for _chunk in client.runs.stream(
                    thread_id,
                    assistant_id,
                    input={"messages": [{"role": "human", "content": content}]},
                    stream_mode="updates",
                    metadata={
                        "seed_batch": batch_id,
                        "seed_title": title,
                        "seed_turn": i,
                        "seed": True,
                    },
                ):
                    pass  # we don't need the tokens, just the completed run

            print(f"[done] {title} ({kind}, {len(turns)} turn(s)) "
                  f"thread={thread_id}")
            return {"title": title, "ok": True, "turns": len(turns),
                    "thread_id": thread_id}

        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] {title}: {e!r}")
            return {"title": title, "ok": False, "error": repr(e)}


async def main_async(args) -> int:
    api_key = os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: set LANGSMITH_API_KEY (or LANGCHAIN_API_KEY) in your environment.",
              file=sys.stderr)
        return 2

    convos = conversations_for_batches(args.batches)
    convos = convos[: args.limit] if args.limit else convos
    batch_id = f"seed-{'-'.join(map(str, args.batches))}-{uuid.uuid4().hex[:8]}"

    n_single = sum(1 for c in convos if len(c["turns"]) == 1)
    n_multi = len(convos) - n_single
    total_runs = sum(len(c["turns"]) for c in convos)
    print(f"Deployment : {args.url}")
    print(f"Assistant  : {args.assistant}")
    print(f"Batch id   : {batch_id}")
    print(f"Conversations: {len(convos)}  ({n_single} one-off, {n_multi} multi-turn)")
    print(f"Total runs : {total_runs}   Concurrency: {args.concurrency}"
          f"{'   [DRY RUN]' if args.dry_run else ''}")
    print("-" * 70)

    if args.dry_run:
        client = None
    else:
        from langgraph_sdk import get_client
        client = get_client(url=args.url, api_key=api_key)
    assistant_id = args.assistant

    sem = asyncio.Semaphore(args.concurrency)
    start = time.time()
    results = await asyncio.gather(*[
        run_conversation(client, assistant_id, c, sem, batch_id, args.dry_run)
        for c in convos
    ])
    elapsed = time.time() - start

    ok = sum(1 for r in results if r["ok"])
    failed = [r for r in results if not r["ok"]]
    print("-" * 70)
    print(f"Completed {ok}/{len(results)} conversations in {elapsed:.1f}s "
          f"(batch {batch_id}).")
    if failed:
        print(f"{len(failed)} failed:")
        for r in failed:
            print(f"  - {r['title']}: {r.get('error')}")
    print("\nFilter these traces in LangSmith by metadata: "
          f"seed = true  /  seed_batch = {batch_id}")
    return 0 if not failed else 1


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Seed LangSmith traces for the ambient analyst agent.")
    p.add_argument("--url", default=os.environ.get("DEPLOYMENT_URL"),
                   required="DEPLOYMENT_URL" not in os.environ,
                   help="LangGraph deployment URL")
    p.add_argument("--assistant", default=os.environ.get("ASSISTANT_ID", DEFAULT_ASSISTANT),
                   help=f"Assistant/graph id (default: {DEFAULT_ASSISTANT})")
    p.add_argument("--concurrency", type=int, default=25,
                   help="Max conversations in flight at once (default: 25 = all)")
    p.add_argument("--batches", nargs="+", type=int, choices=BATCHES, default=[1],
                   help="Seed batches to run (default: 1)")
    p.add_argument("--limit", type=int, default=0,
                   help="Only run the first N selected conversations (0 = all)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print the plan without calling the deployment")
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main_async(parse_args())))
