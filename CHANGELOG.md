# Changelog

All notable changes to **AgentLens** are documented here. This project follows
[Semantic Versioning](https://semver.org/). Setting `version` in `plugin.json`
controls when users receive updates.

## [1.0.0] — 2026-06-24
### Added
- Initial public release as a Claude Code / Cowork plugin under marketplace `arkaya-plugins`.
- `setup-agentlens` skill: one-run installer (login-start service on port 7717, seeds the brain to a
  non-protected path, registers the 3 scheduled ULTRACODE jobs, verifies health).
- `dashboard-optimizer` skill (opt-in nightly self-improvement with adversarial UI validation).
- Zero-dependency `serve.py` with live monitoring API (health, overview, sessions, session, agents,
  graph, debug, cursor); loopback-only bind + path-traversal guard.
- Single-file dashboard SPA: Overview, Sessions, Agents, Graph, Topology, ULTRACODE, AI Feed; tokens,
  4-way provenance, day/night themes.
- CC BY-NC 4.0 licence + commercial dual-licence, SECURITY.md, and CI validation.
