# Security Policy

**AgentLens** is designed to be a *low-trust-surface, local-first* plugin. This
document states exactly what it does and does not do, the threat model, and how
to report a vulnerability.

> Anthropic's own guidance: plugins "can execute arbitrary code on your machine
> with your user privileges. Only install plugins and add marketplaces from
> sources you trust." AgentLens is built to earn that trust by minimising what it
> runs and keeping everything readable and local.

## What this plugin contains (declare-everything)

| Component | Present? | Notes |
|-----------|----------|-------|
| Skills | ✅ 2 | `setup-agentlens` (installer), `dashboard-optimizer` (opt-in nightly). Inert until you invoke them. |
| Hooks | ❌ none | No lifecycle hooks. Nothing runs automatically on Claude Code events. |
| Bundled MCP servers | ❌ none | No `.mcp.json`. The plugin adds no network connectors. |
| Agents shipped by plugin | ❌ none | No bundled sub-agent definitions. |
| Telemetry / analytics | ❌ none | Nothing is sent anywhere by this tool. |
| Bundled binaries | ❌ none | Pure Python 3 standard library + a single-file HTML/JS dashboard. No third-party packages, no `pip install`, no `npm install`. |

Everything is plain text and auditable. There is no obfuscated or minified code.

## What it does at runtime (after you run `setup-agentlens`)

- Installs a **macOS LaunchAgent** that runs `platform/serve.py` at login.
- `serve.py` binds **`127.0.0.1` only** (loopback) — never `0.0.0.0`. The
  dashboard is not reachable from your network.
- The server **reads** your local session transcripts (`~/.claude/projects`,
  Cowork sessions, Cursor state) with **your own user permissions**, and
  **writes** only inside the brain folder (`~/claude-projects/agentlens`).
- It has **no authentication** because it has **no remote surface** — it is a
  read-mostly localhost viewer of files you already own.

## Network egress

- The **dashboard/server make no outbound network calls.** They load two JS
  libraries (Chart.js, D3) from a public CDN for rendering; you can vendor these
  locally to run fully offline (see the dashboard `<head>`).
- The optional **scheduled research jobs** (`ai-release-radar`,
  `ai-deep-dive-weekly`) perform **web searches** when *you* enable them — that
  is their entire purpose, and it is clearly opt-in. The nightly
  `dashboard-optimizer` is local-only.

## Hardening already in place

- Loopback-only bind (`127.0.0.1`).
- Path-traversal guard on `/api/session?file=` (rejects `..` and absolute paths).
- No shell execution from HTTP requests; the server only parses local files.
- LaunchAgent runs as your user (no root, no `sudo`).
- The live brain is kept **out of macOS privacy-protected folders** (Downloads /
  Desktop / Documents) so the background service reads only an explicit,
  user-chosen directory.

## Recommended user practices

- Review `platform/serve.py` and `dashboard/index.html` before installing — they
  are short and dependency-free.
- Keep the brain folder under a path you control (default `~/claude-projects/agentlens`).
- Treat the 3 scheduled jobs as opt-in; click **Run now** once to see exactly
  what they do before trusting them on a schedule.

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue.

- Email: **hello@arkayaventure.com** (subject: `AgentLens security`)
- Include: affected version/commit, reproduction steps, and impact.
- We aim to acknowledge within **2 business days** and to provide a fix or
  mitigation timeline within **7 days** for confirmed issues.

Coordinated disclosure is appreciated; we will credit reporters who wish to be
credited.

## Supply chain

- No third-party runtime dependencies to pin (stdlib only).
- For stable installs, pin the marketplace entry to a tag **and** commit SHA in
  your own `marketplace.json` (see README → Install).
- Releases are tagged and validated with `claude plugin validate . --strict` in
  CI before publication.
