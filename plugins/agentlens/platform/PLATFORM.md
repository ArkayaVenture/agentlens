# AgentLens platform — local, agent-managed, on a dedicated port

The brain is consumed **only through the dashboard**, served locally on a dedicated port.
Markdown digests still accumulate in `knowledge/` for the brain's own memory, but the human-facing
surface is the dashboard at **http://127.0.0.1:7717/**.

> **Why http://127.0.0.1:7717 may be "not working":** nothing is serving it until the server
> runs **on your Mac**. Cowork's shell is an isolated sandbox — it cannot start a process or bind a
> port on your machine. Run the installer below once (on your Mac) and it auto-starts forever after.

## Run it

Always-on (survives reboot/login) — **one command**, run on your Mac:
```bash
bash ~/claude-projects/agentlens/platform/install-service.sh
# installs the LaunchAgent, starts it, opens http://127.0.0.1:7717/
```

Just once, in the foreground (no autostart):
```bash
bash ~/claude-projects/agentlens/platform/start.sh   # → http://127.0.0.1:7717/
```

Health check: `curl -s http://127.0.0.1:7717/api/health`.
Stop/uninstall: `launchctl bootout gui/$(id -u)/com.agentlens.dashboard ; rm ~/Library/LaunchAgents/com.agentlens.dashboard.plist`.
(Day-to-day control is easier via `bash platform/ctl.sh {start|stop|restart|status|logs}`.)

## Live monitoring API (served on the port)
The server parses your `~/.claude/projects` transcripts (with your permissions) into JSON the
dashboard renders live: `/api/health`, `/api/overview`, `/api/sessions`,
`/api/session?file=…` (timeline + flow-of-control + sub-agents), `/api/agents`. The dashboard
auto-refreshes (configurable interval) and lets you drill: Overview → session → sub-agent →
every tool transaction with pass/fail status, plus an ULTRACODE flow view of fan-out/verify loops.

**Token tracking & optimizer:** `/api/overview` also returns `tokens` (in / out / cacheRead /
cacheCreate / cacheHit), `tokensByDay` (the trend graph), and `suggestions` — heuristic,
data-driven tips to cut cost (low cache-hit → keep early context stable for prompt caching; high
per-turn input → /compact + push exploration into sub-agents). Each session drawer shows its token
totals, cache-hit %, and an output-tokens-per-turn sparkline.

**Multiple sources:** the server scans three session stores (overridable via env):
`claude-code` (`~/.claude/projects`), `cowork`
(`~/Library/Application Support/Claude/local-agent-mode-sessions`), and `cursor` (`~/.cursor/projects`).
Each session is tagged with its `source` and a `live` flag (touched within `AGENTLENS_LIVE_WINDOW`, default 300s).

**Internal vs external provenance:** every tool call is classified — INTERNAL = local machine
(Read/Edit/Write/Glob/Grep/local Bash), EXTERNAL = web/other-LLM/cloud (WebSearch/WebFetch, any
`mcp__*` connector, browser tools, network Bash like curl/git push). The UI heat-maps the
internal-vs-external mix per session/workflow (blue→orange), surfaces the **skills** and **MCP
servers** used, and tags each tool event `int`/`ext`. `/api/overview.provenance` and each
`/api/session` carry the counts and `extPct`.

## Architecture (who manages what)

```
            ┌─────────────────────────────────────────────┐
            │  Dashboard (port 7717)  ── the only UI        │
            │  index.html · feed.json · data/*.json         │
            └───────────────▲───────────────────────────────┘
                            │ reads (no-cache)
            ┌───────────────┴───────────────────────────────┐
            │  AgentLens/ (file-based knowledge + control)    │
            │  knowledge/ · config/ · projects/ · doctrine/  │
            └───────────────▲───────────────────────────────┘
                            │ write-through (ULTRACODE)
   ┌────────────────────────┴───────────────────────────┐
   │  Agent loops (scheduled Claude sessions)            │
   │  • ai-release-radar    (daily 01:00)                │
   │  • ai-deep-dive-weekly (Sunday 01:00)               │
   │  each fans out sub-agents → classify → adversarial  │
   │  verify → loop until done → write brain + feed.json │
   └─────────────────────────────────────────────────────┘
```

The **scheduled Claude tasks are the agents** that maintain and enrich the platform. Each run
spawns sub-agents (fan-out), classifies signal vs noise, runs an adversarial verification pass,
loops until done, and writes results back into the brain + `dashboard/feed.json`. The local server
just exposes the brain; it holds no state of its own.


## Roadmap to "fully agent-managed"
1. ✅ Local server on dedicated port + launchd always-on.
2. ✅ Daily + weekly enrichment agents (ultracode) writing the brain + feed.
3. ◻ A "supervisor" scheduled task (e.g. every 6h) that health-checks the port, restarts if down,
   and verifies the last loop ran — wire it once you've confirmed the loops have folder access.
