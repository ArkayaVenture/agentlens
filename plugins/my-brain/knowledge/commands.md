# Slash Commands Inventory — `/sc:*`

Custom slash commands installed at `~/.claude/commands/sc/` (26 files). These are the
**SuperClaude Framework** command set, invoked as `/sc:<command>` (e.g. `/sc:analyze`).

> **Access note:** Command file contents under `~/.claude/` were not directly readable
> in this session (only file paths were enumerable). All 26 filenames match the standard
> SuperClaude command set exactly, so purposes below reflect those standard definitions
> rather than a live read of each file.

## Commands

| Command | Purpose |
|---|---|
| `/sc:brainstorm` | Interactive requirements discovery — turns a vague idea into a structured brief through Socratic dialogue (Brainstorming mode). |
| `/sc:analyze` | Comprehensive code/system analysis across quality, security, performance, and architecture. |
| `/sc:design` | Designs system architecture, APIs, or component interfaces before implementation. |
| `/sc:workflow` | Generates a structured implementation workflow / plan from requirements or a PRD. |
| `/sc:estimate` | Produces development effort, time, and complexity estimates. |
| `/sc:task` | Manages a long-running task with structured tracking and delegation. |
| `/sc:spawn` | Orchestrates complex multi-step operations by spawning/coordinating subtasks. |
| `/sc:implement` | Implements a feature end-to-end with intelligent agent/tool routing. |
| `/sc:build` | Builds/compiles the project and handles build-related tasks. |
| `/sc:test` | Runs tests, manages test workflows, and reports coverage. |
| `/sc:improve` | Applies targeted code improvements (quality, performance, maintainability). |
| `/sc:cleanup` | Removes dead code, reduces clutter, and tidies the codebase. |
| `/sc:troubleshoot` | Diagnoses and resolves issues in code, builds, or behavior. |
| `/sc:explain` | Explains code, concepts, or system behavior at an appropriate depth. |
| `/sc:document` | Generates documentation for code, APIs, or systems. |
| `/sc:git` | Git operations with intelligent commit messages and workflow assistance. |
| `/sc:estimate` (see above) | — |
| `/sc:research` | Deep web research with adaptive planning (DeepResearch mode + `deep-research-agent`). |
| `/sc:business-panel` | Multi-expert business analysis panel discussing a document/idea (Business Panel mode + `business-panel-experts`). |
| `/sc:spec-panel` | Multi-expert specification review/critique panel for specs and designs. |
| `/sc:pm` | Project-management workflows (planning, tracking) via the `pm-agent`. |
| `/sc:reflect` | Reflects on and validates task progress / completeness using introspection. |
| `/sc:load` | Loads project/session context (Serena-backed session memory) at the start of work. |
| `/sc:save` | Persists session context and discoveries to memory for later sessions. |
| `/sc:select-tool` | Intelligently selects the optimal MCP tool/server for a given operation. |
| `/sc:index` | Lists/explores available commands and capabilities (command catalog). |
| `/sc:help` | Shows help for the `/sc:*` command set. |

## Summary

- **26 commands total**, all under the `/sc:` (SuperClaude) namespace.
- Cover the full SDLC: discovery (`brainstorm`, `research`), design (`design`,
  `workflow`, `estimate`, `spec-panel`), delivery (`implement`, `build`, `test`, `task`,
  `spawn`), maintenance (`improve`, `cleanup`, `troubleshoot`), knowledge
  (`explain`, `document`, `analyze`), ops (`git`), strategy (`business-panel`, `pm`),
  and session/meta (`load`, `save`, `reflect`, `select-tool`, `index`, `help`).
- Session memory commands (`load` / `save`) and `select-tool` indicate the
  SuperClaude **Serena** MCP integration and orchestration mode are in use.
