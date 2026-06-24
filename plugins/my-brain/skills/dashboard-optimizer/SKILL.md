---
name: dashboard-optimizer
description: Nightly (04:00–06:00) self-improvement loop for the my-brain platform. Applies learnings from the AI feed + research logs to refine the dashboard UI, validates every change with automated UI tests, enriches the second brain, and safely restarts the server. Runs with the ULTRACODE hybrid doctrine.
when_to_use: Scheduled nightly, or on demand when the dashboard needs a reviewed, tested refinement pass.
---

# dashboard-optimizer (prescriptive)

> Goal: every night, make the my-brain platform measurably better — informed by what the research
> loops learned — **without ever shipping a broken dashboard**. Nothing is "done" until it is
> validated and the server is healthy.

Brain root: `/Users/Souman_Trivedi/claude-projects/my-brain`
Doctrine: read `doctrine/ultracode.md` first and apply it literally.

## ULTRACODE hybrid execution (mandatory)

Run these strategies together, not in isolation:
1. **Classify-and-act** — read the inputs (below), bucket candidate improvements into
   {bug, UX, perf, new-insight, docs} and rank by value × safety. Drop low-value churn.
2. **Tournament** — for any non-trivial UI change, draft 2–3 alternative implementations and pick the
   best against the rubric in `sub-skills/refine-ui.md`.
3. **Fan-out** — use sub-agents to work independent slices in parallel (one per area: overview,
   brain graph, sessions, feed, topology), each returning a small diff + summary.
4. **Adversarial** — a separate validation pass (`sub-skills/validate-ui.md`) tries to break every
   change. A change that fails validation is reverted, not shipped.
5. **Loop-until-done** — iterate refine → validate → fix until the Definition of Done passes.

## Inputs (read every run)
- `knowledge/ai-feed/` (latest daily + weekly digests) — new capabilities/patterns worth adopting.
- `knowledge/best-practices/` — durable how-to learnings.
- `logs/research-log.md` and `logs/optimizer-log.md` — what changed before; avoid repeating.
- The live API: `http://127.0.0.1:7717/api/health|overview|sessions` — current real state.

## Procedure (run the three sub-skills in order)
1. **`sub-skills/refine-ui.md`** — choose & apply at most 1–3 high-value, low-risk improvements to
   `dashboard/index.html` (and `platform/serve.py` only if needed). Prefer small, reversible diffs.
2. **`sub-skills/validate-ui.md`** — MANDATORY gate. Compile checks + run the server against a
   synthetic fixture + probe every endpoint + (if available) screenshot the dashboard and read it
   back. Revert anything that fails.
3. **`sub-skills/enrich-brain.md`** — distil the night's notable feed/best-practice items into the
   brain, and update the AI-feed relationship graph data.

## Safe restart
If `serve.py` changed and all validations passed:
`bash /Users/Souman_Trivedi/claude-projects/my-brain/platform/install-service.sh` (frees the port + reloads).
`index.html` changes need no restart (served fresh).

## Definition of Done
```
[ ] Improvements classified & the 1–3 best applied (tournament-selected)
[ ] validate-ui.md passed: py_compile + node --check + endpoint probes all green
[ ] No regression: /api/health version present, /api/overview has tokens+provenance
[ ] Brain enriched; optimizer-log.md appended with what changed + why + validation result
[ ] If serve.py changed → server restarted & /api/health 200
```

## Logging
Append one entry per run to `logs/optimizer-log.md`:
`<DATE> — applied: <list> · reverted: <list> · validation: PASS/FAIL · server: <version>`
