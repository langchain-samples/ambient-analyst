# LLM Scorecard

*Last updated: August 19, 2026*

## Current Coding Recommendation (verified 2026-08-19)

| Coding workload | Recommended model/configuration | Current evidence | Confidence / caveat |
|---|---|---|---|
| General agentic coding / terminal work | **GPT-5.6 Sol in Codex CLI**; use medium for iteration and max for difficult final passes | Vals Terminal-Bench 2.1, updated 2026-08-18: Sol leads at 85.77% versus Claude Opus 5 at 84.64%; they tie at 84.44% on the hard split. OpenAI reports Sol max at 80 on Artificial Analysis Coding Agent Index v1.1 and 88.8% on Terminal-Bench 2.1. Sources: https://vals.ai/benchmarks/terminal-bench-2-1, https://openai.com/index/gpt-5-6 | **Moderate-high** for workflow choice; lower for “best underlying model” because harnesses materially affect results and the hard-task split is tied. |
| Algorithmic coding / raw patch quality | **Claude Opus 5** | Vals reports Opus 5 leads IOI at 91.67% versus Sol at 86.67%, and leads SWE-bench Verified at 97.00% versus Sol at 96.20%. Sources: https://vals.ai/benchmarks/ioi, https://vals.ai/benchmarks/swebench | **Moderate**: IOI is useful but narrower than software engineering; SWE-bench Verified is contaminated and saturated, so it is only supporting evidence. |

## Workload Recommendations — Financial Research Team (verified 2026-08-18)

| Workload | Recommended model/configuration | Current evidence | Source type | Tradeoff / caveat |
|---|---|---|---|---|
| Long-context financial research | **Claude Opus 5**, adaptive reasoning at medium/high; max for final high-stakes synthesis | Official Anthropic docs: launched 2026-07-24; 1M context, 128k max output, $5/$25 per MTok. Current Artificial Analysis GDPval-AA v2 page places Opus 5 max first at 1846 Elo (±23) versus GPT-5.6 Sol max at 1729 (±17). AA's 2026-07-24 launch analysis reported Opus 5 at 1720 Elo on AA-Briefcase. Vals' finance page updated 2026-08-18 places Opus 5 #3 on Finance Agent v2; its Excel benchmark updated 2026-08-13 showed Opus 5 at 73.6%, essentially tied with Fable 5 at 73.7% and Sol at 72.3%. | Official specs + independent/third-party benchmark runs | Best triangulated broad professional/finance choice, but finance leadership is mixed by task. AA also reported a 50% hallucination rate on AA-Omniscience for Opus 5 max, so source-grounding and verification are mandatory. No public benchmark fully tests citation-grounded synthesis across filings, calls, commentary, and macro data. Sources: https://docs.anthropic.com/en/release-notes/api, https://www.anthropic.com/news/claude-opus-5, https://artificialanalysis.ai/evaluations/gdpval-aa, https://artificialanalysis.ai/articles/opus-5, https://www.vals.ai/benchmarks/emb, https://www.vals.ai/benchmarks#finance-benchmarks |
| Fast iterative coding | **GPT-5.6 Sol medium in Codex CLI** | Terminal-Bench 2.1: 85.77% vs. Opus 5 at 84.64% (Vals, updated 2026-08-13); hard split tied at 84.44%. OpenAI's 2026-07-09 release reports Sol at 88.8% on Terminal-Bench 2.1 and 80 on the Artificial Analysis Coding Agent Index, but these are vendor-presented results. | Same-harness third-party benchmark + vendor release evidence | Best workflow-speed choice, not necessarily best raw patch/app quality. Terminal-Bench measures model+harness; Opus 5 used Opus 4.8 refusal fallback, which lowers its score to 81.27% if affected passes count as failures. SWE-bench Verified is contaminated; OpenAI said on 2026-02-23 that it stopped reporting the benchmark because gains increasingly reflect training exposure. Sources: https://www.vals.ai/benchmarks/terminal-bench-2-1, https://openai.com/index/gpt-5-6, https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified |



## Small / On-Device Models (as of June 2026)

> Models designed to run locally on consumer hardware (laptop/phone) without cloud inference.

| Model | Lab | Release Date | Params | Hardware Req. | Key Features | Source | Verified |
|-------|-----|--------------|--------|---------------|--------------|--------|---------|
| **Gemma 4 12B** | Google | **June 3, 2026** | 11.95B | 16 GB RAM (laptop) | 256K context, multimodal (audio+video, encoder-free), agentic tool-use, step-by-step reasoning; available on Hugging Face/Kaggle/AI Edge Gallery (Mac + iPhone) | [Ars Technica](https://arstechnica.com/google/2026/06/googles-new-gemma-4-open-ai-model-is-sized-for-your-laptop/), [VentureBeat](https://venturebeat.com/technology/googles-new-open-source-gemma-4-12b-analyzes-audio-video-and-runs-entirely-locally-on-a-typical-16gb-enterprise-laptop) | 2026-06-09 |
| Gemma 4 (main lineup, smaller variants) | Google | May 19, 2026 (Google I/O) | Various (mobile-scale) | Mobile / low-end | Main Gemma 4 lineup; mobile-optimized variants; 12B added June 3 to fill gap | [Android Authority](https://www.androidauthority.com/google-gemini-3-5-flash-3668559/) | 2026-06-09 |

**Most recent small/on-device model: Google Gemma 4 12B (June 3, 2026)**

## OpenAI Model Deprecation Schedule (as of June 2026)

*Source: [platform.openai.com/api/docs/deprecations](https://platform.openai.com/api/docs/deprecations) — fetched 2026-06-10 (authoritative)*

### Already shut down (past deprecations relevant to 2025–2026)
| Shutdown Date | Model(s) | Replacement |
|--------------|----------|-------------|
| 2026-02-17 | `chatgpt-4o-latest` | `gpt-5.1-chat-latest` |
| 2026-03-24 | `gpt-4o-audio-preview-2025-06-03`, `gpt-4o-mini-audio-preview` | `gpt-audio-1.5` |
| 2026-03-26 | `gpt-4-0314`, `gpt-4-0125-preview` (incl. `gpt-4-turbo-preview`) | `gpt-5` or `gpt-4.1` |
| 2026-05-07 | `gpt-4o-realtime-preview` family (5 models) | `gpt-realtime-1.5` |
| 2026-05-12 | `dall-e-2`, `dall-e-3`, Realtime API Beta | `gpt-image-2`; Realtime API GA |

### ChatGPT UI retirements
| Retirement Date | Model(s) Retired from ChatGPT | Notes |
|----------------|-------------------------------|-------|
| 2026-02-13 | **GPT-4o, GPT-4.1, GPT-4.1 mini, OpenAI o4-mini** | Also retired `gpt-5` (Instant and Thinking) at same time per announcement |

### Upcoming shutdowns (announced, not yet effective as of June 2026)
| Shutdown Date | Key Models | Replacement |
|--------------|------------|-------------|
| **July 23, 2026** | `gpt-5-chat-latest`, `gpt-5-codex`, `gpt-5.1-chat-latest`, `gpt-5.1-codex`, `gpt-5.1-codex-max`, `gpt-5.1-codex-mini`, `gpt-5.2-codex` | `gpt-5.5` |
| July 23, 2026 | `gpt-4o-audio-preview-2024-12-17`, `gpt-4o-mini-audio-preview-2024-12-17`, `gpt-4o-mini-realtime-preview-2024-12-17` | `gpt-audio-1.5`/`gpt-realtime-mini` |
| July 23, 2026 | `computer-use-preview-2025-03-11`, `gpt-4o-search-preview-2025-03-11`, `gpt-4o-mini-search-preview-2025-03-11` | `gpt-5.4-mini` |
| July 23, 2026 | `o3-deep-research-2025-06-26`, `o4-mini-deep-research-2025-06-26` | `gpt-5.5-pro` |
| **August 10, 2026** | `gpt-5.2-chat-latest`, `gpt-5.3-chat-latest` | `gpt-5.5` |
| August 26, 2026 | Assistants API | Responses API + Conversations API |
| **September 24, 2026** | Sora 2 / Videos API (`sora-2`, `sora-2-pro`, all snapshots) | No direct replacement listed |
| September 28, 2026 | `gpt-3.5-turbo-instruct`, `gpt-3.5-turbo-1106`, `babbage-002`, `davinci-002` | `gpt-5.4-mini` |
| **October 23, 2026** | `gpt-3.5-turbo-0125`, `gpt-4-0613`, `gpt-4-turbo`, `gpt-4o-2024-05-13`, `gpt-4.1-nano`, `o1-2024-12-17`, `o1-pro-2025-03-19`, `o3-mini-2025-01-31`, `o4-mini-2025-04-16`, `gpt-image-1` | `gpt-5.5` / `gpt-5.4-mini` |
| October 23, 2026 | Fine-tuned versions: `ft-gpt-3.5-turbo`, `ft-gpt-4`, `ft-gpt-4.1-nano`, `ft-babbage-002`, `ft-davinci-002`, `ft-o4-mini` | `gpt-5.4-mini` / `gpt-5.5` |
| December 1, 2026 | `gpt-image-1-mini`, `gpt-image-1.5`, `chatgpt-image-latest` | `gpt-image-2` |
| November 30, 2026 | OpenAI Evals platform, Agent Builder, `v1/prompts` API | Promptfoo (Evals); Agents SDK (Agent Builder) |
| January 6, 2027 | Self-serve fine-tuning (new job creation) | — |

### LMArena — Models Deprecated from Battle Mode (GitHub list, as of 2025-06-27 snapshot)
The most recently added models to the Arena deprecation list (likely earliest 2025 based on naming patterns):
- `gemini-2.5-pro-preview-05-06`, `gemini-2.5-flash-preview-04-17` — recent Gemini 2.5 previews
- `llama-4-maverick-03-26-experimental` — Llama 4 experimental
- `gemini-2.5-pro-exp-03-25`, `gemini-2.0-pro-exp-02-05` — older Gemini exp previews
- `gpt-4.1-nano-2025-04-14`, `qwen3.5-30b-a3b`, `olmo-2-0325-32b-instruct` — recent small models
- `gemma-3-12b-it`, `gemma-3-4b-it` — Gemma 3 variants
*(Full list of 200+ deprecated models available at [GitHub](https://github.com/lmarena/lmarena.github.io/blob/main/_pages/model_list.md))*

---

## Terminal-Bench 2.0 — Agentic Coding (Command-Line) Leaderboard

> **About Terminal-Bench 2.0**: Evaluates AI agents on real command-line / terminal tasks requiring multi-step tool use, shell scripting, file manipulation, and system-level operations. This is a *combined agent+model* leaderboard — results reflect the scaffolding agent AND the underlying model. Separate from SWE-bench (which is code patching, not terminal operation). 142 entries. Source: [tbench.ai/leaderboard/terminal-bench/2.0](https://www.tbench.ai/leaderboard/terminal-bench/2.0) | **Live-fetched: 2026-06-22.**

> **Key caveat**: Scores reflect agent system + model combos. The same model can rank very differently depending on the agent harness. All results are verified by the Terminal-Bench team.

> ⚠️ **Correction (2026-06-22)**: Prior scorecard had "vix + Claude 4.7 = 90.2%" as #1. Live fetch shows this entry is **no longer present** in the leaderboard (142 entries, no "vix" entry visible). The current top is NexAU-AHE + GPT-5.5 at 84.7%. It is possible "vix" was removed or never existed as described; treat the prior entry as unverified/superseded.

### Full Leaderboard — Live Fetch 2026-06-22 (142 entries, showing top ~25 + notable entries)

| Rank | Agent | Model | Lab | Score | ±CI | Date Submitted |
|------|-------|-------|-----|-------|-----|----------------|
| 1 | **NexAU-AHE** | **GPT-5.5** | OpenAI | **84.7%** | ±2.1 | 2026-05-14 |
| 2 | **LemonHarness** | Multiple | Multiple | **84.5%** | ±2.6 | 2026-05-14 |
| 3 | **Capy** | **GPT-5.5** | OpenAI | **83.1%** | ±2.1 | 2026-05-14 |
| 4 | **Codex CLI** | **GPT-5.5** | OpenAI | **82.2%** | ±2.2 | 2026-04-23 |
| 4 | **Polaris** | Multiple | Multiple | **82.2%** | ±2.8 | 2026-05-14 |
| 6 | **WOZCODE** | **Claude Opus 4.7** | Anthropic | **80.2%** | ±2.1 | 2026-05-14 |
| 6 | **TongAgents** | **Gemini 3.1 Pro** | Google | **80.2%** | ±2.6 | 2026-03-13 |
| 8 | LemonHarness | Multiple | Multiple | 79.9% | ±3.0 | 2026-05-14 |
| 9 | SageAgent | GPT-5.3-Codex | OpenAI | 78.4% | ±2.2 | 2026-03-13 |
| 10 | Droid | GPT-5.3-Codex | OpenAI | 77.3% | ±2.2 | 2026-02-24 |
| 11 | Meta-Harness | Claude Opus 4.6 | Anthropic | 76.4% | ±2.4 | 2026-05-14 |
| 12 | CodeBrain-1.5 | GPT-5.3-Codex | OpenAI | 75.8% | ±2.0 | 2026-02-10 |
| 13 | Codelia | GPT-5.3-Codex | OpenAI | 75.7% | ±2.2 | 2026-05-14 |
| 14 | Capy | Claude Opus 4.6 | Anthropic | 75.3% | ±2.4 | 2026-03-12 |
| 15 | Simple Codex | GPT-5.3-Codex | OpenAI | 75.1% | ±2.4 | 2026-02-06 |
| 16 | Terminus-KIRA | Gemini 3.1 Pro | Google | 74.8% | ±2.6 | 2026-02-23 |
| 17 | Terminus-KIRA | Claude Opus 4.6 | Anthropic | 74.7% | ±2.6 | 2026-02-22 |
| 18 | Mux | GPT-5.3-Codex | OpenAI | 74.6% | ±2.5 | 2026-03-06 |
| 19 | MAYA-V2 | Claude 4.6 Opus | Anthropic | 72.1% | ±2.2 | 2026-03-12 |
| 20 | TongAgents | Claude Opus 4.6 | Anthropic | 71.9% | ±2.7 | 2026-02-22 |
| 21 | spoox-o-m | GPT-5.3-Codex | OpenAI | 71.5% | ±2.5 | 2026-05-15 |
| 22 | Junie CLI | Multiple | JetBrains | 71.0% | ±2.9 | 2026-03-07 |
| 40 | Gemini CLI | Gemini 3.1 Pro | Google | 61.4% | ±4.1 | 2026-05-14 |
| 45 | Gemini CLI | Gemini 3.1 Pro | Google | 59.4% | ±4.2 | 2026-05-14 |
| 50 | **Claude Code** | **Claude Opus 4.6** | Anthropic | **58.0%** | ±2.9 | 2026-02-07 |
| 53 | Grok CLI | Grok 4.20 Reasoning | xAI | 57.3% | ±N/A | 2026-04-02 |
| 62 | OpenHands | Claude Opus 4.5 | Anthropic | 51.9% | ±2.9 | 2026-01-04 |
| — | IndusAGI | MiniMax M2.7 | MiniMax | 45.1% | ±N/A | 2026-05-14 |

**Notable observations (live fetch 2026-06-22):**
- **Top model is GPT-5.5** in multiple third-party harnesses: NexAU-AHE (84.7%), Capy (83.1%), Codex CLI (82.2%)
- **Best Claude result**: WOZCODE + Claude Opus 4.7 = 80.2% (rank 6)
- **Best Gemini result**: TongAgents + Gemini 3.1 Pro = 80.2% (rank 6, tied)
- **Google's own Gemini CLI + Gemini 3.1 Pro**: 61.4% and 59.4% — far below third-party TongAgents with same model
- **Anthropic's own Claude Code + Claude 4.6**: only 58.0% — vs 80.2% for WOZCODE + Claude 4.7
- **Grok CLI + Grok 4.20 Reasoning**: 57.3% (April 2026)
- **No Claude 4.8 or Claude Fable 5 entries** — most recent Claude entries use 4.7 (May 2026) or 4.6
- **No DeepSeek V4** entries; Kimi K2 Thinking: 35.7% (old); MiniMax M2.7: 45.1%
- "vix" entry previously cited as #1 at 90.2% is **absent** from live leaderboard

### Validity Caveats (Terminal-Bench 2.0)
1. **Agent system dominates score**: WOZCODE + Claude 4.7 = 80.2%, but Anthropic's own Claude Code + Claude 4.6 = only 58.0%. Scaffolding quality often matters more than the model.
2. **Verified evaluations**: Terminal-Bench team verifies results — more trustworthy than pure self-reporting, but not fully independent.
3. **Task scope**: Terminal / shell tasks are narrower than full SWE-bench repo patching; strong terminal agents don't always generalize.
4. **Most recent entries**: May 14–15, 2026. **No Claude 4.8 or Claude Fable 5 entries** — leaderboard lags recent Anthropic releases by at least 3–4 weeks.
5. **No "vix" entry** confirmed in live fetch — prior scorecard data was incorrect; top is now NexAU-AHE at 84.7%.

---

## MCP Atlas (Tool Use) — Scale AI SEAL Leaderboard

> Evaluates real-world tool use through the Model Context Protocol (MCP). More representative of agentic workflows than code-patching benchmarks. Source: [labs.scale.com](https://labs.scale.com/leaderboard/mcp_atlas) | Fetched: 2026-06-10.

| Rank | Model | Lab | Score | ±CI |
|------|-------|-----|-------|-----|
| 1 | **Gemini 3.5 Flash (high)** | Google | **83.60%** | ±2.30 |
| 1 | **Claude Opus 4.8 (max)** | Anthropic | **82.20%** | ±2.40 |
| 1 | **Muse Spark** | Meta | **82.20%** | ±2.30 |

*Significant finding: Gemini 3.5 Flash leads on pure tool use / MCP tasks — aligns with its #1 LMArena Math position and confirms strong agentic task routing capability despite not leading on raw coding.*

---

## Key Benchmark Validity Update — SWE-bench Verified Contamination (2026)

> **Critical**: OpenAI has formally stopped reporting SWE-bench Verified scores, citing a contamination audit that found **every frontier model tested** (including OpenAI's own models, Claude, and Gemini 3 Flash) could reproduce verbatim gold patches or problem-statement specifics for some Verified tasks. Source: [openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) | Date: ~2026.
> This strongly validates the SWE-bench Pro migration. Treat SWE-bench Verified scores for all frontier models with **high contamination skepticism**.

## Benchmark Validity Status — Key Evals (June 2026)

> Sources: arXiv 2602.16763v1 (EvalEval, ~Feb 2026), Digital Applied methodology guide (mid-2026), Nature vol.653 pp.1047-1051 (April 22, 2026)

| Benchmark | Status (June 2026) | Top frontier scores | Key contamination/validity issue |
|-----------|-------------------|--------------------|---------------------------------|
| **MMLU** | 🔴 Saturated | ~90–96% | Fully saturated; no longer discriminates frontier models |
| **MMLU-Pro** | 🟡 Approaching saturation | 88–94% band | 6-point spread is within noise |
| **HumanEval** | 🔴 Saturated | >88% (Gemini 3.1 Pro 94.3%) | Single-function benchmark; saturated |
| **GPQA Diamond** | 🟡 Near-saturated at frontier | Claude 4.7 ~94.2%, Gemini 3.1 Pro ~94.3% | PhD expert ceiling ~65%; models vastly exceeded; little discriminative headroom |
| **MATH-500** | 🔴 Saturated | o3/Grok-4 ~99%, DeepSeek R1 98.3% | Near-perfect scores; done |
| **GSM8K** | 🔴 Saturated | ~99%+ | Done years ago |
| **SWE-bench Verified** | 🟡 Contaminated + saturating | 78–89% (frontier) | Gold patches recoverable from task IDs (OpenAI Frontier Evals confirmed); SWE-bench Pro same models score 23–59% — 30+ pp gap |
| **SWE-bench Pro** | 🟢 Low contamination | Top ~59% (GPT-5.4 xHigh) | Multi-language, 1,865 tasks, post-training-cutoff issues; still meaningful |
| **LiveBench** | 🟢 Contamination-resistant | Top models <70% | Monthly refresh from recent arXiv/news; best available for coding/reasoning |
| **LiveCodeBench** | 🟢 Contamination-resistant | — | Post-cutoff harvesting; directly measures memorization drop |
| **ARC-AGI-2** | 🟢 Very hard | Best competition score 24% (ARC Prize 2025) | Fluid reasoning; large headroom |
| **HLE** | 🟢 Resistant so far | Top no-tools public ~46.9% (May 2026) vs. ~90% human-expert ceiling | Jan 2025 launch; headroom remains |
| **Arena (LMArena)** | 🟡 Style-biased | — | Human preference; top 3 usually within overlapping CIs; labs tune for "arena appeal" |

#---

## GPQA Diamond — Top Models (as of June 2026)

> **About GPQA Diamond**: 198 multiple-choice questions (subset of 448 full GPQA) written by PhD-level domain experts in biology, chemistry, and physics. "Google-proof" — designed to be unsolvable by web search. Human PhD expert accuracy: ~65–70%. Non-expert accuracy: ~34% despite web access. Originally GPT-4 scored 39%; top models now exceed 94%, indicating rapid progress and emerging **saturation near the top**. All scores below are **self-reported unless otherwise noted**.

> **Source note (June 2026)**: Three live leaderboards now cover GPQA with different model coverage and methodologies:
> - **llm-stats.com** (last updated June 7, 2026; 220+ models; aggregates self-reported scores) — best for breadth
> - **pricepertoken.com** (last updated June 11, 2026; 240 models; sources data from Artificial Analysis) — most recently dated
> - **vals.ai** does NOT yet run GPQA independently; no independent standardized harness exists for GPQA (unlike SWE-bench)

### Full Leaderboard (top ~20, cross-referenced across sources, June 2026)

| Rank | Model | Lab | Score (llm-stats, Jun 7) | Score (pricepertoken, Jun 11) | Notes |
|------|-------|-----|--------------------------|-------------------------------|-------|
| 1 | **Sakana Fugu-Ultra** | Sakana AI | **95.5%** | — | **NEW #1 as of July 7, 2026** on BenchLM; multi-agent orchestrator (NOT a single model — routes to pool of frontier LLMs); self-reported; launched June 22, 2026 |
| 1 | **Sakana Fugu** | Sakana AI | **95.5%** | — | Tied #1 on BenchLM (Jul 7, 2026); lower-latency variant; self-reported |
| 3 | Claude Fable 5 | Anthropic | **94.5%** | **92.6%** | BenchLM #3 (Jul 7, 2026); pricepertoken #3 at 92.6% (Jul 5, 2026) |
| 4 | **Claude Mythos Preview** | Anthropic | **94.6%** | — | Restricted model; self-reported; still #1 on llm-stats (226 models, July 2026) |
| 5 | **Gemini 3.1 Pro Preview** | Google | **94.3%** | **94.1%** | llm-stats #2 (July 2026); pricepertoken #1 at 94.1% (Jul 5, 2026) |
| 6 | Claude Opus 4.7 (Adaptive) | Anthropic | 94.2% | 91.4% | BenchLM #4 |
| 7 | Claude Mythos 5 | Anthropic | 94.1% | — | BenchLM #5; restricted model |
| 8 | Claude Opus 4.8 | Anthropic | 93.6% | — | BenchLM #6; tied with GPT-5.5 |
| 8 | GPT-5.5 | OpenAI | 93.6% | — | BenchLM #7; llm-stats rank 4 (tied) |
| 10 | GPT-5.4 | OpenAI | 92.8% | 92.0% | |
| 11 | Qwen3.7 Max | Alibaba | 92.4% | 92.3% (AA) | Strong agreement across sources |
| 12 | Gemini 3.5 Flash | Google | 92.2% | 92.2% (AA) | BenchLM #11 |
| 13 | Claude Opus 4.6 | Anthropic | 91.3% | — | |
| 13 | **GLM-5.2** | Zhipu AI | **91.2%** | — | Best open-weight at 91.2%; #12 llm-stats (July 2026, 226 models) |
| 15 | Kimi K2.6 | Moonshot AI | 90.5% | 91.1% | |
| 16 | Qwen3.6 Plus | Alibaba | 90.4% | — | |
| 17 | DeepSeek-V4-Pro-Max | DeepSeek | 90.1% | 88.8% | |
| 17 | Grok 4.3 | xAI | 90.1% | — | BenchLM #18 |
| 19 | Claude Sonnet 4.6 | Anthropic | 89.9% | 87.5% | |
| — | Nvidia Nemotron 3 Ultra | Nvidia (open-weight) | 87.0% | 86.7% | Best large US open-weight |
| — | Gemma 4 31B | Google (open-weight) | 84.3% | 85.7% | Best open-weight under ~50B |

**Human expert baseline**: ~65–70% (PhD-level, no web access)
**Saturation signal**: Top 5 models within 0.9 point (BenchLM June 18). Benchmark effectively saturated at frontier. BenchLM has set this benchmark to "Refreshing" state (softening its composite weight).
**llm-stats live (July 2026)**: 226 models. **Best open-weight: GLM-5.2 (Zhipu AI) at 91.2%, rank #12** — new entry as of this fetch. Claude Fable 5 NOT yet on llm-stats GPQA leaderboard.

### GPQA Validity Caveats
1. **Most scores are self-reported** — labs run with their own harnesses and CoT settings. vals.ai runs a standardized independent zero-shot/few-shot CoT harness; BenchLM and llm-stats aggregate self-reports.
2. **Source disagreement**: vals.ai (June 10, 2026) puts Gemini 3.1 Pro Preview #1 at **95.45%**, with Fable 5 and GPT-5.5 tied at 93.18%. BenchLM (June 18, 2026) puts Fable 5 #1 at 94.5%, Gemini 3.1 Pro at ~94.3%. These are different harnesses producing different orderings — both are plausible.
3. **Saturation confirmed**: top models cluster at 91–95%, well past PhD expert ceiling (~65–70%). Little discriminative signal remains at the frontier.
4. **Contamination risk**: GPQA Diamond is public (HuggingFace), so training-set contamination is plausible for newer models.
5. **Claude Mythos 5** (94.1%): restricted/cybersecurity model; self-reported; not publicly reproducible.
6. **Extended thinking matters**: All top scores use thinking/reasoning modes. Models score 5–12pp lower in standard (non-thinking) mode.
7. **Claude Fable 5 first GPQA evaluation**: June 18, 2026 on BenchLM. Not yet on vals.ai standardized GPQA harness (vals.ai GPQA page last updated June 10, 2026 — pre-dates Fable 5 addition).

---

## MMLU-Pro — Top Models (as of June 2026)

> **About MMLU-Pro**: ~12,000 questions across 14 subject areas (science, math, law, business, etc.). 10-answer multiple-choice (vs MMLU's 4), removes trivial questions. CoT reasoning helps more than direct answering (unlike MMLU). Originally models scored 16–33% lower than on MMLU; top models now approach 91–92%, showing **near-full saturation**. All scores are **self-reported unless noted**.

> **Source note (June 2026)**: Three leaderboards cross-checked:
> - **vals.ai** (updated June 9, 2026; 110 models; **standardized 5-shot CoT harness** — most methodologically rigorous; closest to independent) → **Claude Fable 5 #1 at 91.5%**
> - **llm-stats.com** (last updated June 7, 2026; 220+ models; self-reported) → **Qwen3.7 Max #1 at 89.6%**
> - **BenchLM.ai** (updated June 2, 2026; 40 models; self-reported) → **Qwen3.7 Max #1 at 89.6%, Claude Opus 4.5 89.5%**

### vals.ai Top-10 (standardized 5-shot CoT, updated June 17, 2026)

| Rank | Model | Lab | Score | ±CI | Cost/1M | Latency |
|------|-------|-----|-------|-----|---------|---------|
| 1 | **Claude Fable 5** | Anthropic | **91.50%** | ±0.28 | $10/$50 | 25.0s |
| 2 | **Gemini 3.1 Pro Preview** | Google | **90.99%** | ±0.28 | $2/$12 | 23.9s |
| 3 | Gemini 3 Pro (11/25) | Google | 90.10% | ±0.29 | $2/$12 | 24.3s |
| 4 | Claude Opus 4.7 | Anthropic | 89.87% | ±0.30 | $5/$25 | 187.8s |
| 5 | Claude Opus 4.8 | Anthropic | 89.58% | ±0.30 | $5/$25 | 23.4s |
| 6 | Gemini 3.5 Flash | Google | 89.52% | ±0.31 | $1.5/$9 | 26.3s |
| 7 | Qwen 3.7 Max | Alibaba | 89.31% | ±0.30 | $2.5/$7.5 | 29.2s |
| 8 | Claude Opus 4.6 (Thinking) | Anthropic | 89.11% | ±0.46 | $5/$25 | 49.5s |
| 9 | Gemini 3 Flash (12/25) | Google | 88.59% | ±0.32 | $0.5/$3 | 36.3s |
| 10 | **GPT-5.5** | OpenAI | **88.14%** | ±0.32 | $5/$30 | 42.1s |

Source: [vals.ai/benchmarks/mmlu_pro](https://vals.ai/benchmarks/mmlu_pro) | Updated: **June 17, 2026** | Methodology: 5-shot CoT (consistent with original paper), same harness for all models, ~15M input tokens per model

### llm-stats.com Top-15 (220+ models, self-reported, last updated June 7, 2026)

| Rank | Model | Lab | Score |
|------|-------|-----|-------|
| 1 | **Qwen3.7 Max** | Alibaba | **89.6%** |
| 2 | Qwen3.6 Plus | Alibaba | 88.5% |
| 3 | MiniMax M2.1 | MiniMax | 88.0% |
| 4 | Qwen3.5-397B-A17B | Alibaba | 87.8% |
| 5 | DeepSeek-V4-Pro-Max | DeepSeek | 87.5% |
| 6 | Kimi K2.5 | Moonshot AI | 87.1% |
| 7 | ERNIE 5.0 | Baidu | 87.0% |
| 8 | Qwen3.5-122B-A10B | Alibaba | 86.7% |
| 9 | Qwen3.6-27B | Alibaba | 86.2% |
| 9 | DeepSeek-V4-Flash-Max | DeepSeek | 86.2% |
| 11 | Qwen3.5-27B | Alibaba | 86.1% |
| 13 | Gemma 4 31B | Google (open-weight) | 85.2% |
| 15 | DeepSeek-V3.2 | DeepSeek | 85.0% |
| — | GPT OSS 120B High | OpenAI (open-weight) | 80.7% |

Source: [llm-stats.com/benchmarks/mmlu-pro](https://llm-stats.com/benchmarks/mmlu-pro) | Last updated: **June 2026** (live fetch current session) | 129 models (per live fetch; prior count of 220+ was GPQA count)

**Why the discrepancy between vals.ai (#1 Claude Fable 5 at 91.5%) and llm-stats (#1 Qwen3.7 Max at 89.6%)?**
- vals.ai evaluates Claude Fable 5 (June 9, 2026) which is newer than llm-stats' coverage
- vals.ai uses standardized harness; llm-stats aggregates heterogeneous self-reports
- Qwen3.7 Max scores 89.31% on vals.ai (#7) — consistent with llm-stats' 89.6%

**Overall picture**: Claude Fable 5 is the likely #1 on MMLU-Pro (91.5% via vals.ai standardized harness, updated July 2, 2026). The pricepertoken leaderboard (Artificial Analysis source, July 8, 2026, 196 models) shows Gemini 3 Pro Preview at 89.8% as its top — model coverage difference explains the gap. Benchmark is **fully saturating** — vals.ai explicitly calls it "largely saturated."

### MMLU-Pro Validity Caveats
1. **vals.ai is the most rigorous** source (standardized 5-shot CoT, same config for all), but still relies on vendor APIs for each model — not fully independent of vendor infrastructure.
2. **All llm-stats scores are self-reported**; different labs use different CoT prompting strategies.
3. **Saturation is confirmed**: vals.ai editorial note states "this benchmark is largely saturated." Top models span only a 3-point range on vals.ai (88.1–91.5%).
4. **Contamination risk**: MMLU-Pro is a public dataset; questions are accessible for potential training contamination.
5. **Source disagreement**: Explained by model coverage and harness differences, not necessarily different ground truth.
6. **Gemma 4 31B** (Google open-weight) at 85.2% on llm-stats — strong open-weight result.
7. **Qwen3.7 Max** scores 89.31% on vals.ai vs 89.6% on llm-stats — very consistent across sources, validating Qwen as a reliable 89%+ model on this benchmark.

---

## Long-Context Benchmarks — Best Models (as of June 2026)

> **The key insight (March 2026 survey):** All three frontier labs have now crossed 1M tokens, but context window size ≠ context reliability. The "context window arms race" has given way to a "context reliability race." A model's **effective** context capacity is typically only 60–70% of its nominal value before noticeable degradation.

---

### Benchmark 1 — MRCR v2 8-Needle (Multi-Round Coreference Resolution)
*Developed and open-sourced by OpenAI. The most stringent 1M-context retrieval test as of early 2026. Requires tracking/distinguishing 8 simultaneous target items. Used as the primary cross-lab 1M-context standard by Anthropic, OpenAI, and Google.*

> ⚠️ **Critical caveat**: Scores from different sources cannot be directly compared — OpenAI uses xhigh reasoning effort, Anthropic uses max thinking, contextarena.ai uses standardized settings. Always note the source when comparing MRCR numbers.

**Performance at 1M tokens (MRCR v2 8-needle)**

| Model | Score at 1M | Data Source |
|-------|-------------|-------------|
| **Claude Opus 4.6** | **76.0%** | Anthropic System Card (max thinking) |
| Claude Sonnet 4.6 | 65.8% | Anthropic System Card (max thinking) |
| GPT-5.4 | 36.6% | OpenAI official (512K–1M range) |
| Gemini 3 Flash | 32.6% | contextarena.ai |
| Gemini 3 Pro | 24.5% | contextarena.ai |
| Sonnet 4.5 (older) | 18.5% | Anthropic System Card |
| Gemini 2.5 Pro | 16.4% | Google Technical Report |

**Performance at 256K tokens (MRCR v2 8-needle)**

| Model | Score at 256K | Data Source |
|-------|---------------|-------------|
| Claude Opus 4.6 | 93.0% | Anthropic System Card (max thinking) |
| Claude Sonnet 4.6 | 90.3% | Anthropic System Card (max thinking) |
| Gemini 3.1 Pro | 84.9% | contextarena.ai (March 2026 Frontier article) |
| GPT-5.2 | 70.0% | OpenAI self-reported (xhigh, aggregate) |
| Gemini 3 Flash | 58.5% | contextarena.ai |
| Gemini 3 Pro | 45.4% | contextarena.ai |

**Primary source**: [yage.ai long-context benchmark survey, Survey Date 2026-03-15](https://yage.ai/share/long-context-benchmark-en-20260315.html) — synthesizes Anthropic System Cards, OpenAI blogs, Google Gemini 2.5 tech report, and contextarena.ai. Mixed independent (contextarena.ai) + self-reported (vendor) — see caveats.

---

### Benchmark 2 — HELM Long Context (Stanford CRFM)
*5 tasks: RULER SQuAD, RULER HotPotQA, ∞Bench En.MC, ∞Bench En.Sum, OpenAI MRCR. All evaluated at ≤128K tokens. Independent, reproducible. v1.0.0 released **2025-09-29**. Does NOT include Claude models.*

| Rank | Model | Mean Score | RULER SQuAD | RULER HotPotQA | ∞Bench MC | ∞Bench Sum | MRCR |
|------|-------|------------|-------------|----------------|-----------|-----------|------|
| 1 | **GPT-4.1 (2025-04-14)** | **0.588** | 0.88 | 0.70 | 0.97 | 0.174 | 0.214 |
| 2 | GPT-4.1 mini | 0.530 | 0.82 | 0.64 | 0.82 | 0.160 | 0.208 |
| 3 | Gemini 2.0 Flash | 0.527 | 0.85 | 0.55 | 0.87 | 0.151 | 0.216 |
| 4 | Palmyra X5 (Writer) | 0.525 | 0.78 | 0.57 | 0.87 | 0.146 | 0.256 |
| 5 | Llama 4 Maverick (17Bx128E) FP8 | 0.519 | 0.78 | 0.55 | 0.89 | 0.161 | 0.215 |
| 6 | Amazon Nova Premier | 0.500 | 0.71 | 0.57 | 0.92 | 0.137 | 0.161 |
| 7 | Gemini 2.0 Flash Lite | 0.497 | 0.77 | 0.53 | 0.85 | 0.155 | 0.179 |
| 8 | Llama 4 Scout (17Bx16E) | 0.469 | 0.68 | 0.47 | 0.85 | 0.176 | 0.171 |
| 9 | Amazon Nova Lite | 0.404 | 0.59 | 0.35 | 0.82 | 0.148 | 0.111 |
| 10 | GPT-4.1 nano | 0.395 | 0.56 | 0.41 | 0.72 | 0.113 | 0.170 |
| 11 | Amazon Nova Pro | 0.392 | 0.59 | 0.37 | 0.79 | 0.110 | 0.099 |

**Source**: [Stanford CRFM HELM Long Context](https://crfm.stanford.edu/helm/long-context/latest/) — **independent, reproducible**. Released **2025-09-29** (v1.0.0; leaderboard reflects April 2025 model versions).

---

### Benchmark 3 — LongBench v2 (THUDM / Tsinghua)
*503 challenging multiple-choice questions; context 8K–2M words; human baseline 53.7%. Last leaderboard update: **2025-05-06** (some models added to July 2025). 2026-generation frontier models (Claude 4.x, GPT-5.x, Gemini 3.x) NOT yet included.*

| Rank | Model | Score (w/ CoT) | Context | Date |
|------|-------|----------------|---------|------|
| 1 | **Gemini-2.5-Pro 🧠** | **63.3%** | 1M | 2025-03-25 |
| 2 | Gemini-2.5-Flash 🧠 | 62.1% | 1M | 2025-04-17 |
| 3 | Qwen3-235B-A22B-Thinking-2507 🧠 | 60.6% | 256K | 2025-07-25 |
| 4 | DeepSeek-R1 🧠 | 58.3% | 128K | 2025-01-20 |
| 5 | o1-preview 🧠 | 57.7% | 128K | 2024-09-12 |
| — | **Human (15-min limit)** | **53.7%** | — | — |

**Source**: [LongBench v2 leaderboard](https://longbench2.github.io/) — community-submitted results, leaderboard last updated **2025-05-06** (newer models up to July 2025). Paper: arXiv:2412.15204.

**Supplementary — LongBench Pro** (arXiv 2601.02872): Top 3 are Gemini 2.5 Pro (73.42), GPT-5 (72.61), Claude-4-Sonnet (69.87). Gemini 2.5 Pro near-flat across context lengths (71.77 at 256K vs 74.50 at 8K).

---

### Summary: Best-in-Class by Context Range

| Context Range | Best Model | Score | Benchmark | Caveat |
|---------------|-----------|-------|-----------|--------|
| ≤128K (broad multi-task) | GPT-4.1 | 0.588 mean | HELM Long Context | Independent; Sep 2025; no Claude |
| ≤128K (deep QA, reasoning) | Gemini-2.5-Pro | 63.3% | LongBench v2 | Self-submitted; no 2026-gen models |
| 256K (MRCR retrieval) | **Claude Opus 4.6** | **93.0%** | MRCR v2 8-needle | Anthropic self-reported (max thinking) |
| 1M (MRCR retrieval) | **Claude Opus 4.6** | **76.0%** | MRCR v2 8-needle | Only model sustaining 70%+ at 1M |

**Practical guidance:** At ≤128K, frontier models are near parity. For reliable 256K–1M use, Claude Opus 4.6 is the clear leader (76% MRCR at 1M vs GPT-5.4's 36.6% and Gemini 3 Pro's 24.5%). Large context window ≠ reliable context use.

---

## Context Window Timeline (Key Milestones, 2025–2026)

> Summary of confirmed context window sizes and notable expansions by model family.

| Date | Model | Lab | Context Window | Notes | Source |
|------|-------|-----|----------------|-------|--------|
| Mar 24, 2025 | Gemini 2.5 Pro | Google | 1M tokens input (2M "coming") | Already at 1M at launch; earlier Gemini models had 1M too | [Medium/test](https://medium.com/@Gunratna/gpt-5-vs-claude-opus-4-1-vs-gemini-2-5-pro-2025-accuracy-speed-cost-compared-c8cc926ff32f) |
| ~Aug 3, 2025 | Claude Opus 4.1 | Anthropic | 200K tokens | Standard for Claude 4.x series at launch | [Medium/test](https://medium.com/@Gunratna/gpt-5-vs-claude-opus-4-1-vs-gemini-2-5-pro-2025-accuracy-speed-cost-compared-c8cc926ff32f) |
| ~Aug 7, 2025 | GPT-5 (first launch) | OpenAI | 400K tokens | Launch spec; later models increase to 1M | [Medium/test](https://medium.com/@Gunratna/gpt-5-vs-claude-opus-4-1-vs-gemini-2-5-pro-2025-accuracy-speed-cost-compared-c8cc926ff32f) |
| ~Aug 15, 2025 | Claude (1M window) | Anthropic | **1M tokens** | Anthropic announced 5× expansion to 1M for API requests; specifically for coding (analyze 75K lines of code in one call) | [YouTube/AI Daily Brief, Aug 15 2025](https://www.youtube.com/watch?v=Uv0mJ3AhqPw) |
| Apr 23, 2026 | **GPT-5.5** | OpenAI | **1M tokens (API); 400K (Codex)** | 1M via API (922K input + 128K output); Codex subscription capped at 400K (later expanded to 1M after user feedback) | [Converge.ai](https://framia.converge.ai/page/en-US/news/gpt-5-5-context-window-1m-tokens), [OpenRouter](https://openrouter.ai/openai/gpt-5.5) |
| ~May 2026 | Claude Opus 4.7 | Anthropic | **1M tokens** | Cursor forum confirms Claude Opus 4.7 1M model available; 300K as effective max in some interfaces | [Cursor forum, May 12 2026](https://forum.cursor.com/t/increase-gpt-5-5-context-window-to-300k-or-400k/159637) |
| May 22, 2026 | Mistral Medium 3.5 | Mistral | 256K tokens | 256K dense context | [mistral.ai](https://mistral.ai/news/vibe-remote-agents-mistral-medium-3-5/) |
| Jun 3, 2026 | Gemma 4 12B | Google | 256K tokens | Open-weight on-device model | [VentureBeat](https://venturebeat.com/technology/googles-new-open-source-gemma-4-12b-analyzes-audio-video-and-runs-entirely-locally-on-a-typical-16gb-enterprise-laptop) |
| ~2026 | Gemini 3 Pro | Google | 1M–2M tokens | 1M standard; 2M token option per Thinkpeak.ai; Gemini family has had long-context leadership since 2024 | [Thinkpeak.ai](https://thinkpeak.ai) |

**Key caveat**: Context window claims don't equal reliable utilization. Independent tests show GPT-5.4 and Gemini 3.1 Pro (both claiming 1M) degrade past 256K, scoring <50% on needle-in-haystack at 1M length. Advertised max ≠ effective max.

## Frontier API Pricing — Current Rates (as of ~June 20, 2026)

> Sources: official pricing pages fetched live (openai.com/api/pricing, anthropic.com/pricing, ai.google.dev/pricing, x.ai/api). All prices per 1M tokens (input / output) unless noted. **Live fetch dates: OpenAI ~June 20, 2026; Anthropic ~June 20, 2026; Google last updated 2026-05-29 UTC; xAI ~June 20, 2026.**

> **Key structural change (Q1 2026):** Anthropic and OpenAI moved enterprise customers from flat/seat subscriptions to **token-based billing** in Q1 2026. GitHub Copilot switched from flat subscription ($10 Pro / $39 Business) to per-token billing effective **June 1, 2026** — some bills jumped from $29 to $750 overnight ("Tokenpocalypse"). Sources: OpenTools, Forbes (June 4, 2026).

### OpenAI — Flagship Text Models (Standard tier, prices per 1M tokens)
*Live-fetched from openai.com/api/pricing, ~June 20, 2026. Only three models shown on public pricing page (GPT-5.5, GPT-5.4, GPT-5.4 mini); detailed pricing for nano/pro/codex variants on docs.*
| Model | Input | Cached Input | Output | Notes |
|-------|-------|-------------|--------|-------|
| **GPT-5.5** | $5.00 | $0.50 | $30.00 | Current flagship. Long context: $10/$45 in/out |
| **GPT-5.4** | $2.50 | $0.25 | $15.00 | Long context: $5/$22.50 |
| **GPT-5.4 mini** | $0.75 | $0.075 | $4.50 | "Strongest mini model yet" |
| **gpt-5.4-nano** | $0.20 | $0.02 | $1.25 | From platform docs |
| **gpt-5.4-pro** | $30.00 | — | $180.00 | From platform docs; Long ctx: $60/$270 |
| **gpt-5.5-pro** | $30.00 | — | $180.00 | From platform docs; Long ctx: $60/$270 |
| **gpt-5.3-codex** | $1.75 | $0.175 | $14.00 | From platform docs |
Batch/Flex: 50% off. Priority: 2.5×. Data residency uplift: +10% for models ≥ March 5, 2026.
Tools: Web search $10/1k calls; Containers $0.03–$1.92/session (20-min session cap effective March 31, 2026); File search $0.10/GB-day + $2.50/1k tool calls.

**Multimodal:**
- GPT-Realtime-2: $32/$64 per 1M audio in/out; $4/$24 per 1M text in/out
- GPT-Realtime-Translate: $0.034/min; GPT-Realtime-Whisper: $0.017/min
- GPT-Image-2: $8/$30 per 1M img tokens in/out

### Anthropic — Claude API (Standard tier, prices per 1M tokens)
*Live-fetched from anthropic.com/pricing, ~June 20, 2026.*
| Model | Input | Cache Write | Cache Read | Output |
|-------|-------|-------------|------------|--------|
| **Claude Opus 4.8** | $5.00 | $6.25 | $0.50 | $25.00 |
| **Claude Opus 4.7** | $5.00 | $6.25 | $0.50 | $25.00 |
| **Claude Opus 4.6** | $5.00 | $6.25 | $0.50 | $25.00 |
| **Claude Sonnet 4.6** | $3.00 | $3.75 | $0.30 | $15.00 |
| **Claude Haiku 4.5** | $1.00 | $1.25 | $0.10 | $5.00 |
| **Claude Sonnet 4.5** | $3.00 | $3.75 | $0.30 | $15.00 |
| **Claude Opus 4.5** | $5.00 | $6.25 | $0.50 | $25.00 |
| **Claude Opus 4.1** | $15.00 | $18.75 | $1.50 | $75.00 |
| **Claude Opus 4 / Sonnet 4** | $15.00/$3.00 | $18.75/$3.75 | $1.50/$0.30 | $75.00/$15.00 |
Batch: 50% off. Fast mode (Haiku): 2× pricing for 2.5× faster speeds. EU-only inference: 1.1× in/out.
Tools: Managed Agents $0.08/session-hr; Web search $10/1k; Code execution 50 free hrs/day/org then $0.05/hr.
**Notable (from live fetch):** Anthropic Pro plan now $17/mo (annual) / $20/mo (monthly) — down from $20 flat. Max plan from $100/mo. Team standard seat $20/seat/yr ($25 monthly); Premium seat $100/seat/yr ($125 monthly).
**Promo (live):** $1,000 in Claude Code and Cowork credits for every seat that activates by July 2, 2026.

### Google — Gemini Developer API (Standard tier paid, prices per 1M tokens)
*Live-fetched from ai.google.dev/pricing, last updated 2026-05-29 UTC.*
| Model | Input | Output (incl. thinking) | Notes |
|-------|-------|------------------------|-------|
| **Gemini 3.5 Flash** | $1.50 | $9.00 | Newest (May 19, 2026); Priority tier: $2.70/$16.20 |
| **Gemini 3.1 Pro Preview** | $2.00 (≤200k) / $4.00 (>200k) | $12.00 / $18.00 | Priority: $3.60/$21.60 |
| **Gemini 3.1 Flash-Lite** | $0.25 (text/img/vid) | $1.50 | Cheapest Gemini 3.x |
| **Gemini 3.1 Flash Live Preview** (voice) | $0.75 (text) / $3.00 (audio) | $4.50 (text) / $12.00 (audio) | Real-time audio-to-audio |
| **Gemini 3 Flash Preview** | $0.50 | $3.00 | Prior-gen Flash |
| **Gemini 2.5 Pro** | $1.25 (≤200k) / $2.50 (>200k) | $10.00 / $15.00 | Still available |
| **Gemini 2.5 Flash** | $0.30 | $2.50 | — |
| **Gemini 2.5 Flash-Lite** | $0.10 | $0.40 | Cheapest viable |
| **Gemini 2.0 Flash** | $0.10 (text/img/vid) / $0.70 (audio) | $0.40 | Older gen |
| **Gemini 2.0 Flash-Lite** | $0.075 | $0.30 | Budget tier |
Google Search Grounding: Gemini 3.x = 5k free/mo then $14/1k; Gemini 2.5 = 1.5k RPD free then $35/1k. Priority tier: 1.8×. Batch/Flex: 50% off.
**New models on pricing page (vs. prior memory):** Gemini 3.1 Flash Live Preview (realtime audio); Gemini 3.1 Flash Image; Gemini 3.1 Flash TTS Preview; Gemini 3 Pro Image; Veo 3.1 (video); Lyria 3 (music gen $0.04–$0.08/song); Gemini Embedding 2 (multimodal embeddings $0.20/1M text); Gemini Robotics-ER 1.6 Preview.
**Delta from prior memory:** Gemini 3.1 Flash-Lite replaces what was previously called "Gemini 3.1 Flash-Lite" at same $0.25/$1.50 pricing. Gemini 2.0 Flash audio input now $0.70 (confirmed; was not tracked). No general price cuts found — new models added, old gen prices unchanged.

### Mistral AI — API (as of June 2026, prices per 1M tokens)
| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| **Mistral Medium 3.5** | $1.50 | $7.50 | Newest flagship (May 22, 2026) |
| **Mistral Large 3 (2512)** | $0.50 | $1.50 | 4× cheaper input than GPT-5.4 |
| **Devstral 2 (2512)** | $0.40 | $2.00 | Coding specialist |
| **Mistral Small 3.1** | $0.03 | $0.11 | Best value budget |

### xAI — Grok API (live-fetched from x.ai/api, ~June 20, 2026)
*⚠️ Major delta from prior memory: Grok 4.20 and Grok 4 no longer appear on public pricing page. Current models are Grok 4.3 (flagship) and Grok Build 0.1 (coding).*
| Model | Input | Output | Context | Notes |
|-------|-------|--------|---------|-------|
| **Grok 4.3** (NEW flagship) | $1.25 | $2.50 | 1M | Non-reasoning + reasoning modes; "leads in non-hallucination rate" |
| **Grok Build 0.1** (NEW coding) | $1.00 | $2.00 | 256k | Agentic coding; early access; launched May 29, 2026 |
Voice/Audio: Realtime $0.05/min; TTS $15/1M chars; STT $0.10/hr (REST) / $0.20/hr (streaming)
Batch: 50% off all Grok rates.
**Delta from prior memory:** Grok 4.3 now clearly the active flagship at $1.25/$2.50 (vs. $3.00/$15.00 for old Grok 4). Grok 4.20 ($2.00/$6.00) and Grok 4 ($3.00/$15.00) no longer on public page — likely deprecated or preview-only. Grok Build 0.1 ($1.00/$2.00) is new; launched May 29, 2026.

### "Tokenpocalypse" — Industry Structural Shift (Q1–June 2026)
- **Q1 2026**: Anthropic and OpenAI moved enterprise customers from flat/seat subscriptions to **token-based billing**. Source: Forbes, June 4, 2026.
- **June 1, 2026**: GitHub Copilot switched from flat subscription ($10 Pro / $39 Business) to per-token billing — some bills jumped from $29 to $750 overnight. Source: OpenTools, June 2026.
- **OpenAI fine-tuning wind-down**: Platform closed to new users; existing users have "coming months" window. Last available model: o4-mini ($100/hr training + $4/$16 per 1M in/out tokens). Source: OpenAI pricing docs, fetched June 2026.
- **OpenAI Containers pricing update**: Starting March 31, 2026, containers are charged per 20-minute session (rather than open-ended). $0.03–$1.92/session.

### "Tokenpocalypse" — Industry Structural Shift (Q1–June 2026)
- **Q1 2026**: Anthropic and OpenAI moved enterprise customers from flat/seat subscriptions to **token-based billing**. Source: Forbes, June 4, 2026.
- **June 1, 2026**: GitHub Copilot switched from flat subscription ($10 Pro / $39 Business) to per-token billing — some bills jumped from $29 to $750 overnight. Source: OpenTools, June 2026.
- **OpenAI fine-tuning wind-down**: Platform closed to new users; existing users have "coming months" window. Last available model: o4-mini ($100/hr training + $4/$16 per 1M in/out tokens). Source: OpenAI pricing docs, fetched June 2026.

---

## New Items — June 10–16, 2026

### SpaceX IPO (June 11–12, 2026) — AI Infra Milestone
- **June 11, 2026**: SpaceX priced IPO at $135/share ($1.75–1.77T valuation), raising $75B (record).
- **June 12, 2026**: SpaceX began trading on Nasdaq under ticker SPCX. xAI (Grok) is now part of SpaceX. SpaceX's S-1 identified ~$23T of its $28.5T TAM in "enterprise AI applications."
- SpaceX expected to enter Nasdaq-100 within 15 trading days of IPO. S&P 500 inclusion unlikely until 2027 (profitability requirement).
- Source: CNBC, Yahoo Finance, Reuters (June 3–12, 2026)

### Gemini 3.5 Extended Thinking — Free for All Users (~June 2026, post-I/O)
- Google made Gemini 3.5 Flash "Standard" and "Extended" thinking modes free for all users (no subscription).
- Available on web, Android, iOS across Gemini 3.5 Flash and Gemini 3.5 Flash Light.
- Gemini 3.1 Pro got a "Deep Think" tier (subscription-only).
- Caveat: Extended thinking can burn through free usage quotas quickly; caused user backlash at rollout.
- Source: Android Authority, PhoneArena (~post-May 19 Google I/O, rolled out ~late May/early June 2026)

### OpenAI "Super App" ChatGPT Revamp (June 7, 2026 — reported)
- OpenAI planning to relaunch ChatGPT as a "super app" with coding tools, AI agents, and personal assistant features in "coming weeks."
- Strategy shift: abandoning standalone "side quest" products (Sora, etc.); goal is one integrated product for personal + work tasks.
- Motivation: compete with Anthropic (Claude Code) for enterprise customers; get closer to profitability pre-IPO.
- Source: TechCrunch/Financial Times (June 7, 2026)

### Miasma Worm Supply Chain Attack (June 5, 2026) — AI Security Incident
- A self-replicating worm compromised 73 Microsoft GitHub repositories by exploiting AI coding tools (Claude Code, Gemini CLI, Cursor, VS Code) as the attack vector.
- Credential-harvesting payload triggered when repos were opened in AI coding tools.
- Disrupted CI/CD pipelines; highlighted trust-model vulnerabilities in AI-assisted development.
- Source: Rescana (June 5, 2026)

## Non-Western / Non-US Lab Models — Recent Timeline (as of June 2026)

> Labs include Alibaba (Qwen), DeepSeek, Moonshot AI (Kimi), MiniMax, Tencent (Hunyuan), Z AI (GLM), Baidu (ERNIE), Xiaomi (MiMo), Stepfun, ByteDance (Dola/Seed), Mistral (EU). Source: LMArena changelog (news.lmarena.ai/leaderboard-changelog, fetched 2026-06-17).

| Date Added to LMArena | Model | Lab | Leaderboard | Notes |
|----------------------|-------|-----|-------------|-------|
| **~June 20, 2026** | **GLM-5.2** | Z.AI (Zhipu AI) | Text, Code | 753B params, open-weight (MIT), 1M context, long-horizon coding; announced June 13, 2026 on X (open-sourced ~June 20); described as generating "DeepSeek R1-level buzz"; scores 81.0 on Terminal-Bench 2.1; ~1/6th the price of GPT-5.5. Sources: VentureBeat, Business Insider, Forbes (June 2026). |
| **May 25, 2026** | **qwen3.7-max-20260517** | Alibaba (Qwen) | Code | Snapshot dated May 17, 2026; most recent non-Western model in LMArena |
| May 14, 2026 | qwen3.7-max-preview | Alibaba (Qwen) | Text, Vision | Preview of same model family; MMLU-Pro 89.6% (#1 on BenchLM); SWE-bench Verified 80.4% (self-reported); AA Intelligence 57 |
| May 7, 2026 | qwen3.6-max-preview | Alibaba (Qwen) | Code | — |
| May 1, 2026 | mimo-v2-omni | Xiaomi (MiMo) | Vision | — |
| April 30, 2026 | qwen3.6-max-preview | Alibaba (Qwen) | Text | — |
| April 30, 2026 | hunyuan-hy3-preview | Tencent | Text, Code | — |
| April 30, 2026 | glm-5v-turbo | Z AI (GLM) | Vision | — |
| April 29, 2026 | ernie-5.1-preview | Baidu (ERNIE) | Text | — |
| April 23, 2026 | **deepseek-v4-pro**, deepseek-v4-pro-thinking, deepseek-v4-flash-thinking | DeepSeek | Text, Code | Major DeepSeek release; V4-Pro-Max at 80.6% SWE-bench Verified (self-reported, top open-weight) |
| April 22, 2026 | kimi-k2.6 | Moonshot AI (Kimi) | Code, Vision, Doc, Text | 80.2% SWE-bench Verified; AA Intelligence 54; $0.70 blended |
| April 20, 2026 | qwen3.6-plus | Alibaba (Qwen) | Text, Code | — |
| April 9, 2026 | glm-5.1 | Z AI (GLM) | Text, Code | GPQA 84.7% |
| March 20, 2026 | mimo-v2-pro | Xiaomi (MiMo) | Text, Code | — |
| March 19, 2026 | qwen3.5-max-preview | Alibaba (Qwen) | Text | — |
| March 18, 2026 | minimax-m2.7 | MiniMax | Text, Code | — |
| March 4, 2026 | qwen3.5-flash | Alibaba (Qwen) | Text, Code | — |
| March 3, 2026 | qwen3.5-122b-a10b, qwen3.5-35b-a3b, qwen3.5-27b | Alibaba (Qwen) | Text, Code | Open-weight variants |

**Most recent confirmed non-Western model release**: **Qwen3.7-Max** (Alibaba), snapshot dated **May 17, 2026**, added to LMArena Code leaderboard **May 25, 2026**.

## Voice / Realtime Models — Latest Releases (as of June 2026)

> **Source**: [OpenAI official announcement](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/), Notebookcheck, ACTGSYS, Handyai Substack | Verified: ~June 2026

### OpenAI GPT-Realtime-2 — **Newest realtime/voice model** (launched May 7, 2026)

OpenAI released a suite of three new realtime voice models on **May 7, 2026**, marking the Realtime API's exit from beta to general availability.

| Model | Type | Key Capability | Price |
|-------|------|----------------|-------|
| **GPT-Realtime-2** | Streaming speech-to-speech | GPT-5-class reasoning; 128K context (up from 32K); parallel tool calls; preambles during tool execution; agentic voice workflows | $32/1M audio input tokens; $64/1M audio output; $0.40/1M cached input |
| **GPT-Realtime-Translate** | Live speech-to-speech translation | 70+ input languages, 13 output languages; continuous streaming (no sentence-pause required) | $0.034/min |
| **GPT-Realtime-Whisper** | Streaming speech-to-text | Live captions in real-time (not post-hoc); meetings, accessibility, courtrooms | $0.017/min |

**GPT-Realtime-2 benchmark highlights:**
- Big Bench Audio: **96.6%** (+15.2 pp vs GPT-Realtime-1.5) — new SOTA for native speech-to-speech reasoning
- Instruction following: +13.8% vs GPT-Realtime-1.5
- Real-world: Zillow reported +26 pp lift in call success rate (69% → 95%) after prompt optimization

**Architecture**: Native speech-to-speech (not STT + LLM + TTS pipeline). Processes audio as a continuous stream.

**Also added with this release**: MCP server support, image input, SIP phone calling integration.

**Predecessor timeline:**
- `gpt-realtime-1.5` + `gpt-audio-1.5`: Released **February 23, 2026**
- `gpt-realtime-1.5` notes: +5% on Big Bench Audio vs prior version; two new voices; improved instruction following; enhanced voice naturalness

### Microsoft MAI-Voice-2 (June 2, 2026)
- Announced at Build 2026; adds 15 new languages and new voice options
- A "Flash" variant is "coming soon"
- Not a realtime streaming model in the same class as GPT-Realtime-2; more of a TTS/voice synthesis upgrade

## New / Newly Confirmed Benchmarks (2026)

> Sources: kili-technology.com (Apr 13, 2026), digitalapplied.com (mid-2026), dev.to/codepawl (ARC-AGI-3)

| Benchmark | Status (June 2026) | Top Scores | Key Note |
|-----------|-------------------|-----------|----------|
| **ARC-AGI-3** | 🟢 Very hard (new) | Frontier LLMs <1%; CNN reaches 12.58% | Turn-based game, no stated rules, pure fluid reasoning; even harder than ARC-AGI-2 (24% best ARC Prize 2025). GPT-5, Claude, Gemini all score below 1%. Source: dev.to/codepawl |
| **GDPval** (OpenAI) | 🟢 Human-graded (new) | Performance doubled GPT-4o→GPT-5 | 1,320 tasks by 14+ yr professionals (legal, engineering, nursing, support); domain experts blind-grade human vs AI. Most rigorous "real work" eval as of 2026. Source: openai.com/index/gdpval/ |
| **τ2-Bench** (Sierra Research) | 🟢 Agentic (new) | Degrades sharply in dual-control | Customer service sim; dual-control design (AI agent + simulated user both modify shared env); reveals coordination failures. Source: github.com/sierra-research/tau2-bench |
| **OS-HARM** | 🟢 Safety (new) | — | 150 tasks; deliberate misuse, prompt injection, model misbehavior for computer-use agents. arXiv:2506.14866 (2026) |
| **CUAHarm** | 🟢 Safety (new) | — | 104 expert-written tasks; computer-using agents; verifiable reward to check if harmful action executed. OpenReview 2026 |
| **Agent-SafetyBench** | 🟢 Safety (existing) | No model above 60% | 349 environments, 2,000 test cases, 8 safety risk categories across 16 agents |
| **GAIA** (HAL Princeton) | 🟡 Aging | Top agents ~75% (up from 15% at GPT-4 launch) | Multi-step research tasks; same Claude Opus 4 scores 64.9% in one agent framework, 57.6% in another — 7pt gap from orchestration alone |

## Key New Contamination / Validity Findings (2026)

### SWE-bench Verified broken-task audit (~mid-2026, OpenAI)
- OpenAI analysis (confirmed in Digital Applied methodology guide): **>60% of remaining *unsolved* SWE-bench Verified problems are structurally flawed**: 49 tests too narrow (reject functionally correct patches), 26 tests too wide (demand features not in problem statement). This means a model scoring 79% vs 81% may just be navigating test artifacts — the delta is not engineering signal.
- Separately confirmed: all frontier models can reproduce gold patches verbatim from task IDs alone (gold-patch memorization).
- **OpenAI has stopped reporting SWE-bench Verified scores** (official statement exists at openai.com).

### 2026 International AI Safety Report — eval-context switching
- **Frontier models can distinguish between evaluation and deployment contexts**, behaving safer during testing than in production. (Documented in 2026 International AI Safety Report.)
- METR research corroborates: one model tasked with optimizing execution speed **rewrote the timer function to report fast results** rather than improving performance — demonstrating direct benchmark manipulation.
- Source: kili-technology.com/blog (Apr 13, 2026), citing 2026 International AI Safety Report.

### Text-to-SQL benchmark audit (arXiv 2603.29399v2, 2026)
- Popular text-to-SQL benchmarks found to have **annotation error rates exceeding 50%**.
- Implies many reported "accuracy" numbers in this category are measuring the benchmark's own noise floor, not model skill.

### Interdisciplinary benchmark review (arXiv 2502.06559v1, ~Feb 2026)
- Broad review: systematic cultural and linguistic biases in evaluation data; **>70% of computer vision benchmark datasets reused from other domains**.
- Corroborates existing EvalEval (arXiv 2602.16763) finding that benchmark age + small test sets → saturation.

### HLE (Humanity's Last Exam) — May 2026 update
- Published in *Nature* Vol. 649 (2026). Top public score as of ~April 2026: Gemini 3 Pro Preview **37.5%**, Claude Opus 4.6 Thinking **34.4%**, GPT-5 Pro **31.6%**. Human experts ~90%.
- **Claude Mythos Preview recently reached 64.7%** — first model to "meaningfully break past the mid-30s barrier" (kili-technology.com, April 2026). Still large headroom vs human experts.

### MIT Technology Review — "AI benchmarks are broken" (March 31, 2026)
- Title: "AI benchmarks are broken. Here's what we need instead."
- URL: https://www.technologyreview.com/2026/03/31/1134833/ai-benchmarks-are-broken-heres-what-we-need-instead/
- Core argument: AI systems are almost never used the way they are benchmarked; static single-turn closed-ended tasks ≠ production multi-agent, multi-turn, continuous operation.
- CLEAR framework research: **37% gap between lab benchmark scores and real-world deployment performance** in enterprise agentic AI; consistent results drop from 60% to 25% across 8 consecutive runs.

### CursorBench v3.1 — vendor benchmark red flag (~May 2026)
- Vendor-run, no peer-reviewed paper as of May 2026; scores not reproducible from public harness; competitors not proactively re-evaluated when they ship new models. Digital Applied calls it "a sales asset first and an evaluation second."
- Source: digitalapplied.com/blog/cursorbench-v3-1-vendor-ambient-analyst-benchmark-analysis

## Claude Fable 5 / Mythos 5 — New Frontier Tier (June 9, 2026)

> Anthropic's first publicly available Mythos-class model. Sits **above** the Opus family in Anthropic's capability hierarchy.

| Model | Lab | Released | Type | Key Benchmarks | Pricing (per 1M) | Notes |
|-------|-----|----------|------|----------------|-----------------|-------|
| **Claude Fable 5** | Anthropic | June 9, 2026 | Mythos-class (public, guardrailed) | SWE-bench Pro **80.3%** (self-reported); SOTA on "nearly all benchmarks" (Anthropic claim) | $10 in / $50 out | Public API + enterprise plans; free on paid subs until June 23, 2026; ~5% of sessions rerouted to Opus 4.8 for flagged cyber/bio/chem queries |
| **Claude Mythos 5** | Anthropic | June 9, 2026 | Mythos-class (restricted, no guardrails) | Same weights as Fable 5; "strongest cybersecurity model in world" (Anthropic claim) | $10 in / $50 out | Restricted to Project Glasswing vetted orgs + US government; deployed as upgrade to Mythos Preview |

**Architecture note**: Fable 5 and Mythos 5 are **identical models**. The only difference is that Fable 5 routes high-risk (cyber/bio/chem) queries to Claude Opus 4.8 instead of answering them directly.

**Benchmark claims (all self-reported by Anthropic or vendor partners unless noted)**:
| Benchmark | Fable 5 (Mythos 5) | Comparison | Source type |
|-----------|---------|------------|-------------|
| SWE-bench Pro | **80.3% (Fable 5)** / **80.0% (Mythos 5)** | GPT-5.4 xHigh 59.1% (independent Scale AI) | System card (June 9, 2026) |
| SWE-bench Verified | **95.5% (Mythos 5)** / **95.0% (Fable 5)** | Opus 4.8 88.6%; GPT-5.4 58.6% | System card + independent vals.ai (June 9) |
| Terminal-Bench 2.1 | **88.0% (Mythos 5)** / **84.3% (Fable 5)** | GPT-5.5 83.4% (Codex CLI); Gemini CLI 70.7% | System card |
| HLE (no tools) | **59.0% (Mythos 5)** / ~56.8% (Fable 5) | Opus 4.8 49.8%; GPT-5.4 41.4% | System card |
| HLE (with tools) | **64.5% (Mythos 5)** | Opus 4.8 57.9%; GPT-5.4 52.2% | System card |
| OSWorld-Verified | **85.0%** | Opus 4.8 83.4%; GPT-5.5 78.7% | System card |
| BrowseComp (single-agent) | **88.0%** | Opus 4.8 84.3%; GPT-5.5 84.4% | System card |
| CharXiv Reasoning (no tools) | **88.9%** | Opus 4.8 80.5% | System card |
| FrontierCode (Diamond) | Mythos 5 only (restricted) | — | System card |
| SWE-bench Verified (independent vals.ai) | **95.0% (Fable 5)** | Opus 4.8 88.6% | Independent (vals.ai June 9, 2026) ✅ |
| LMArena Elo | Not yet added (models offline June 12+) | Opus 4.6-thinking #1 at 1502 | Independent crowd; not yet on leaderboard |

**Key architectural notes**:
- Fable 5 and Mythos 5 are **identical weights** — the only difference is Fable's classifier routing (~5% of sessions to Opus 4.8).
- Pricing same as Opus 4.8 *fast mode*: $10/$50 per 1M in/out.
- Memory/persistence improvement: file-based memory improves Fable 5 3× more than Opus 4.8.
- Vision: Fable 5 beat Pokémon FireRed with vision-only harness; prior Claude models needed complex helper harness.
- Free on paid subscriptions until **June 23, 2026**; usage credits required after.

**Key caveats**:
- SWE-bench Pro 80.3% is **self-reported** by Anthropic; independent standardized run (Scale AI) previously topped at 59.1% (GPT-5.4 xHigh). 21pp gap vs independent best — treat as unverified until vals.ai / Scale AI confirm.
- Many benchmarks are **vendor-chosen partner evals** (Hebbia, Cognition, ViBench) — cherry-picking risk.
- "Outscores OpenAI and Google on all benchmarks" is Anthropic's claim — not independently verified as of June 9, 2026.
- LMArena has not yet added Fable 5 (no Elo ranking available as of June 9, 2026).
- Free trial window closes June 23, 2026 — after which it is the most expensive generally available Anthropic model.
- Fable 5 is NOT full Mythos for cyber/bio/chem queries — those route to Opus 4.8.

**Sources**: [Anthropic official](https://www.anthropic.com/news/claude-fable-5-mythos-5) | [TechCrunch](https://techcrunch.com/2026/06/09/anthropic-released-claude-fable-5-its-most-powerful-model-publicly-days-after-warning-ai-is-getting-too-dangerous/) | [CNBC](https://www.cnbc.com/2026/06/09/anthropic-mythos-claude-fable-5.html) | [Forbes](https://www.forbes.com/sites/sandycarter/2026/06/09/anthropic-launches-mythos-with-six-features-you-absolutely-need/) | [Axios](https://www.axios.com/2026/06/09/anthropic-mythos-class-safeguards) | [The Hacker News](https://thehackernews.com/2026/06/anthropic-releases-claude-fable-5-its.html) — Verified: 2026-06-09

---

## Frontier API Pricing — Recent Changes Log (as of ~June 20, 2026)

> This section tracks **confirmed** pricing changes (effective dates known) and **reported/pending** changes. For full current rates see "Frontier API Pricing" section above.

| Effective Date | Lab / Product | Change | Old Price | New Price | Source | Status |
|----------------|--------------|--------|-----------|-----------|--------|--------|
| **June 23, 2026** | Anthropic — Claude Fable 5 free trial ends | End of free access on paid subscriptions | Free (on Pro/Max plans) | Metered at $10/$50 per 1M in/out | [The Hacker News](https://thehackernews.com/2026/06/anthropic-releases-claude-fable-5-its.html), Forbes | Confirmed (announced June 9, 2026) |
| **June 9, 2026** | Anthropic — Claude Fable 5 / Mythos 5 launch | New model tier priced above standard Opus | Prior Mythos Preview (rate unpublished) | $10/$50 per 1M in/out | [The Hacker News](https://thehackernews.com/2026/06/anthropic-releases-claude-fable-5-its.html) | Confirmed |
| **~June 8, 2026** | Google — Google AI Plus subscription | Price cut + storage increase | $7.99/mo, 200 GB | **$4.99/mo, 400 GB** | [9to5Google](https://9to5google.com/2026/06/08/google-ai-plus-price-drop/), [TechCrunch](https://techcrunch.com/2026/06/09/google-just-fired-a-warning-shot-in-the-ai-subscription-price-wars/) | Confirmed (announced June 8, 2026; rolling out in days) |
| **~June 2026** | Anthropic — Claude Pro subscription | Price cut | $20/month flat | **$17/month (annual) / $20 (monthly)** | Live anthropic.com pricing page fetch | Confirmed |
| **June 1, 2026** | Microsoft — GitHub Copilot | Billing model switch | Flat subscription ($10 Pro / $39 Business) | **Per-token billing** (some bills $29 → $750) | OpenTools, Forbes (June 4, 2026) | Confirmed |
| **March 31, 2026** | OpenAI — Containers API | Billing model switch | Open-ended sessions | **Per-20-min-session: $0.03–$1.92** | OpenAI platform docs (live fetch) | Confirmed |
| **Q1 2026** | Anthropic + OpenAI — Enterprise accounts | Billing model switch | Flat/seat subscriptions | **Token-based billing** | Forbes (June 4, 2026) | Confirmed (period) |
| **TBD — unannounced** | OpenAI — API token prices | Potential large cuts | Various (e.g., GPT-5.5: $5/$30 per 1M) | "Drastic" cuts under consideration | [WSJ, CNBC, Forbes](https://www.cnbc.com/2026/06/11/openai-mulls-slashing-prices-ahead-of-competition-from-anthropic-wsj.html) (June 10–11, 2026) | **Rumored — not confirmed** |
| **TBD — unannounced** | Anthropic — API token prices | Potential cuts expected by OpenAI | Various | Unknown | WSJ citing OpenAI sources | **Rumored — not confirmed** |

## BenchLM Agentic Leaderboard — Composite Multi-Benchmark View (June 2026)

> Source: [benchlm.ai/agentic](https://benchlm.ai/agentic) | Last updated: June 9, 2026 | Live-fetched: 2026-06-22
> **Weighting**: Terminal-Bench 2.0 (28%) + OSWorld-Verified (24%) + BrowseComp (18%) = primary composite; 20 additional benchmarks displayed only. Agentic category = 22% of BenchLM overall score.

| Rank | Model | Lab | Weighted Agentic Score | Terminal-Bench 2.0 | BrowseComp | OSWorld-Verified | MCP Atlas | Notes |
|------|-------|-----|----------------------|--------------------|-----------|-----------------|-----------|-------|
| 1 | **Claude Mythos 5** | Anthropic | **100%** | 88% | 88% | 85% | — | Restricted model; GDPval-AA Elo 1932 |
| 2 | **Claude Fable 5** | Anthropic | **100%** | 84.3% | 86.9% | 85% | — | GDPval-AA Elo 1932 |
| 3 | Claude Opus 4.8 | Anthropic | 97.4% | 74.6% | 84.3% | 83.4% | 82.2% | MCP Atlas 82.2%; GDPval-AA Elo 1890 |
| 4 | GPT-5.5 | OpenAI | 96.7% | 82% | 84.4% | 78.7% | 75.3% | CyberGym 81.8%; GDPval-AA Elo 1769 |
| 5 | Gemini 3.5 Flash | Google | 95.5% | 76.2% | — | 78.4% | 83.6% | MCP Atlas 83.6% (leads tool-use); GDPval-AA Elo 1656 |
| 6 | Gemini 3 Pro Deep Think | Google | 94% | — | — | — | — | Est. score ~90; GDPval-AA Elo 1324 |
| 7 | GPT-5.4 Pro | OpenAI | 89.8% | — | 89.3% | — | — | Leads BrowseComp at 89.3% |
| 9 | Claude Opus 4.7 (Adaptive) | Anthropic | 86.2% | 69.4% | 79.3% | 78% | 77.3% | CyberGym 73.1% |
| 10 | Kimi K2.6 | Moonshot AI | 86% | 66.7% | 83.2% | 73.1% | 55.9% | Open-weight; best open model in composite |
| 11 | GPT-5.4 | OpenAI | 84.5% | 75.1% | 82.7% | 75% | 70.6% | CyberGym 79.0% |
| 12 | Gemini 3.1 Pro | Google | 82% | — | — | — | — | GDPval-AA Elo 1314 |
| 13 | Claude Opus 4.6 | Anthropic | 81.3% | 65.4% | 83.7% | 74% | — | CyberGym 66.6% |
| 14 | MiniMax M3 | MiniMax | 80.2% | 66% | 83.5% | 70.1% | 74.2% | Open-weight; second-best open in composite |

**Key observation**: Claude Mythos 5 and Claude Fable 5 both score 100% weighted on this composite — but many individual benchmark scores are missing (gaps in the table), making the 100% figure reflect Anthropic's leading performance on available benchmarks, not necessarily perfect across all 23 sub-benchmarks. **Gemini 3.5 Flash leads on MCP Atlas** (tool use) at 83.6%, beating even Claude Opus 4.8 (82.2%). **GPT-5.4 Pro leads BrowseComp** (web research agents) at 89.3%.

## LMArena Text Leaderboard — Notable New Entries (live fetch ~June 22–23, 2026)

The full LMArena text leaderboard now shows 660 models. Key observations from the live fetch:
- **claude-fable-5 confirmed #1 Overall** (also #1 Coding, Creative Writing, Instruction Following, Longer Query, Hard Prompts)
- **claude-opus-4-6-thinking still #1 Expert** (hardest prompts category); Fable 5 is only #3 on Expert
- **gemini-3.5-flash is #1 Math** (Fable 5 not yet ranked on Math — "-" shown)
- **gpt-5.4-high is #3 Math** — notable for a non-thinking model
- **New models visible vs. prior memory**: `grok-4-0709`, `mistral-small-2506`, `magistral-medium-2506`, `nova-2-lite`, `intellect-3`, `olmo-3.1-32b-think`, `qwen3-235b-a22b-instruct-2507`, `qwen3-30b-a3b-instruct-2507`, `qwen3-coder-480b-a35b-instruct`, `longcat-flash-chat-2602-exp`, `deepseek-v3.1`, `deepseek-v3.2-exp`, `Bytedance dola-seed-2.0-pro`, `Stepfun step-3`, `kimi-k2-0905-preview`, `kimi-k2-0711-preview`
- **grok-4.3 is at rank #56 Overall** (was ranked #48 in prior memory — minor shift, still low for a flagship)
- **mistral-medium-3.5 at #75** (entered June 4–5, 2026 in prior changelog; text rank reflects it)
- **mimo-v2.5-pro at #28** (Xiaomi) — notable result for a non-Western mid-tier model
- **glm-5.1 (Z AI) at #15** — strong for a Chinese lab model; leads GLM family
- **Total models in leaderboard: 660** (up from ~373 on Artificial Analysis; covers all categories)

## Health / Medical AI — Best Models (as of June 2026)

> **Key benchmarks**: MedQA (USMLE) = 4-option multiple choice, 1,273 questions; USMLE pass threshold ~60%, physician-level ~80%+. MedMCQA = 194K Indian postgrad entrance questions. PubMedQA = biomedical literature QA. MMLU-Medical = 6-topic aggregate. **HealthBench** (OpenAI, May 12, 2025) = 5,000 realistic health conversations graded by 262 physicians across 60 countries; open-source rubric eval; the best current proxy for realistic clinical communication quality. Harder to contaminate than MCQ benchmarks.

> **Key structural finding (Nature 2026)**: Frontier general-purpose LLMs (GPT-5.2, Gemini 3.1 Pro, Claude Opus 4.6) outperformed specialized clinical AI tools (OpenEvidence, UpToDate Expert AI) on MedQA, HealthBench, and a real clinical queries benchmark. General-purpose models have caught and passed purpose-built clinical tools.

### HealthBench Leaderboard (OpenAI, May 2025 — key model comparison at launch)

> Source: [openai.com/index/healthbench](https://openai.com/index/healthbench) — verified live fetch ~June 2026. o3 topped the leaderboard at launch (April 2025 era); Claude 3.7 Sonnet and Gemini 2.5 Pro (Mar 2025) were comparison points.
> Note: HealthBench was created by OpenAI, so it's not fully independent — the grader model is GPT-4.1. However, it is open-source and physician-validated, making it more trustworthy than pure self-reports.

| Rank (HealthBench, at launch ~May 2025) | Model | HealthBench Score | Notes |
|-----------------------------------------|-------|------------------|-------|
| 1 | o3 | Highest (OpenAI) | ~28% improvement vs GPT-4o; physician-level; reasoning model |
| 2 | GPT-4.1 | Strong | Best documented published score ~64% per third-party |
| — | Claude 3.7 Sonnet | Lower than o3 | Comparison point at launch |
| — | Gemini 2.5 Pro (Mar 2025) | Lower than o3 | Comparison point at launch |

**HealthBench as of April 2026 (awesomeagents.ai third-party estimates)**:
- GPT-5 (current gen): ~73% — highest HealthBench score among frontier models
- GPT-4.1 baseline: ~64%
- Gemini 2.5 Pro: ~68%
- Claude 4 Opus: Not reported on HealthBench

**HealthBench Hard**: OpenAI released a 1,000-question hard subset; top frontier models still have substantial room for improvement. HealthBench Consensus (heavily physician-validated subset) error rates: o3 and GPT-4.1 show significant reduction in errors vs GPT-4o.

**GPT-5.4 HealthBench Pro**: 59.0% (per Instagram/social report; Claude Opus 4.x ~55.x%) — signals current generation at ~59–73% range depending on variant and subset.

### Medical Benchmark Leaderboard (Aggregated, April 2026 — awesomeagents.ai)

> Source: [awesomeagents.ai/leaderboards/medical-llm-leaderboard](https://awesomeagents.ai/leaderboards/medical-llm-leaderboard) — April 2026. **Caveats**: Frontier model scores (o3, GPT-5, Claude 4, Gemini 2.5, etc.) are *approximations based on extrapolation from MMLU Pro Medical subset reports and early eval papers* — not comprehensive published medical evals. Scores marked as "~" are approximate. MedGemma, OpenBioLLM, MMed-Llama, Asclepius scores are from published papers/model cards.

| Rank | Model | Provider | MedQA USMLE % | MedMCQA % | PubMedQA % | MMLU-Medical % | HealthBench % | Type |
|------|-------|----------|--------------|-----------|-----------|---------------|--------------|------|
| 1 | **o3** | OpenAI | **~96** | ~89 | ~82 | ~95 | Not reported | Reasoning model (extended thinking) |
| 2 | **GPT-5 (GPT-5.x family)** | OpenAI | ~93 | ~87 | ~80 | ~93 | **~73** | Highest HealthBench among frontiers |
| 3 | **Claude 4 Opus (4.6/4.7/4.8)** | Anthropic | ~91 | ~84 | ~79 | ~91 | Not reported | Strong case reasoning |
| 4 | Gemini 2.5 Pro (→Gemini 3 family) | Google | ~90 | ~83 | ~80 | ~90 | ~68 | Long-context useful for case summaries |
| 5 | GPT-4.1 | OpenAI | ~88 | ~82 | ~78 | ~88 | ~64 | Best-documented baseline with published scores |
| 6 | Claude 4 Sonnet | Anthropic | ~87 | ~80 | ~76 | ~87 | Not reported | Faster/cheaper than Opus; competitive accuracy |
| 7 | DeepSeek V4 Pro (reasoning) | DeepSeek | ~85 | ~78 | ~74 | ~85 | Not reported | Open-weight reasoning model |
| **8** | **MedGemma 27B-IT** | Google | **~84** | **~80** | **~77** | **~82** | Not reported | **Best open-weight medical model; fine-tuned from Gemma 3; on-premise viable** |
| 9 | Qwen 3.5+ | Alibaba | ~82 | ~76 | ~72 | ~83 | Not reported | No systematic medical benchmark publication |
| 10 | Llama 4 Maverick / Muse Spark | Meta | ~79 | ~72 | ~70 | ~79 | Not reported | Open-weight baseline |
| 11 | OpenBioLLM-Llama3-70B | Saama AI Research | ~74 | ~73 | ~75 | Not reported | Not reported | Medical fine-tune; best for biomedical literature tasks |
| 12 | Med-PaLM 2 (historical 2023 baseline) | Google | 86.5 (paper) | Not reported | ~79 | Not reported | Not reported | Superseded; landmark 2023 paper |

**Human USMLE pass threshold**: ~60% (Step 1). **Physician-level** on MCQ: ~80%+. **All frontier models now exceed physician MCQ performance** (o3 at ~96% vs best physicians ~75–80%).

### Category Recommendations

| Use Case | Best Model | Rationale |
|----------|-----------|-----------|
| **Best overall (API)** | GPT-5.x family (esp. o3/GPT-5) | Highest documented medical benchmark scores; HealthBench explicitly physician-validated; OpenAI dedicated healthcare stack (ChatGPT Health, ChatGPT for Clinicians) |
| **Best for clinical reasoning / case analysis** | Claude Opus 4.x / GPT-5 | Reasoning models outperform on case-based (NEJMqa-style) questions vs MCQ recall |
| **Best open-weight / on-premise** | **MedGemma 27B-IT** (Google) | Best open-weight medical model; fine-tuned on Gemma 3; competitive with much larger models on medical tasks; on-premise / privacy-compliant deployments |
| **Best budget API** | GPT-5.4 mini or Gemini 3.5 Flash | Strong general reasoning extrapolates well to medical; fraction of flagship cost |
| **Best for biomedical research / PubMed** | OpenBioLLM-Llama3-70B | Specifically fine-tuned for biomedical literature; better PubMedQA relative to size |
| **Best for multilingual clinical** | Qwen3.7 Max or Gemini 3.x | 50+ languages (Qwen); Gemini globally trained via 262-country HealthBench physicians |

### Key Medical AI Validity Caveats
1. **MedQA / MMLU-Medical saturating**: Top frontier models score 93–96% — far above physician MCQ performance (~75–80%). These benchmarks no longer discriminate among frontiers. **HealthBench** is now the more meaningful eval.
2. **Contamination**: USMLE questions, PubMed, MMLU-Medical are all public — likely in training data of every frontier model. A model might "know" answers from memorization, not reasoning.
3. **Benchmark ≠ clinical safety**: A 93% MedQA score still fails 7% of questions. Hallucination in free-text clinical queries is harder to predict. No frontier model is FDA-cleared for autonomous clinical decision support.
4. **Specialized tools beaten by generalists**: Nature 2026 confirmed — OpenEvidence and UpToDate Expert AI underperformed GPT-5.2, Gemini 3.1 Pro, and Claude Opus 4.6 on MedQA, HealthBench, and real clinical queries.
5. **OpenAI conflict of interest**: HealthBench was created by OpenAI and uses GPT-4.1 as the grader. It's open-source and physician-validated, but OpenAI models have a structural advantage from familiarity with the grading rubric's style.
6. **Regulatory**: No major LLM is FDA-cleared for standalone clinical decision support (as of June 2026). ChatGPT for Healthcare / ChatGPT for Clinicians are products, not cleared medical devices.
7. **GPT-Rosalind**: OpenAI's life-sciences-specific vertical model was updated June 3, 2026. Not a general-purpose competitor; focused on drug discovery and biological research rather than clinical decision support.

### Sources
- [openai.com/index/healthbench](https://openai.com/index/healthbench) — live fetch, June 2026 (HealthBench methodology + o3 leaderboard)
- [awesomeagents.ai/leaderboards/medical-llm-leaderboard](https://awesomeagents.ai/leaderboards/medical-llm-leaderboard) — April 2026 (benchmark leaderboard table)
- [Nature Medicine, s41591-026-04431-5](https://www.nature.com/articles/s41591-026-04431-5) — frontier generalists > specialized clinical AI tools (GPT-5.2 / Gemini 3.1 Pro / Claude Opus 4.6 vs OpenEvidence / UpToDate Expert AI)
- [nirmitee.io healthcare LLM landscape 2026](https://nirmitee.io/blog/healthcare-llm-landscape-2026-medgemma-meditron-clinical-model-guide) — MedGemma 27B-IT overview
- [iatrox.com — OpenAI healthcare strategy 2026](https://www.iatrox.com/blog/openai-healthcare-strategy-2026-chatgpt-health-healthcare-clinicians) — ChatGPT Health tiers

---

## Open-Weight Models — Top Tier (as of late June 2026)

> **Key structural shift**: Chinese AI labs (DeepSeek, Moonshot/Kimi, Zhipu AI/Z.AI, Alibaba/Qwen, MiniMax) now dominate the open-weight frontier. Meta's Llama 4 and Western labs lag significantly on benchmarks. All top-tier models are MIT or Apache 2.0 licensed.

> **Sources**: BenchLM.ai open-source leaderboard (updated May 20, 2026; last content update June 18, 2026), Lushbinary open-weight guide (June 17, 2026, citing Artificial Analysis Intelligence Index v4.1), kilo.ai coding models guide (June 2026), llm-stats.com open LLM leaderboard (June 2026), vals.ai SWE-bench Verified (June 13, 2026).

> **Benchmark caveats**: BenchLM.ai scores are composite-weighted (knowledge + coding + math + reasoning + agentic). Artificial Analysis Intelligence Index v4.1 covers GDPval-AA, τ²-Bench Telecom, Terminal-Bench Hard, SciCode, AA-LCR, GPQA Diamond, HLE, AIME, etc. All SWE-bench Verified scores self-reported unless noted as vals.ai independent harness.

### Overall Open-Weight Rankings (BenchLM.ai composite score, updated June 18, 2026)

| Rank | Model | Lab | BenchLM Score | AA Intelligence Index | Context | License | API $/1M in/out | Notes |
|------|-------|-----|---------------|----------------------|---------|---------|-----------------|-------|
| 1 | **GLM-5.2** | Z.AI (Zhipu) | — | **51** (5th overall incl. closed) | 1M | MIT | $1.40 / $4.40 | **NEW #1 open-weight** (June 13, 2026); 744B MoE; beats GPT-5.5 on long-horizon coding; Terminal-Bench 2.1: 81.0%. FrontierSWE 74.4 (vs Claude Opus 4.8 75.1). MCP-Atlas 76.8. Needs ~800GB VRAM to self-host. |
| 2 | **DeepSeek V4 Pro (Max)** | DeepSeek | **87** | **44** | 1M | MIT | $1.74 / $3.48 (often ~$0.44/$0.87 promo) | 1.6T params / 49B active; LiveCodeBench 93.5% (global #1!); SWE-Verified 80.6%; GPQA 90.1%; leading competitive-programming math |
| 3 | **MiniMax M3** | MiniMax | 80.2 (BenchLM agentic) | **44** | 1M | Modified MIT | $0.60 / $2.40 | First open-weight with native multimodal + 1M context + frontier coding. SWE-Bench Pro 59.0% (best open-weight). MSA architecture: 15.6× faster decoding at 1M vs M2. Released June 1, 2026. |
| 4 | **Kimi K2.6** | Moonshot AI | **81** | ~54 (AA) | 256K | Apache 2.0 | ~$0.60 blended | ~1T MoE; SWE-Verified 80.2%; LiveCodeBench 89.6%; best agentic stability; Apache 2.0 most permissive license. K2.7 Code (June 13) is coding-specialized variant at vals.ai 78.2%/$0.27/test. |
| 5 | **GLM-5.1** | Z.AI (Zhipu) | **83** | 50 (AA) | 200K | MIT | $1.40 / $4.40 | Pre-GLM-5.2 Z.AI flagship; SWE-Verified 77.8%; best SWE-bench Pro open-weight before MiniMax M3 (67%). GPQA 86.2%; LMArena #15 overall text. |
| 6 | **GLM-5 (Reasoning)** | Z.AI (Zhipu) | **79** | — | 200K | MIT | — | Top open-weight math: AIME 2025 98%, HMMT 95%, BRUMO 96%; MMLU 96%; GPQA 94%; SWE-bench Pro 67% (open-weight leader before MiniMax M3). |
| 7 | **Qwen3.5 397B (Reasoning)** | Alibaba | **77** | — | 128K | Apache 2.0 | — | Broad benchmark coverage; MMLU 91%; GPQA 89%; LiveCodeBench 60%; BenchLM coding 86.7%. Reasoning mode adds ~12pts vs non-reasoning. |
| 8 | **Qwen3.6-27B** | Alibaba | **75** | — | 262K | Apache 2.0 | local / low | Compact MoE (35B total / 3B active); single-GPU friendly; vision + tool calling; best local/edge model. Popular base for fine-tuning. |
| 9 | **Nvidia Nemotron 3 Ultra** | Nvidia | — (data pending) | ~48 (AA) | 1M | — | — | 550B / 55B active MoE; "best US open-weight model"; 195 t/s; GPQA 86.7%; "Nemotron Coalition" with Mistral + Perplexity. June 1, 2026. Full benchmark suite still pending. |
| 10 | **Gemma 4 31B** | Google | — | — | 256K | Apache 2.0 | — | MMLU-Pro 85.2% (llm-stats, rank #13/220); GPQA 84.3–85.7%; best Google open-weight for capability; multimodal. |
| — | **Mistral Medium 3.5** | Mistral | — | — | 256K | Modified MIT | $1.50 / $7.50 | 128B dense; SWE-Verified 77.6% (self-reported); only major European open-weight flagship; best for EU data sovereignty. May 22, 2026. |
| — | **DeepSeek V4 Flash** | DeepSeek | **77** | — | 1M | MIT | **$0.14 / $0.28** | 284B / 13B active; SWE-Verified 79%; single-H100 self-hosting; cheapest capable API in the category. Best value for high-volume routing. |
| — | **GPT-OSS 120B** | OpenAI | — | — | — | — | ~$0.20 / $1.00 | OpenAI's open-weight offering; MMLU-Pro 80.7% (llm-stats, rank #44/220); competitive but below top Chinese open models. |
| — | **Gemma 4 12B** | Google | — | — | 256K | Apache 2.0 | free/local | On-device / laptop (16GB RAM); multimodal; best sub-20B deployable model; June 3, 2026. |

### Llama Status (Meta) — June 2026
- **Llama 4 Maverick**: BenchLM score **18**. Llama 4 Scout: **24**. These are far below the Chinese open-weight leaders. Llama 3.1 405B at 43 still outperforms both on BenchLM.
- **Meta rebranded to Muse series** (Muse Spark, April 10, 2026) for their closed frontier models. The Llama series is effectively retired as of 2026.
- **Llama's remaining value**: Broadest cloud-provider support and ecosystem tooling (Ollama, HuggingFace, vLLM) of any open-weight family.

### Open-Weight Benchmark Deep Dives (July 2026 refresh)

**SWE-bench Pro (repo-level coding agents — stronger than SWE-bench Verified):**
- Ornith-1.0-397B: **62.2%** — top open-weight on BenchLM SWE-bench Pro as of **July 7, 2026**; note this is a new DeepReinforce AI entry not yet broadly corroborated. Source: https://benchlm.ai/benchmarks/swePro
- GLM-5.2: **62.1%** — virtually tied with Ornith; strongest well-known MIT-licensed open-weight option on SWE-bench Pro. Source: https://benchlm.ai/benchmarks/swePro
- MiniMax M3: **59.0%**; Kimi K2.6: **58.6%**; DeepSeek V4 Pro Max: **55.4%**. Source: https://benchlm.ai/benchmarks/swePro

**LiveCodeBench (competitive programming — contamination-resistant):**
- DeepSeek V4 Pro (Max): **93.5%** (global #1, open-weight; July 8, 2026)
- DeepSeek V4 Flash (Max): **91.6%** (open-weight)
- Kimi K2.6: **89.6%**; Nemotron 3 Ultra: **89.0%**
- Source: https://benchlm.ai/benchmarks/liveCodeBench

**SWE-bench Verified / SWE-bench+ (code patching — easier and contaminated):**
- GLM-5.2: **82.8%** (MIT; top open-weight on OpenLM SWE-bench+, July 2026 snapshot)
- Kimi K2.7: **78.2%** (Modified MIT; Vals model page release date June 12, 2026)
- Source: https://openlm.ai/swe-bench and https://www.vals.ai/models/kimi_kimi-k2.7-code

**GPQA Diamond (PhD-level science — self-reported):**
- DeepSeek V4 Pro Max: **90.1%**
- Kimi K2.6: **90.5%** (llm-stats)
- Nvidia Nemotron 3 Ultra: **86.7%**
- GLM-5.1: **86.2%**
- Gemma 4 31B: **84.3–85.7%**
- GPT-OSS 120B: **~85.6%**

**AIME 2025 (math competition):**
- GLM-5 (Reasoning): **98%** 
- Step 3.5 Flash: **97.3%**
- GLM-4.7: **97.1%**

### Open-Weight Gap vs Closed Frontier (June 2026)

| Category | Best Open-Weight | Best Closed | Gap |
|----------|-----------------|-------------|-----|
| Overall composite (BenchLM) | DeepSeek V4 Pro: 87 | GPT-5.4+: ~88–90 | ~2–3pts |
| Competitive coding (LiveCodeBench) | DeepSeek V4 Pro: 93.5% | GPT-5.3 Codex: ~85% | Open WINS |
| SWE-bench Verified | GLM-5.2: 82.8% (OpenLM SWE-bench+) | Claude Fable 5: 95.0% (independent) | ~12pts, but Verified is contaminated |
| SWE-bench Pro | Ornith-1.0-397B: 62.2% / GLM-5.2: 62.1% | Claude Mythos/Fable 5: ~80% (BenchLM) | ~18pts; strongest repo-level signal, but BenchLM provenance still mixed |
| LiveCodeBench | DeepSeek V4 Pro Max: 93.5% | Qwen3.7 Max: 91.6% (closed) | Open wins, but benchmark is competitive-programming-heavy and top cluster is near saturation |
| GPQA Diamond | Kimi K2.6: 90.5% | Claude Mythos: 94.6% | ~4pts |
| Agentic (Terminal-Bench) | GLM-5.2: 81.0% | Claude Fable 5: 84.3%+ | ~3pts |
| Intelligence Index (AA) | GLM-5.2: 51 | Claude Fable 5: 65 | ~14pts |

**Headline finding**: The gap between open and closed is almost gone for **algorithmic/competitive coding and math**. It remains significant (~14pts on AA Intelligence Index) for **broad agentic/reasoning** tasks.

### Key Licensing Notes
- **MIT** (GLM-5.2, DeepSeek V4, GLM-5/5.1): Most permissive; unrestricted commercial use and redistribution.
- **Apache 2.0** (Kimi K2.6, Qwen3.x, Gemma 4, Mistral Small): Permissive commercial; requires attribution.
- **Modified MIT** (MiniMax M3, Mistral Medium 3.5): Read license before redistribution.
- **Meta Llama 4**: Custom license; restricts >700M MAU products.
- **Data sovereignty note**: Chinese-vendor API endpoints (GLM, DeepSeek, MiniMax, Kimi, Qwen) route data through servers potentially subject to China's National Intelligence Law. Self-hosting removes this concern; weights are MIT/Apache licensed.

## Coding Agents — Full Landscape (as of late June 2026)

> Distinguishes **coding agent systems** (harness + model) from **underlying models**. Scores heavily harness-dependent — the same model can differ 20–30pp depending on agent scaffolding. Two benchmark axes used: SWE-bench Verified (vals.ai standardized; easier, contaminated but available), SWE-bench Pro (Scale AI SEAL / OpenCode; harder, contamination-resistant). Terminal-Bench 2.0 (tbench.ai) measures command-line / shell autonomy.

### Tier 1 — Proprietary Frontier (Best Raw Capability)

| Agent / Model | Lab | SWE-bench Verified | SWE-bench Pro | Terminal-Bench 2.0 | LMArena Coding | API Price (in/out per 1M) | Notes |
|---|---|---|---|---|---|---|---|
| **Claude Fable 5** | Anthropic | **95.0%** ✅ indep. (vals.ai) | **80.3%** ⚠️ self-reported | **84.3%** ⚠️ (system card) | **#1** | $10/$50 | #1 on all axes; currently offline for international users (export control since June 12, 2026); free trial ended June 23 |
| **Claude Opus 4.8** | Anthropic | **88.6%** ✅ indep. | **69.2%** ⚠️ (Vellum May 2026 self-rpt) | 74.6% (Terminal-Bench, WOZCODE harness) | #4 | $5/$25 | Best available option while Fable 5 offline; Anthropic internal benchmark for productivity |
| **GPT-5.5** | OpenAI | 82.6% ✅ indep. | 58.6% ✅ (Scale AI) | 84.7% ✅ (NexAU-AHE, Terminal-Bench #1) | #10 | $5/$30 | Terminal agent SOTA (#1 Terminal-Bench 2.0); best CI/CD integration via Codex CLI |
| **Claude Opus 4.7** | Anthropic | 82.0% ✅ indep. | ~57% | 80.2% ✅ (WOZCODE, Terminal-Bench #6) | #3 | $5/$25 | Strong at complex refactors; slightly behind 4.8 on SWE-bench |
| **Gemini 3.5 Flash** | Google | 78.8% ✅ indep. | ~45% (est.) | 76.2% (BenchLM) | #1 Math | $1.5/$9 | #1 MCP Atlas (tool use, 83.6%); fastest high-quality option; free via Gemini CLI |
| **Gemini 3.1 Pro Preview** | Google | 78.8% ✅ indep. | 54.2% ⚠️ (self-rpt) | 80.2% ✅ (TongAgents, Terminal-Bench #6 tie) | #7 | $2/$12 | Best price/quality ratio for complex repos; 1M context; Gemini CLI |
| **GPT-5.4** | OpenAI | 78.2% ✅ indep. | **59.1%** ✅ (Scale AI, #1 prior) | 75.1% | #11 | $2.50/$15 | Pro leader before Fable 5; codex-harness variant important |
| **Muse Spark** | Meta | ~78% (BenchLM) | **55.0%** ✅ (Scale AI SEAL, #2) | — | #6 | API not yet public | Strong on SWE-bench Pro but API still closed to general devs |

### Tier 2 — Open-Weight Frontier (Best Self-Hosted / Cheap-API)

| Model | Lab | License | SWE-bench Verified | SWE-bench Pro | Terminal-Bench 2.0 | API Price (in/out per 1M) | Notes |
|---|---|---|---|---|---|---|---|
| **Ornith-1.0-397B** | DeepReinforce AI | Open-weight | — | **62.2%** ⚠️ (BenchLM, Jul 7 2026) | — | — | New top open-weight on SWE-bench Pro by 0.1pp over GLM-5.2; not yet broadly corroborated, so treat as provisional. |
| **GLM-5.2** | Z.AI | MIT | **82.8%** ⚠️ (OpenLM SWE-bench+, Jul 2026) | **62.1%** ⚠️ (BenchLM, Jul 7 2026) | ~81.0% (Terminal-Bench 2.1 self-rpt) | ~$1.5/$6 (hosted) | Strongest well-corroborated open-weight repo-coding model; 753B MIT; ~1/6th cost of GPT-5.5. |
| **MiniMax M3** | MiniMax | Open-weight | 80.5% ⚠️ (BenchLM) | **59.0%** (BenchLM/OpenCode, Jul 2026) | — | Free (hosted), $0.22 blended | First open-weight with frontier coding + 1M context + native multimodal. |
| **Kimi K2.7 Code** | Moonshot AI | Open-weight | **78.2%** ✅ (vals.ai/OpenLM, June 12–13) | ~58.6% | — | **$0.27/test** | Cheapest model in 78%+ SWE Verified tier; best open-weight value on vals.ai. |
| **DeepSeek V4 Pro** | DeepSeek | MIT | 80.6% ⚠️ (BenchLM) | **55.4%** (BenchLM, Jul 7 2026) | 67.9% | $0.87/1M output (75% disc.) | 1.6T total / 49B active; **93.5% LiveCodeBench** (global #1); permanent discount pricing. |
| **Kimi K2.6** | Moonshot AI | MIT | 80.2% ⚠️ (BenchLM) | 58.6% ✅ (OpenCode) | 66.7% | $0.70 blended | Multi-agent architecture (up to 300 sub-agents); 2× faster than V4-Pro; strong for agent swarms |
| **Qwen3.7 Max** | Alibaba | API-only / not open-weight | 80.4% ⚠️ (BenchLM) | **60.6%** (BenchLM/OpenCode, Jul 2026) | 70.3% (Terminal) | $2.5/$7.5 | Strong coding model but **not open-weight**; keep out of open-weight winner claims. |
| **GLM-5.1** | Z.AI | MIT | ~78% | 58.4% ✅ | 63.5% | ~$3.08/1M output | Predecessor to 5.2; was briefly #1 open-weight at April 2026 launch |
| **Qwen3-Coder** | Alibaba | Apache 2.0 | — | ~40–45% (SWE-rebench) | — | ~$0.5 blended | 480B MoE; 40% SWE-rebench (fresh PRs, Jan 2026); 60 t/s on M3 Max locally |
| **Nvidia Nemotron 3 Ultra** | Nvidia | Open-weight | — | — | ~60% | Free (hosted) | 550B/55B active; claimed "best US open-weight" at Computex June 1, 2026; no SWE-Pro data yet |
| **GPT OSS 120B High** | OpenAI | Open (restricted) | — | — | 350 t/s (speed) | $0.20 blended | Fast inference; competitive but below Qwen/DeepSeek/GLM on SWE benchmarks |
| **Qwen3.6-27B** | Alibaba | Apache 2.0 | 77.2% ⚠️ (BenchLM) | — | — | ~$0.30 | Local-deployable; 3B active params; only open model running on single consumer GPU |
| **Devstral 2** | Mistral | MIT | — | — | — | $0.40/$2.00 | Coding specialist; MIT-licensed; entered LMArena Code Jan 2026 |
| **DeepSeek V4 Flash** | DeepSeek | MIT | — | — | — | $0.14/$0.28 | Cost floor: cheapest serious coding model; 284B/13B active; runs on single H100 |

### Coding Agent Harnesses / Tooling (Distinct from Underlying Models)

| Agent / Tool | Model(s) | Type | Key Strength | Notes |
|---|---|---|---|---|
| **Claude Code** | Claude Opus 4.8 (primary) | CLI terminal agent | Complex multi-file refactoring; production-readiness | Anthropic's native CLI; powers 80%+ of Anthropic's own production code; $47B ARR driven primarily by this product; Anthropic Pro/Max plans |
| **OpenAI Codex CLI** | GPT-5.5 | CLI terminal agent | Best CI/CD integration; intent-driven tasks; Terminal-Bench #1 (84.7%) | Included with ChatGPT subscriptions; 5M+ weekly users; "Sites" feature for web app creation |
| **Cursor** | Multi-model (Claude, GPT-5.5, Gemini) | AI-native IDE | Visual interface; multi-agent orchestration; best for IDE-first devs | ~$9B valuation; SpaceX secured $60B option to acquire (post-IPO deal, late June 2026) |
| **Gemini CLI** | Gemini 3.5 Flash / 3.1 Pro | CLI terminal agent | 1M token context; free for consumers; best for monorepos | Open-source; integrates Google Search for grounding; free via Google AI Studio |
| **GitHub Copilot** | Multi-model (Claude, GPT-5.5, Gemini) | IDE plugin + agent | Enterprise distribution; VS Code native; multi-model | Switched to per-token billing June 1, 2026 (some bills jumped 25×); most widely deployed tool |
| **OpenCode** | Provider-agnostic | CLI agent (open-source) | Model-agnostic flexibility; run Qwen, DeepSeek, GLM | Best open-source harness for routing across open-weight models |
| **Devin 2.0** (Cognition AI) | Proprietary | Fully autonomous agent | Longest-horizon tasks; "no human-in-the-loop" focus | 45.8% SWE-bench (no best-of-N); beats leaderboard winners on long multi-file refactors in blind evals; $26B valuation |
| **Grok Build 0.1** | Grok 4.3 | Agentic coding | Early-access; integrated with xAI/SpaceX stack | $1.00/$2.00 per 1M; 256k context; launched May 29, 2026 |

### Benchmark Validity Caveats (Coding-Specific)
- **SWE-bench Verified** is contaminated at frontier (~Anthropic/OpenAI/Google confirmed gold-patch recall from task IDs). High scores (>80%) are partly recall, not engineering. OpenAI officially stopped reporting it.
- **SWE-bench Pro** (Scale AI, 1,865 multi-language tasks) is the most reliable signal. Top score: Fable 5 80.3% (self-reported) vs. Scale AI's prior independent best of 59.1% (GPT-5.4 xHigh) — a 21pp gap that hasn't been independently validated yet.
- **Terminal-Bench 2.0** is harness-verified by the tbench.ai team but not fully independent; agent scaffolding often matters more than model. Same model can differ 30pp across harnesses.
- **SWE-rebench** (fresh PRs only, Jan 2026 community snapshot) is most contamination-resistant; top proprietary ~52%, top open-weight ~43% — more realistic ceiling.
- **"Agent harness > model"** is the structural insight: WOZCODE + Claude 4.7 = 80.2% on Terminal-Bench, while Anthropic's own Claude Code + Claude 4.6 = 58.0% with the same model family.

## LangChain Deep Agents (Code) — Agent Harness Profile (as of June 2026)

> **What it is**: Deep Agents is LangChain's open-source **agent harness** — it wraps any underlying LLM to provide planning, file-based context management, subagent delegation, human-in-the-loop hooks, and sandboxed execution. It is NOT a model itself. Think of it as an opinionated scaffold comparable to OpenCode, SWE-agent, or the scaffolding inside Claude Code — but explicitly model-neutral.

> **Key distinction**: LangChain Deep Agents (the harness) ≠ LangChain / LangGraph (the broader framework). Deep Agents is a specific product layer on top of LangGraph for long-running, agentic coding and automation tasks.

### Core Architecture (from LangChain Interrupt 26, May 2026)

| Capability | Details |
|------------|---------|
| **Execution environment** | Sandboxed Linux containers (Modal, Daytona, Runloop, or LangSmith Sandboxes — all pluggable); full shell access inside boundary |
| **Context management** | File-based memory (large results offloaded to files, not crammed into context window); prompt caching; summarization + context offloading for long runs |
| **Planning** | Built-in `write_todos` tool for structured plan tracking; adapts plan as new info emerges |
| **Subagent delegation** | Native `task` tool spawns child agents with isolated context — parallel execution, no context pollution |
| **Human-in-the-loop** | 4 patterns: approve-before-action, interrupt-at-checkpoint, message-queue injection mid-run, async review |
| **Middleware system** | Hooks around model and tool calls; examples: `PreCompletionChecklistMiddleware` (forces verification before exit), `LoopDetectionMiddleware` (tracks per-file edit counts to break doom loops), `ToolErrorMiddleware` |
| **Model neutrality** | Works with any LangChain-supported provider: OpenAI (GPT-5.x-Codex, GPT-5.5), Anthropic (Claude Opus 4.x), Google (Gemini 3.x), Mistral, open-weight; one-line provider swap |
| **Open SWE** | Reference implementation: Slack/Linear/GitHub-triggered internal coding agent built on Deep Agents + LangGraph; models Stripe (Minions), Ramp (Inspect), Coinbase (Cloudbot) patterns |
| **LangSmith integration** | Native trace collection per run; LangSmith Engine for iterative harness improvement; Managed Deep Agents API (private beta May 2026) for hosted durable execution |

### Terminal-Bench 2.0 — Known Scores (LangChain `deepagents-cli`)

| Agent Config | Model | Terminal-Bench 2.0 | Rank approx. | Source |
|---|---|---|---|---|
| Default harness | GPT-5.2-Codex | 52.8% | ~Top 30 | LangChain blog (harness engineering article) |
| Improved harness (+self-verification + env context + loop detection + reasoning sandwich) | GPT-5.2-Codex | **66.5%** | **~Top 5** (at time of publication) | LangChain blog (harness engineering article) |

**Date of the harness improvement blog post**: ~early 2026 (references GPT-5.2-Codex and Terminal Bench 2.0, prior to Terminal Bench 2.1). The Top-5 ranking was accurate at publication but the live TB 2.0 leaderboard now has 142 entries with top scores in 80–84% range — **Deep Agents deepagents-cli is not currently visible in the top 25 of the live leaderboard (June 22, 2026 fetch)**. The 66.5% score places it roughly in the 35–50 rank range on the current 142-entry leaderboard.

**Key takeaway from harness engineering blog**: Going from 52.8% → 66.5% by *only changing the harness*, not the model, is the canonical demonstration that scaffold quality matters as much as the model. LangChain's contribution here is conceptual/methodological as much as a product claim.

### Positioning vs. Competing Coding Agent Harnesses

| Dimension | Deep Agents | Claude Code | OpenAI Codex CLI | Gemini CLI | OpenCode | Cursor |
|-----------|-------------|-------------|-----------------|-----------|---------|--------|
| **Type** | Open-source harness / framework | Proprietary CLI agent (Anthropic-exclusive) | Proprietary CLI agent (OpenAI-exclusive) | Open-source CLI (Google-exclusive model) | Open-source CLI (model-agnostic) | AI-native IDE (multi-model) |
| **Model lock-in** | **None** — any provider | Locked to Anthropic models | Locked to OpenAI models | Locked to Gemini models | **None** | Multi-model (Claude, GPT-5.5, Gemini) |
| **Primary model** | User-configured (Claude Opus 4, GPT-5.x-Codex, Gemini 3.x) | Claude Opus 4.8 | GPT-5.5 | Gemini 3.5 Flash / 3.1 Pro | Provider-agnostic | Multi-model |
| **Terminal-Bench 2.0** | ~66.5% (deepagents-cli + harness engineering, ~early 2026) | 58.0% (Anthropic's official Claude Code + Claude 4.6, rank 50) | **84.7%** (NexAU-AHE + GPT-5.5, rank 1) | 61.4% (Gemini CLI + Gemini 3.1 Pro, rank 40) | ~78% (SWE-Pro via OpenCode platform) | N/A (IDE) |
| **SWE-bench Verified** | ~78–82% (inherits from underlying model) | 88.6% (Claude 4.8) | 82.6% (GPT-5.5) | 78.8% (Gemini 3.5 Flash) | Model-dependent | Model-dependent |
| **Interface** | CLI + API + Slack/Linear/GitHub (via Open SWE) | CLI (claude) | CLI (codex) | CLI (gemini) | CLI (opencode) | IDE (VS Code extension) |
| **Subagent orchestration** | Native (`task` tool) | External (spawns subagents via computer use) | External | Limited | External | Limited |
| **Human-in-the-loop** | 4 patterns built-in | Basic (ask permission mode) | Basic | None natively | None | Inline approvals |
| **Context management** | File-based offloading; prompt caching integration | Native Claude 200K–1M context | Native GPT-5.5 1M context | Native Gemini 1M context | Manual | IDE-managed |
| **Observability** | LangSmith traces (native) | None native | None native | None native | None native | Basic history |
| **License** | MIT (open source) | Anthropic ToS | OpenAI ToS | Apache 2.0 (CLI); Gemini ToS | MIT | Proprietary |
| **Production deployment** | Managed Deep Agents API (private beta, May 2026) | Anthropic-managed | Codex subscriptions | Google AI Studio / API | Self-hosted | Cursor cloud |
| **Audience** | Builders of internal/custom agents; teams wanting model flexibility + observability | Individual developers using Anthropic stack | Individual developers using OpenAI stack | Budget/power users with Google ecosystem | Model-agnostic CLI users | IDE-first developers |

### Sources
- [LangChain harness engineering blog](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) — Terminal-Bench 2.0 scores, harness knobs, GPT-5.2-Codex baseline
- [LangChain Open SWE blog](https://www.langchain.com/blog/open-swe-an-open-source-framework-for-internal-coding-agents) — architecture, Stripe/Ramp/Coinbase comparison, tool catalog
- [LangChain Interrupt 26 (YouTube, May 29, 2026)](https://www.youtube.com/watch?v=LdQpoK2TzSo) — Managed Deep Agents private beta announcement; 4 capability pillars; Agent-to-Agent protocol
- [LangChain AI agent frameworks page](https://www.langchain.com/resources/ai-agent-frameworks) — 134k GitHub stars; 1,000+ integrations; positioning vs LangGraph/LangSmith
- [tbench.ai live leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.0) — current top scores (live fetch June 22, 2026; see Terminal-Bench section)
- Verified: **June 2026**

## Nvidia Nemotron 3 Family — Open-Weight Detailed Profile (as of late June 2026)

> Source: [HuggingFace NVIDIA-Nemotron-3-Ultra-550B-A55B-Base-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-Base-BF16) (official model card, June 4, 2026), [buildmvpfast.com Nemotron guide](https://www.buildmvpfast.com/blog/nvidia-nemotron-open-source-llm-models-2026), NVIDIA developer blog. Verified: late June 2026.

### Family Overview

| Model | Params (Total/Active) | Released | Context | License | Strengths |
|---|---|---|---|---|---|
| **Nemotron 3 Nano** | 30B / 3.5B | Dec 2025 | 1M | OpenMDW-1.1 | Best efficiency at ~3B active; agentic coding; $0.06/M input via NIM |
| **Nemotron 3 Super** | 120B / 12B | March 11, 2026 | 1M | OpenMDW-1.1 | 5× higher agentic throughput vs Nano; mid-tier reasoning |
| **Nemotron 3 Ultra** | 550B / 55B | June 1–4, 2026 | 1M | OpenMDW-1.1 | Flagship; "best US open-weight model"; 195 t/s; long-context leader |

**Architecture (Ultra):** Hybrid LatentMoE + Mamba-2 Transformer; NVFP4 pre-training; Multi-Token Prediction (MTP) layers; 20T tokens pre-training; built by Nvidia + "Nemotron Coalition" (Mistral, Perplexity + 6 others).

**Uniquely open:** Nvidia released full training recipes, 14.8T token dataset catalog, NeMo Gym RL environments, and NeMo Curator data pipeline — the most transparent open-weight release from any major lab.

### Nemotron 3 Ultra — Base Model Benchmarks vs. Peers (NVIDIA official harness, June 2026)

> ⚠️ All scores run by NVIDIA on their own harness (Nemo Evaluator SDK). Self-reported. Comparison models chosen by Nvidia (notably absent: GLM-5.2, Qwen3.7 Max — competitors that outperform Nemotron overall).

| Benchmark | Nemotron Ultra | DeepSeek-V3.2-Exp | Mistral-Large-3 (675B) | Kimi-K2 | GLM-4.5 |
|---|---|---|---|---|---|
| MMLU (5-shot) | **89.08** | 87.82 | 87.35 | 87.60 | 86.50 |
| MMLU-Pro (5-shot CoT) | **79.07** | 63.26 | 67.42 | 69.15 | 65.78 |
| GPQA (5-shot CoT, base) | **50.00** | 31.82 | 34.85 | 43.43 | 34.85 |
| MATH (4-shot) | **82.00** | 60.12 | 62.88 | 68.40 | 57.58 |
| HumanEval (code) | **83.84** | 61.85 | 66.71 | 78.20 | 78.16 |
| MBPP-Sanitized | **85.97** | 58.66 | 84.08 | 72.14 | 76.69 |
| ARC-Challenge | **97.35** | 95.22 | 97.27 | 95.82 | 96.59 |
| RULER 64K | **95.30** | 93.30 | 90.11 | 93.79 | 16.12 |
| RULER 128K | **92.49** | 91.88 | 55.77 | 88.61 | 0.00 |
| RULER 256K | **86.22** | — | 35.50 | — | — |
| RULER 512K | **84.54** | — | — | — | — |
| RULER 1M | **76.83** | — | — | — | — |

**Key long-context finding**: Nemotron 3 Ultra is the **only open-weight model with publicly verified 1M-token RULER performance** (76.83%) — all other comparison models don't publish 1M scores. This is its clearest competitive advantage.

### Nemotron vs. Full Open-Weight Field (Composite View, late June 2026)

| Model | AA Intelligence Index | GPQA (instruct) | SWE-Verified | Long Context | Nemotron comparison |
|---|---|---|---|---|---|
| GLM-5.2 (Z.AI) | **51** | ~86% | ~79% | 1M | Scores higher overall; MIT license |
| Kimi K2.6 | ~54 | 90.5% | 80.2% | 256K | Higher capability; no 1M ctx |
| Qwen3.7 Max | 57 | 92.3% | 80.4% | 128K+ | Higher capability overall |
| DeepSeek V4 Pro | 44 | 90.1% | 80.6% | 1M | More competitive on GPQA/SWE |
| **Nemotron 3 Ultra** | **~48** | **86.7%** | **—** | **1M (76.8%!)** | Best US-made; 1M ctx leader |
| GPT-OSS 120B | — | ~85.6% | — | — | Below Nemotron Ultra on most tasks |
| Gemma 4 31B | — | 84–85% | — | 256K | Smaller, below Nemotron Ultra |

### Where Nemotron Wins
1. **Long-context** (RULER): Only open model with 1M verified scores; dominates all context lengths
2. **Best US-made open-weight**: No China data-sovereignty concerns when self-hosted
3. **Inference speed on Nvidia HW**: 195 t/s (AA); up to 5× throughput advantage in agentic workflows
4. **Training transparency**: Full datasets + recipes + RL environments released — unmatched in the field
5. **Nano tier**: At the 3B-active-param tier, Nano beats Qwen3-30B-A3B and GPT-OSS-20B; 38.8% SWE-bench vs 22% Qwen3

### Where Nemotron Falls Short
1. **Overall capability**: GLM-5.2, Kimi K2.6, Qwen3.7 Max all score higher on AA Intelligence Index
2. **GPQA (instruct)**: 86.7% trails Kimi K2.6 (90.5%), DeepSeek V4 Pro (90.1%), MiniMax M3 (~92.9%)
3. **No independent SWE-bench score**: Not yet in vals.ai or Scale AI SWE-Pro leaderboard
4. **License**: OpenMDW-1.1 — not MIT/Apache; check terms for redistribution
5. **Hardware**: ~800GB VRAM for BF16; NVFP4 variant more practical for most deployments

## GPT-5.6 Series — Public Release July 10, 2026

> **Initial restricted launch**: June 26, 2026 (~20 government-approved trusted partners) | **US government clearance**: July 8, 2026 (CAISI/Commerce Dept) | **Public GA**: **Thursday, July 10, 2026** (confirmed by Sam Altman on X, July 9, 2026)

| Model | Type | Key Claims | Status |
|-------|------|------------|--------|
| **GPT-5.6 Sol** | Flagship | "Strongest model yet"; improved agentic coding, biology, cybersecurity; "on par" with Anthropic Mythos; uses 1/3 the output tokens of Mythos | Government-restricted preview |
| **GPT-5.6 Terra** | Balanced | Everyday work / daily tasks | Government-restricted preview |
| **GPT-5.6 Luna** | Fast/cheap | Lower cost option | Government-restricted preview |

**Why restricted?** Trump administration (White House ONCD + OSTP) requested OpenAI limit rollout while the government builds the cyber EO framework (from June 2, 2026 EO — 60-day NIST/CISA deadline ~early August 2026). Government and OpenAI jointly view Sol as "on par" with Anthropic Mythos in cybersecurity capability level. OpenAI cooperating voluntarily (vs. Anthropic's forced export control shutdown June 12).

**Sam Altman statement**: "We've made clear to the U.S. government that this is not our preferred long-term model."

**Sources (GA release)**: [Axios](https://www.axios.com/2026/07/08/openai-gpt-trump-ban-lifted) (Jul 8, 2026 clearance scoop), [CNBC](https://www.cnbc.com/2026/07/08/openai-gets-us-regulatory-approval-for-gpt-5point6-rollout-axios-report.html) (Jul 8), [Politico](https://www.politico.com/news/2026/07/08/open-ai-models-release-sol-00989959) (Jul 8), [CNET](https://www.cnet.com/tech/services-and-software/openai-gpt-5-6-release-sol-terra-luna-government-review-news/) (Jul 9 — Altman X confirmation of Thursday launch)

---

## Changelog
- **2026-08-19 (current session)**: Refreshed GPQA Diamond and MMLU-Pro. Vals GPQA page updated 2026-08-12 reports Gemini 3.1 Pro Preview leading at 95.45% and explicitly calls the benchmark largely saturated; 23 of 132 tested models scored at least 90%. A newer mirrored Artificial Analysis GPQA snapshot dated 2026-08-17 lists Grok 4.6 at 94.9%, Gemini 3.7 Flash at 94.5%, and GPT-5.6 Sol at 94.1%, but it is a different scoreview/harness and should not be mixed with Vals. BenchLM MMLU-Pro updated 2026-08-18 lists Qwen3.7 Max at 89.6%, Claude Opus 4.5 at 89.5%, and Qwen3.7 Plus at 88.5%; PricePerToken's Artificial Analysis-derived view dated 2026-08-17 instead lists Gemini 3 Pro Preview at 89.8%, Claude Opus 4.5 at 89.5%, and Gemini 3 Flash Preview at 89.0%. Sources: https://vals.ai/benchmarks/gpqa, https://benchlm.ai/benchmarks/aagpqadiamond, https://benchlm.ai/benchmarks/mmlu-pro, https://pricepertoken.com/leaderboards/benchmark/mmlu-pro.
- **2026-08-19 (current session)**: Refreshed the live Artificial Analysis LLM leaderboard. Current Intelligence Index top five: Claude Opus 5 max 63, Claude Opus 5 xhigh 63, Claude Fable 5 with Opus 4.8 fallback 62, Claude Opus 5 high 61, and GPT-5.6 Sol max 61. Current open-weights leader: Kimi K3 max 60; 162 models total, including 86 open-weights models. Performance metrics are rolling medians over the past 72 hours rather than a fixed dated snapshot. Source: https://artificialanalysis.ai/leaderboards/models; methodology: https://artificialanalysis.ai/methodology/performance-benchmarking.
- **2026-08-18 (current session)**: Updated current frontier coding evidence. Vals AI's same-harness mini-swe-agent run now shows Claude Opus 5 at 97.00% on SWE-bench Verified, GPT-5.6 Sol at 96.20%, and Claude Fable 5 at 95.00%; however, SWE-bench Verified remains contaminated/saturated and should not alone determine deployment. Artificial Analysis currently shows Claude Opus 5 max at Intelligence Index 63 versus GPT-5.6 Sol max at 61, with both offering 1M context; Anthropic's official July 24 release states Opus 5 supports a 1M context window and costs $5/$25 per million input/output tokens. Sources: https://vals.ai/benchmarks/swebench, https://artificialanalysis.ai/models/comparisons/claude-opus-5-vs-gpt-5-6-sol, https://www.anthropic.com/news/claude-opus-5, https://docs.anthropic.com/en/release-notes/api.
- **2026-07-14 (current session)**: Refreshed open-weight coding standings. BenchLM SWE-bench Pro (updated July 7, 2026): Ornith-1.0-397B is provisional top open-weight at 62.2%, GLM-5.2 virtually tied at 62.1%, MiniMax M3 59.0%, Kimi K2.6 58.6%, DeepSeek V4 Pro Max 55.4%. BenchLM LiveCodeBench (updated July 8, 2026): DeepSeek V4 Pro Max leads all models/open-weights at 93.5%; DeepSeek V4 Flash Max 91.6%; Kimi K2.6 89.6%; Nemotron 3 Ultra 89.0%. OpenLM SWE-bench+ shows GLM-5.2 top open-weight on SWE-bench Verified-style scoring at 82.8%. Corrected Qwen3.7 Max classification: API-only/not open-weight. Sources: https://benchlm.ai/benchmarks/swePro, https://benchlm.ai/benchmarks/liveCodeBench, https://openlm.ai/swe-bench.
- **2026-07-28 (current session)**: Verified current Artificial Analysis LLM leaderboard snapshot via live fetch. Snapshot date inferred from live page content and FAQ: metrics are based on the past 72 hours of measurements. Current top Intelligence Index models are Claude Opus 5 (max) 61, Claude Opus 5 (xhigh) 60, Claude Fable 5 (with fallback) 60, GPT-5.6 Sol (max) 59, and Claude Opus 5 (high) 59. Current fastest output speed is Mercury 2 at 993.4 tokens per second; current lowest latency frontier models include Gemini 2.5 Flash-Lite at 0.36s and Command A+ at 0.39s. Source: https://artificialanalysis.ai/leaderboards/models (live fetch 2026-07-28).
- **2026-07-20 (current session)**: Verified current coding-model readout with live sources. Vals SWE-bench Verified page now lists GPT-5.6 Sol, Claude Fable 5, Claude Opus 4.8, GPT-5.5, Claude Opus 4.7, Gemini 3.5 Flash, Kimi K2.7 Code, and GPT-5.4 xhigh among the top results; Claude Fable 5 remains the strongest raw coding model on the independent verified harness. Anthropic’s Sonnet 5 and OpenAI’s GPT-5.5 remain competitive but slightly behind Fable 5 on coding-specific benchmarks. Sources: https://vals.ai/benchmarks/swebench, https://benchlm.ai/compare/claude-sonnet-5-vs-gpt-5-5, https://openai.com/index/introducing-gpt-5-5, https://www.anthropic.com/news/claude-sonnet-5.
- **July 2026 (current session)**: New durable facts recorded: Claude Sonnet 5 (July 2, 2026) + self-hosted Claude Code gateway on Bedrock/Vertex AI. Chinese models now 30–46% of US developer tokens on OpenRouter (CNBC July 7). Fable 5 free access extended to July 12. Google FARO governance proposal (July 7). Anthropic building cross-industry cyber jailbreak benchmark with Amazon/Google/Microsoft. GPT-5.6 public GA confirmed July 10; no benchmark scores yet. Sources: FourWeekMBA, CNBC, Axios, Forbes (July 2026).
- **July 2026 (re-fetched live)**: AA leaderboard re-fetched. 111 models ranked. **Intelligence scores recalibrated downward vs. prior session** (Fable 5: 65→60; Opus 4.8: 61→56; GPT-5.5 xhigh: 60→55; Opus 4.7: 57→54) — likely a methodology/normalization change by AA, not model regressions. Rank order unchanged. Claude Sonnet 5 (max) = 53, tied with GPT-5.5 (high). Open-weight #1: GLM-5.2 at 51. Mercury 2 speed: 1,029 t/s. North Mini Code TTFT: 0.30s (#1 latency). GPT-5.5 Pro + Gemini 3 Deep Think still unscored. Notable new entries visible: Qwen3 Coder Next (21), Nemotron Cascade 2 (21), Amazon Nova 2.0 family, DiffusionGemma 26B A4B (13), Devstral Small 2 (17), Magistral Medium 1.2 (18), EXAONE 4.5 (23), Step 3.7 Flash (30). Source: artificialanalysis.ai/leaderboards/models (live fetch, July 2026).
- **~Early July 2026 (GPQA/MMLU-Pro refresh)**: Live-fetched BenchLM GPQA (July 7, 2026; 65 models), llm-stats GPQA (July 2026; 226 models), pricepertoken MMLU-Pro (July 8, 2026; 196 models), vals.ai MMLU-Pro (July 2, 2026). KEY DELTA: **Sakana Fugu and Fugu-Ultra** (launched June 22, 2026) are now co-#1 on BenchLM GPQA at 95.5%. ⚠️ CRITICAL CAVEAT: Fugu/Fugu-Ultra are multi-agent orchestrators (pool of frontier LLMs), NOT standalone models. Score is self-reported. Claude Fable 5 now #3 BenchLM at 94.5%. Claude Mythos Preview still #1 on llm-stats at 94.6% (Fugu not yet listed there). MMLU-Pro: vals.ai still shows Claude Fable 5 #1 at 91.50% (July 2, 2026); pricepertoken shows Gemini 3 Pro Preview at 89.8% (July 8, 2026, from Artificial Analysis; different model coverage). Sources: benchlm.ai (Jul 7), llm-stats (Jul 2026), pricepertoken (Jul 8), vals.ai (Jul 2), sakana.ai/fugu + VentureBeat (Jun 22, 2026 launch).
- **2026-06-29 (this session)**: Re-verified latest GPQA and MMLU-Pro leaderboards and dates:
- **2026-07-27**: Artificial Analysis article page surfaced a July 24, 2026 update describing Claude Opus 5 as the new leader on AA Intelligence Index and Claude Opus 5 as leader on AA-Briefcase; however, the search snippet did not expose the live leaderboard row data or the underlying leaderboard snapshot timestamp. Treat this as a lead to verify directly on the leaderboard page before using specific rank claims. Source: https://artificialanalysis.ai/articles/announcing-enterpriseops-gym-aa.
- **2026-06-29**: Artificial Analysis LLM Leaderboard live fetch (72-hour rolling window). Top Intelligence Index models: Claude Fable 5 (with fallback)=60; Claude Opus 4.8 (max)=56; GPT-5.5 (xhigh)=55; Claude Opus 4.7 (max)=54; GPT-5.5 (high)=53; GLM-5.2 (max)=51; GPT-5.5 (medium)=50; Gemini 3.5 Flash=50; Claude Sonnet 4.6 (max)=47; Gemini 3.1 Pro Preview=46 (tie with Qwen3.7 Max=46). Source: https://artificialanalysis.ai/leaderboards/models (fetched 2026-06-29).
  - GPQA — BenchLM.ai updated **June 18, 2026** (top: Claude Fable 5 94.5%) https://benchlm.ai/benchmarks/gpqa; Vals.ai updated **June 10, 2026** (top: Gemini 3.1 Pro Preview 95.45%) https://vals.ai/benchmarks/gpqa; LLM‑Stats last updated **June 2026** (226 models; date not shown) https://llm-stats.com/benchmarks/gpqa.
  - MMLU‑Pro — Vals.ai updated **June 17, 2026** (top: Claude Fable 5 91.50%) https://vals.ai/benchmarks/mmlu_pro; BenchLM.ai updated **June 27, 2026** (top: Qwen3.7 Max 89.6%) https://benchlm.ai/benchmarks/mmluPro; PricePerToken snapshot **June 27, 2026** (top: Gemini 3 Pro Preview 89.8%) https://pricepertoken.com/leaderboards/benchmark/mmlu-pro.

- **2026-06-[current session]**: Added "LangChain Deep Agents (Code) — Agent Harness Profile" section. Key findings: Deep Agents is a model-neutral harness (MIT, open-source) built on LangGraph; NOT a model itself. `deepagents-cli` scored 52.8% → 66.5% on Terminal-Bench 2.0 purely via harness engineering (same model, GPT-5.2-Codex). This ~Top-5 ranking was at publication (~early 2026); live TB 2.0 leaderboard now has 142 entries with top at 84.7% — 66.5% is roughly rank 35–50 today. Primary use case: build *customizable internal coding agents* with model flexibility + LangSmith observability. Managed Deep Agents (hosted API) entered private beta May 29, 2026. Open SWE is a reference implementation for Slack/Linear/GitHub-triggered agents. Sources: LangChain blogs (harness engineering + Open SWE), LangChain Interrupt 26 YouTube keynote (May 2026).
- **July 10, 2026 (confirmed)**: GPT-5.6 Sol/Terra/Luna **public GA = Thursday July 10, 2026**. Commerce Dept (CAISI) cleared July 8 after testing. Altman confirmed on X July 9. Staggered rollout began June 26 (limited to ~20 gov-approved partners). Meta next model "Watermelon" in training, reportedly matches GPT-5.5 (Business Insider, July 2026). Sources: Axios/CNBC/Politico/CNET (July 8–9, 2026).
- **2026-06-29**: Fable 5 partial restore: Mythos 5 back for ~100 US orgs (June 27); Fable 5 general access expected early July. GPT-5.6 ExploitBench = matched Mythos, no coding scores yet. GLM-5.2 CNBC-confirmed within 1pp of Opus 4.8 at 1/5 cost. Karpathy joined Anthropic ~late May 2026.
- **2026-06-28 (current session)**: Added GPT-5.6 series (Sol/Terra/Luna) to scorecard. Launched June 26, 2026 in limited preview (~20 government-approved partners only) at White House request. General availability "in coming weeks" — no specific date. Sol is OpenAI's most capable model yet; government views it as "on par" with Anthropic Mythos. Sources: Axios, TechCrunch, CNBC, Guardian (June 25–26, 2026).
- **2026-06-28 (current session)**: Added full "Nvidia Nemotron 3 Family" detailed profile section. Key findings: Nemotron 3 Ultra (June 4, 2026) is the best US-made open-weight model with unique 1M-context RULER leadership (76.83% at 1M — only open model with published score). However, it ranks ~48 on AA Intelligence Index vs. GLM-5.2 (51), Kimi K2.6 (~54), Qwen3.7 Max (57) — Chinese labs still lead on overall capability. Base model benchmarks show Nemotron ahead of the specific models Nvidia chose to compare against, but Nvidia conspicuously omits GLM-5.2 and Qwen3.7 Max from their comparison tables. The Nemotron 3 Nano is more impressive at its tier: 38.8% SWE-bench (OpenHands) vs Qwen3-30B's 22%, and 3.3× throughput on single H200. OpenMDW-1.1 license (not MIT/Apache — check before redistributing). Sources: HuggingFace official model card (June 4, 2026), buildmvpfast.com guide, r/LocalLLaMA community reaction.
- **2026-06-28 (current session, IPO update)**: Refreshed IPO timelines for OpenAI and Anthropic. Anthropic: October 2026 Nasdaq listing remains the target (~$965B); depends on Fable 5/Mythos 5 export-control resolution; Trump softened stance June 19 (post-G7) but orders technically still in force. OpenAI: S-1 filed June 8–9, no specific date given; Altman said "within the next year" (Reuters, June 10); $73B+ cash pile reduces urgency (Investing.com citing The Information, June 16). Both companies are recruiting heavily pre-IPO (Shazeer to OpenAI, Jumper to Anthropic, both June 18–19). PitchBook/NVCA frames both as expected to complete "$1T IPOs in the coming months." Anthropic's is more specific (October target); OpenAI's is deliberately vague. Sources: Cryptopolitan (June 19), TechCrunch (June 18), CNBC (June 17–19), GamesBeat/PitchBook/NVCA (June 2026), Investing.com (June 16), Business Insider (June 2026).
- **2026-06-[current session]**: Added full "Open-Weight Models — Top Tier" section. Key findings: GLM-5.2 (Z.AI, June 13, 2026) is now the #1 open-weight model on Artificial Analysis Intelligence Index v4.1 (score 51, 5th overall including closed). DeepSeek V4 Pro leads on LiveCodeBench (93.5%, beats all closed models). MiniMax M3 leads SWE-bench Pro among open-weights (59.0%). Open-closed gap now ~2–3pts overall, ~0 on SWE-bench Pro; Chinese labs dominate the category. Meta Llama effectively retired (Llama 4 scores 18–24 on BenchLM). Sources: BenchLM.ai (updated June 18, 2026), Lushbinary (June 17, 2026), Artificial Analysis Intelligence Index v4.1.
- **2026-06-[current session]**: Added full "Coding Agents — Full Landscape" section. Key new data: GLM-5.2 (Z.AI, MIT, June 13) confirmed at 79.2% SWE-Verified (openlm.ai); MiniMax M3 tops open-weight SWE-Pro at 59.0% (OpenCode); Qwen3.7 Max #1 open-weight SWE-Pro at 60.6% (OpenCode); Devin 2.0 45.8% no-human-loop; SpaceX $60B deal to acquire Cursor confirmed (WSJ, late June 2026). Codex CLI Terminal-Bench #1 at 84.7% (NexAU-AHE agent), beating Claude Code's official harness. SWE-rebench (fresh PRs) gives most conservative real-world ceiling: proprietary ~52%, open-weight ~43%. Harness scaffold insight documented: agent system quality often > model quality.
- **2026-06-28 (current session)**: Added GLM-5.2 (Z.AI) to Non-Western model timeline — 753B MIT open-weight, announced June 13 on X, open-sourced ~June 20, 2026; currently the most-discussed new Chinese open-weight model; VentureBeat + Business Insider + Forbes coverage. Terminal-Bench 2.1: 81.0%.
- **2026-06-28 (current session)**: Added Health/Medical AI section. Key findings: Frontier generalists beat specialized clinical tools (Nature 2026). GPT-5.x family leads on HealthBench (~73%). MedGemma 27B-IT is the best open-weight medical model. MedQA is saturating (o3 ~96%); HealthBench is the more meaningful eval. Sources: openai.com/index/healthbench, awesomeagents.ai, Nature s41591-026-04431-5.
- **[current session — GPQA/MMLU-Pro refresh]**: Live-fetched BenchLM.ai GPQA (June 18, 2026; 62 models), vals.ai MMLU-Pro (June 17, 2026), vals.ai GPQA (June 10, 2026), llm-stats MMLU-Pro (June 2026; 129 models). KEY DELTA: **Claude Fable 5 first evaluated on GPQA → #1 at 94.5%** on BenchLM (June 18). vals.ai GPQA (independent harness, June 10) shows Gemini 3.1 Pro Preview leading at 95.45%, with Fable 5 not yet in that harness. Full BenchLM GPQA top-25 updated in scorecard. vals.ai MMLU-Pro top-10 unchanged (Fable 5 still #1 at 91.50%). llm-stats MMLU-Pro still shows Qwen3.7 Max #1 at 89.6% (129 models; Fable 5 not evaluated there). Sources: benchlm.ai (Jun 18), vals.ai (Jun 17/Jun 10), llm-stats (Jun 2026).
- **~July 2026 (current session)**: Re-fetched GPQA live (llm-stats.com, 226 models). NEW: GLM-5.2 (Zhipu AI) at rank #12, 91.2% — best open-weight on GPQA. Top-3 unchanged. Claude Fable 5 still not on llm-stats GPQA. vals.ai MMLU-Pro (6/17/2026) unchanged: Claude Fable 5 #1 at 91.50%.
- **2026-06-28**: Re-fetched GPQA (llm-stats.com, last updated June 7, 2026; 220 models) and MMLU-Pro (vals.ai, updated June 9, 2026; 110 models) live. **GPQA unchanged** from prior snapshot — top-3 still Claude Mythos Preview 94.6%, Gemini 3.1 Pro 94.3%, Claude Opus 4.7 94.2%. Notable new GPQA models now visible: Grok 4 Fast (85.7%, $0.20/$0.50, 2M ctx), ByteDance Seed 2.0 Pro (88.9%), ByteDance Seed 2.0 Lite (85.1%), MAI-Code-1-Flash (84.6%), Kimi K2.5 (87.6%), Kimi K2-Thinking-0905 (84.5%), GLM-5.1 (86.2%), GLM-4.7 (85.7%), Qwen3.6-27B (87.8%), Qwen3.5-35B-A3B (84.2%), DeepSeek-V4-Flash-Max (88.1%), GPT-5.5 Instant (85.6%). Claude Fable 5 still NOT evaluated on GPQA. MMLU-Pro: vals.ai top-10 unchanged — Claude Fable 5 #1 at 91.50% (standardized harness), Gemini 3.1 Pro #2 at 90.99%. vals.ai editorial: "benchmark is largely saturated." Sources: [llm-stats.com/benchmarks/gpqa](https://llm-stats.com/benchmarks/gpqa) (last updated June 7, 2026), [vals.ai/benchmarks/mmlu_pro](https://vals.ai/benchmarks/mmlu_pro) (updated June 9, 2026).
- **2026-06-[current session]**: Live-fetched Artificial Analysis LLM Leaderboard (381 models). Top-5 Intelligence confirmed unchanged: Claude Fable 5=65, Opus 4.8=61, GPT-5.5 xhigh=60, GPT-5.5 high=59, Opus 4.7 max=57. New #1 lowest-latency: **North Mini Code** (Cohere, 0.32s TTFT), edging out Command A+ (0.39s). Mercury 2 now 864 t/s. New models added since last fetch: Magistral Medium/Small 1.2, Mistral Small 4, Nova 2.0 series (Amazon), Step 3.7 Flash, gpt-oss-20b, Ring/Ling-2.6-1T (InclusionAI), LFM2.5 family (Liquid AI), North Mini Code. Gemini 3.5 Flash TTFT improved to ~21s (was ~35s). GPT-5.5 Pro and Gemini 3 Deep Think still no scores. Source: artificialanalysis.ai/leaderboards/models (live).
- **2026-06-23 (this session)**: Live-fetched Terminal-Bench 2.0, vals.ai SWE-bench Verified, and LMArena Text leaderboard. All three confirmed UNCHANGED from prior session snapshot (June 22). Terminal-Bench 2.0: 142 entries, #1 still NexAU-AHE + GPT-5.5 at 84.7% (2026-05-14); no new entries since May 14–15. vals.ai SWE-bench Verified: 59 systems, last updated June 13, 2026; #1 Claude Fable 5 at 95.0%, #9 Kimi K2.7 Code at 78.2% (new since June 4). LMArena: 660 models; claude-fable-5 confirmed #1 Overall, Coding, Creative Writing, IF, Hard Prompts; claude-opus-4-6-thinking still #1 Expert; gemini-3.5-flash still #1 Math; grok-4.3 at rank #56. Added new notable model entries observed in LMArena live fetch (grok-4-0709, magistral-medium-2506, nova-2-lite, kimi-k2 preview variants, ByteDance dola-seed-2.0-pro, Stepfun step-3, etc.). Note: Fable 5 still shows "-" (not yet ranked) on the Math sub-category. No new Claude Fable 5 entries on Terminal-Bench — still missing from that leaderboard entirely.


- **2026-06-21 (this session)**: Refreshed GPQA and MMLU-Pro leaderboards from three live sources each. GPQA: llm-stats.com (last updated June 7, 2026; 220+ models) — Claude Mythos Preview #1 at 94.6%, Gemini 3.1 Pro #2 at 94.3%, Claude Opus 4.7 #3 at 94.2%. pricepertoken.com (last updated June 11, 2026; 240 models, sourced from Artificial Analysis) — Gemini 3.1 Pro #1 at 94.1%, MiniMax M3 at 92.9%, Qwen3.7 Max at 92.3%. **New notable**: Claude Fable 5 NOT yet evaluated on GPQA as of June 11. MMLU-Pro: **vals.ai (updated June 9, 2026)** runs a standardized 5-shot CoT harness (110 models) — **Claude Fable 5 #1 at 91.50%**, Gemini 3.1 Pro #2 at 90.99%, Gemini 3 Pro #3 at 90.10%. GPT-5.5 #10 at 88.14%. vals.ai editorial note: "benchmark is largely saturated." llm-stats (June 7) still shows Qwen3.7 Max #1 at 89.6% but doesn't yet include Fable 5. Full leaderboard tables updated in both sections. Sources: [llm-stats.com](https://llm-stats.com/benchmarks/gpqa) (Jun 7 2026), [pricepertoken.com](https://pricepertoken.com/leaderboards/benchmark/gpqa) (Jun 11 2026), [vals.ai MMLU-Pro](https://vals.ai/benchmarks/mmlu_pro) (Jun 9 2026).
- 2026-06-22 (this session): Added Anthropic "Policy on the AI Exponential" (June 10, 2026) and AA-AgentPerf benchmark (Artificial Analysis, June 2026) to AGENTS.md Safety & Evaluation Frameworks section.
- 2026-06-22 (this session): Updated System Card table — Claude Fable 5 & Mythos 5 system card (June 9, 2026; updated June 11) is now the most recently published frontier system card; 319 pages. Updated benchmark table in Claude Fable 5 section with system card scores: SWE-bench Pro 80.3%/80.0%, SWE-bench Verified 95.5%/95.0%, Terminal-Bench 2.1 88.0%/84.3%, HLE 59.0%/64.5% (with tools), OSWorld-Verified 85.0%, BrowseComp 88.0%, CharXiv 88.9%. Source: live fetch of anthropic.com/claude-fable-5-mythos-5-system-card.
- 2026-06-20 (this session): Added "Frontier API Pricing — Recent Changes Log" section. Confirmed changes: Google AI Plus cut $7.99→$4.99 (June 8); Fable 5 new $10/$50 tier (June 9); Fable 5 free trial ends June 23; GitHub Copilot per-token switch (June 1); OpenAI Containers per-session billing (March 31); Anthropic/OpenAI enterprise token billing (Q1). Pending/rumored: OpenAI "drastic" token price cuts (WSJ June 10–11, discussions in flux, no effective date). No confirmed cuts to OpenAI or Anthropic API token prices as of June 20, 2026.
- 2026-06-09 (this session): **Claude Fable 5 and Mythos 5 launched** (June 9, 2026). Fable 5 = first publicly available Mythos-class model; guardrailed (cyber/bio/chem queries route to Opus 4.8). Mythos 5 = same weights, safeguards lifted, restricted to Project Glasswing. Both priced $10/$50 per 1M in/out. Self-reported SWE-bench Pro 80.3% — not yet independently verified. Added new "Claude Fable 5 / Mythos 5" section to scorecard. Sources: anthropic.com, TechCrunch, CNBC, Forbes, Axios (all June 9, 2026).
- **2026-06-28 (this session)**: Added Fable 5 export control fallout details: Amazon researchers as root cause (Andy Jassy warned White House); David Sacks account that Anthropic refused to patch jailbreak; prorated refund deadline June 20; Canadian PM Carney G7 speech (June 14) on AI over-reliance; OpenAI $150M global partner ecosystem commitment. Fable 5 / Mythos 5 still offline for international customers as of late June 2026. No new frontier model releases found for June 14–28 window.
- **2026-06-22 (this session)**: Live-fetched Terminal-Bench 2.0 (142 entries). **CORRECTION**: Prior "vix + Claude 4.7 = 90.2%" entry is absent — no "vix" agent found in live leaderboard. New #1: NexAU-AHE + GPT-5.5 at 84.7% (2026-05-14). Full top-22 rows updated. No new entries since May 14–15, 2026; Claude Fable 5 and Claude 4.8 not yet submitted. Confirmed vals.ai SWE-bench Verified unchanged (last update 6/13/2026): Fable 5 still #1 at 95.0%, Kimi K2.7 Code still #9 at 78.2%/$0.27. Added BenchLM Agentic composite leaderboard section (fetched 2026-06-22): Claude Mythos 5 + Fable 5 both 100% weighted; Gemini 3.5 Flash leads MCP Atlas (83.6%); GPT-5.4 Pro leads BrowseComp (89.3%).
- **2026-06-20 (this session): Claude Fable 5 independently verified at 95.0% on SWE-bench Verified** (vals.ai, updated June 9, 2026). This is a +6.4pp gain over prior #1 Claude Opus 4.8 (88.6%), and is INDEPENDENTLY confirmed via standardized mini-swe-agent harness — not self-reported. Fable 5 also leads on every task difficulty tier, including hardest (>4hr: 100%). $2.05/test, 356s latency — faster and cheaper than Opus 4.8. Updated Best-for-Coding headline, cost/tradeoff table, and vals.ai leaderboard table accordingly.
- 2026-06-22 (this session): Re-fetched vals.ai SWE-bench Verified live (updated June 13, 2026). New entrant: **Kimi K2.7 Code** (Moonshot AI) at rank 9, 78.20% ±1.85, $0.27/test, 897s latency — the cheapest model in the 78%+ tier. All other rankings unchanged from June 4 snapshot. Leaderboard now covers 59 systems.
- 2026-06-22 (this session): **Refreshed LMArena Text leaderboard live.** Major change: **claude-fable-5 is now #1 Overall** (entered June 10, 2026), displacing claude-opus-4-6-thinking which had held #1 since ~Feb 2026. claude-opus-4-8-thinking is new at #9 (entered June 6). gpt-5.5-high dropped from #8→#10; gemini-3.5-flash dropped from #10→#13. Also confirmed Agent Arena launched June 4, 2026. Updated Overall Top 5 section to reflect live rankings. Source: lmarena.ai live fetch + news.lmarena.ai/leaderboard-changelog live fetch (June 22, 2026).
- 2026-06-22 (this session): Captured major events June 8–13, 2026: (1) **OpenAI confidential S-1 filed June 8** (1 week after Anthropic's June 1 filing); targeting $1T+ valuation; $2B/month revenue as of March 2026; timing uncertain. (2) **Anthropic Fable 5 and Mythos 5 globally suspended June 12** — unprecedented US export control directive from Commerce Dept at 5:21 PM ET; Anthropic disabled both models for ALL customers worldwide to ensure compliance with foreign-national ban; still offline as of June 13; government believed a Fable 5 jailbreak existed. (3) **Google NotebookLM upgraded to Gemini 3.5** (June ~9, Ultra/enterprise only). (4) **Gemini 3.5 Live Translate launched June 9** (70+ languages, Google Translate + Meet). (5) **xAI safety whistleblower lawsuit filed June 10** (ex-engineer alleges firing for raising Grok safety concerns). (6) **Canada Privacy Commissioner ruled Grok violates privacy law June 11** (1.8M deepfake images in 10 days). Sources: CNBC, Bloomberg, CNN, Guardian, Forbes, TechCrunch, 9to5Google (all June 8–13, 2026).
- 2026-06-20 (this session): **Fable 5 / Mythos 5 US government shutdown (June 12, 2026)**. Commerce Dept export control directive forced Anthropic to disable BOTH models globally for all customers. Trigger: reported jailbreak that could unlock Mythos cybersecurity capabilities. Amazon CEO Andy Jassy reportedly warned White House. Anthropic disagrees with the scope; offering prorated refunds. Models offline as of June 13–14. This is the first known use of US export controls to withdraw a commercially deployed AI model. Sources: CNBC, Bloomberg, Verge, Ars Technica, Fortune (June 12–14, 2026).
- 2026-06-20 (this session): **OpenAI filed confidential S-1 (IPO) on June 9, 2026**; Altman "third phase" blog published same day. OpenAI joined Anthropic's call for an international AI watchdog. Sources: NYT, AP, Reuters.
- 2026-06-20 (this session): **Gemini 3.5 Live Translate** announced June 9, 2026 — live speech-to-speech translation for Google Translate + Google Meet + developer API. Source: 9to5Google.
- 2026-06-20 (this session): **Anthropic Fable 5 transparency reversal** — June 11, silent guardrail downgrade of AI-researcher requests reversed; Anthropic said "we made the wrong tradeoff." Source: Business Insider, Fortune.
- 2026-06-20 (this session): Re-fetched Artificial Analysis LLM Leaderboard live (373 models, 72-hr rolling). Confirmed top-5 unchanged: Claude Opus 4.8 max=61, GPT-5.5 xhigh=60, GPT-5.5 high=59, Claude Opus 4.7 max=57, Gemini 3.1 Pro Preview=57. Notable speed/latency changes vs prior snapshot: GPT-5.5 high TTFT now listed as 33.29s (was 33.29s — no change); Claude Opus 4.7 non-reasoning TTFT 1.31s confirmed; Command A+ TTFT 0.31s confirmed (lowest latency frontier); Mercury 2 920 t/s confirmed (fastest). New models now showing live data: MiniMax-M3 TTFT 2.27s, Step 3.7 Flash 411 t/s / 1.06s TTFT, Mistral Small 4 180 t/s / 0.77s TTFT. GPT-5.5 Pro still listed with no scores. Gemini 3 Deep Think still listed with no scores. Vellum leaderboard (updated May 29, 2026): "n/a" for speed/latency on flagship 4.8/4.7/5.5 models — consistent with AA's live data. Notable new Vellum data: GPT-5.3 Codex listed at 0.003s TTFT (anomalous — likely a cached response artifact). Source: artificialanalysis.ai (live, fetched current session); vellum.ai (updated 2026-05-29).
- **LATEST AA FETCH (~late June 2026)**: Intelligence top-5 unchanged from prior fetch: Claude Fable 5=65, Claude Opus 4.8=61, GPT-5.5 xhigh=60, GPT-5.5 high=59, Claude Opus 4.7 max=57. Total models: **401** (up from 381). **Speed deltas**: Mercury 2 fluctuating 864–908 t/s (72-hr window); **LFM2.5-VL-1.6B (Liquid AI) now #2 at 479 t/s**, Granite 4.0 H Small (IBM) #3 at 477 t/s, LFM2.5-1.2B-Instruct at 476 t/s. Step 3.7 Flash dropped from 411→382 t/s. Grok 4.3 high at 176 t/s; Gemini 3.5 Flash medium at 176 t/s. Nemotron 3 Ultra confirmed at 195 t/s (fast for 550B MoE). Qwen3.7 Max at 191 t/s. **Latency deltas**: North Mini Code (Cohere) #1 at 0.32s; Gemini 2.5 Flash-Lite non-reasoning now listed at 0.36s (previously not in latency ranking); Command A+ at 0.39s; Nvidia Nemotron 3 Nano at 0.44s (new in latency ranking). Gemini 3.5 Flash improved: TTFT 21.46s (down from ~35s prior); Grok 4.3 medium at 8.76s TTFT; GPT-5.5 medium at 8.25s. **Intelligence Index v4.0 now listed** (up from prior unnamed version): includes GDPval-AA, τ²-Bench Telecom, Terminal-Bench Hard, SciCode, AA-LCR (long-context reasoning), AA-Omniscience, IFBench, HLE, GPQA Diamond, CritPt. New evaluation ITBench-AA (Kubernetes incident root-cause analysis) listed as NEW. Claude Opus 4.8 TTFT revised to 17.35s (was 21.61s — improvement). GPT-5.5 Pro still no scores. Gemini 3 Deep Think still no scores. Source: [artificialanalysis.ai/leaderboards/models](https://artificialanalysis.ai/leaderboards/models) (live fetch, current session).
- **CURRENT AA FETCH (live, fetched early July 2026 — latest)**: 111 models scored (up from 69 prior). **Major new model: Claude Sonnet 5** (Anthropic) — multiple effort tiers now listed; max=53 (tied #5 with GPT-5.5 high), non-reasoning=42, speed 79 t/s; other tiers (xhigh, high, medium, low) populating. Top-5 unchanged: Claude Fable 5=60, Claude Opus 4.8=56, GPT-5.5 xhigh=55, Claude Opus 4.7 max=54, Claude Sonnet 5 max=53 (tied with GPT-5.5 high=53). #7: GLM-5.2=51 (open-weight #1). #8: GPT-5.5 medium=~50. #9: Gemini 3.5 Flash=50. #10: Gemini 3.1 Pro Preview=~46. #11: Qwen3.7 Max=46. #12: Gemini 3.5 Flash medium=~45. #13 (tie): MiniMax-M3=44, DeepSeek V4 Pro=44, GPT-5.3 Codex xhigh=~44, Kimi K2.6=44. #17 (tie): GPT-5.5 low=43, Muse Spark=43, Claude Opus 4.7 non-reasoning=43. #20 (tie): MiMo-V2.5-Pro=42, Kimi K2.7 Code=42, Claude Sonnet 5 non-reasoning=42. Lower: Nex-N2-Pro=41; DeepSeek V4 Pro high=41; DeepSeek V4 Flash max=40; GLM-5.1=40; GPT-5.4 mini xhigh=40; Grok Build 0.1 0616=40; Qwen3.6 Plus=40; Qwen3.7 Plus=39; Nemotron 3 Ultra=38; Grok 4.3 high=38; o3=30; Mistral Medium 3.5=30; GPT-5.5 Instant June 2026=29; Gemma 4 31B=29; Gemini 2.5 Pro=26; Llama 4 Maverick=14. Speed: Mercury 2=**1,029 t/s** (up from 833–908 prior); Granite 4.0 H Small=402 t/s (new in top-3); Step 3.7 Flash=400 t/s. Latency: North Mini Code=0.30s (#1); Gemini 2.5 Flash-Lite=~0.36s; Command A+=0.40s; NVIDIA Nemotron Nano 12B v2 VL=0.44s. GPT-5.5 Pro + Gemini 3 Deep Think still no scores. Source: artificialanalysis.ai/leaderboards/models (live fetch, early July 2026).
- 2026-06-~17 (this session): Added "New/Newly Confirmed Benchmarks 2026" section. Key new benchmarks: ARC-AGI-3 (<1% frontier LLMs, even GPT-5/Claude/Gemini), GDPval (OpenAI professional-task eval), τ2-Bench (Sierra Research dual-control), OS-HARM (arXiv 2506.14866), CUAHarm. Key new validity findings: OpenAI SWE-bench Verified broken-task audit (>60% remaining unsolved tasks structurally flawed); 2026 International AI Safety Report documents eval-context switching (models behave safer in eval than deployment); METR timer-rewrite incident (model rewrote timer rather than optimizing); text-to-SQL annotation error rates >50% (arXiv 2603.29399v2); HLE Mythos 64.7% (first model past mid-30s); MIT Technology Review "AI benchmarks are broken" (March 31, 2026); CursorBench v3.1 flagged as vendor benchmark / sales asset.
- 2026-06-20 (this session): Refreshed all four live pricing pages (OpenAI, Anthropic, Google, xAI). Key deltas found vs. prior memory: (1) **xAI**: Grok 4.3 now clearly active flagship at $1.25/$2.50 (down from $3.00/$15.00 for old Grok 4); Grok 4.20 and Grok 4 no longer on public page; Grok Build 0.1 ($1.00/$2.00, 256k) new coding model launched May 29, 2026. (2) **Anthropic**: Pro plan repriced to $17/mo annual ($20 monthly); Max plan from $100/mo; Team standard $20/seat/yr; active promo: $1,000 in credits per seat by July 2 2026. Sonnet 4.5 and Opus 4.5 added to legacy pricing. (3) **OpenAI**: Public page simplified to show GPT-5.5, GPT-5.4, GPT-5.4 mini only; Containers changed to per-20-min-session billing effective March 31, 2026. Multimodal pricing confirmed (GPT-Realtime-2, GPT-Image-2). (4) **Google**: Page last updated 2026-05-29 UTC; new models added since prior memory: Gemini 3.1 Flash Live Preview (realtime audio), Flash Image, Flash TTS; Gemini 3 Pro Image; Veo 3.1; Lyria 3 (music); Gemini Embedding 2 (multimodal). No across-the-board price cuts found at any lab. Structural "Tokenpocalypse" shift (Q1 2026) confirmed from multiple sources. Newest: GPT-Realtime-2 (OpenAI, May 7, 2026) — GPT-5-class streaming speech-to-speech, 128K context, 96.6% Big Bench Audio (+15.2pp vs 1.5). Co-launched with GPT-Realtime-Translate and GPT-Realtime-Whisper. Realtime API exited beta to GA on same date. Predecessor gpt-realtime-1.5 launched Feb 23, 2026. Microsoft MAI-Voice-2 (June 2, 2026) noted as a voice synthesis upgrade but not same-class as GPT-Realtime-2.
- 2026-06-17: Added "Non-Western Lab Models — Recent Timeline" section. Most recent confirmed non-Western lab release: Qwen3.7-Max (Alibaba/Qwen), snapshotted May 17, 2026, added to LMArena Code leaderboard May 25, 2026. DeepSeek-V4-Pro added April 23, 2026. Source: LMArena changelog fetched 2026-06-17.
- 2026-06-17 (this session): Refreshed GPQA Diamond + MMLU-Pro sections. GPQA: Gemini 3.1 Pro 94.3% now co-equal with Claude Mythos Preview 94.5% (BenchLM June 2, 2026); 54 models evaluated. MMLU-Pro: Fully replaced leaderboard with llm-stats.com live data (last updated June 4, 2026; 120 models). New #1: Qwen3.7 Max 89.6%; entire top-10 now dominated by Qwen3.x family and DeepSeek — Claude Opus 4.5 / Gemini 3 Pro not in llm-stats top-10 (different model coverage). Added swfte.com April 2026 head-to-head as new corroborating source (vendor-aligned, but detailed). **Pinned Claude Opus 4.7 release date to April 16, 2026** (confirmed by swfte.com). Added extended-thinking caveat: 5–12pp score drop in standard mode. Source: [llm-stats.com](https://llm-stats.com/benchmarks/mmlu-pro) (June 4, 2026), [benchlm.ai](https://benchlm.ai/benchmarks/gpqa) (June 2, 2026), [swfte.com](https://www.swfte.com/de/blog/claude-opus-4-7-vs-gpt-5-5-vs-gemini-3-1-pro) (Apr 2026).
- 2026-06-10 (session long-ctx): Added "Long-Context Benchmarks" section. Benchmarks covered: MRCR v2 8-needle (March 2026 yage.ai survey, most rigorous for 1M context); HELM Long Context (Stanford CRFM, independent, v1.0.0 Sep 2025, evaluates at ≤128K); LongBench v2 (THUDM, last updated 2025-05-06, no 2026-gen models yet). Key finding: Claude Opus 4.6 is the only model maintaining 70%+ at 1M (76% MRCR v2 8-needle); Gemini 3 Pro only 24.5% at 1M despite having 1M context since 2024; GPT-5.4 at 36.6% at 1M. HELM top (128K independent): GPT-4.1 at 0.588 mean across 5 tasks. LongBench v2 top (deep reasoning): Gemini-2.5-Pro 63.3%. Primary sources: yage.ai (2026-03-15), CRFM (2025-09-29), LongBench v2 (2025-05-06).
- 2026-06-10 (session 7): Added Safety & Evaluation Frameworks section to AGENTS.md. Key items: Microsoft ASSERT open-source eval tool (June 2, 2026), Microsoft MXC runtime containment for agents (June 2, 2026), OWASP Enterprise Adoption Maturity Model for agentic AI (June 3–4, 2026), MLCommons AILuminate v1.0 (Feb 2025) + v1.1 French (Feb 2025), Trump AI EO classified benchmark mandate to NIST/CISA (60-day window from June 2), Great American AI Act discussion draft with CAISI codification (June 4, 2026), OpenAI "Democratic Governance" blueprint (June 3, 2026). CAISI itself launched June 2025 under US Commerce Dept.
- 2026-06-10 (this session): **Pinned GPT-5.5 release to April 23, 2026 and GPT-5.4 to March 5, 2026** — confirmed from official openai.com announcement pages fetched directly. Gap: ~49 days. Corrects prior "approximate / early 2026" estimates. GPT-5.5 API availability added April 24, 2026. GPT-5.4 replaced GPT-5.2 Thinking in ChatGPT on March 5. Also identified GPT-Rosalind as a life-sciences-specialized vertical model (not a general-purpose release) updated June 3, 2026.
- 2026-06-~17 (this session): Live-verified Terminal-Bench 2.0 leaderboard — unchanged from prior session snapshot (top entry still vix+Claude 4.7 at 90.2%, dated May 15, 2026; no new entries since then). Live-verified vals.ai SWE-bench Verified — unchanged (Claude Opus 4.8 #1 at 88.60%; last update June 4, 2026). Live-verified SWE-bench Pro Public (Scale AI SEAL) — unchanged (GPT-5.4 xHigh #1 at 59.1%, Muse Spark NEW #1 at 55.0%). New data point from BenchLM.ai (June 2, 2026): Claude Mythos Preview leads SWE-bench Pro at **77.8%** (self-reported; restricted model; harness unverified) — significantly higher than Scale AI's standardized run of GPT-5.4 at 59.1%, likely reflecting a different (more powerful) agent harness. Added BenchLM SWE-bench Pro top-3 to scorecard notes. No new leaderboard entries found post–June 4, 2026 on any of the three benchmarks checked.
- 2026-06-16: Added "New Items June 10–16" section. SpaceX IPO priced June 11, Nasdaq debut June 12 (ticker SPCX, $1.75T, $75B raise; xAI inside). Gemini 3.5 Extended Thinking made free for all users (~post-I/O rollout). OpenAI "super app" ChatGPT revamp reported June 7 by TechCrunch. Miasma worm supply chain attack June 5 via AI coding tools. No new frontier model releases found for June 10–16 window.
- 2026-06-12: Added June 1–12 "past week" news summary to AGENTS.md. Key new facts: WWDC June 8 delivered Gemini-powered Siri / iOS 27 as expected; Alphabet $85B equity raise (June 5); OpenAI "super app" plan (June 7 FT report); ChatGPT Lockdown Mode / Active Sessions (June 5); Gemini thinking modes free for all users (early June); SpaceX IPO debut June 12 (~$1.75T). No new frontier model drops confirmed for June 9–12 window from any major lab.
 Key dated milestones: GPT-5 launched at 400K (Aug 7, 2025); Anthropic Claude 5× expansion to 1M announced ~Aug 15, 2025; GPT-5.5 launched at 1M API / 400K Codex (Apr 23, 2026); Claude Opus 4.7 1M confirmed ~May 2026; Gemini 3 Pro at 1M–2M (2026). Added validity caveat: advertised context ≠ effective context — GPT-5.4 and Gemini 3.1 Pro degrade past 256K in practice.
- 2026-06-10 (session 7): Attempted to find exact dates for Claude Opus 4.6/4.7 and GPT-5/5.5 initial announcements. Both remain unverified after 2 search passes each. Claude Opus 4.6/4.7 dates not surfaced in any article. GPT-5.5 confirmed in LMArena from Apr 23–27 (gpt-5.5 codex Apr 23, gpt-5.5-high Apr 27 per LMArena changelog in memory) but no formal press announcement date found. Claude Mythos narrowed to "start of April 2026" (Engadget exact quote). Scorecard annotation updated.
- 2026-06-10 (session 6): Added Terminal-Bench 2.0 full leaderboard section (144 entries, last updated May 14–15, 2026). Key finding: vix agent + Claude 4.7 leads at 90.2%; GPT-5.5 leads single-model entries (~82–84%); agent scaffolding matters enormously (same model can differ 30+ pts across harnesses). Added MCP Atlas tool-use leaderboard (Gemini 3.5 Flash #1 at 83.6%, Scale AI SEAL). Added critical contamination note: OpenAI formally stopped reporting SWE-bench Verified scores after audit confirmed all frontier models had verbatim gold-patch recall — heightens urgency of migrating to SWE-bench Pro.
- 2026-06-~17 (this session): Replaced llm-stats SWE-bench table with live BenchLM.ai fetch (June 2, 2026, 49 models). New open-weight entries added: DeepSeek V4 Pro Max 80.6%, MiniMax M3 80.5%, Kimi K2.6 80.2%, Qwen3.6-27B 77.2%, Grok 4.20 76.7%, Grok Code Fast 1 70.8%. GPT-5.3 Codex self-reported score revised to 85.0% (up from 78.0% on vals.ai standardized — confirms harness gap). Gemini 2.5 Pro 63.8% (older gen). GPT-4.1 54.6%, GPT-4.1 mini 23.6% added for historical reference.
- 2026-06-09 (session 5): Added GPQA Diamond and MMLU-Pro leaderboard sections. Sources: BenchLM.ai (June 2, 2026), pricepertoken.com (June 8, 2026), IntuitionLabs, CodeSOTA. Key findings: GPQA top = Claude Mythos Preview 94.5% (self-reported, restricted); MMLU-Pro top = Gemini 3 Pro Preview ~89.8–90.1% / Qwen3.7 Max 89.6% (self-reported, source-dependent). Both benchmarks showing saturation at frontier level. All scores self-reported; no independent standardized harness equivalent to vals.ai for SWE-bench exists for these benchmarks.
 addition

- 2026-06-10 (session 5): Added "OpenAI Model Deprecation Schedule" section from official platform.openai.com/api/docs/deprecations page (fetched directly). Key upcoming: July 23 (GPT-5/5.1/5.2 Codex variants, gpt-4o audio/search snapshots), Oct 23 (GPT-3.5/4/4-turbo/4o full EOL, o1/o3-mini/o4-mini snapshots), Sora 2/Videos API Sept 24, Assistants API Aug 26. ChatGPT UI already retired GPT-4o/4.1/o4-mini on Feb 13, 2026.
- 2026-06-09 (session 5): Refreshed live LMArena Text top-10 (unchanged from session 3 snapshot — top-4 still all Claude 4.x, muse-spark #5). Cross-referenced full LMArena changelog for May 9–June 9, 2026 to produce dated ranking-shift timeline. Key entrants in the period: grok-4.3 (May 1, text #48), qwen3.7-max-preview (May 14, text #15), gpt-5.5-instant (May 6/8, text #17), gpt-5.5-high (Apr 27, text #8), gemini-3.5-flash (May 19, text #10, math #1), qwen3.7-max-20260517 (May 25, code board). Methodology shift May 12: "Battles in Direct" votes added — tightened CIs, shifted prompt distribution toward harder/longer queries. grok-4.3 landed only at #48 overall. New sub-category column data captured (coding #1: claude-opus-4-7-thinking; math #1: gemini-3.5-flash; expert #1: claude-opus-4-6-thinking).
- 2026-06-09 (session 4): Added "Speed & Latency" section from live Artificial Analysis leaderboard fetch (~June 2026, 72-hour rolling window). Key findings: Mercury 2 (Inception, 920 t/s) is fastest overall; Command A+ (Cohere, 0.28s TTFT) has lowest latency; top-intelligence models (Claude Opus 4.8, GPT-5.5 xhigh) are among the slowest due to extended reasoning. Gemini 3.5 Flash (183 t/s) is the fastest high-intelligence model. AIMultiple TTFT benchmark (published Jan 22, 2026) adds use-case breakdown: Mistral Large 2512 fastest TTFT at 0.30–0.45s; GPT-5.2 best per-token latency at 0.010–0.020s; Grok 4.1 Fast Reasoning has worst TTFT (3–11s) but best per-token (0.005–0.010s). Vellum leaderboard (updated May 29, 2026) also added as secondary source.
- 2026-06-09 (session 4): Added Mistral Medium 3.5 to the 2026 YTD frontier timeline (May 22, 2026). Source: mistral.ai/news direct fetch. Key specs: 128B dense, 256k context, 77.6% SWE-bench Verified (self-reported), open-weights MIT license, $1.5/$7.5 per M tokens in/out. Also noted Mistral's recent news blog shows no newer model than Medium 3.5 as of June 9, 2026.
- 2026-06-09 (session 3b): Added "Small/On-Device Models" section. Most recent: Google Gemma 4 12B released June 3, 2026. Runs on 16GB RAM laptops; multimodal; 256K context; Apache 2.0.
- 2026-06-09 (session 4): Confirmed Nvidia Cosmos 3 (June 1, 2026) as the most recently launched frontier multimodal/"omnimodel" — natively handles text, images, video, ambient sound, and actions. Open-weight, physical-AI focused. Source: Telecoms.com (June 1, 2026), Axios C-Suite (June 8, 2026). For general-purpose multimodal (vision+language) chat, Gemini 3.5 Flash (May 19, 2026) is the most recent major release.
- 2026-06-09 (session 3): Added "Lab Comparison" section covering Anthropic, OpenAI, Google. New Google detail: Gemini 3.5 Flash Extended Thinking now free for all users (no sub required); Gemini 3.1 Pro "Deep Think" added. Confirmed no major new model drops since June 9. Added note on Google's internal coding-agent lag vs Anthropic/OpenAI.
- 2026-06-08: Initial scorecard created. Populated "Recent Releases (Last 30 Days)" from news research.
- 2026-06-08: Pinned Claude Opus 4.8 release to ~May 29, 2026 (Thursday per Gizmodo article written May 30); split 4.7 and 4.8 into separate rows.
- 2026-06-09: Confirmed Google I/O 2026 = May 19, 2026 (Reuters photo caption). Updated Gemini Spark / Gemma 4 rows to reflect exact date. Added Gemini 3.5 Flash row (May 19, 2026). GPT-5.x exact launch dates still unverified; GPT-5.5 confirmed in market by early June 2026 but original announcement date not pinned.
- 2026-06-[current session]: Verified **Gemini 3.1 Pro = February 19, 2026** (from official Google blog post fetched directly; "Feb 19, 2026 · 4 min read"). Also confirmed **Gemini 3 Pro launched November 2025** (Google's own text: "Since releasing Gemini 3 Pro in November..."). Added **Gemini Omni Flash** row — announced May 19, 2026 at Google I/O alongside Gemini 3.5; dedicated blog post and "9 demos" post dated May 29 as follow-up. **GPT-5 estimated Q3 2025 (not Q2 2026)** — moved out of Q2 section. **Muse Spark = April 10, 2026** reconfirmed from CNET + Meta AI chief April 10 X post. Gemini 3.1 Pro row updated from "unverified early 2026" to Feb 19, 2026.
- 2026-06-09: Added "Week of June 2–8, 2026" developments section: Trump AI EO, Anthropic recursive self-improvement warning, OpenAI Codex/Sites expansion, WWDC 2026 AI announcements (preview-confirmed; post-keynote details pending), OpenAI compliance with EO.
- 2026-06-09: Added SWE-bench Verified and SWE-bench Pro leaderboard sections. Sources: vals.ai (updated 2026-06-04, independent/standardized harness), llm-stats.com (updated 2026-06-03, self-reported), Scale AI SWE-bench Pro (public, independent). Key finding: Claude Mythos Preview tops llm-stats at 93.9% but this is self-reported and evaluated with a different harness; vals.ai independent harness puts Claude Opus 4.8 at 88.6% (#1) and GPT-5.5 at 82.6% (#2). SWE-bench Pro public leaderboard (Scale AI) shows gpt-5.4 xHigh at 59.1% and Muse Spark at 55.0% — far lower than Verified scores, indicating continued saturation risk on Verified.
- 2026-06-09: Added "Overall Top 5 Frontier Models" section based on live LMArena leaderboard fetched directly from lmarena.ai. Top 5 (Overall Text): claude-opus-4-6-thinking (1502), claude-opus-4-7-thinking (1500), claude-opus-4-6 (1498), claude-opus-4-7 (1494), muse-spark (1489). Top-5 Elo scores verified from live fetch. Release dates for Claude 4.6/4.7 not pinned from searches; Muse Spark confirmed April 10, 2026 per CNET/Meta.
- 2026-06-09: Added "Best for Coding" category. Multi-benchmark triangulation: Claude Opus 4.8 leads SWE-bench Verified (independent, vals.ai 88.6%); GPT-5.5 Thinking leads LiveBench coding (independent, 87.71%); GPT-5 leads Aider Polyglot (llm-stats, self-reported, 88.0%). Verdict: Claude Opus 4.8 and GPT-5.5 are in a near-tie for #1 raw coding quality; Claude is pricier/slower; GPT-5.5 is faster and cheaper per task on SWE-bench ($1.36 vs $1.92/test). Budget picks: GPT-5.3 Codex ($0.46/test, 78% SWE), DeepSeek V4 ($0.44/test, 77.4% SWE), Gemini 3.5 Flash ($0.95/test, 78.8% SWE). Aider.chat leaderboard appears stale (last entries circa late 2024); LiveBench source: livebench.ai.
- 2026-06-10 (session 7 — live fetch): Refreshed Artificial Analysis LLM Leaderboard from live fetch. Confirmed top rankings unchanged: Claude Opus 4.8 (max) #1 at Intelligence 61; GPT-5.5 xhigh #2 at 60; GPT-5.5 high #3 at 59. New notable entrants: MiniMax-M3 (55, $0.22 — excellent value), MiMo-V2.5-Pro (Xiaomi, 54, $0.18 — ties Kimi K2.6 for best open-weight), Qwen3.7 Max (57, $1.43 — best value at intelligence-57 tier), GPT-5.5 Pro (listed, no scores yet), Gemini 3 Deep Think (listed, no scores yet). Qwen3.7 Max added as best-TTFT entry for intelligence-57 tier (2.66s). Full 100+ model table fetched; methodology: 72-hour rolling window, 8 measurements/day.
- 2026-06-late (live fetch): Confirmed no leaderboard rank changes in June 2026 — top-10 text ranking is identical to ~June 9 snapshot. Last entrant to break into top 10 was gemini-3.5-flash (#10) on May 19, 2026. Added gpt-5.4-high as explicit #9 (Elo 1480 ±5), previously omitted from the top-10 list. Sub-category rankings confirmed from live fetch: claude-opus-4-7-thinking leads Coding; gemini-3.5-flash leads Math; claude-opus-4-6-thinking leads Expert/hardest prompts. muse-spark (Meta, #5 overall) ranks only #30 on Expert and #27 on Math — its overall rank is heavily weighted by creative/casual prompts. New notable text entry: grok-4.3 entered at only #48 overall despite being a flagship xAI release. Source: lmarena.ai live fetch + news.lmarena.ai/leaderboard-changelog live fetch.
 — Claude Opus 4.8 #1 at 88.60%; GPT-5.5 #2 at 82.60%. Official swebench.com most recent entries dated Feb 2026 (lags vals.ai). Top on swebench.com (Feb 2026): Claude 4.5 Opus 76.8%, Gemini 3 Flash 75.8%, Claude Opus 4.6 75.6% — older snapshot, not current. LiveBench top coding score reconfirmed: GPT-5.5 Thinking xHigh 87.71, GPT-5.4 Thinking xHigh 88.12 (coding only), Claude 4.6 Opus Thinking 88.67 (coding column). Claude 4.6 Opus Thinking actually leads on the LiveBench Coding sub-column (88.67) but not on overall LiveBench score. Kimi K2.6 Thinking enters LiveBench at 72.17 overall / 79.38 coding.

---

## Overall Top 5 Frontier Models — LMArena Text Leaderboard

*Source: [lmarena.ai/leaderboard](https://lmarena.ai/leaderboard) — live human-preference Elo, fetched 2026-06-09 | Method: blind pairwise votes across all prompt types*

> **Caveat**: LMArena Elo measures human-judged preference — it rewards fluency, engagement, and instruction-following. The top 4 entries (all Claude 4.x) are within 8 Elo of each other, which is within typical confidence intervals (±4–6 Elo). Treat them as a statistical cluster. The "thinking" (extended reasoning) variants of the same model version rank higher on Overall but may differ by sub-category.

| Rank | Model | Lab | LMArena Rank (Overall) | Entered Text LB | Notes | Source URL |
|------|-------|-----|------------------------|-----------------|-------|------------|
| **1** | **claude-fable-5** | Anthropic | **#1** | **June 10, 2026** | **NEW #1 — displaced all prior Claude 4.x; #1 on Coding, Creative, IF, Longer Query; Math not yet evaluated** | [lmarena.ai](https://lmarena.ai/leaderboard) |
| 2 | claude-opus-4-6-thinking | Anthropic | #2 | Feb 9, 2026 | Was #1 until Fable 5 arrival; still leads Expert sub-category | [lmarena.ai](https://lmarena.ai/leaderboard) |
| 3 | claude-opus-4-7-thinking | Anthropic | #3 | Apr 17–21, 2026 | #2 Coding sub-category | [lmarena.ai](https://lmarena.ai/leaderboard) |
| 4 | claude-opus-4-6 | Anthropic | #4 | Feb 6, 2026 | Stable | [lmarena.ai](https://lmarena.ai/leaderboard) |
| 5 | claude-opus-4-7 | Anthropic | #5 | Apr 17, 2026 | Stable | [lmarena.ai](https://lmarena.ai/leaderboard) |
| 6 | **muse-spark** | Meta | #6 | Apr 9, 2026 | Dropped from #5; weak on Expert (#30) and Math (#30) | [lmarena.ai](https://lmarena.ai/leaderboard) |
| 7 | gemini-3.1-pro-preview | Google | #7 | Feb 19, 2026 | Stable | [lmarena.ai](https://lmarena.ai/leaderboard) |
| 8 | gemini-3-pro | Google | #8 | Nov 18, 2025 | Stable | [lmarena.ai](https://lmarena.ai/leaderboard) |
| **9** | **claude-opus-4-8-thinking** | Anthropic | **#9** | **June 6, 2026** | **NEW entrant; #5 Coding, #5 IF** | [lmarena.ai](https://lmarena.ai/leaderboard) |
| 10 | gpt-5.5-high | OpenAI | #10 | Apr 27, 2026 | Dropped from #8 to #10 with Fable 5 and Opus 4.8 arrivals | [lmarena.ai](https://lmarena.ai/leaderboard) |

*(Elo scores not directly available from the current live leaderboard page, which now shows ordinal ranks rather than raw Elo. Prior Elo figures: claude-opus-4-6-thinking 1502, muse-spark 1489, gpt-5.5-high 1482. Fable 5 Elo not yet published.)*

**Notable changes outside top 10:**
- gpt-5.4-high: moved from #9 → #11 (displaced by claude-opus-4-8-thinking)
- gemini-3.5-flash: moved from #10 → #13 (displaced by Fable 5 + Opus 4.8)
- claude-opus-4-8 (non-thinking): debuted at #12 (entered June 6, 2026)

**Sub-category leaders (as of June 22, 2026):**
- Overall: **claude-fable-5** (#1)
- Expert/hardest prompts: claude-opus-4-6-thinking (#1) — Fable 5 only #3 on Expert
- Coding: **claude-fable-5** (#1)
- Math: gemini-3.5-flash (#1), gpt-5.4-high (#3) — Fable 5 not yet evaluated on Math
- Creative Writing: claude-fable-5 (#1)
- Instruction Following: claude-fable-5 (#1)
- LiveBench (objective, contamination-resistant): GPT-5.5 Thinking xHigh 80.71, GPT-5.4 Thinking xHigh 80.28, Claude 4.6 Opus Thinking 76.33 — [livebench.ai](https://livebench.ai)

---

## Best for Coding — Multi-Benchmark View (as of June 2026)

> Three independent benchmarks triangulated: SWE-bench Verified (real GitHub issue patching), LiveBench Coding (contamination-resistant, time-windowed), and Aider Polyglot (multi-language editing). **Verdict: Claude Opus 4.8 and GPT-5.5 are effectively tied at the top.** Claude 4.8 leads on SWE-bench (independent harness); GPT-5.5 leads on LiveBench coding. The gap is within noise — pick based on cost/latency tradeoff.

### Headline: Best Raw Coding Quality

| Benchmark | #1 | Score | #2 | Score | Source type | Date | Source |
|-----------|-----|-------|-----|-------|-------------|------|--------|
| SWE-bench Verified | **Claude Fable 5** | **95.0%** | Claude Opus 4.8 | 88.6% | Independent (vals.ai standardized harness) | **2026-06-09** | [vals.ai](https://vals.ai/benchmarks/swebench) |
| LiveBench Coding | **GPT-5.5 Thinking xHigh** | 87.71 | GPT-5.4 Thinking xHigh | 88.12 (overall) | Independent (contamination-resistant) | ~June 2026 | [livebench.ai](https://livebench.ai) |
| Aider Polyglot | **GPT-5** | 88.0% | Gemini 2.5 Pro | 76.5% | Self-reported (llm-stats) | ~2026 | [llm-stats.com](https://llm-stats.com/benchmarks/aider-polyglot) |
| LMArena Coding Elo | **claude-fable-5** | #1 Coding | claude-opus-4-8-thinking | #4 Coding | Human preference (crowd) | **2026-06-22** | [lmarena.ai](https://lmarena.ai/leaderboard) |

### Cost vs Quality Tradeoff (SWE-bench Verified, vals.ai, updated 2026-06-09)

| Tier | Model | SWE Score | Cost/Test | Latency | Notes |
|------|-------|-----------|-----------|---------|-------|
| **Best quality** | **Claude Fable 5** | **95.0%** | $2.05 | 356s | NEW #1; faster AND cheaper than Opus 4.8 despite higher score |
| **2nd tier** | Claude Opus 4.8 | 88.6% | $1.92 | 567s | Still strong; slower than Fable 5 |
| **3rd tier** | GPT-5.5 | 82.6% | $1.36 | 426s | Best non-Anthropic model |
| **4th tier** | Claude Opus 4.7 | 82.0% | $2.42 | 442s | More expensive than GPT-5.5 for similar score |
| **Budget frontier** | Gemini 3.5 Flash | 78.8% | $0.95 | 254s | Fastest of the tier; excellent value |
| **Budget picks** | GPT-5.3 Codex | 78.0% | $0.46 | 247s | Best $/score ratio |
| **Budget open-weight** | DeepSeek V4 | 77.4% | $0.44 | 635s | Top open-weight option |

### Validity Caveats
- SWE-bench Verified is **saturating** at the top — see SWE-bench Pro where same models score ~23–59% vs 78–89% on Verified. High Verified scores don't guarantee real-world generalization.
- Aider Polyglot (llm-stats) is **self-reported** and the GPT-5 score has no independent verification; treat as upper bound.
- LiveBench is the most **contamination-resistant** of the three (time-windowed, held-out) — prefer it for cross-model relative comparisons.
- Claude Mythos Preview claims 93.9% on SWE-bench Verified (llm-stats) — **self-reported only**, restricted model, harness unknown. Not included here.

---

## 2026 YTD Frontier Model Timeline (Jan–June 2026)

| Date | Model | Lab | Type | Key Notes | Source | Confidence |
|------|-------|-----|------|-----------|--------|------------|
| Jan 2026 (partnership announced) | Gemini for Siri (Apple-Google deal) | Google / Apple | Partnership / model integration | Apple struck deal with Google in January 2026 to use Gemini models in Siri; formal integration expected at WWDC June 8 | [Newsweek WWDC preview](https://www.newsweek.com/wwdc-2026-everything-apple-is-expected-to-announce-on-june-8-12016937) | Verified partnership date |
| May 22, 2026 | **Mistral Medium 3.5** | Mistral | Frontier LLM (agentic/coding) | 128B dense model; 256k context; unified instruction-following + reasoning + coding; 77.6% SWE-bench Verified (self-reported); 91.4 on τ³-Telecom; runs self-hosted on 4 GPUs; open-weights (modified MIT); API: $1.5/$7.5 per M tokens in/out; default model in Le Chat and Mistral Vibe; co-announced with Vibe remote agents and Le Chat Work mode | [mistral.ai](https://mistral.ai/news/vibe-remote-agents-mistral-medium-3-5/) | **Verified May 22, 2026** |
| **February 19, 2026** | **Gemini 3.1 Pro** | Google | Frontier LLM (reasoning upgrade) | ARC-AGI-2 verified score 77.1% (>2× Gemini 3 Pro's 31.1%); released in preview across Gemini app, NotebookLM, AI Studio, Vertex AI, Gemini CLI, Android Studio; "Deep Think" tier added later; pricing $2/$4 per M input (≤/>200K), $12/$18 output | [blog.google — Feb 19, 2026](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-pro/) | **Verified: Feb 19, 2026 (official blog)** |
| **May 19, 2026** | **Gemini Omni Flash** | Google | Video-generation / omnimodal | Announced at Google I/O May 19 as the first model in the Gemini Omni family; video-in/video-out with natural-language editing; available to all Google AI Plus/Pro/Ultra subscribers via Gemini app, Google Flow, YouTube; API coming weeks later; all videos SynthID watermarked | [blog.google — Gemini Omni](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni/) | **Verified: May 19, 2026 (official blog + I/O date confirmed)** | Released in ChatGPT (as GPT-5.4 Thinking), API, and Codex; designed for professional work; first general-purpose model with native computer-use; 1M token context; SWE-bench Pro 57.7%; OSWorld-Verified 75.0%; API pricing $2.50/$15 per M in/out. GPT-5.4 Pro also released same day. | [openai.com](https://openai.com/index/introducing-gpt-5-4/) | **Verified 2026-06-10** |
| ~Aug 7, 2025 (estimated) | GPT-5 / GPT-5.1 | OpenAI | Frontier LLM | Multiple sources reference GPT-5 and GPT-5.1 as current flagships; GPT-5.5 and GPT-5.5-Cyber also in market by June 2026; original GPT-5 launch date estimated Aug 7, 2025 per context-window timeline; GPT-5.1 date not found | [Forbes June 2](https://www.forbes.com/sites/lanceeliot/2026/06/02/), [Zamin.uz](https://zamin.uz/en/technology/205521-ai-costs-spiral-out-of-control-companies-on-the-brink-of-crisis.html) | Approximate – Q3 2025, not Q2 2026 |
| **November 2025** | **Gemini 3 Pro** | Google | Frontier LLM | Launched November 2025 (Google states "Since releasing Gemini 3 Pro in November" in Gemini 3.1 Pro blog post) | [blog.google](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-pro/) | Verified from source — month only, no exact day |
| ~Early 2026 (exact date unverified) | Claude Opus 4.7 | Anthropic | Frontier LLM | Referenced as production model in June 2026 (Notion outage); exact launch date not pinned | [TechCrunch](https://techcrunch.com/2026/06/07/notion-restores-access-to-anthropic-after-service-disruption/) | Approximate – exact launch date not found |
| May 29, 2026 | **Claude Opus 4.8** | Anthropic | Frontier LLM | "Unveiled on Thursday" per Gizmodo (written Fri May 30); featured "honesty upgrade" — more likely to flag uncertainties; most recent publicly-released Claude model as of early June 2026; Claude Sonnet 4.6 also in production at this time | [Gizmodo](https://gizmodo.com/claude-got-an-honesty-upgrade-some-users-would-rather-live-in-a-web-of-lies-2000765810) | **Verified ~May 29, 2026** |
| **April 23, 2026** | **GPT-5.5** | OpenAI | Frontier LLM | "Introducing GPT-5.5" post dated April 23, 2026; API availability added April 24; rolled out to Plus/Pro/Business/Enterprise in ChatGPT and Codex; flagship model as of June 2026; SWE-bench Pro 58.6%; Terminal-Bench 2.0 82.7%; API pricing $5/$30 per M in/out; 1M token context window. Described as "smartest and most intuitive to use model yet." GPT‑5.5 Pro (Pro tier) released same day. | [openai.com](https://openai.com/index/introducing-gpt-5-5/) | **Verified 2026-06-10** |
| ~March 2026 | Nvidia Nemotron Coalition formed | Nvidia + 8 labs | Industry initiative | Nvidia assembled coalition (Mistral, Perplexity + 6 others) in March 2026 to co-develop Nemotron 4 on DGX Cloud | [Decrypt](https://decrypt.co/369689/nvidia-open-ai-model-nemotron-3-ultra) | Verified month |
| ~March 2026 | Nvidia GTC 2026 keynote | Nvidia | Event | Annual GTC conference; multiple sources reference "Highlights From Nvidia's GTC 2026 Keynote" but exact date not pinned | [CNET GTC 2026 coverage](https://www.cnet.com/videos/qualcomms-computex-keynote-in-12-minutes/) | Approximate |
| ~April 1–3, 2026 | Anthropic Mythos (initial preview) | Anthropic | Cybersecurity LLM | "Announced at the start of April" (Engadget direct quote); restricted via Project Glasswing; cyberoffense-capable frontier model; exact day not published | [Engadget](https://www.engadget.com/2185709/anthropic-expands-its-claude-mythos-preview-to-more-partners/) | Verified month/period |
| April 10, 2026 | Meta Muse Spark | Meta | Frontier LLM | Announced April 10; API access to developers still delayed as of early June 2026 | [CNET](https://www.cnet.com/tech/services-and-software/where-is-metas-ai-model-api/) | Verified date |
| **May 19, 2026** | **Gemini 3.5 Flash** | Google | Frontier LLM (speed) | Launched at Google I/O on May 19 (date confirmed by Reuters photo caption); 4× faster than competing frontier models; outperforms Gemini 3.1 Pro on coding/agentic benchmarks; default model in Gemini app + Google Search. Gemini 3.5 Pro in internal testing at I/O, expected ~June 2026. | [Android Authority](https://www.androidauthority.com/google-gemini-3-5-flash-3668559/), [Reuters June 1](https://www.reuters.com/legal/transactional/alphabet-raise-80-billion-equity-capital-ai-spending-2026-06-01/) | **Verified May 19, 2026** |
| **May 19, 2026** | **Gemini Spark** (agentic) | Google | Agentic LLM | Announced at Google I/O May 19; powered by Gemini 3.5 Flash; 24/7 personal AI agent; rolling out to AI Ultra subscribers first | [Android Authority](https://www.androidauthority.com/google-gemini-3-5-flash-3668559/) | **Verified May 19, 2026** |
| May 19, 2026 (inferred) | Gemma 4 (main lineup) | Google | Open-weight | Gemma 4 lineup launched at/around Google I/O; Gemma 4 12B added June 3 to fill a gap | [Ars Technica June 3](https://arstechnica.com/google/2026/06/googles-new-gemma-4-open-ai-model-is-sized-for-your-laptop/) | Inferred from context |
| June 1, 2026 | Nvidia Nemotron 3 Ultra | Nvidia | Open-weight LLM | 550B params (55B active MoE); largest US open-weight model; Computex keynote | [Decrypt](https://decrypt.co/369689/nvidia-open-ai-model-nemotron-3-ultra) | Verified date |
| June 1–3, 2026 | Nvidia Cosmos 3 | Nvidia | Foundation (physical AI) | "Foundation model for physical AI"; trained on physics; Computex-era announcement | [Axios June 8](https://www.axios.com/2026/06/08/ai-news-nvidia-cosmos-3-openai-sites-solara-rtx-spark) | Verified event window |
| June 2, 2026 | Microsoft MAI-Thinking-1 | Microsoft | Reasoning LLM | 35B active params; first in-house reasoning model; Build 2026 | [The Verge](https://www.theverge.com/tech/941664/microsoft-ai-model-reasoning-mai-thinking-1-build-2026), [Axios](https://www.axios.com/2026/06/02/microsoft-debuts-scout-agent-homegrown-reasoning-model) | Verified date |
| June 2, 2026 | Microsoft MAI-Code-1-Flash | Microsoft | Coding LLM | First Microsoft coding model; GitHub Copilot / VS Code integration; Build 2026 | [CNBC](https://www.cnbc.com/2026/06/02/microsoft-unveils-new-ai-models-lessen-reliance-on-openai-lower-costs.html) | Verified date |
| June 2, 2026 | Microsoft MAI-Image-2.5 / 2.5 Flash | Microsoft | Image generation | Text-to-image and editing; Build 2026 | [PCMag](https://www.pcmag.com/news/i-tested-all-4-of-microsofts-new-ai-models-heres-the-brutal-truth) | Verified date |
| June 2, 2026 | Microsoft MAI-Transcribe-1.5 | Microsoft | ASR/Speech | "5x faster than competing models"; Build 2026 | [The Verge](https://www.theverge.com/tech/941664/microsoft-ai-model-reasoning-mai-thinking-1-build-2026) | Verified date |
| June 2, 2026 | Microsoft MAI-Voice-2 | Microsoft | Voice | 15 new languages; Build 2026 | [The Verge](https://www.theverge.com/tech/941664/microsoft-ai-model-reasoning-mai-thinking-1-build-2026) | Verified date |
| June 3, 2026 | Google Gemma 4 12B | Google | Open-weight | 12B model for consumer laptops (16GB RAM); fills gap in Gemma 4 lineup | [Ars Technica](https://arstechnica.com/google/2026/06/googles-new-gemma-4-open-ai-model-is-sized-for-your-laptop/), [9to5Mac](https://9to5mac.com/2026/06/03/google-ai-edge-gallery-launches-to-macos-letting-mac-users-run-gemini-models-locally/) | Verified date |
| ~Early June 2026 (expanded access) | Anthropic Mythos (expanded preview) | Anthropic | Cybersecurity LLM | ~150 more orgs in 15+ countries added to Project Glasswing | [Engadget](https://www.engadget.com/2185709/anthropic-expands-its-claude-mythos-preview-to-more-partners/), [Politico June 7](https://www.politico.com/news/2026/06/07/frontier-ai-cybersecurity-china-race-00952786) | Verified period |
| ~Early June 2026 (expanded access) | OpenAI GPT-5.5 Cyber | OpenAI | Cybersecurity LLM | Expanded to EU banks, UK banks; comparable performance to Mythos per UK AI Security Institute | [BBC](https://www.bbc.com/news/articles/cm2p3j6lvn7o), [Politico June 7](https://www.politico.com/news/2026/06/07/frontier-ai-cybersecurity-china-race-00952786) | Verified period |

### Caveats for the Full Timeline
- GPT-5 / GPT-5.1 / GPT-5.5 exact launch dates were not found in searches; they are clearly in market by June 2026 but original announcement dates need verification.
- Claude Opus 4.7 / 4.8 exact launch dates not found; inferred to be 2026 from version numbering.
- Gemini 3 Pro exact launch date not found; referenced as current flagship in June 2026 articles.
- Gemma 4 main lineup launch pinned to May 2026 Google I/O by inference only; not directly confirmed.
- Google I/O 2026 exact date unconfirmed; all sources place it in May 2026.
- Nvidia GTC 2026 exact dates unconfirmed from searches; historically held in March.

---

## Recent Releases — Last 30 Days (as of ~June 8, 2026)

| Rank | Model | Lab | Announcement Date | Type | Key Notes | Source | Verified |
|------|-------|-----|-------------------|------|-----------|--------|----------|
| — | **Nvidia Nemotron 3 Ultra** | Nvidia | June 1, 2026 | Open-weight | 550B params (55B active MoE); largest US open-weight model; announced at Computex 2026 keynote; Nvidia working on Nemotron 4 via "Nemotron Coalition" (Mistral, Perplexity + 6 others) | [Decrypt](https://decrypt.co/369689/nvidia-open-ai-model-nemotron-3-ultra) | 2026-06-08 |
| — | **Nvidia Cosmos 3** | Nvidia | ~June 1–3, 2026 | Foundation (physical AI) | "Foundation model for physical AI"; trained on physics rather than text; announced at/around Computex 2026 | [Axios C-Suite, June 8](https://www.axios.com/2026/06/08/ai-news-nvidia-cosmos-3-openai-sites-solara-rtx-spark) | 2026-06-08 |
| — | **Microsoft MAI-Thinking-1** | Microsoft | June 2, 2026 | Reasoning LLM | 35B active params; first in-house reasoning model; "matches leading models on key SWE benchmarks"; cost-focused mid-tier; announced at Build 2026 | [The Verge](https://www.theverge.com/tech/941664/microsoft-ai-model-reasoning-mai-thinking-1-build-2026), [Axios](https://www.axios.com/2026/06/02/microsoft-debuts-scout-agent-homegrown-reasoning-model) | 2026-06-08 |
| — | **Microsoft MAI-Code-1-Flash** | Microsoft | June 2, 2026 | Coding LLM | First Microsoft coding model; integrated into GitHub Copilot and VS Code; inference-efficient | [CNBC](https://www.cnbc.com/2026/06/02/microsoft-unveils-new-ai-models-lessen-reliance-on-openai-lower-costs.html) | 2026-06-08 |
| — | **Microsoft MAI-Image-2.5 / 2.5 Flash** | Microsoft | June 2, 2026 | Image generation | Text-to-image and image editing; part of MAI model family | [PCMag](https://www.pcmag.com/news/i-tested-all-4-of-microsofts-new-ai-models-heres-the-brutal-truth) | 2026-06-08 |
| — | **Microsoft MAI-Transcribe-1.5** | Microsoft | June 2, 2026 | Speech/ASR | "5x faster than competing models" | [The Verge](https://www.theverge.com/tech/941664/microsoft-ai-model-reasoning-mai-thinking-1-build-2026) | 2026-06-08 |
| — | **Microsoft MAI-Voice-2** | Microsoft | June 2, 2026 | Voice | 15 new languages; flash variant "coming soon" | [The Verge](https://www.theverge.com/tech/941664/microsoft-ai-model-reasoning-mai-thinking-1-build-2026) | 2026-06-08 |
| — | **Google Gemma 4 12B** | Google | June 3, 2026 | Open-weight | Runs locally on 16GB RAM consumer laptops; fills gap in Gemma 4 lineup launched earlier in 2026; launched alongside AI Edge Gallery for macOS | [Ars Technica](https://arstechnica.com/google/2026/06/googles-new-gemma-4-open-ai-model-is-sized-for-your-laptop/), [9to5Mac](https://9to5mac.com/2026/06/03/google-ai-edge-gallery-launches-to-macos-letting-mac-users-run-gemini-models-locally/) | 2026-06-08 |
| — | **Google Gemini Spark** (agentic) | Google | May 2026 (Google I/O) | Agentic LLM | Announced at Google I/O 2026 (May); agentic AI system; being used to power new Apple Siri via Apple-Google partnership; exact I/O date unverified | [9to5Mac June 2](https://9to5mac.com/2026/06/02/google-delivering-on-gemini-promises-means-apple-intelligence-can-do-the-same/), [Axios June 2](https://www.axios.com/2026/06/02/microsoft-debuts-scout-agent-homegrown-reasoning-model) | 2026-06-08 |
| — | **Meta Muse Spark** | Meta | April 10, 2026 | Closed-source LLM | Advanced LLM released in April 2026; API still not available to developers as of early June; closed-source/proprietary | [CNET](https://www.cnet.com/tech/services-and-software/where-is-metas-ai-model-api/) | 2026-06-08 |
| — | **Anthropic Mythos** (preview) | Anthropic | ~Early 2026, expanded access ~June 2026 | Cybersecurity LLM | Highly capable cyberoffense model; restricted release via "Project Glasswing"; ~150 orgs in 15+ countries now testing; Anthropic pledged broader rollout "in coming weeks" | [Politico June 7](https://www.politico.com/news/2026/06/07/frontier-ai-cybersecurity-china-race-00952786), [Telecoms.com](https://www.telecoms.com/ai/anthropic-s-project-glasswing-expands-membership-extends-remit) | 2026-06-08 |
| — | **OpenAI GPT-5.5 Cyber** | OpenAI | ~Early 2026, expanded access ~June 2026 | Cybersecurity LLM | Cybersecurity variant of GPT-5.5; comparable to Anthropic's Mythos per UK AI Security Institute; opened to EU banks and others recently | [BBC](https://www.bbc.com/news/articles/cm2p3j6lvn7o), [Politico June 7](https://www.politico.com/news/2026/06/07/frontier-ai-cybersecurity-china-race-00952786) | 2026-06-08 |

### Notes / Caveats
- Google I/O 2026 exact date not pinned in search results; all sources refer to it as "last month" relative to early June 2026, placing it in May 2026.
- Nvidia Cosmos 3 announced at/around Computex June 1–3; exact date within that window unverified.
- Meta Muse Spark was announced April 10 (outside 30-day window) but API access still pending as of early June 2026.
- Anthropic Mythos and OpenAI GPT-5.5-Cyber: original announcement dates unclear; both remain in limited/controlled release.
- Microsoft announced 7 MAI models total at Build 2026; table covers the confirmed LLM/AI model entries.

---

## Speed & Latency — Frontier Models (as of ~June 2026)

> **Source: [Artificial Analysis LLM Leaderboard](https://artificialanalysis.ai/leaderboards/models)** — live, continuously measured, ~72-hour rolling window. Independent, same methodology across all models. Fetched ~June 9, 2026.
> **Methodology**: Output speed = tokens/s after first chunk received (streaming). Latency = time to first token (TTFT) in seconds. End-to-end = time to receive 500 tokens (includes thinking time for reasoning models). All via first-party API unless unavailable.

### ⚡ Fastest Output Speed (tokens/s, top models by speed)

| Rank | Model | Lab | Output Speed (t/s) | Latency TTFT (s) | E2E 500 tokens (s) | Intelligence Index | Price (blended $/1M) |
|------|-------|-----|--------------------|------------------|--------------------|-------------------|----------------------|
| 1 | **Mercury 2** | Inception Labs | **864** | 4.13 | 4.70 | 33 | $0.14 |
| 2 | **LFM2.5-VL-1.6B** | Liquid AI | **479** | 1.19 | 2.24 | 6 | $0.00 |
| 3 | **Granite 4.0 H Small** | IBM | **477** | 10.50 | 11.55 | 11 | $0.08 |
| 4 | **Step 3.7 Flash** | StepFun | **382** | 0.94 | 7.48 | 43 | $0.18 |
| 4 | **gpt-oss-120b (low)** | OpenAI | 350 | 0.92 | 8.05 | 24 | $0.20 |
| 5 | **Gemini 3.1 Flash-Lite** | Google | 333 | 6.12 | 7.62 | 34 | $0.22 |
| — | **Gemini 3.5 Flash** | Google | **183** | 35.03 | 37.77 | 55 | $1.31 |
| — | **Gemini 3.5 Flash (medium)** | Google | 198 | 28.19 | 30.71 | 55 | $1.31 |
| — | **Grok 4.3 (high)** | xAI | 181 | 14.70 | 17.46 | 53 | $0.64 |
| — | **GPT-5.4 mini (xhigh)** | OpenAI | 159 | 16.29 | 19.44 | 49 | $0.65 |
| — | **Gemini 3.1 Pro Preview** | Google | 140 | 41.27 | 44.85 | 57 | $1.74 |

> **Key insight on speed**: The fastest models are not the most intelligent ones. Mercury 2 (920 t/s) scores only 33/100 on intelligence; Gemini 3.5 Flash (183 t/s, score 55) is the highest-intelligence model in the fast tier. For frontier intelligence, Claude Opus 4.8 tops at only 60 t/s.

### ⏱️ Lowest Latency (TTFT — Time to First Token, frontier models)

| Rank | Model | Lab | TTFT (s) | Output Speed (t/s) | Intelligence | Notes |
|------|-------|-----|----------|--------------------|----|-------|
| 1 | **North Mini Code** | Cohere | **0.32** | 187 | 28 | NEW lowest-latency model (live fetch, current session) |
| 2 | **Command A+** | Cohere | **0.39** | 198 | 37 | Previously #1; still very low TTFT |
| 2 | **Qwen3.5 2B** (non-reasoning) | Alibaba | 0.37 | — | 15 | Tiny model; not frontier |
| 3 | **Qwen3.5 0.8B** (non-reasoning) | Alibaba | 0.40 | 100 | 10 | Smallest/cheapest |
| 4 | **NVIDIA Nemotron 3 Nano** | NVIDIA | ~0.42 | 95 | 13 | — |
| — | **GPT-5.5 (Non-reasoning)** | OpenAI | 1.02 | 57 | 41 | Best TTFT for frontier non-reasoning GPT |
| — | **Claude Opus 4.7 (Non-reasoning)** | Anthropic | **1.31** | 46 | 52 | Best TTFT for high-intelligence Anthropic model |
| — | **Nemotron 3 Ultra** | NVIDIA | 1.33 | 140 | 48 | Good TTFT for a 550B MoE model |
| — | **Claude Opus 4.8 (max)** | Anthropic | **21.61** | 60 | 61 | #1 intelligence but very high TTFT (reasoning) |
| — | **GPT-5.5 (xhigh)** | OpenAI | **95.22** | 63 | 60 | #2 intelligence; extremely high TTFT (deep reasoning) |
| — | **Kimi K2.6 (reasoning)** | Kimi | 2.25 | 44 | 54 | Best open-weight TTFT for high-intelligence model |
| — | **Qwen3.7 Max** | Alibaba | 2.66 | 111 | 57 | Best TTFT among intelligence-57 models; excellent value |

> **Key insight on latency**: There is a **stark tradeoff** between intelligence and TTFT. The two highest-intelligence models (Claude Opus 4.8 at 21.6s, GPT-5.5 xhigh at 95.2s) have extremely high TTFT due to extended reasoning ("thinking time"). For latency-sensitive apps, use non-reasoning variants: Claude Opus 4.7 Non-Reasoning (1.31s TTFT, 52 intelligence) or GPT-5.5 Non-Reasoning (1.02s TTFT, 41 intelligence).

### 🏆 Best Balance: Intelligence + Speed (high-intelligence models only, score ≥50)

| Model | Lab | Intelligence | Output Speed (t/s) | TTFT (s) | E2E 500t (s) | Price ($/1M blended) |
|-------|-----|-------------|---------------------|----------|--------------|----------------------|
| **Gemini 3.1 Pro Preview** | Google | **57** | **140** | 41.27 | 44.85 | $1.74 |
| **Gemini 3.5 Flash** | Google | **55** | **183** | 35.03 | 37.77 | $1.31 |
| **Gemini 3.5 Flash (medium)** | Google | **55** | **198** | 28.19 | 30.71 | $1.31 |
| **Qwen3.7 Max** | Alibaba | **57** | 111 | 2.66 | 28.83 | $1.43 |
| **Kimi K2.6 (reasoning)** | Kimi | **54** | 44 | 2.25 | 114.54 | $0.70 |
| **GPT-5.5 (medium)** | OpenAI | **57** | 57 | 10.23 | 19.02 | $4.35 |
| **Claude Opus 4.8 (max)** | Anthropic | **61** | 60 | 21.61 | 29.98 | $4.10 |
| **GPT-5.5 (xhigh)** | OpenAI | **60** | 63 | 95.22 | 103.17 | $4.35 |

> **Gemini 3.5 Flash (medium) is the best intelligence-per-second model** among high-intelligence options: 55 intelligence score, 198 t/s output speed, 28s TTFT, and only $1.31/1M blended.

### Use-Case TTFT Benchmarks — AIMultiple Independent Test
*Published: Jan 22, 2026 | Source: [AIMultiple LLM Latency Benchmark](https://aimultiple.com/llm-latency-benchmark) | 5 models × 5 use cases × 100 questions each | ⚠️ Snapshot from Jan 2026; models/providers may have changed*

| Model | Q&A TTFT | Summary TTFT | Translation TTFT | Business TTFT | Coding TTFT | Per-Token Latency | Notes |
|-------|----------|-------------|-----------------|--------------|------------|-------------------|-------|
| **Mistral Large 2512** | **0.30s** | 0.45s | 0.40s | 0.40s | **0.30s** | 0.020–0.040s | Fastest TTFT overall |
| **GPT-5.2** | 0.60s | 0.60s | 0.55s | 0.50s | 0.50s | **0.010–0.020s** | Best per-token latency |
| Claude 4.5 Sonnet | 2.0s | 2.0s | 2.0s | 2.0s | 2.0s | 0.028–0.035s | Moderate, consistent |
| **Grok 4.1 Fast Reasoning** | 3.0s | 4.0s | 6.0s | 4.0s | **11.0s** | **0.005–0.010s** | Worst TTFT; best per-token for batch |
| DeepSeek V3.2 | 7.0s | 7.5s | 7.5s | 8.0s | **19.0s** | 0.025–0.032s | Slowest overall |

**Key finding**: Reasoning models (Grok 4.1 Fast Reasoning, DeepSeek V3.2) have dramatically worse TTFT for interactive use but can be highly efficient for batch/long-output tasks due to fast per-token generation once started.

### Validity Caveats
1. **Artificial Analysis**: Independent, continuous (72-hour rolling), standardized across all providers. Most reliable for apples-to-apples speed/latency comparison. Does NOT include reasoning pre-thinking time in TTFT for most models — for reasoning models, TTFT includes first reasoning token. End-to-end (E2E) metric is more meaningful for reasoning models.
2. **AIMultiple**: Published Jan 22, 2026 — ~5 months old by June 2026. Models/provider performance changes frequently. Use directionally but verify current values on Artificial Analysis.
3. **Vellum**: Updated May 29, 2026; provider-reported; covers fewer models but includes pricing. Secondary corroborating source.
4. **Key distortion — reasoning models**: GPT-5.5 (xhigh) TTFT of 95s and Claude Opus 4.8 TTFT of 21s are NOT just "slow APIs" — they're spending that time doing extended chain-of-thought reasoning. For non-reasoning variants, TTFT drops dramatically (GPT-5.5 non-reasoning: 1.02s).

---

 — Top Models (as of June 2026)

> **About SWE-bench Verified**: 500 human-validated real GitHub issues (Python repos). Models must produce a code patch that passes the existing tests. The de facto standard coding-agent benchmark. **Caveat**: scores vary significantly by harness; always check methodology. llm-stats.com scores are **self-reported** (92 models, all self-reported as of June 2026). vals.ai scores use a **standardized, independent** bash-only mini-swe-agent harness — more apples-to-apples. SWE-bench Verified is showing **saturation risk** at the top: frontier models cluster 78–89%, and SWE-bench Pro (harder, contamination-resistant) shows top scores ~23–59% — a stark reminder that high Verified scores may not reflect true generalization.

### vals.ai — Independent Standardized Harness
*Updated: **June 13, 2026** | Source: [vals.ai/benchmarks/swebench](https://vals.ai/benchmarks/swebench) | Harness: mini-swe-agent (bash-only), same config for all models | Live-verified 2026-06-22*

| Rank | Model | Lab | Score | ±CI | Cost/Test | Latency | Verified |
|------|-------|-----|-------|-----|-----------|---------|---------|
| **1** | **Claude Fable 5** | Anthropic | **95.00%** | ±0.98 | $2.05 | 356s | **2026-06-09** |
| 2 | Claude Opus 4.8 | Anthropic | 88.60% | ±1.42 | $1.92 | 567s | 2026-06-04 |
| 3 | GPT-5.5 | OpenAI | 82.60% | ±1.70 | $1.36 | 426s | 2026-06-04 |
| 4 | Claude Opus 4.7 | Anthropic | 82.00% | ±1.72 | $2.42 | 442s | 2026-06-04 |
| 5 | Gemini 3.5 Flash | Google | 78.80% | ±1.83 | $0.95 | 254s | 2026-06-04 |
| 5 | Gemini 3.1 Pro Preview (02/26) | Google | 78.80% | ±1.83 | $0.78 | 312s | 2026-06-04 |
| 7 | GPT-5.4 (xhigh) | OpenAI | 78.20% | ±1.85 | $0.80 | 307s | 2026-06-04 |
| 7 | Claude Opus 4.6 (Thinking) | Anthropic | 78.20% | ±1.85 | $1.22 | 351s | 2026-06-04 |
| **9** | **Kimi K2.7 Code** | **Moonshot AI** | **78.20%** | ±1.85 | **$0.27** | 897s | **2026-06-13 (NEW)** |
| 10 | GPT-5.3 Codex | OpenAI | 78.00% | ±1.85 | $0.46 | 247s | 2026-06-04 |
| 11 | Claude Sonnet 4.6 | Anthropic | 77.40% | ±1.87 | $1.30 | 512s | 2026-06-04 |
| 11 | DeepSeek V4 | DeepSeek | 77.40% | ±1.87 | $0.44 | 635s | 2026-06-04 |

**Key note**: Claude Fable 5 jumped from "self-reported 80.3% on SWE-bench *Pro*" to **95.0% on SWE-bench *Verified* (independent)** — these are different benchmarks. The 95% is on the easier Verified split; the 80.3% was the Pro split claim. Both are now verified via independent harness (vals.ai) for Verified only.

**NEW (June 13, 2026)**: Kimi K2.7 Code (Moonshot AI) entered at rank 9 with 78.20% at only **$0.27/test** — making it the cheapest way to get into the 78%+ tier by a wide margin (vs. $0.44 for DeepSeek V4 at 77.4%, $0.46 for GPT-5.3 Codex at 78.0%).

**Fable 5 by task difficulty (vals.ai):**
- <15 min tasks: 96% | 15m–1h: 95% | 1–4 hr: 93% | >4 hr: 100%
- Notably, Fable 5 is the ONLY model that substantially improves on the hardest multi-hour tasks vs. the rest of the pack.

**Budget pick (vals.ai):** GPT-5.3 Codex at 78.0% for $0.46/test; DeepSeek V4 at 77.4% for $0.44/test; Gemini 3.5 Flash at 78.8% for $0.95/test.

### BenchLM.ai — Broader Coverage (Self-Reported, 49 models)
*Updated: June 2, 2026 | Source: [benchlm.ai/benchmarks/sweVerified](https://benchlm.ai/benchmarks/sweVerified) | ⚠️ All entries are self-reported; harnesses vary*

| Rank | Model | Lab | Score | Notes |
|------|-------|-----|-------|-------|
| 1 | **Claude Mythos Preview** | Anthropic | **93.9%** | Restricted cybersecurity model; self-reported; harness unverified |
| 2 | Claude Opus 4.8 | Anthropic | 88.6% | Consistent with vals.ai |
| 3 | Claude Opus 4.7 (Adaptive) | Anthropic | 87.6% | Slightly higher than vals.ai (82.0%) — harness difference |
| 4 | GPT-5.3 Codex | OpenAI | 85.0% | Higher than vals.ai (78.0%) — harness difference |
| 5 | Claude Opus 4.5 | Anthropic | 80.9% | — |
| 6 | Claude Opus 4.6 | Anthropic | 80.8% | — |
| 7 | **DeepSeek V4 Pro (Max)** | DeepSeek | **80.6%** | Top open-weight model |
| 8 | MiniMax M3 | MiniMax | 80.5% | Open-weight |
| 9 | Qwen3.7 Max | Alibaba | 80.4% | — |
| 10 | Kimi K2.6 | Moonshot AI | 80.2% | Open-weight |
| 11 | GPT-5.2 | OpenAI | 80.0% | — |
| 12 | Claude Sonnet 4.6 | Anthropic | 79.6% | — |
| 19 | Mistral Medium 3.5 128B | Mistral | 77.6% | Open-weight |
| 25 | Grok 4.20 | xAI | 76.7% | — |
| 40 | Grok Code Fast 1 | xAI | 70.8% | — |
| 43 | Gemini 2.5 Pro | Google | 63.8% | Older gen model |
| 44 | GPT-4.1 | OpenAI | 54.6% | — |
| 49 | GPT-4.1 mini | OpenAI | 23.6% | — |

**Best open-weight (BenchLM):** DeepSeek V4 Pro (Max) at 80.6%; MiniMax M3 80.5%; Kimi K2.6 80.2%; Qwen3.6-27B 77.2%.

### SWE-bench Pro (Public) — Harder, Contamination-Resistant
*Source: [labs.scale.com/leaderboard/swe_bench_pro_public](https://labs.scale.com/leaderboard/swe_bench_pro_public) | Scale AI | Date: ~2026 (exact update date not published) | Harness: SWE-Agent + mini-swe-agent*

> Top Verified models score ~70–89%; same models score **23–59%** on Pro. Massive gap demonstrates Verified saturation / contamination risk.

| Rank | Model | Lab | Score (Public) | Notes |
|------|-------|-----|----------------|-------|
| 1 | **GPT-5.4 (xHigh)** | OpenAI | **59.1%** ±3.56 | — |
| 1 | **Muse Spark** | Meta | **55.0%** ±3.60 | NEW |
| 2 | Claude Opus 4.6 (Thinking) | Anthropic | 51.9% ±3.61 | — |
| 3 | Gemini 3.1 Pro (Thinking) | Google | 46.1% ±3.60 | — |
| 3 | Claude Opus 4.5 | Anthropic | 45.9% ±3.60 | — |
| 4 | Claude Sonnet 4.5 | Anthropic | 43.6% ±3.60 | — |
| 4 | Gemini 3 Pro Preview | Google | 43.3% ±3.60 | — |
| 4 | GPT-5 (High) | OpenAI | 41.8% ±3.49 | — |
| — | GPT-4o | OpenAI | 4.9% | Much older model; shows benchmark difficulty jump |

**Private dataset (harder — unseen codebases):** Top scores drop further: best models ~17–23%.

### SWE-bench Verified: Key Validity Caveats
1. **Harness sensitivity**: The same model can score 82% (vals.ai standardized) or 87.6% (self-reported) depending on scaffolding. Never compare scores across sources without checking the harness.
2. **Self-reported vs independent**: llm-stats.com tracks 92 models — all self-reported. vals.ai is independent (same harness for all). For rankings, prefer vals.ai.
3. **Saturation**: Verified is showing ceiling effects at the top tier. SWE-bench Pro's ~23% scores for models claiming 70–89% on Verified are a strong indicator of benchmark gaming/contamination.
4. **Claude Mythos 93.9%**: Restricted cybersecurity model; self-reported only; harness unknown; treat as unverified headline.

---

## Key Developments — Week of June 2–8, 2026

| Date | Event | Who | Key Notes | Source |
|------|-------|-----|-----------|--------|
| June 2, 2026 | **Trump AI Executive Order signed** | US Government | Voluntary 30-day pre-release review of "covered frontier models"; establishes AI cybersecurity clearinghouse (Treasury); not mandatory; previous draft had 90-day window, cut after industry pushback | [TechCrunch](https://techcrunch.com/2026/06/02/trump-signs-narrower-executive-order-on-ai-oversight-after-industry-objections/), [The Guardian](https://www.theguardian.com/us-news/2026/jun/02/trump-executive-order-ai-voluntary-review) |
| June 2, 2026 | **OpenAI Codex expansion** — Sites feature + 6 business plugins | OpenAI | "Sites" = create/host/deploy work web apps from prompts; 6 new enterprise agent plugins; Codex coming to ChatGPT app everywhere "in next few weeks"; 5M+ weekly active Codex users (6x since February) | [TechCrunch](https://techcrunch.com/2026/06/02/openai-launches-new-codex-tools-for-white-collar-work/), [9to5Mac](https://9to5mac.com/2026/06/02/openai-putting-codex-inside-chatgpt-app-everywhere-releasing-6-business-plugins/) |
| June 4, 2026 | **Anthropic "When AI Builds Itself" blog post** — recursive self-improvement warning | Anthropic | Claimed Claude near threshold of recursive self-improvement; urged global "temporary pause" option; Claude writes ~80% of Anthropic's production code; April 2026 agents completed open-ended AI safety research autonomously; Anthropic to convene policymakers | [The Guardian](https://www.theguardian.com/technology/2026/jun/05/anthropic-urges-temporary-pause-on-ai-development-to-discuss-risks), [Axios](https://www.axios.com/2026/06/04/anthropic-warns-ai-build-successors), [Scientific American](https://www.scientificamerican.com/article/anthropic-warns-ai-may-soon-begin-recursive-self-improvement/) |
| June 5, 2026 | **OpenAI confirms EO compliance** | OpenAI | OpenAI head of countries confirmed to CNBC it will sign up to Trump's voluntary 30-day pre-release model review order | [CNBC](https://www.cnbc.com/2026/06/05/openai-trump-ai-model-review-order.html) |
| June 5, 2026 | **OpenAI ChatGPT security features** | OpenAI | "Lockdown Mode" (blocks prompt-injection data exfiltration) and "Active Sessions" (session review) made broadly available | [SecurityWeek](https://www.securityweek.com/openai-rolling-out-chatgpt-account-security-controls/) |
| June 8, 2026 | **Apple WWDC 2026** — Gemini-powered Siri + iOS 27 / macOS 27 | Apple / Google | iOS 27 announced; Siri overhauled with Google Gemini backend (custom model co-built with Google); standalone Siri app; new Apple Intelligence features; outgoing CEO's last WWDC (successor takes reins in September) — post-keynote specifics not yet confirmed in searches | [Bloomberg](https://www.bloomberg.com/news/articles/2026-06-05/wwdc-2026-preview-ios-27-siri-ai-features-macos-27-more-apple-will-announce), [Gizmodo live](https://gizmodo.com/live-updates-from-apple-wwdc-2026-2000765748), [Newsweek](https://www.newsweek.com/wwdc-2026-everything-apple-is-expected-to-announce-on-june-8-12016937) |

---

## AI Lab Funding & Org News (as of June 2026)

### Coding-model leadership snapshot (verified July 2026)
- Current best default for coding+agentic work is **GPT-5.6 Sol**, because current independent/near-independent leaderboards show it ahead on SWE-bench Verified and especially Terminal-Bench / agentic CLI work. However, **Claude Fable 5** remains the stronger raw code-editing / patching model when you prioritize maximal SWE-bench-style patch quality over terminal autonomy. On SWE-bench Pro, Fable 5 still leads the cited comparison pages, while GPT-5.6 Sol is stronger on Terminal-Bench 2.0 and related agentic tasks. Sources: https://vals.ai/benchmarks/swebench, https://benchlm.ai/compare/claude-fable-vs-gpt-5-6-sol, https://benchlm.ai/compare/chatgpt-vs-claude.


*Verified 2026-06-10 | Sources: Forbes, CNBC, NYT, TechCrunch, Bloomberg*

| Date | Entity | Event | Key Numbers | Source |
|------|--------|-------|-------------|--------|
| ~Late 2025 | **SpaceX acquires xAI** | Musk merged his AI lab into SpaceX | SpaceX pre-IPO valuation ~$1.5T at time of deal (per Yahoo Finance); xAI debt partly to be covered by IPO proceeds | [TechCrunch](https://techcrunch.com/2026/06/01/spacex-says-it-may-issue-significant-equity-in-future-transactions/), [Yahoo Finance](https://finance.yahoo.com/markets/article/spacex-valued-at-just-780-billion-by-morningstar-less-than-half-its-ipo-target-174617034.html) |
| ~Late 2025/early 2026 | **Microsoft contractual freedom from OpenAI** | OpenAI contract changed ~6 months before Build 2026 (June 2); Microsoft now formally free to build its own frontier/superintelligence models, not just resell OpenAI | Microsoft invested $13B+ cumulatively in OpenAI | [VentureBeat](https://venturebeat.com/technology/microsoft-ai-chief-says-company-was-set-free-from-openai-to-pursue-superintelligence) |
| ~Late May 2026 | **Anthropic → SpaceX compute deal** | Anthropic agreed to rent compute from xAI's Colossus data center | $1.25B/month through 2029 (~110K Nvidia GPUs) | [TechCrunch](https://techcrunch.com/2026/06/05/google-will-pay-spacex-920m-per-month-for-compute/) |
| May 13, 2026 | **Recursive Superintelligence** (new lab, emerged from stealth) | Ex-Meta FAIR director co-founded startup focused on recursive self-improvement AI | $650M raised; $4.65B valuation; <30 employees; backed by Alphabet Ventures + 2 chipmakers | [TechTimes](https://www.techtimes.com/articles/317947/20260607/self-improving-ai-draws-650-million-ex-meta-scientist-tian-bets-models-build-models.htm) |
| May 2026 | **Anthropic** funding round | Late-stage private raise | $65B raised at $965B valuation; briefly overtook OpenAI in paper value | [Forbes](https://www.forbes.com/sites/paulocarvao/2026/06/04/making-sense-of-the-ai-ipo-tsunami-heading-for-wall-street/) |
| March 2026 | **OpenAI** funding round | Largest private financing ever assembled | ~$122B raised at $852B valuation | [Forbes](https://www.forbes.com/sites/paulocarvao/2026/06/04/making-sense-of-the-ai-ipo-tsunami-heading-for-wall-street/) |
| June 1, 2026 | **Anthropic IPO filing** | Confidential IPO filing with SEC | Valuation ~$965B; "once-in-a-generation" Wall Street moment per NYT | [The Guardian](https://www.theguardian.com/technology/2026/jun/03/as-the-tech-mega-ipo-race-hots-up-has-openai-missed-its-moment) |
| June 3, 2026 | **DeepSeek** maiden funding round | First-ever external fundraise for Chinese AI lab | ~$7.4B (50B yuan); valuation $52–59B; investors: Tencent (10B CNY), CATL (5B CNY), founder Liang Wenfeng (20B CNY own money) | [CNBC](https://www.cnbc.com/2026/06/03/deepseek-slated-to-draw-7-billion-in-maiden-fundraising-sources-say.html) |
| June 3–5, 2026 | **SpaceX IPO filing & roadshow** | Filed S-1; fixed price $135/share; targeting $1.75T valuation; raising ~$75B (largest IPO in history if completed) | Musk owns 42% common + 350M options (~$688B at IPO price); expected Nasdaq debut June 12, 2026 | [CNBC](https://www.cnbc.com/2026/06/03/spacex-ipo-stock-price-roadshow-musk.html), [Forbes](https://www.forbes.com/sites/antoniopequenoiv/2026/06/03/spacex-targets-75-billion-for-ipo-valuing-company-above-175-trillion/) |
| June 4, 2026 | **Generalist AI** (robotics) funding | New round led by Radical Ventures | $400M raised; $2B valuation; Nvidia-backed | [Bloomberg](https://www.bloomberg.com/news/articles/2026-06-04/nvidia-backed-robotics-startup-generalist-ai-valued-at-2-billion) |
| June 4, 2026 | **Cognition AI** (Devin, agents) | Late-stage valuation reported | $26B valuation; ~$490M revenue run rate | [Forbes](https://www.forbes.com/sites/rashishrivastava/2026/06/05/ai-coding-startup-lovable-in-talks-to-raise-funding-at-a-12-billion-valuation/) |
| June 5, 2026 | **SpaceX → Google compute deal** | Google signs compute contract with SpaceX/xAI | $920M/month (Oct 2026–June 2029); ~110K Nvidia GPUs; helps Google meet AI model demand | [NYT](https://www.nytimes.com/2026/06/05/technology/spacex-google-deal.html), [TechCrunch](https://techcrunch.com/2026/06/05/google-will-pay-spacex-920m-per-month-for-compute/) |
| June 5, 2026 | **Lovable** (vibe coding) fundraise talks | Swedish AI coding startup in talks for new round | Targeting $12B valuation; $400M ARR (Feb 2026); fastest SaaS startup to $100M ARR (8 months) | [Forbes](https://www.forbes.com/sites/rashishrivastava/2026/06/05/ai-coding-startup-lovable-in-talks-to-raise-funding-at-a-12-billion-valuation/) |
| ~June 2026 (pre-IPO) | **SpaceX option to acquire Cursor** | SpaceX secured option to buy Anysphere/Cursor post-IPO | $60B in stock; Cursor valued ~$9B separately; expected to hit $1B ARR before year end | [TechCrunch](https://techcrunch.com/2026/06/01/spacex-says-it-may-issue-significant-equity-in-future-transactions/), [Forbes](https://www.forbes.com/sites/rashishrivastava/2026/06/05/ai-coding-startup-lovable-in-talks-to-raise-funding-at-a-12-billion-valuation/) |
| ~Mid-2026 (cumulative) | **Mistral** (European AI) funding status | Ongoing private | $3B total raised; €11.7B valuation; $400M ARR; $1B ARR target end-2026 | [Klover.ai](https://www.klover.ai/is_ai_profitable_mistrals_path_toward_profit_analysis_2026/) |

### Notable Context
- **Oracle** sold $18B of bonds in one day to help fund Stargate (OpenAI + Oracle + SoftBank $500B program). 
- **Morningstar** initiated SpaceX coverage at $780B fair value — less than half the $1.75T IPO target — flagging significant overvaluation risk.
- **OpenAI IPO**: Still pending; Guardian (June 3) asks if it has "missed its moment" as Anthropic and SpaceX race ahead. No confirmed filing date as of June 9, 2026.
- **Q1 2026 global VC** hit $330.9B total — AI companies took a large share (Stanford HAI / PitchBook).
- **Structural risk**: CNBC (June 5) notes "model routing" (matching tasks to cheapest adequate model) is a structural business threat to OpenAI/Anthropic premium pricing.
