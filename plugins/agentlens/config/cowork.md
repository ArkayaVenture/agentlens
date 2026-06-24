# Claude Cowork configuration

## Connected folders (this session)
- `~/claude-projects` → the brain (read/write)
- `~/IdeaProjects`, `~/IdeaProjects-external`, `~/Downloads` → read/write
- `~/.claude`, `~/Documents` (OneDrive) → **not mountable** (protected); visible via Glob path-listing only.

## Recommended connectors (MCP, app-level)
Based on the work themes (Marvin platform, Jira/Confluence, Slack, K8s/cloud, docs), wire these
Cowork connectors so sessions and the dashboard can pull live data:
- **Atlassian (Jira + Confluence)** — already used in Cursor; highest value for task/issue context.
- **Slack** — Marvin has heavy Slack-connectivity work; useful for digests and the dashboard.
- **Google Drive / OneDrive** — meeting notes, decks, mapping spreadsheets live in Documents.
- **GitHub** — repo activity for the dashboard's "work" view.
See chat for the live Connect buttons (registry suggestions surfaced this session).

## Scheduled tasks (the self-enrichment loops)
| Task | Cadence | What it does |
|------|---------|--------------|
| `ai-release-radar` | daily 01:00 | Sweeps official AI/LLM provider release notes & changelogs; writes a dated digest to `knowledge/ai-feed/` and updates `dashboard/feed.json`. |
| `ai-deep-dive-weekly` | Sunday 01:00 | Deeper sweep: Claude best-practices, multi-agent platforms, connectors/plugins/skills, trends; enriches `knowledge/best-practices/` and the brain. |

> Scheduled tasks run only while the Claude app is open; if it's closed when due, they run on next launch.

## Dashboard (the only UI)
- Served locally on a **dedicated port (7717)** by `platform/serve.py`; open http://127.0.0.1:7717/ .
- Dark, Dynatrace-style, drill-down from topology nodes → skills/agents/MCP/projects/loops.
- Refreshed automatically by the daily/weekly agent loops (they write `dashboard/feed.json`).
- Per the "visible only through this dashboard on the machine" requirement, there is no separate
  Cowork sidebar artifact — the local served dashboard is the single surface.
