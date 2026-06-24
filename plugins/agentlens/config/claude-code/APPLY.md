# Applying Claude Code config (manual — `~/.claude` is not writable from Cowork)

Cowork cannot read or write `~/.claude` (protected location). So these changes are delivered
here as drop-in files + commands. Apply them in a terminal. Review before running.

## 1. Import MCP servers

Two equivalent options.

**Option A — merge JSON.** Open `mcp-import.json` (in this folder). It contains a
`{ "mcpServers": { ... } }` block with secrets shown as `<REDACTED — set me>`. Fill in the real
values, then merge the `mcpServers` keys into your `~/.claude.json` (project-level) or run via CLI.

**Option B — CLI.** Edit `mcp-add-commands.sh`, replace each `<REDACTED — set me>` with the real
secret, then:

```bash
bash ~/claude-projects/agentlens/config/claude-code/mcp-add-commands.sh
claude mcp list      # verify
```

> ⚠️ The authoritative GLOBAL configs (`~/.cursor/mcp.json`, Claude Desktop config,
> `~/.claude.json`) could not be read from Cowork, so four global Cursor servers
> (`avm-dev`, `pm-agents-npn`, `Atlassian-MCP-Server`, `marvin-cocierge-services`) are listed
> by NAME ONLY in `../mcp-servers.md`. Re-extract their definitions with:
> `cat ~/.cursor/mcp.json` and add them the same way.

## 2. Bypass-permissions mode (⚠️ security tradeoff — read this)

The ultracode doctrine asks for autonomous, prompt-free runs. Claude Code supports this, but it
disables the per-action approval prompts that normally protect you from a bad command or a
prompt-injection in a repo/file. **Only enable on a machine and repos you trust.** Prefer scoping
it to specific projects rather than globally.

Per-session (safest — explicit, one run):
```bash
claude --dangerously-skip-permissions
```

Make it the default for a project — add to that project's `.claude/settings.json`:
```json
{ "permissions": { "defaultMode": "bypassPermissions" } }
```

Global default — add to `~/.claude/settings.json` (broadest blast radius; not recommended):
```json
{ "permissions": { "defaultMode": "bypassPermissions" } }
```

Mitigations if you enable it: keep work in version control, run inside the projects you intend,
and keep the adversarial/verification step from the doctrine mandatory.

## 3. Install the ultracode doctrine so every session uses it

Make Claude Code load the doctrine automatically by referencing it from your global memory.
Append this line to `~/.claude/CLAUDE.md`:

```
@~/claude-projects/agentlens/doctrine/ultracode.md
```

(That `@path` import pulls the doctrine into every session's context. Alternatively paste the
doctrine's "Operating defaults" section directly into `~/.claude/CLAUDE.md`.)

For Cowork, restate the doctrine at the top of important requests, or keep this brain folder
connected so the doctrine file is available.

## 4. Verify
```bash
claude mcp list
claude config get permissions.defaultMode   # if you set it
grep -n "ultracode" ~/.claude/CLAUDE.md
```
