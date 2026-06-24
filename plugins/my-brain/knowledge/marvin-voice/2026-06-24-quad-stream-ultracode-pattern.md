# Quad-stream ultracode pattern — proven on Marvin voice path 2026-06-24

## What it is

A reusable shape for shipping N related-but-distinct code changes in a single coherent PR landing, without N parallel branches stomping on each other and without an N-PR review chain. Each "stream" runs the full ultracode hybrid (fanout → adversary → loop-until-dry → implement) in its own git worktree; an integrator merges them all into one unified branch with `# stream-X:` provenance markers preserved through every conflict resolution.

Operational artefacts:
- The skill: `~/.claude/skills/ultracode-quad-stream/SKILL.md`
- The reference landing: PR #923 / `d612a53c` on `marvin-surface` — four streams shipped together (URL doc reader, doc Q&A, voice sanitiser, Slack transcript) as 4,207 lines across 15 files, 483 tests green

## Why this pattern

Three problems it solves at once:

1. **Shared-file collisions** when multiple semi-independent changes need to touch the same file (`validator/tools.py` had additions from all four streams). With one-PR-per-stream, the last to land eats a rebase fight. With this pattern, streams write to disjoint regions tagged with markers, integrator does the three-way merge once with all four in mind.

2. **Cross-stream wiring** where Stream B reads what Stream A writes (a cache, a callable). Hard to design with N separate PRs because A might land with no callers, B might land referencing a non-existent symbol. In this pattern, B's prompt knows A's coordination-point name; integrator verifies both halves exist.

3. **Honest residual-risk surface.** Each stream's "I cut a corner here" notes accumulate in the integrator's `residual_risks` list and become PR description bullets. Not buried in commit messages.

## When NOT to use this pattern

- Only 1 work item: plain ultracode workflow.
- 2 work items: borderline — use this if shared files exist, plain workflow if not.
- 5+ work items: integrator conflict surface grows quadratically with stream count. Re-decompose.
- Streams don't touch any shared files at all: you don't need an integrator; just N separate PRs.

## The 5 design rules that made it work

1. **File ownership boundary per stream.** Before launching, list which files each stream owns end-to-end and which are shared. Stream prompts include this verbatim. If you can't write the table, the decomposition is wrong.

2. **`# stream-X: BEGIN/END` markers on every additive edit to a shared file.** The integrator's job becomes "preserve all marker blocks across merge conflicts" — a mechanical rule rather than a judgement call.

3. **Coordination-point naming.** Stream A's prompt explicitly names the cache/callable it produces; Stream B's prompt explicitly names what it consumes. Match the names. Integrator verifies both sides exist post-merge.

4. **Integrator runs the stream's own venv pytest, not the host repo's venv.** Host venv `PATH` leakage masks `src/` imports via stale installs of the same package. The 2026-06-24 landing hit this — host venv had a stale `agents.teams_call.validator` shadowing the new `url_reader` until we used the worktree's `.venv/bin/pytest`.

5. **Marker-count audit in the integrator's verification field.** Count markers per shared file after merge (e.g. "tools.py=21 markers across 4 streams"). If a stream's marker count drops to zero in a shared file, intent was lost — abort merge and re-do.

## What it costs

- ~10 agents per stream + integrator agents = ~45 agents for a 4-stream run
- Wall clock: 25-45 min for 4 streams on this size repo
- Token cost: ~3.5-4M subagent tokens for a 4-stream run with full test sweeps

These costs only make sense when shipping >1 work item simultaneously AND when the streams share files.

## The honest residual-risk pattern

The integrator's output included this section verbatim — copy-paste into the PR description:

```
1. Cross-stream cache wiring is one-way: ...
2. Stream C's TTS-safety filter NOT applied to Slack: ...
3. Removed tests/__init__.py to fix pytest collection: ...
4. _build_tool_context now caches per-call ToolContext: ...
5. BRIDGE GAP: chat-message handler is dead-but-safe until bridge subscribes: ...
6. Stream D introduces 3 env vars; deployer overlay update is follow-up: ...
7. Stream D privacy: transcripts post to channel by default ...
8. SSRF guard DNS is sync; wrap in asyncio.wait_for if sinkhole stalls appear ...
```

Every item is a thing the integrator chose not to fix (correctly) and is leaving for follow-up. Surfacing them in the PR description means the next reviewer sees them, not the next debugger at 2am.

## What to copy when reusing the pattern

The `runStream(id, worktree, focus)` helper inside the master workflow is the load-bearing abstraction. Each call returns a structured `IMPL_RESULT` (commit_sha + files_modified + tests_passed + integration_notes); the integrator's final agent reads all N results and produces an `INTEGRATION` schema. Both schemas are in the skill at `~/.claude/skills/ultracode-quad-stream/SKILL.md`.

The conflict-resolution `how` field in `INTEGRATION.conflicts_resolved` is the audit trail. For the 2026-06-24 run, it had 7 entries — each one a short prose paragraph that names the conflict, names how it was resolved, and names which stream's marker count proves the resolution preserved intent.

## Pointers

- Skill: `~/.claude/skills/ultracode-quad-stream/SKILL.md`
- Reference run output: brain-pod transcript dir for workflow run `wf_0ce15c71-1a8` on 2026-06-24
- PR: McK-Private/marvin-surface#923 (merge commit `d612a53c`)
- The five files that mattered:
  - `src/agents/teams_call/validator/url_reader.py` (Stream A, 509 lines, SSRF-guarded fetcher)
  - `src/agents/teams_call/validator/fetched_docs.py` (Stream B, per-call ephemeral cache)
  - `src/agents/teams_call/validator/output_sanitiser.py` (Stream C, TTS-safety filter)
  - `src/agents/teams_call/slack_post.py` (Stream D, summary + transcript thread)
  - `src/agents/teams_call/validator/tools.py` (shared, 21 stream-X markers preserved)
