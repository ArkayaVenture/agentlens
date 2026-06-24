# Custom Agents Inventory

Custom subagents installed at `~/.claude/agents/` (18 files).

> **Access note:** Agent file contents under `~/.claude/` were not directly readable
> in this session (only the file paths were enumerable). Seventeen of these agents are
> the standard **SuperClaude Framework** agent set — their filenames match the framework
> exactly, so purposes below reflect those standard definitions. `mimir` is a
> user-custom agent; its purpose is inferred from the matching `mimir-*` skill suite and
> project work. Treat the SuperClaude descriptions as "standard framework purpose" rather
> than a live read of each file.

## SuperClaude framework agents

| Agent | Purpose |
|---|---|
| `system-architect` | Designs scalable system architecture; long-term technical decisions, component boundaries, and cross-cutting structure. |
| `backend-architect` | Backend/API design — reliability, data integrity, service boundaries, and server-side architecture. |
| `frontend-architect` | Front-end architecture — UI structure, accessibility, performance, and component design. |
| `devops-architect` | CI/CD, infrastructure-as-code, deployment, observability, and automation of operational concerns. |
| `python-expert` | Production-grade Python: idiomatic, well-tested, maintainable code and Python-specific best practices. |
| `security-engineer` | Identifies vulnerabilities and ensures secure-by-design; threat modeling and security hardening. |
| `performance-engineer` | Diagnoses and optimizes performance bottlenecks (latency, throughput, resource usage). |
| `quality-engineer` | Test strategy, coverage, edge cases, and quality assurance across the codebase. |
| `refactoring-expert` | Improves code structure / reduces technical debt while preserving behavior. |
| `root-cause-analyst` | Systematic investigation of failures and bugs to find true underlying causes, not symptoms. |
| `requirements-analyst` | Turns vague ideas into concrete, structured requirements and specifications. |
| `technical-writer` | Produces clear technical documentation tailored to the audience. |
| `learning-guide` | Explains concepts and teaches progressively; education-oriented assistant. |
| `socratic-mentor` | Mentors via Socratic questioning — guides discovery rather than giving direct answers. |
| `deep-research-agent` | Multi-hop autonomous web research with adaptive planning and evidence synthesis (pairs with `/sc:research` and DeepResearch mode). |
| `business-panel-experts` | Multi-expert business analysis panel (simulates a panel of named business thinkers; pairs with `/sc:business-panel`). |
| `pm-agent` | Project/product management agent — planning, coordination, and delivery tracking (pairs with `/sc:pm`). |

## User-custom agent

| Agent | Purpose (inferred) |
|---|---|
| `mimir` | Custom agent for the **Mimir** knowledge-service suite (see the `mimir-*` skills: ingest / index / serve / chat / deploy-kind / egress-audit). Likely orchestrates or operates the Mimir RAG stack. _(inferred — content not readable)_ |

## Summary

- **18 agents total**: 17 standard SuperClaude framework agents + 1 user-custom (`mimir`).
- The SuperClaude set spans architecture (`system/backend/frontend/devops`),
  engineering quality (`quality/performance/refactoring/root-cause`), domain expertise
  (`python/security`), product/process (`requirements/pm`), communication
  (`technical-writer`), learning (`learning-guide/socratic-mentor`), and research/strategy
  (`deep-research-agent/business-panel-experts`).
