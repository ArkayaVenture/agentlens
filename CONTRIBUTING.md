# Contributing to AgentLens

Thanks for your interest! Contributions are welcome under the project's licence.

## Ground rules
- By contributing, you agree your contribution is licensed under **CC BY-NC 4.0**, and you grant
  **Arkaya Venture Limited** the right to also offer it under a commercial licence (dual-licensing).
- Keep the plugin **dependency-free** (Python standard library + the single-file dashboard). No
  `pip`/`npm` runtime deps, no hooks, no bundled MCP servers, no telemetry. These are deliberate
  security properties — PRs that add them will be declined.
- Keep all code **plain and auditable** — no obfuscation or minification.

## Workflow
1. Fork and branch from `main`.
2. Make focused changes. Update `CHANGELOG.md`.
3. Validate locally:
   ```bash
   claude plugin validate . --strict
   python3 -m py_compile plugins/AgentLens/platform/serve.py
   node --check <(python3 - <<'PY'
import re;print("\n".join(re.findall(r"<script>(.*?)</script>", open("plugins/AgentLens/dashboard/index.html").read(), re.S)))
PY
)
   ```
4. Open a PR describing what changed and why. The CI release gate runs `claude plugin validate --strict`.

## Security issues
Do **not** open public issues for vulnerabilities — see [SECURITY.md](./SECURITY.md).

## Questions / commercial use
hello@arkayaventure.com · https://arkayaventure.com
