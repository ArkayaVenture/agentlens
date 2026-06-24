# Projects Overview

## Who & what

Souman Trivedi is a McKinsey developer (souman_trivedi@external.mckinsey.com) working primarily on **Marvin** — an internal "digital twin" / agentic AI platform for McKinsey consultants ("your second brain") — and its surrounding ecosystem. The work spans four broad areas: (1) the Marvin platform itself (memory, surfaces, agents, skill marketplace, sandboxing), (2) Kubernetes / Namespace-as-a-Service (NaaS) and AWS infrastructure tooling, (3) security threat-modeling and review tooling, and (4) Claude Code / OpenClaw plugin and skill development. A large amount of work is done agentically with Claude Code, with recorded preferences captured in per-project memory files.

This overview is built from active repos under `IdeaProjects` and `IdeaProjects-external`, Claude Code project memory under `~/.claude/projects/*/memory/`, demo folders in `Downloads`, and work artifacts in `Documents`. Many repos are numbered/duplicated iterations (e.g. `marvin` through `marvin-8`, several `naas-ack-operator*`, `Davisfox*`, `nanoclaw-*`), indicating heavy experimentation and prototyping.

## Discovered projects / repos

Locations: `IJ` = `/Users/Souman_Trivedi/IdeaProjects`, `IJX` = `/Users/Souman_Trivedi/IdeaProjects-external`, `DL` = `/Users/Souman_Trivedi/Downloads`, `DOC` = `/Users/Souman_Trivedi/Documents`.

### Marvin platform (core)

| Name | Location | One-line purpose | Notes |
|---|---|---|---|
| marvin-7 | IJ | Marvin v1.1: digital-twin platform for consultants — iOS/macOS SwiftUI app + Go backend + MCP gateway (36 tools) + kind local cluster | Most complete; rich README. Active mem dir |
| marvin | IJ | Marvin monorepo: offline-first document sync (Go backend + Apple universal app), Bearer-token auth, brain service | Core repo |
| marvin-slack-connectivity | IJ | Multi-surface AI assistant (Slack Twin/Study + MCP + Voice) with per-user Hindsight memory, M365+Slack ingest | Active; large agent-session history |
| marvin-2 … marvin-8, marvin-6-scaffold, marvin-zero | IJ | Iteration/variant copies of the Marvin platform | Numbered experiments |
| marvin-mem, marvin-mem-v6, marvin-core-mem | IJ | Marvin memory subsystem (tiers L1–L4, Hindsight banks, integration strategy) | mem-v6 has rich memory notes (SPIFFE, digital-twin research) |
| marvin-capture | IJ | Capture/ingest component for Marvin | Has memory dir |
| marvin-skill-marketplace, marvin-marketplace.code-workspace | IJ | Skill/agent marketplace for Marvin (Okta-gated); migrations, client contract | Rich feedback memory |
| marvin-seals, marvin-seals.code-workspace | IJ | "Marvin SEALs": autonomous AI agent teams (18 seals) handling all Marvin engineering under a determinism doctrine; pre-empts Checkov/Wiz/SonarQube/Semgrep/Trivy/ZAP | Distinctive ops/security agent army |
| marvin-microvm-openclaw | IJ | MicroVM sandboxing for running OpenClaw under Marvin | Stub README |
| marvin-bots, marvin-teams-bot, marvin-teams-voice | IJ | Marvin bot surfaces (Teams text + voice) | |
| marvin-clawhub, marvin-clawhub-spec2 | IJ | "ClawHub" hub for Marvin/OpenClaw | |
| marvin-persona-builder | IJ | Persona construction for Marvin profiles | |
| marvin-cocierge-services | IJ | "Cocierge" services for Marvin | |
| marvin-lib, marvin-docs | IJ | Shared library; technical docs (ADRs, dev guide, specs, experiments) | |
| Marvin-1.1-design, Marvin-1.1-design-main, marvin-design-prototype | IJ | Marvin 1.1 design/prototype work | |
| marvin-code-beyond-ai-dlc | IJ | Marvin x "code beyond AI DLC" work | |
| Marvin Meeting Prep - Pressure Testing Demo | DL | Lovable/Vite + Supabase demo app (marvin-chat, speech-to-text, firm-experts edge functions); Playwright/Vitest | Demo |

### Kubernetes / NaaS / AWS infrastructure

| Name | Location | One-line purpose |
|---|---|---|
| naas-ack-operator, naas-ack-operator-fix, naas-ack-operator-v2 | IJ | "ACK Guardian" K8s operator: manages AWS IAM roles + EKS Pod Identity via official ACK IAM/EKS controllers |
| container-deployer-k8s-naas | IJ | "Namespace Guardian": K8s operator automating namespace lifecycle (RBAC, network policies, quotas, ArgoCD, Vault) |
| container-tf-patterns | IJ | Terraform patterns for container infra |
| container-eksv2-5-clusters | IJ | EKS 2.5 cluster definitions |
| CNG_CCP-addon_ack-aws-route53-controller, CNG_CCP-addon_naas-meta-controller, CNG_CCP-addon_secrets, CNG_CCP-ns_operator, CNG_CCP-customize_git_repos | IJ | CNG/CCP platform add-ons (Route53, NaaS meta-controller, secrets, namespace operator, git customization) |
| OFT-CFC-cluster-addons-profiles | IJ | Cluster add-on profiles |
| naas-operators.code-workspace | IJ | Workspace grouping the NaaS operators |
| terraform-aws-agentcore, aws-agentcore-playground, ideaforge-ai-agentcore | IJ | AWS Bedrock AgentCore experiments / Terraform |
| test-kube-builder | IJ | Kubebuilder operator scaffolding experiments |

### Security threat-modeling & review

| Name | Location | One-line purpose |
|---|---|---|
| ThreatLens skill suite | DOC `.cursor/.cursor/skills/` | Threat-modeling orchestrator: STRIDE analysis, DREAD ranking, attack-paths, actor-profiling, detection-engineering, tabletop-scenarios, system-schema synthesis |
| security-review skill | DOC `.cursor/.cursor/skills/security-review/` | Deep security-review skill with reference library (injection, XSS, SSRF, CSRF, crypto, supply-chain) + language (go/java/js/py) + infra (docker/k8s/terraform/ci-cd) guides |
| deepsec-scan, api-endpoint-scan | DOC `.cursor/.cursor/skills/` | Deep security scan + API endpoint scanning skills |
| marvin-cert-csrs | DOC | Certificate signing requests for Marvin |
| slack-admin-review | DOC | Digital-profile study / Slack admin review notes |
| (also: marvin-seals security pre-emption; SPIFFE/SPIRE zero-trust in marvin-mem-v6) | IJ | Security woven into the Marvin platform |

### Claude Code / OpenClaw tooling & plugins

| Name | Location | One-line purpose |
|---|---|---|
| openclaw | IJ | OpenClaw: self-hosted personal AI assistant reachable on WhatsApp/Telegram/Slack/Discord/Teams/Signal/iMessage etc.; gateway control plane |
| openclaw-msteams | IJX | MS Teams channel plugin for OpenClaw sending/receiving as a real M365 user (delegated Graph auth) |
| turbo-whisper | IJX | Open-source cross-platform voice dictation/STT app (Whisper) with a Claude Code plugin for voice input |
| nanoclaw, nanoclaw-docker-sandboxes, -matrix, -signal, -skills, -slack, -whatsapp, microclaw, grishahq-nanoClaw | IJX | "nanoClaw" minimal OpenClaw variants + channel adapters + sandboxes |
| Claw-ui, Claw-ui-spec2 | IJ | Next.js UI for Claw/Marvin ("ClawHub") |
| plugin-marketplace, forge-marketplace | IJ | Plugin / skill marketplaces |
| agent-power-pack, claude-power-pack, codex-power-pack | IJX | Agent/Claude/Codex "power pack" tool bundles |
| multi-claude | IJ | Multi-instance Claude orchestration |
| ms-365-mcp-server, mcp-neo4j-agent-memory, cdg-mcp-hub, mcp_jira | IJ/IJX | MCP servers (M365, Neo4j agent memory, hub, Jira) |

### Agentic PM / product & other

| Name | Location | One-line purpose |
|---|---|---|
| ideaforge-ai, ideaForgeAI-v2, ideaforgeai-analytics | IJ | "IdeaForge AI": multi-agent full-stack product-management platform (ideation→research→PRD→Jira), React/Vite |
| forge, forge-v1, forge-prototype-archive | IJ | "Forge" agent platform iterations |
| pm-agents, pm-agents-fix-tags, agents-at-scale, Council-of-personas | IJ | PM agent teams / persona councils / scaling agents |
| review-agent, review-agent-1, e2e-test-framework-draft | IJ | Automated code-review agents; E2E test framework |
| mck-enterprise-data-brain, mck-intelligence, mimir, keystone, k0 | IJ | McKinsey data/intelligence and platform experiments |
| code-beyond-ai-dlc(-aim), code-beyond-claude-superpowers, code-beyond-sprint-Intelligence-agent | IJ | "Code Beyond" AI development-lifecycle experiments |
| Davisfox, Davisfox-test-5, Nod.ie, thyme-bot, zaplie-bot, pennie-bot, xmeet-ai, TeamsMediaBot/teams-media-bot/mediabotv2, whatsapp-teams-bot-bridge | IJ/IJX | Assorted bot / media / bridge prototypes |
| avm-ai-tools, awesome-llm-apps, v0-agentic-ai-solution, Inception-Exploration, AtmanCode | IJ | Tooling, references, exploratory work |

### Loose migration/spec docs (in IJ root)

`MIGRATION_PLAN.md`, `MCKINSEY_MIGRATION_READINESS.md`, `MIGRATION_PHASE2_*` (script + mapping CSVs + source-sanitisation), `MARVIN_BOTS_WORKFLOW_FIXES.md`, `MARVIN_SURFACE_WORKFLOW_FIXES.md` — a Marvin bots/surface migration effort (phase-2 source sanitisation + mapping).

## Themes

- **Marvin platform** — the dominant theme: a consultant-facing digital-twin/"second brain" with per-user memory (Hindsight, L1–L4 tiers), multiple surfaces (Slack, MCP/IDE, Voice, Teams, iOS/macOS), a skill/agent marketplace, persona building, FDL orchestrator, and autonomous engineering agents ("SEALs"). Built and iterated across dozens of `marvin-*` repos.
- **K8s / NaaS infrastructure** — Kubernetes operators (Namespace Guardian, ACK Guardian) for AWS IAM/EKS Pod Identity, namespace lifecycle, RBAC, network policies, Vault, ArgoCD; Terraform patterns; EKS clusters; CNG/CCP platform add-ons; AWS Bedrock AgentCore.
- **Security** — threat-modeling (STRIDE/DREAD/attack-paths), security-review and deep-scan skills, certificate management, and proactive scanner pre-emption baked into the Marvin SEALs doctrine; SPIFFE/SPIRE zero-trust.
- **Claude tooling / OpenClaw plugins** — OpenClaw self-hosted assistant + channel plugins (Teams, Slack, WhatsApp, Signal, Matrix), nanoClaw variants, Claude Code power-packs, MCP servers, plugin/skill marketplaces, and turbo-whisper voice input.
- **Agentic PM / product** — IdeaForge AI and Forge multi-agent product-management platforms, PM agent teams, review agents.
- **Demos & artifacts** — Lovable/Supabase "Meeting Prep Pressure Testing" demo, meeting-prep coach prototypes, memory-architecture docs, NaaS diagrams, Product-to-Capability mapping, regulatory reports.

## Recorded preferences & feedback

Distilled from `~/.claude/projects/*/memory/feedback_*.md` and `project_*` memory files (names are self-describing; bodies are protected by access policy). Strong recurring signals:

- **Git discipline** — `feedback_no_direct_push_main` (no direct pushes to main), `feedback_marvin_pr_base` (PRs target a specific Marvin base branch), `feedback_seals_branching_rite` and `project_marketplace_git_policy` / `project_marvin_seals_git_policy` (defined branching/merge policies per repo). `project_marvin_migrations_renumber` notes care around migration numbering.
- **No emojis** — `feedback_no_emojis`: do not use emojis in output.
- **Parallelism by default** — `feedback_default_parallel_agent`: default to spawning parallel sub-agents; contrasted with `feedback_serial_workflow` (some flows must stay serial) — pick deliberately.
- **Use the right waiting/monitoring primitive** — `feedback_use_monitor_for_waits`: use the Monitor tool for waits rather than busy-looping; `feedback_per_minute_status`: give periodic (per-minute) status updates on long runs.
- **Genuine security findings only** — `feedback_security_findings_genuine`: report only real security findings, no padding/false positives.
- **No tactical busywork** — `feedback_no_tactical_work`: avoid low-value tactical tasks; focus on substantive work.
- **Infra safety** — `feedback_no_direct_cluster_exec` (don't exec directly against clusters), `feedback_relax_egress_netpols` (guidance on egress NetworkPolicy handling).
- **Memory tooling** — `feedback_use_hindsight_for_memory`: use Hindsight as the memory store. `feedback_loop_marvin_seals`: feedback loop conventions for the SEALs agents.

Project-context memory also captured: SPIFFE initiative, MarvinMem integration strategy, digital-twin research, Neptune infra, P3 triggers, agent-runtime & marketplace-client contracts, architecture diagrams, and an Okta marketplace integration.

> Note: memory file *bodies* under `~/.claude` could not be opened (access policy / mount limits), so the preferences above are inferred from the precise, self-describing memory filenames plus corroborating repo READMEs. Treat the exact wording as approximate.
