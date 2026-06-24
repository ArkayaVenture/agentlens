---
name: setup-my-brain
description: One-run setup for the my-brain dashboard + second brain. Installs the always-on local service on port 7717, seeds a persistent brain folder from the plugin bundle, registers the scheduled ULTRACODE jobs, wires memory, and verifies everything. Use when the user says "set up my-brain", "set up the my-brain dashboard", "install my-brain", or runs this skill after installing the my-brain plugin.
when_to_use: A user has installed the my-brain plugin and wants to stand up the dashboard + second brain on their Mac.
---

# setup-my-brain (prescriptive, one-run)

Goal: take the installed **my-brain plugin** and stand up the entire capability — a persistent
second brain on disk, an always-on local service at login (dashboard on **port 7717**), the scheduled
enrichment + optimizer jobs, and memory wiring — with adversarial verification at each step. Apply the
ULTRACODE doctrine (`doctrine/ultracode.md`): classify → act → adversarially verify → loop until done.

The plugin bundle (read-only) lives at `${CLAUDE_PLUGIN_ROOT}`. The **live brain** must live in a
writable, stable location so the service and the nightly loops can write to it.

## 0. Resolve paths (do this first)
- **SRC** = `${CLAUDE_PLUGIN_ROOT}` (the plugin bundle: contains `platform/`, `dashboard/`, `skills/`).
- **BRAIN** = the persistent brain folder. Default `~/claude-projects/my-brain`. If the user already has
  a my-brain folder (e.g. one connected to Cowork) prefer that and confirm it with them.
- Confirm `SRC/platform/serve.py` and `SRC/dashboard/index.html` exist. If not, the plugin is corrupt —
  tell the user to reinstall it.

## 1. Seed the persistent brain (shell)
Run: `bash "${CLAUDE_PLUGIN_ROOT}/platform/seed-brain.sh" "${CLAUDE_PLUGIN_ROOT}" "<BRAIN>"`
This refreshes code/UI/doctrine/config into BRAIN and seeds knowledge/projects **without** clobbering any
existing accumulated content. It prints the resolved BRAIN path on the last line — use it below.

## 2. Install the always-on service (shell)
Run: `bash "<BRAIN>/platform/bootstrap.sh"`
This generates a LaunchAgent (label `com.mybrain.dashboard`) with BRAIN's absolute path (starts at login
+ auto-restarts on crash), frees port 7717, starts the server, installs the bundled skills into
`~/.claude/skills`, and opens the dashboard. Then confirm: `curl -s http://127.0.0.1:7717/api/health`
returns a `version` and lists your sources.
Day-to-day control thereafter: `bash "<BRAIN>/platform/ctl.sh" {start|stop|restart|status|logs}`.

## 3. Register the 3 scheduled jobs (Cowork/Claude only — not from shell)
Read `<BRAIN>/BUILD-KIT/scheduled-jobs.md`. For EACH of the three jobs, create a scheduled task with its
`taskId`, `cronExpression`, `description`, and `prompt` — but FIRST replace any `~/claude-projects/my-brain`
in the prompt with the actual **BRAIN** path from step 1. Use the scheduling tool / `schedule` skill. After
creating each, trigger **Run now** once so its web/search/file tools are pre-approved.
The three jobs: `ai-release-radar` (daily 01:00), `ai-deep-dive-weekly` (Sun 01:00), `dashboard-optimizer` (nightly 04:00).

## 4. Initialise the brain + wire memory
- The structure (`knowledge/{ai-feed,best-practices}`, `config/`, `doctrine/`, `logs/`, `inbox/`,
  `dashboard/`) is created by seed-brain.sh; confirm it exists.
- If `dashboard/feed.json` is empty/seed, run the `ai-release-radar` job once now to populate the feed.
- Append an init line to `<BRAIN>/logs/research-log.md`: "<DATE> — brain initialised for <user> by setup-my-brain".
- If the **Anthropic memory plugin/connector is available**, point it at `<BRAIN>/knowledge` so memories
  persist into and read from the file-based brain. Then run the `consolidate-memory` skill over
  `<BRAIN>/knowledge/` + `<BRAIN>/inbox/` for memory hygiene. If no memory plugin is installed, the
  file-based brain + `consolidate-memory` already provide the second-brain behaviour.

## 5. Verify (adversarial) + report
- `curl` `/api/health` (version + sources) and `/api/overview` (tokens + provenance + live).
- Open the dashboard; confirm Overview, Sessions, Agents, Graph, Topology, ULTRACODE, AI Feed render with
  no `undefined` and no blank panels.
- Confirm the 3 jobs are registered/enabled (`mcp__scheduled-tasks__list_scheduled_tasks`).
- Report: service status + URL, BRAIN path, the 3 jobs + next-run times, whether memory was wired, and any
  remaining manual follow-up (Run-now approvals).

## Definition of Done
```
[ ] BRAIN seeded at a writable path; runtime dirs present
[ ] Service running at http://127.0.0.1:7717/ (health has version + sources), set to start at login
[ ] 3 scheduled jobs registered with BRAIN-correct paths, each Run-now approved
[ ] feed populated; research-log appended; skills present in ~/.claude/skills
[ ] consolidate-memory run; memory plugin wired if available
[ ] Dashboard tabs verified; concise setup report delivered
```
