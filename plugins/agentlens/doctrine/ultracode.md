# ⚡ The ULTRACODE Doctrine

> The standing operating procedure for **every** Claude, Claude Code, and Claude Cowork session
> on this machine. The default is not "do the task" — it is "attack the task with multiple
> strategies in parallel until it is verifiably done."

## Core principle

Never solve important work with a single linear pass. Always combine **two or more** of the
strategies below, run them as **parallel workflows**, and **loop until done** with adversarial
verification. Prefer breadth (many agents exploring) early, depth (one agent committing) late.

## The five strategies

1. **Fan-out** — Decompose the task and dispatch multiple sub-agents in parallel, each owning a
   slice (a file area, a hypothesis, a source set). Sub-agents write results to disk and return
   short summaries, not raw dumps. Use for discovery, inventory, multi-file edits, research.

2. **Classify-and-act** — First triage: classify each item/finding into buckets
   (e.g. trivial / risky / needs-research / out-of-scope) and route each bucket to the right
   handler. Avoids treating everything with the same heavyweight process.

3. **Adversarial** — Pair every "builder" pass with a "red-team" pass: a separate agent (or a
   fresh-context review) tries to break the result — find bugs, missing cases, security issues,
   weak sources, hallucinated claims. Nothing is "done" until it survives the adversary.

4. **Loop-until-done** — Define an explicit, checkable Definition of Done up front. Iterate
   build → verify → fix until every criterion passes. Track progress on a task list. Do not stop
   at "probably fine."

5. **Tournament** — When quality matters and the path is uncertain, generate N candidate
   solutions (in parallel, with varied approaches/prompts), score them against rubric +
   adversarial checks, and advance the winner (optionally bracketed over several rounds).

## Hybrid playbooks (always pick ≥2)

| Work type | Recommended hybrid |
|-----------|--------------------|
| Research / "latest in AI" | Fan-out (sources) → Classify-and-act (signal vs noise) → Adversarial (verify claims, cite) → Loop |
| Build a feature/dashboard | Tournament (designs) → Loop-until-done (impl) → Adversarial (review/test) |
| Refactor / cleanup | Classify-and-act (risk-tier files) → Fan-out (parallel edits) → Adversarial (tests) → Loop |
| Incident / debugging | Fan-out (hypotheses) → Tournament (fixes) → Adversarial (reproduce) → Loop |
| Knowledge enrichment | Fan-out (collect) → Classify-and-act (file vs discard) → Loop (consolidate) |

## Operating defaults

- **Parallelism**: launch independent sub-agents/tool calls in the same batch; never serialize
  work that has no dependency.
- **Permissions**: sessions run in **bypass-permissions mode** for autonomy (see the security
  note in `config/claude-code/APPLY.md` — this trades safety prompts for speed; only enable on
  trusted machines/repos).
- **Verification is mandatory**: every non-trivial task ends with an adversarial/verification
  step (tests, fact-checks, diffs, screenshots).
- **Write-through to the brain**: durable findings are written into `AgentLens/` so the next
  session and the dashboard inherit them.
- **Status cadence**: track work on a task list; surface a concise outcome, not a play-by-play.

## Definition of Done (template)

```
[ ] All acceptance criteria enumerated and checked
[ ] Adversarial pass run; issues found are fixed or logged
[ ] Sources cited / tests green / diff reviewed
[ ] Durable knowledge written back to AgentLens/
[ ] Task list updated; concise summary delivered
```
