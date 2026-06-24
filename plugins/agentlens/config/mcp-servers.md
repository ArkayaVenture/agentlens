# MCP Servers — Discovered Configurations

Extracted from MCP server definitions found on this Mac, for import into Claude Code.
All secret values (tokens/keys/passwords) are redacted as `<REDACTED — set me>`.

_Generated: 2026-06-23_

## Access note

The authoritative GLOBAL config files could **not be read** in this environment — they
live outside the connected folders and no available tool (Read / Grep / Bash) could open
them. Their existence is confirmed (via path listing) but their contents are unknown:

- `~/.cursor/mcp.json` — Cursor global MCP config — **EXISTS, unreadable**
- `~/Library/Application Support/Claude/claude_desktop_config.json` — Claude Desktop — **EXISTS, unreadable**
- `~/.claude.json` — Claude Code user config — **EXISTS, unreadable**
- `~/.claude/settings.json` — Claude Code settings — **EXISTS, unreadable**
- `~/Library/Application Support/Code/User/settings.json` — VS Code — **NOT found**
- `~/Library/Application Support/Code/User/mcp.json` — VS Code — **NOT found**

Everything in the "Fully captured" table below was read directly from project-level
config files inside connected folders.

## Fully captured servers (read from project config files)

| Server name | Source (tool / file) | Transport | Command / URL | Required env keys | Notes |
|---|---|---|---|---|---|
| `context7` | Cursor — `IdeaProjects/fdl-foundation/.cursor/mcp.json` | http | `https://mcp.context7.com/mcp` | (none) | Library / framework docs lookup |
| `Atlassian` | Cursor — `IdeaProjects/fdl-foundation/.cursor/mcp.json` | stdio (remote bridge) | `npx mcp-remote https://mcp.atlassian.com/v1/mcp` | (none in file; auth via OAuth login) | Jira / Confluence access |
| `pyright` | Cursor — `IdeaProjects/review-agent/.cursor/mcp.json`, `review-agent-1/.cursor/mcp.json` | stdio | `python3 /workspace/.mcp/mcp_pyright.py` | (none) | Python type checking / LSP for code review |
| `typescript` | Cursor — `IdeaProjects/review-agent/.cursor/mcp.json`, `review-agent-1/.cursor/mcp.json` | stdio | `python3 /workspace/.mcp/mcp_typescript.py` | (none) | TypeScript LSP / type checking for code review |
| `skill-marketplace` | Claude Code — `IdeaProjects/forge/.mcp.json`, `forge-marketplace/.mcp.json` | stdio | `marketplace-mcp` | `MARKETPLACE_URL`, `MARKETPLACE_TOKEN` | Internal skill marketplace (local at 127.0.0.1:8080) |
| `office-memory` | VS Code — `Downloads/agentic-o365-connector/office-agentic-compliance/.vscode/mcp.json` | http | `http://127.0.0.1:8787/mcp` | (none) | Local O365 / office agent memory service |

## Global Cursor servers — names only (config unreadable)

These server keys are proven to exist by Cursor's per-project MCP cache directories
(`~/.cursor/projects/*/mcps/user-<NAME>/...`), but their transport, command/URL, and env
vars live in the unreadable global `~/.cursor/mcp.json` and could not be captured.
**Re-extract these manually from `~/.cursor/mcp.json`.**

| Server name (key) | Source | Status | Likely purpose (unverified) |
|---|---|---|---|
| `avm-dev` | Cursor global | name only — config unreadable | unknown (re-check `~/.cursor/mcp.json`) |
| `pm-agents-npn` | Cursor global | name only — config unreadable | unknown |
| `Atlassian-MCP-Server` | Cursor global | name only — config unreadable | likely Jira/Confluence (cf. `Atlassian` above) |
| `marvin-cocierge-services` | Cursor global | name only — config unreadable | unknown (project-specific) |

## Empty configs (no servers defined)

The following `.mcp.json` files exist but contain `"mcpServers": {}` (nothing to import):

- `IdeaProjects-external/nanoclaw/.mcp.json`
- `IdeaProjects-external/nanoclaw-slack/.mcp.json`
- `IdeaProjects-external/nanoclaw-signal/.mcp.json`
- `IdeaProjects-external/nanoclaw-matrix/.mcp.json`
- `IdeaProjects-external/nanoclaw-whatsapp/.mcp.json`
- `IdeaProjects-external/nanoclaw-docker-sandboxes/.mcp.json`
