# Configuration

AgentLens is fully local and configured via environment variables read by the service at start,
plus an optional `dashboard/config.json` (created automatically when you customize dashboards).

## Source roots (which platforms to read)
| Variable | Default |
|---|---|
| `AGENTLENS_CLAUDE_PROJECTS` | `~/.claude/projects` |
| `AGENTLENS_COWORK_ROOT` | `~/Library/Application Support/Claude/local-agent-mode-sessions` |
| `AGENTLENS_CURSOR_USER` | `~/Library/Application Support/Cursor/User` |
| `AGENTLENS_PORT` | `7717` |
| `AGENTLENS_LIVE_WINDOW` | `900` (seconds) |

## Provenance taxonomy (generic, configurable)
| Variable | Meaning |
|---|---|
| `AGENTLENS_MCP_LOCAL` | comma list of MCP-server name substrings to tag **local** |
| `AGENTLENS_MCP_EXTERNAL` | comma list to tag **external** |
| `AGENTLENS_WEB_MCP` | public web/data MCP vendors (default: tavily, context7, fetch, brave, exa, firecrawl) |

LLM vendors (OpenAI, Anthropic/Claude, Google/Gemini, Qwen, Mistral, Llama, Bedrock, …) are
identified automatically and shown as contributors in the Provenance view.

Nothing here is hardcoded to any person, company, or project — the dashboard reflects **your** data.
