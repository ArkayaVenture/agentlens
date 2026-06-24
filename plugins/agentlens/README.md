# 🧠 AgentLens — Claude Code / Cowork plugin

A self-contained plugin that stands up a **second brain** plus an **always-on local dashboard** for all
your Claude Code, Cowork and Cursor work on your Mac. One skill installs everything.

## What you get

- **Live dashboard** at **http://127.0.0.1:7717/** (installed as a login-start macOS service that
  auto-restarts): live sessions, sub-agents, tool calls, **tokens in/out + cache hit + top
  token-consuming sessions + token-by-tool**, **4-way data provenance** (internal machine / firm MCP /
  external web / external LLM) with click-through, a force-directed **Workflow Brain**, a **Topology**
  capability graph, an **ULTRACODE** strategy view, and a chronological **AI Feed**. Day/night themes.
- **A file-based second brain** under `knowledge/`, continuously enriched.
- **3 scheduled ULTRACODE jobs**: `ai-release-radar` (daily), `ai-deep-dive-weekly` (Sunday),
  `dashboard-optimizer` (nightly self-improvement + validation).

## Install (2 steps)

1. Install this plugin (you're here).
2. Run the **`setup-agentlens`** skill — or say *"set up the AgentLens dashboard"*. It seeds a persistent
   brain folder (default `~/claude-projects/agentlens`), installs the always-on service on port 7717,
   registers the 3 scheduled jobs, wires memory, and verifies everything.

That's it. The service starts at login and auto-restarts; control it anytime with
`bash ~/claude-projects/agentlens/platform/ctl.sh {start|stop|restart|status|logs}`.

## What's in the bundle

| Path | Purpose |
|------|---------|
| `skills/setup-agentlens/` | One-run installer skill (entry point). |
| `skills/dashboard-optimizer/` | Nightly self-improvement skill + sub-skills (refine / validate / enrich). |
| `platform/serve.py` | Zero-dependency Python server + live monitoring API. |
| `platform/bootstrap.sh` | Portable, self-locating service installer (LaunchAgent on port 7717). |
| `platform/seed-brain.sh` | Seeds/refreshes the persistent brain from this bundle. |
| `platform/ctl.sh` · `start.sh` · `install-service.sh` | Service control + foreground run. |
| `platform/cursor_parser.py` | Best-effort Cursor SQLite reader. |
| `dashboard/index.html` · `feed.json` | The single-file dashboard SPA + its feed. |
| `doctrine/ultracode.md` | The ULTRACODE execution doctrine the jobs follow. |
| `config/` · `knowledge/` · `projects/` | Config inventory + seed knowledge base. |
| `BUILD-KIT/scheduled-jobs.md` | The 3 jobs, verbatim (cron + full prompts). |

## Privacy

Everything runs locally and reads your own transcripts with your own permissions. Nothing is uploaded by
this tool.

## Tuning knobs (env vars read by `serve.py`)

`AGENTLENS_PORT` (7717) · `AGENTLENS_LIVE_WINDOW` (900s) · `AGENTLENS_DASHBOARD` ·
`AGENTLENS_CLAUDE_PROJECTS` · `AGENTLENS_COWORK_ROOT` · `AGENTLENS_CURSOR_ROOT` ·
`AGENTLENS_FIRM_MCP` (comma list of MCP servers to classify as "firm/internal").

## Uninstall the service

```
launchctl bootout gui/$(id -u)/com.agentlens.dashboard
rm ~/Library/LaunchAgents/com.agentlens.dashboard.plist
```
