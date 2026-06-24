<div align="center">

# 🧠 my-brain — Second Brain & Live Dashboard

### Your local command center for everything you build with Claude Code, Cowork & Cursor.

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-0b6bcb.svg)](./LICENSE)
[![Commercial licence](https://img.shields.io/badge/Commercial-licence%20available-1f9d63.svg)](./COMMERCIAL-LICENSE.md)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-8a7dff.svg)](https://code.claude.com/docs/en/plugins)
[![Local-first](https://img.shields.io/badge/Local--first-no%20telemetry-04141f.svg)](./SECURITY.md)
[![Release](https://img.shields.io/github/v/release/arkayaventure/my-brain?color=2f6bff)](https://github.com/arkayaventure/my-brain/releases)

**A self-contained Claude plugin that installs an always-on local dashboard (port 7717) and a
self-enriching second brain — live sessions, sub-agents, tokens, 4-way data provenance, and an
ULTRACODE strategy view. Fully local. No hooks. No bundled MCP. No telemetry.**

[Install](#-install-30-seconds) · [Features](#-what-you-get) · [Security](./SECURITY.md) · [Commercial use](./COMMERCIAL-LICENSE.md) · [arkayaventure.com →](https://arkayaventure.com)

![my-brain dashboard — Overview](./marketing/screenshots/overview.png)

<sub>Built by <a href="https://arkayaventure.com"><b>Arkaya Venture Limited</b>, UK</a> · Licensed CC BY-NC 4.0</sub>

</div>

---

## ⚡ Install (30 seconds)

In **Claude Code** (or Cowork), add the marketplace and install the plugin:

```text
/plugin marketplace add arkayaventure/my-brain
/plugin install my-brain@arkaya-plugins
```

Then run the setup skill (or just say *"set up the my-brain dashboard"*):

```text
/my-brain:setup-my-brain
```

That seeds a persistent brain at `~/claude-projects/my-brain`, installs the always-on service on
**http://127.0.0.1:7717/**, registers the 3 scheduled jobs, and verifies everything.

> **Prefer a pinned install?** Pin the plugin to a tag **and** commit SHA in your own marketplace
> entry for reproducible deployments — see [Pinned / enterprise install](#-pinned--enterprise-install).

> **Cowork users:** download `my-brain.plugin` from [Releases](https://github.com/arkayaventure/my-brain/releases)
> and install it from the Cowork plugin panel.

## 🧩 What you get

| | |
|---|---|
| **📊 Live monitoring** | Every Claude Code, Cowork & Cursor session on your machine — messages, tool calls, sub-agent fan-out, durations, models. Drill from Overview → session → sub-agent → individual tool call with pass/fail status. |
| **🪙 Token economics** | Tokens in/out, cache reads, **cache-hit %**, top token-consuming sessions, token-by-tool attribution, and data-driven cost-cutting suggestions. |
| **🌐 4-way data provenance** | Every tool call classified as **internal (machine) / firm MCP / external web / external LLM**, heat-mapped per workflow with click-through. Know exactly where your data goes. |
| **🕸️ Workflow Brain + Topology** | A force-directed graph of your workflows and a capability topology of skills, agents, commands and MCP connectors. |
| **⚡ ULTRACODE view** | Detects fan-out, tournament, loop-until-done, adversarial and classify-and-act strategies across your real sessions. |
| **📡 Self-enriching AI Feed** | Scheduled ULTRACODE research loops keep a dated, cited digest of the AI ecosystem and feed the dashboard. |
| **🌗 Day/night themes** | Clean McKinsey-style navy/blue dark + white light. |

## 🔐 Security & privacy (read this — it's short)

my-brain is built to be **trustworthy by construction**:

- **No hooks, no bundled MCP servers, no telemetry, no third-party dependencies** (Python stdlib + a single HTML file).
- The server **binds `127.0.0.1` only** — never your network — and has a path-traversal guard on its API.
- It **reads your own transcripts with your own permissions** and writes only inside the brain folder.
- The optional research jobs do web searches **only when you enable them**. Everything else is local.

Full posture, threat model, and disclosure process: **[SECURITY.md](./SECURITY.md)**.

## 📦 What's in the plugin

```
plugins/my-brain/
├── .claude-plugin/plugin.json     # manifest (CC-BY-NC-4.0)
├── skills/
│   ├── setup-my-brain/            # one-run installer (entry point)
│   └── dashboard-optimizer/       # opt-in nightly self-improvement + sub-skills
├── platform/                      # serve.py (stdlib server), bootstrap/ctl/seed scripts
├── dashboard/                     # single-file dashboard SPA + feed.json
├── doctrine/ · config/ · knowledge/ · projects/   # seed second brain
└── BUILD-KIT/scheduled-jobs.md    # the 3 scheduled jobs, verbatim
```

## 🏷️ Pinned / enterprise install

For reproducible deployments, reference the plugin pinned to a tag and full commit SHA in your own
`marketplace.json`:

```json
{
  "name": "my-team",
  "owner": { "name": "Your Team" },
  "plugins": [
    { "name": "my-brain",
      "source": { "source": "github", "repo": "arkayaventure/my-brain",
                  "ref": "v1.0.0", "sha": "<full-40-char-commit-sha>" } }
  ]
}
```

Run `claude plugin validate . --strict` before rolling out.

## 📜 Licence

**Free for non-commercial use** under [Creative Commons Attribution-NonCommercial 4.0](./LICENSE) —
attribution to **Arkaya Venture Limited, UK** is always required (see [NOTICE](./NOTICE)).

**Commercial use requires a paid licence.** Using my-brain inside a for-profit company, in a paid
product, or as a hosted service? See **[COMMERCIAL-LICENSE.md](./COMMERCIAL-LICENSE.md)** or email
**soumen.trivedi@arkayaventure.co.uk**.

## 🚀 About Arkaya Venture

my-brain is built and maintained by **[Arkaya Venture Limited](https://arkayaventure.com)** (UK) —
we build local-first, secure AI tooling for people who do serious work with agents.

**Follow & connect:** [Website](https://arkayaventure.com) · [LinkedIn](https://www.linkedin.com/company/arkaya-venture) · [X](https://x.com/arkayaventure) · [Facebook](https://www.facebook.com/arkayaventure)

<div align="center"><sub>© 2026 Arkaya Venture Limited, United Kingdom · CC BY-NC 4.0 · ⭐ star this repo if it's useful</sub></div>
