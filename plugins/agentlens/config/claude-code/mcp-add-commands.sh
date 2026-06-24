#!/usr/bin/env bash
# Claude Code MCP server add commands — generated 2026-06-23
# Run these to register the discovered MCP servers with Claude Code.
# Secrets are placeholders; fill in real values before running.
# Use --scope user for global, or run inside a project for project scope.

set -euo pipefail

# --- context7 (HTTP transport — library/framework docs) ---
claude mcp add --transport http context7 https://mcp.context7.com/mcp

# --- office-memory (HTTP transport — local O365 agent memory; ensure service is running on :8787) ---
claude mcp add --transport http office-memory http://127.0.0.1:8787/mcp

# --- Atlassian (stdio via mcp-remote bridge — Jira/Confluence; auth happens via OAuth on first run) ---
claude mcp add Atlassian -- npx mcp-remote https://mcp.atlassian.com/v1/mcp

# --- pyright (stdio — Python type checking for code review; adjust path if not /workspace) ---
claude mcp add pyright -- python3 /workspace/.mcp/mcp_pyright.py

# --- typescript (stdio — TypeScript LSP for code review; adjust path if not /workspace) ---
claude mcp add typescript -- python3 /workspace/.mcp/mcp_typescript.py

# --- skill-marketplace (stdio — internal skill marketplace) ---
# fill in secrets: replace <REDACTED — set me> with the real MARKETPLACE_TOKEN
claude mcp add skill-marketplace \
  --env MARKETPLACE_URL=http://127.0.0.1:8080 \
  --env MARKETPLACE_TOKEN='<REDACTED — set me>' \
  -- marketplace-mcp

# ---------------------------------------------------------------------------
# NOT INCLUDED — global Cursor servers whose config could not be read in this
# environment. Re-extract their transport/command/url/env from ~/.cursor/mcp.json
# and add them manually:
#   - avm-dev
#   - pm-agents-npn
#   - Atlassian-MCP-Server   (likely same as Atlassian above)
#   - marvin-cocierge-services
# ---------------------------------------------------------------------------
