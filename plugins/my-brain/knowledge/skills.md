# Skills Inventory

An inventory of all Claude / Cursor skills installed on this Mac, grouped by source.

> **Access note:** Skill contents under the user's protected home directory
> (`~/.claude/Claude Skills/`) could not be read directly in this session — only
> their file paths were enumerable (via `Glob`). For those, the **name** is exact
> (from the directory name) and the **purpose** is *inferred from naming + related
> memory files* and marked _(inferred)_. Skills under `Documents/.cursor/...` and the
> copy in `Downloads/.claude/...` were read in full, so their purposes are verbatim
> from each skill's `description:` frontmatter.

---

## 1. Global skills — `~/.claude/Claude Skills/`

These live in the user's global Claude config (`/Users/Souman_Trivedi/.claude/Claude Skills/`).
Contents were not directly readable; purposes below are inferred from skill names and
the project memory files (the `mimir-*` and `marvin-*` clusters correspond to active
IdeaProjects repos).

| Skill | Purpose (inferred) |
|---|---|
| `graphify` | Graph generation / visualization helper (likely turns data or relationships into graph/diagram output). |
| `mimir-chat` | **Mimir suite** — conversational / chat interface over the Mimir knowledge service. |
| `mimir-ingest` | **Mimir suite** — ingest documents/data into the Mimir store. |
| `mimir-index` | **Mimir suite** — build / refresh the Mimir search index. |
| `mimir-serve` | **Mimir suite** — run/serve the Mimir backend (query API). |
| `mimir-deploy-kind` | **Mimir suite** — deploy Mimir to a local KinD (Kubernetes-in-Docker) cluster. |
| `mimir-egress-audit` | **Mimir suite** — audit outbound network egress for the Mimir deployment. |
| `mck-core-meetings` | McKinsey "core meetings" helper (likely meeting prep/notes/summaries tooling). |
| `marvin-v1-orchestration` | **Marvin suite** — orchestration skill for the Marvin agent platform (v1). |
| `archflow` | Architecture-flow / workflow skill (ships a `GETTING_STARTED.md`; likely architecture diagramming or pipeline orchestration). |

**Notable cluster — `mimir-*` (6 skills):** a full self-hosted RAG/knowledge-service
lifecycle: `ingest` → `index` → `serve` → `chat`, plus ops skills `deploy-kind` and
`egress-audit`. Maps to the `marvin-mem-*` / Mimir IdeaProjects work.

**Notable cluster — `marvin-*`:** `marvin-v1-orchestration` ties into the larger
**Marvin** agent-platform work (many `marvin-*` repos under `~/IdeaProjects` and
associated project-memory files for marvin-5/6/7, marvin-capture, marvin-skill-marketplace).

---

## 2. Cursor skills — `~/Documents/.cursor/.cursor/skills/`

Read in full. This is a complete, self-contained **ThreatLens** threat-modeling suite
plus standalone security-scanning skills.

| Skill | Purpose (verbatim) |
|---|---|
| `threatlens-orchestrator` | Runs the full ThreatLens threat-modeling pipeline end-to-end: read-only probes of connected source MCPs (Confluence, GitHub), scouts product context, synthesizes a System Schema, profiles threat actors, enumerates STRIDE threats, ranks with DREAD, generates attack paths, produces detection use cases, authors tabletop scenarios, and persists the full report. Triggers on "threat model this app", "run a full threat model", etc. |
| `scout-product-context` | Discovers and summarizes product context for a repo (what it does, components, tech stack, integrations, data sensitivity, security-relevant files) so later phases have grounded inputs; can pull from read-only Confluence/GitHub MCPs. |
| `synthesize-system-schema` | Synthesizes a canonical System Schema (components, data flows, trust boundaries, Mermaid DFD) from a ProductContext — the structured input for STRIDE. |
| `actor-profiling` | Identifies relevant threat actors using HMG IS1/IS2 taxonomy (13 actor types), MITRE ATT&CK Groups, and STIX 2.1; produces a ThreatActorProfile enriching downstream phases. |
| `stride-analysis` | Enumerates actor-aware STRIDE threats given a System Schema + Actor Profile; each threat cites a component/data flow and a mitigation. |
| `dread-ranking` | Scores threats on the DREAD rubric (Damage, Reproducibility, Exploitability, Affected Users, Discoverability) with justifications; outputs a ranked list / heatmap. |
| `attack-paths` | Generates end-to-end attack paths from DREAD-ranked threats, mapping steps to MITRE ATT&CK techniques and attributing to likely actors (kill-chain narratives). |
| `detection-engineering` | Produces detection use cases (XQL logic targeting Cortex XSIAM) and monitoring alerts covering the highest-risk attack paths; each maps to an attack-path step and ATT&CK technique. |
| `tabletop-scenarios` | Generates facilitator-ready tabletop (TTX) scenarios from a threat model's attack paths + detections: narrative, inject timeline, expected responses, discussion questions, lessons. |
| `security-review` | Security code review for vulnerabilities (injection, XSS, auth, authz, crypto); triggers on "security review", "find vulnerabilities", "OWASP review"; confidence-based reporting. |
| `deepsec-scan` | Runs a `deepsec` security scan against the current repo end-to-end; outputs per-finding markdown, split summaries under `.deepsec/`, and a self-contained `REPORT.html`. Default agent/model `codex` + `gpt-5.5`; requires AI Gateway key; asks before copying reports / opening a GitHub issue. |
| `api-endpoint-scan` | Scans live web services for unauthenticated internet-exposed endpoints: exposed OpenAPI specs, open GraphQL introspection, dangerous HTTP methods, header gaps, TLS issues, CNAME takeover; single + batch. |

**Notable cluster — `threatlens` (10 skills):** a coherent end-to-end threat-modeling
pipeline orchestrated by `threatlens-orchestrator`, with each downstream stage as its own
skill: scout → schema → actor profiling → STRIDE → DREAD → attack-paths →
detection-engineering → tabletop-scenarios (+ `security-review`). Heavily standards-aligned
(STRIDE, DREAD, MITRE ATT&CK, STIX 2.1, HMG IS1/IS2) and tuned for **Cortex XSIAM / XQL**.

**Standalone security scanners:** `deepsec-scan` (repo-wide SAST-style scan with HTML report)
and `api-endpoint-scan` (external attack-surface / exposed-endpoint discovery).

---

## 3. Documents Claude skill — `~/Documents/Claude/.claude/skills/`

| Skill | Purpose (verbatim) |
|---|---|
| `wiz-vulnerability-cross-correlation` | Correlates **Wiz** vulnerability findings (per Wiz Project) with **Dynatrace** evidence and multi-cloud MCP context (AWS, GCP, Azure, OCI, Kubernetes), routing by the provider Wiz reports per finding. Delivers a fixed seven-table RCA (metadata through gaps). Related skills: `dynatrace-mcp` (deep DQL), `mcp-security-guardrails`. Use when investigating CVEs across Wiz + Dynatrace + clouds, given a Wiz project/product id, severity tiers, lookback windows, or for a single consolidated RCA + remediation plan. (`allowed-tools: Read, CallMcpTool`.) |

> Note: a verbatim copy of this skill also exists at
> `~/Downloads/.claude/skills/wiz-vulnerability-cross-correlation/` (with `reference.md`,
> `reference/query-templates.md`, and worked-example files), which is how the content was read.

---

## Summary counts

- **Global (`~/.claude/Claude Skills/`):** 10 skills (6× `mimir-*`, `graphify`, `mck-core-meetings`, `marvin-v1-orchestration`, `archflow`) — _content not readable; purposes inferred._
- **Cursor (`~/Documents/.cursor/...`):** 12 skills (10-skill ThreatLens suite + `deepsec-scan` + `api-endpoint-scan`) — _read in full._
- **Documents Claude:** 1 skill (`wiz-vulnerability-cross-correlation`) — _read in full._
- **Total: 23 skills.**

### Notable clusters at a glance
- **ThreatLens** (Cursor) — 10-stage STRIDE/DREAD/ATT&CK threat-modeling pipeline.
- **mimir-\*** (global) — 6-skill self-hosted RAG/knowledge-service lifecycle + ops.
- **marvin-\*** (global) — Marvin agent-platform orchestration (`marvin-v1-orchestration`).
- **Security scanning** (Cursor + Documents) — `deepsec-scan`, `api-endpoint-scan`, `wiz-vulnerability-cross-correlation`: a strong security/vuln-management theme across this developer's tooling.
