---
name: ambient-analyst-continuous-learning
description: The meta-routine for improving across sessions — what to capture into /memory after each research task so the agent compounds knowledge instead of restarting. Use at the end of any research task, or when the user gives feedback or corrects you.
---

# Continuous Learning

Your memory persists to the LangSmith Context Hub, so what you write down today is in your context next session. This skill is the discipline that turns each task into durable improvement instead of throwaway work.

## The two memory surfaces

- `/memories/agent/scorecard.md` — **facts about models** (rankings, scores, sources, dates). Maintained per the `ambient-analyst-scorecard-maintenance` skill.
- `/memories/agent/AGENTS.md` — **everything else durable**: standing learnings, user preferences, reliable sources, methodology refinements, and open questions to revisit.

Both are loaded into your context every run. Keep them concise and high-signal — they cost context budget, so prune noise.

## The end-of-task routine

After any meaningful research task, before you finish, ask:

1. **Did I learn a durable fact about a model?** → update `/memories/agent/scorecard.md` (ambient-analyst-scorecard-maintenance skill).
2. **Did I find a reliable (or unreliable) source?** → note it in `AGENTS.md`under "Trusted sources" / "Sources to distrust", with why.
3. **Did the user state a preference or correct me?** → record it in `AGENTS.md`under "User preferences" / "Learnings". Capture the *principle*, not just the one-off fix (e.g. "user wants cost included in every model comparison").
4. **Did I hit a methodology improvement?** → note it (e.g. "LiveCodeBench is more reliable than HumanEval for recency"). Consider whether it belongs in a skill rather than memory (see below).
5. **What's still open or stale?** → add to an "Open questions / to re-verify" list with dates, so future-you knows what to chase.

## AGENTS.md structure (keep these sections)

```markdown
# LLM Research Agent — Memory

## Role & standing context
<who I am, what I optimize for>

## User preferences
- <preference> (learned YYYY-MM-DD)

## Learnings (methodology & domain)
- <durable insight> (YYYY-MM-DD, source if applicable)

## Trusted sources
- <source> — why reliable

## Sources to distrust / handle with care
- <source> — why

## Open questions / to re-verify
- [ ] <thing> (since YYYY-MM-DD)
```

## Memory hygiene

- **Update promptly**, in the same turn, once you have enough context to record something accurately — don't defer it to "later".
- **Capture the why**, not just the what. Encode corrections as reusable principles.
- **Date entries** so freshness is auditable.
- **Revise, don't pile up.** When a learning is superseded, edit it and note the change rather than leaving contradictory entries.
- **Never store secrets.** No API keys, tokens, or credentials in memory, ever.
- **Don't store transient junk.** One-off task details, small talk, or this-session-only context don't belong in memory.

## Skills vs memory

- A **reusable workflow** (a repeatable "how to do X") belongs in a **skill**, not memory. If you find yourself re-deriving a procedure, consider proposing a new skill or refining an existing one (skills live under `/skills/`).
- A **fact, preference, or source** belongs in **memory**.

## Close the loop

End your answer by stating what you persisted (scorecard rows, AGENTS.md entries) and what you deliberately did not save and why, so the user can see your memory is being curated, not hoarded.
