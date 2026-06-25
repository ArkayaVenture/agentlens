# Data-Handling Declaration & Conformance

**AgentLens** · © 2026 **Arkaya Venture Limited**, United Kingdom · Licensed CC BY-NC 4.0

## Declaration of purpose
AgentLens exists **only** to help you **learn from, understand, and improve the efficiency of your own
AI-coding work** — spotting bottlenecks, seeing where tokens and context go, and understanding how your
sessions and tools behave. It is a read-only mirror of data you already own. It is **not** a telemetry,
tracking, exfiltration, or advertising tool, and it has no such capability.

## Declaration: your data never leaves your machine
AgentLens reads your local session transcripts and Cursor store **with your own user permissions** and
serves a dashboard on **loopback only**. **No user data is transmitted off your machine — to Arkaya
Venture, to Anthropic, or to anyone.** There is no telemetry, no analytics, no account, and no
outbound user-data request anywhere in the product.

## Conformance — verified by ULTRACODE (generate → classify → adversarial → tournament)
We enumerated every network touchpoint in the shipped code (**generate**), classified each
(**classify**), challenged the claim "could any user data leave?" (**adversarial**), and kept the
strongest evidence (**tournament**).

| Touchpoint | Where | Classification | User data sent? |
|---|---|---|---|
| HTTP server bind | `serve.py` → `TCPServer(("127.0.0.1", port))` | **Loopback only** (never `0.0.0.0`) | No — not reachable off-host |
| Dashboard ↔ server | `index.html` `fetch()` → `/api/*`, `/feed.json` | **Loopback** (same machine) | No |
| Cursor reader | `cursor_parser.py` → `sqlite3` `mode=ro&immutable=1` + `urllib.parse` (string only) | **Local file read** (no network) | No |
| Config persistence | `POST /api/config` → local `config.json` on disk | **Local disk** | No |
| Chart library | `index.html` loads `chart.js` from `cdn.jsdelivr.net` | **Outbound CDN fetch of a JS library** | **No user data** — only the public library is downloaded; vendor it locally to be fully air-gapped |

**Adversarial findings:** no `requests`/`http.client`/`socket.connect`/`urlopen` to any remote host;
no analytics or tracking endpoints; no auth/account; the only off-host request is the public Chart.js
CDN, which transmits nothing about you. **Verdict: PASS — user data never leaves the machine.**

## Reproduce this audit yourself
```bash
# any outbound HTTP client or non-loopback bind? (expect: only the 127.0.0.1 bind)
grep -REn "requests|http\.client|urlopen|socket\.connect|0\.0\.0\.0" plugins/*/platform 2>/dev/null || \
  grep -REn "requests|http\.client|urlopen|socket\.connect|0\.0\.0\.0" platform
# every outbound URL in the dashboard (expect: only the chart.js CDN)
grep -oE "https?://[^\" )]+" plugins/*/dashboard/index.html 2>/dev/null || grep -oE "https?://[^\" )]+" dashboard/index.html
```

## Fully-offline mode (optional)
To remove even the Chart.js CDN call, download `chart.umd.js` next to `index.html` and change the
`<script src=…>` to a relative path. AgentLens then makes **zero** outbound requests.

_This declaration is shown in-product under **Privacy** and shipped in the repository so anyone can
verify and trust it before installing._
