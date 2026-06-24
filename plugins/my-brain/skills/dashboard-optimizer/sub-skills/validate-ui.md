# sub-skill: validate-ui  (the adversarial gate — MANDATORY)

No change ships unless ALL of these pass. If any fails, revert that change and log it.

## 1. Static checks
```bash
python3 -m py_compile /Users/Souman_Trivedi/claude-projects/my-brain/platform/serve.py
# extract inline <script> and syntax-check:
python3 - <<'PY'
import re;open('/tmp/app.js','w').write('\n;\n'.join(re.findall(r'<script>(.*?)</script>',open('/Users/Souman_Trivedi/claude-projects/my-brain/dashboard/index.html').read(),re.S)))
PY
node --check /tmp/app.js
```

## 2. Synthetic-fixture endpoint probes
Build a tiny fixture (claude-code + cowork dirs, a session with mixed tools incl. usage), launch the
server against it on a spare port, and assert:
- `/api/health` → has `version` and `features`.
- `/api/overview` → has `tokens.inTotal`, `provenance.{internal,firm,web,llm}`, `topSessions`, `live`.
- `/api/sessions` → rows carry `source`, `live`, `extPct`, `tokensInTotal`.
- `/api/session?file=…` → `meta.prov`, per-tool `tokens` + `origin`, timeline `turnTokens`.
- `/api/session?file=../../etc/passwd` → 400 (path-traversal guard intact).

## 3. Render check (best effort)
If a browser/screenshot tool is available, load `http://127.0.0.1:7717/`, screenshot each tab
(Overview, Sessions, Agents, Graph, AI Feed, Topology, ULTRACODE), and read the image back to
confirm no blank panels / no `undefined` / no JS error overlay. Otherwise assert each endpoint the
tabs depend on returns non-empty.

## 4. Regression guard
Diff the change; confirm no tab/route/feature was removed and the API stayed backward-compatible.

## Output
Return PASS/FAIL per check. On any FAIL → revert the offending diff, keep the rest, and record it.
