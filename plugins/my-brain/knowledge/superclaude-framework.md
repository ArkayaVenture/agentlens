# SuperClaude Framework (installed)

The **SuperClaude Framework** is installed globally at `~/.claude/`. It is a
configuration layer that extends Claude with a standard set of behavioral modes,
rules, principles, MCP-server integrations, and a `/sc:*` command + agent library.
It is detectable from the framework files at the root of `~/.claude/` plus the
matching `commands/sc/*` and `agents/*` sets.

> **Access note:** The framework `.md` files under `~/.claude/` could not be read
> directly in this session (only their paths were enumerable). The summaries below
> describe the standard role of each file in the SuperClaude framework; treat them as
> "what these files configure" rather than a verbatim read.

## Framework files present (root of `~/.claude/`)

| File | What it configures |
|---|---|
| `CLAUDE.md` | Top-level entry point — imports/wires together the framework (flags, rules, principles, modes, MCP docs) into the active Claude config. |
| `FLAGS.md` | Defines behavioral flags (e.g. `--think`, `--uc`/token-efficiency, `--delegate`, mode toggles) and the rules for auto-activating them. |
| `PRINCIPLES.md` | Core engineering principles guiding decisions (evidence-based, simplicity, maintainability, etc.). |
| `RULES.md` | Hard operational rules / guardrails for how Claude must behave (safety, workflow, tooling discipline). |
| `RESEARCH_CONFIG.md` | Configuration for deep-research behavior (depth, planning, source handling) — pairs with DeepResearch mode and `/sc:research`. |
| `BUSINESS_PANEL_EXAMPLES.md` | Worked examples for the Business Panel feature (multi-expert business analysis). |
| `BUSINESS_SYMBOLS.md` | Symbol/notation legend used by the Business Panel output format. |

### Behavioral modes (`MODE_*.md`)

| Mode file | Purpose |
|---|---|
| `MODE_Brainstorming.md` | Collaborative discovery — Socratic requirement elicitation from vague ideas. |
| `MODE_Introspection.md` | Self-reflection / reasoning transparency for validating progress and decisions. |
| `MODE_Orchestration.md` | Intelligent tool selection and parallel coordination of subtasks/agents. |
| `MODE_Task_Management.md` | Structured tracking of multi-step work, todos, and delegation. |
| `MODE_Token_Efficiency.md` | Compressed/symbol-based communication to reduce token usage (the `--uc` style). |
| `MODE_DeepResearch.md` | Multi-hop autonomous web-research behavior (planning, fan-out, synthesis). |
| `MODE_Business_Panel.md` | Simulated panel of business experts analyzing a document or strategy. |

### MCP server integration docs (`MCP_*.md`)

Each file documents when and how to use a specific MCP server. The framework
references **seven** MCP servers:

| MCP server | Role |
|---|---|
| **Context7** (`MCP_Context7.md`) | Official library/framework documentation lookup and version-accurate code patterns. |
| **Magic** (`MCP_Magic.md`) | UI component generation (modern front-end components / design-system snippets). |
| **Morphllm** (`MCP_Morphllm.md`) | Fast, pattern-based bulk code edits / multi-file transformations. |
| **Playwright** (`MCP_Playwright.md`) | Browser automation and end-to-end testing (real browser interaction). |
| **Sequential** (`MCP_Sequential.md`) | Structured multi-step reasoning / sequential thinking for complex analysis. |
| **Serena** (`MCP_Serena.md`) | Semantic code understanding + **session memory/project context** (backs `/sc:load` and `/sc:save`). |
| **Tavily** (`MCP_Tavily.md`) | Web search / retrieval (feeds DeepResearch and `/sc:research`). |

## How the pieces fit together

- **`CLAUDE.md`** is the orchestration root that pulls in `FLAGS`, `RULES`,
  `PRINCIPLES`, every `MODE_*`, and every `MCP_*` document.
- **Flags** (`FLAGS.md`) and **modes** (`MODE_*`) change Claude's behavior on demand
  (or auto-activate based on context); **`RULES.md` / `PRINCIPLES.md`** are the
  always-on guardrails and values.
- The **`/sc:*` commands** (see `commands.md`) and **agents** (see `agents.md`) are
  the user-facing surface; they route work to the appropriate **MCP servers** per the
  `MCP_*` docs.
- **Serena** + `/sc:load` / `/sc:save` provide cross-session memory; **Sequential**
  powers deep analysis; **Tavily** + DeepResearch power research; **Context7 / Magic /
  Morphllm / Playwright** support docs lookup, UI generation, bulk edits, and browser
  testing respectively.

**Bottom line:** This is a full SuperClaude install — 7 framework config files, 7
behavioral modes, 7 MCP-server integrations (Context7, Magic, Morphllm, Playwright,
Sequential, Serena, Tavily), 26 `/sc:*` commands, and 17 framework agents — plus the
user's own additions (the `mimir`/`marvin` skill+agent suites and the ThreatLens /
security skills documented elsewhere in this brain).
