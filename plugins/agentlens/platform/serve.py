#!/usr/bin/env python3
"""
agentlens platform server  ·  dedicated local port (default 7717)

Serves the interactive "Command Center" dashboard AND a live monitoring API built by parsing
session transcripts from MULTIPLE sources on this machine:
  - claude-code : ~/.claude/projects
  - cowork      : ~/Library/Application Support/Claude/local-agent-mode-sessions
  - cursor      : ~/.cursor/projects   (best-effort; Cursor mostly uses SQLite)
Because YOU run this process, it reads those transcripts with your own permissions.

Every tool call is classified as INTERNAL (local machine: files, local bash, local search) or
EXTERNAL (web / other LLMs / cloud MCP connectors), so the UI can heat-map the internal-vs-external
data mix per session and workflow. Skills and MCP servers used are surfaced as semantics.

Zero dependencies (Python 3 stdlib only).

Env / flags:
  --port / AGENTLENS_PORT             (default 7717)
  AGENTLENS_CLAUDE_PROJECTS           (default ~/.claude/projects)
  AGENTLENS_COWORK_ROOT               (default ~/Library/Application Support/Claude/local-agent-mode-sessions)
  AGENTLENS_CURSOR_ROOT               (default ~/.cursor/projects)
  AGENTLENS_DASHBOARD                 (default ../dashboard)
  AGENTLENS_LIVE_WINDOW               (seconds; a session is "live" if touched within this; default 300)

Endpoints:
  /  /feed.json
  /api/health  /api/overview  /api/sessions  /api/session?file=NS  /api/agents
  /api/graph   /api/debug
"""
import argparse, http.server, socketserver, os, json, glob, datetime, functools, urllib.parse, traceback, time

PORT_DEFAULT = 7717
ROOT = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.normpath(os.environ.get("AGENTLENS_DASHBOARD", os.path.join(ROOT, "..", "dashboard")))
PROJECTS_DIR = os.path.expanduser(os.environ.get("AGENTLENS_CLAUDE_PROJECTS", "~/.claude/projects"))
COWORK_DIR = os.path.expanduser(os.environ.get("AGENTLENS_COWORK_ROOT", "~/Library/Application Support/Claude/local-agent-mode-sessions"))
CURSOR_DIR = os.path.expanduser(os.environ.get("AGENTLENS_CURSOR_ROOT", "~/.cursor/projects"))
SOURCES = [
    {"label": "claude-code", "root": PROJECTS_DIR, "flat": True},
    {"label": "cowork", "root": COWORK_DIR, "flat": False},
    {"label": "cursor", "root": CURSOR_DIR, "flat": False},
]
MAX_SESSIONS = 600
MAX_BYTES = 300 * 1024 * 1024
LIVE_WINDOW = int(os.environ.get("AGENTLENS_LIVE_WINDOW", "900"))  # a session is "live/active" if touched within 15 min
VERSION = "0.5-provenance4-tokens"

# --- AgentLens Pro engine (optional) -------------------------------------------------
# The advanced token-optimization & forecasting engine ships only in the private
# agentlens-core distribution. When absent (Community Edition), AgentLens falls back to
# the built-in basic heuristics below. This is the open-core extension point.
try:
    import agentlens_pro as _pro
    PRO = True
except Exception:
    _pro = None
    PRO = False


# Data-provenance taxonomy (generic + configurable; no hardcoded org/personal names).
#   local = this machine (files, local bash, local search)
#   mcp   = MCP connectors (sub-typed local vs external; default "unknown")
#   web   = public web (search / fetch / browser)
#   llm   = external LLM calls (vendor-identified)
PROV_CATS = ("local", "mcp", "web", "llm")
def _envset(name):
    return set(x.strip().lower() for x in os.environ.get(name, "").split(",") if x.strip())
# Configure which MCP servers count as local vs external (substring match). Default: unknown.
MCP_LOCAL = _envset("AGENTLENS_MCP_LOCAL")
MCP_EXTERNAL = _envset("AGENTLENS_MCP_EXTERNAL")
# Generic public web/data MCP vendors → treated as external MCP unless overridden.
WEB_MCP = _envset("AGENTLENS_WEB_MCP") or {"tavily", "context7", "fetch", "brave", "exa", "firecrawl", "serper"}
# Public LLM vendors (name substring -> display label). Identifies external-LLM contributors.
LLM_VENDORS = {"openai": "OpenAI", "gpt": "OpenAI", "anthropic": "Anthropic", "claude": "Anthropic (Claude)",
               "gemini": "Google (Gemini)", "vertex": "Google", "palm": "Google", "qwen": "Qwen (Alibaba)",
               "mistral": "Mistral", "mixtral": "Mistral", "llama": "Llama (Meta)", "bedrock": "AWS Bedrock",
               "perplexity": "Perplexity", "groq": "Groq", "cohere": "Cohere", "deepseek": "DeepSeek",
               "grok": "xAI (Grok)", "xai": "xAI", "ollama": "Ollama (local)", "lmstudio": "LM Studio (local)",
               "llamacpp": "llama.cpp (local)"}
def llm_vendor(s):
    s = (s or "").lower()
    for k, v in LLM_VENDORS.items():
        if k in s:
            return v
    return None
def mcp_subtype(server):
    s = (server or "").lower()
    if any(x in s for x in MCP_LOCAL):
        return "local"
    if any(x in s for x in MCP_EXTERNAL) or s in WEB_MCP or any(x in s for x in WEB_MCP):
        return "external"
    return "unknown"

# ---------------- helpers ----------------

def pretty_project(dirname):
    s = dirname.lstrip("-")
    for marker in ("Projects-", "Downloads-", "Documents-", "Desktop-", "src-", "code-"):
        if marker in s:
            return s.split(marker)[-1]
    return s

def _ts(o):
    return o.get("timestamp") or ""

def _iter_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return

def _content_items(msg):
    c = msg.get("content")
    if isinstance(c, list):
        return c
    if isinstance(c, str):
        return [{"type": "text", "text": c}]
    return []

def _short(s, n=160):
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[:n - 1] + "…"

def _duration(a, b):
    try:
        da = datetime.datetime.fromisoformat(a.replace("Z", "+00:00"))
        db = datetime.datetime.fromisoformat(b.replace("Z", "+00:00"))
        return max(0, int((db - da).total_seconds()))
    except Exception:
        return None

def _int(x):
    return x if isinstance(x, int) else 0

# -------- provenance (internal machine vs external web/LLM/cloud) --------

WEB_TOOLS = {"WebSearch", "WebFetch", "web_search", "web_fetch"}
_NET_BASH = ("curl ", "wget ", "http://", "https://", "npm ", "npx ", "pnpm ", "yarn ",
             "pip ", "pip3 ", "git clone", "git pull", "git push", "git fetch", "brew ",
             "apt ", "apt-get", "docker pull", "docker push", "kubectl ", "aws ", "gcloud ", "az ", "ssh ", "scp ")

def mcp_server(name):
    if name and name.startswith("mcp__"):
        parts = name.split("__")
        return parts[1] if len(parts) > 1 else "mcp"
    return None

def classify_tool(name, summary=""):
    """Generic data-provenance category: local | mcp | web | llm."""
    n = name or ""
    low = n.lower()
    srv = mcp_server(n)
    if srv:
        return "llm" if llm_vendor(srv) else "mcp"
    if n in WEB_TOOLS or low.startswith("web") or "chrome" in low or "browser" in low or "playwright" in low:
        return "web"
    if llm_vendor(low):
        return "llm"
    if n == "Bash":
        s = (summary or "").lower()
        return "web" if any(k in s for k in _NET_BASH) else "local"
    return "local"

def contributor_of(name, summary=""):
    """Return (category, contributor_label, subtype) for drill-down."""
    cat = classify_tool(name, summary)
    srv = mcp_server(name)
    if cat == "llm":
        return cat, (llm_vendor((srv or name)) or (srv or name)), "external"
    if cat == "mcp":
        sv = srv or name
        return cat, sv, mcp_subtype(sv)
    return cat, (name or "tool"), ("local" if cat == "local" else "external")

def _prov_rollup(prov):
    tot = sum(prov.values())
    ext = prov.get("mcp", 0) + prov.get("web", 0) + prov.get("llm", 0)
    return tot, ext

def usage_of(o):
    u = None
    msg = o.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("usage"), dict):
        u = msg["usage"]
    elif isinstance(o.get("usage"), dict):
        u = o["usage"]
    if not isinstance(u, dict):
        return (0, 0, 0, 0)
    def g(*keys):
        for k in keys:
            v = u.get(k)
            if isinstance(v, (int, float)):
                return int(v)
        return 0
    return (g("input_tokens", "inputTokens", "prompt_tokens"),
            g("output_tokens", "outputTokens", "completion_tokens"),
            g("cache_read_input_tokens", "cacheReadInputTokens", "cache_read"),
            g("cache_creation_input_tokens", "cacheCreationInputTokens", "cache_creation"))

# -------- source scanning + namespaced file resolution --------

def _ns(label, root, abspath):
    return label + "::" + os.path.relpath(abspath, root)

def resolve_file(f):
    """Map a namespaced file ('label::relpath') back to (abspath, root, label).
    Falls back to claude-code root for un-namespaced paths (backward compat)."""
    if "::" in f:
        label, rel = f.split("::", 1)
        for s in SOURCES:
            if s["label"] == label:
                return os.path.join(s["root"], rel), s["root"], label
    return os.path.join(PROJECTS_DIR, f), PROJECTS_DIR, "claude-code"

def _source_files(src):
    root = src["root"]
    if not os.path.isdir(root):
        return []
    if src.get("flat"):
        cand = glob.glob(os.path.join(root, "*", "*.jsonl"))
    else:
        cand = glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True)
    return [fp for fp in cand if (os.sep + "subagents" + os.sep) not in fp]

def list_main_sessions():
    out = []
    now = time.time()
    for src in SOURCES:
        label, root = src["label"], src["root"]
        for fp in _source_files(src):
            try:
                st = os.stat(fp)
            except Exception:
                continue
            rel = os.path.relpath(fp, root)
            parts = rel.split(os.sep)
            if label == "claude-code":
                proj = pretty_project(parts[0])
            elif label == "cowork":
                proj = "cowork"
            else:
                proj = (label if len(parts) <= 1 else label + ":" + parts[0][:12])
            out.append({
                "source": label, "project": proj, "projectDir": parts[0],
                "file": _ns(label, root, fp), "size": st.st_size,
                "mtime": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                "mtimeEpoch": st.st_mtime, "live": (now - st.st_mtime) < LIVE_WINDOW,
            })
    out.sort(key=lambda x: x["mtimeEpoch"], reverse=True)
    return out[:MAX_SESSIONS]

def subagent_abspaths(session_file):
    fp, root, label = resolve_file(session_file)
    base = fp[:-6] if fp.endswith(".jsonl") else fp
    return sorted(glob.glob(os.path.join(base, "subagents", "agent-*.jsonl")))

# -------- parsing --------

def light_parse(path):
    msgs = assistant = tools = thinking = 0
    by_tool = {}
    subagent_spawns = 0
    prov = {"local": 0, "mcp": 0, "web": 0, "llm": 0}
    skills = set(); mcps = set()
    models = set()
    first_ts = last_ts = None
    last_text = ""
    sid = None; cwd = None
    tin = tout = cread = ccreate = 0
    for o in _iter_lines(path):
        t = o.get("type"); ts = _ts(o)
        if ts:
            first_ts = first_ts or ts; last_ts = ts
        sid = sid or o.get("sessionId"); cwd = cwd or o.get("cwd")
        msg = o.get("message") or {}
        ua, ub, uc, ud = usage_of(o)
        tin += ua; tout += ub; cread += uc; ccreate += ud
        if msg.get("model"):
            models.add(msg["model"])
        if t in ("user", "assistant"):
            msgs += 1
        if t == "assistant":
            assistant += 1
            for it in _content_items(msg):
                k = it.get("type")
                if k == "tool_use":
                    tools += 1
                    name = it.get("name", "tool"); inp = it.get("input", {}) or {}
                    by_tool[name] = by_tool.get(name, 0) + 1
                    if name == "Task":
                        subagent_spawns += 1
                    prov[classify_tool(name, inp.get("command", "") if name == "Bash" else "")] += 1
                    srv = mcp_server(name)
                    if srv:
                        mcps.add(srv)
                    if name == "Skill":
                        skills.add(inp.get("skill") or inp.get("command") or "skill")
                elif k == "thinking":
                    thinking += 1
                elif k == "text" and it.get("text"):
                    last_text = it["text"]
    tot, ext = _prov_rollup(prov)
    return {
        "sessionId": sid, "cwd": cwd, "messages": msgs, "assistantMsgs": assistant,
        "toolCalls": tools, "thinking": thinking, "subagentSpawns": subagent_spawns,
        "byTool": by_tool, "models": sorted(models), "firstTs": first_ts, "lastTs": last_ts,
        "durationSec": _duration(first_ts, last_ts), "lastText": _short(last_text, 200),
        "tokensIn": tin, "tokensOut": tout, "cacheRead": cread, "cacheCreate": ccreate,
        "tokensInTotal": tin + cread + ccreate, "tokensTotal": tin + cread + ccreate + tout,
        "internalCalls": prov["local"], "externalCalls": ext, "prov": prov,
        "extPct": round(ext / tot, 3) if tot else 0,
        "skills": sorted(skills), "mcpServers": sorted(mcps),
    }

def sessions_enriched():
    rows = []
    for s in list_main_sessions():
        fp, _root, _label = resolve_file(s["file"])
        if s["size"] > MAX_BYTES:
            info = {"messages": "?", "toolCalls": "?", "note": "large file skipped in list"}
        else:
            info = light_parse(fp)
        s.update(info)
        s["subagentFiles"] = len(subagent_abspaths(s["file"]))
        rows.append(s)
    return rows

def _tool_summary(name, inp):
    if name == "Bash":
        return _short(inp.get("command", ""), 120)
    if name in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
        return _short(inp.get("file_path", inp.get("notebook_path", "")), 120)
    if name in ("Grep", "Glob"):
        return _short(inp.get("pattern", "") + ("  " + inp.get("path", "") if inp.get("path") else ""), 120)
    if name == "Task":
        return _short((inp.get("subagent_type", "") + ": " + inp.get("description", "")).strip(": "), 120)
    if name == "TaskCreate":
        return _short(inp.get("subject", ""), 120)
    if name == "Skill":
        return _short(inp.get("skill") or inp.get("command") or "", 120)
    if name in WEB_TOOLS or (name or "").startswith("mcp__"):
        return _short(inp.get("query") or inp.get("url") or json.dumps(inp)[:120], 120)
    for v in inp.values():
        if isinstance(v, str) and v:
            return _short(v, 120)
    return ""

def session_detail(session_file):
    fp, root, label = resolve_file(session_file)
    if not os.path.isfile(fp):
        return {"error": "not found", "file": session_file}
    timeline = []; by_tool = {}; spawns = []; pending = {}
    first_ts = last_ts = None; sid = cwd = None; models = set()
    tin = tout = cread = ccreate = 0; tturns = []
    prov = {"local": 0, "mcp": 0, "web": 0, "llm": 0}; skills = set(); mcps = set(); tool_origin = {}; tool_tokens = {}
    i = 0
    for o in _iter_lines(fp):
        t = o.get("type"); ts = _ts(o)
        if ts:
            first_ts = first_ts or ts; last_ts = ts
        sid = sid or o.get("sessionId"); cwd = cwd or o.get("cwd")
        side = bool(o.get("isSidechain"))
        msg = o.get("message") or {}
        if msg.get("model"):
            models.add(msg["model"])
        ua, ub, uc, ud = usage_of(o)
        tin += ua; tout += ub; cread += uc; ccreate += ud
        if ub:
            tturns.append(ub)
        if t == "assistant":
            turn_rows = []
            for it in _content_items(msg):
                k = it.get("type")
                if k == "text" and it.get("text"):
                    timeline.append({"i": i, "ts": ts, "lane": "assistant", "kind": "text",
                                     "summary": _short(it["text"]), "side": side}); i += 1
                elif k == "thinking":
                    timeline.append({"i": i, "ts": ts, "lane": "assistant", "kind": "thinking",
                                     "summary": _short(it.get("thinking", "(thinking)")), "side": side}); i += 1
                elif k == "tool_use":
                    name = it.get("name", "tool"); inp = it.get("input", {}) or {}
                    by_tool[name] = by_tool.get(name, 0) + 1
                    summ = _tool_summary(name, inp)
                    cat = classify_tool(name, inp.get("command", "") if name == "Bash" else "")
                    tool_origin[name] = cat
                    prov[cat] += 1
                    srv = mcp_server(name)
                    if srv:
                        mcps.add(srv)
                    if name == "Skill":
                        skills.add(inp.get("skill") or inp.get("command") or "skill")
                    row = {"i": i, "ts": ts, "lane": "tool", "kind": "tool_use", "tool": name,
                           "summary": summ, "side": side, "status": "pending", "origin": cat,
                           "mcp": srv, "turnTokens": 0}
                    timeline.append(row); idx = len(timeline) - 1
                    pending[it.get("id")] = idx; turn_rows.append((idx, name)); i += 1
                    if name == "Task":
                        spawns.append({"description": inp.get("description", ""),
                                       "subagent_type": inp.get("subagent_type", inp.get("subagentType", "")),
                                       "prompt": _short(inp.get("prompt", ""), 240), "ts": ts})
            # attribute this turn's marginal tokens (uncached input + output) to its tool calls
            cost = ua + ub
            if turn_rows and cost:
                share = cost / len(turn_rows)
                for ix, nm in turn_rows:
                    timeline[ix]["turnTokens"] = cost
                    tool_tokens[nm] = tool_tokens.get(nm, 0) + share
        elif t == "user":
            for it in _content_items(msg):
                if it.get("type") == "tool_result":
                    tid = it.get("tool_use_id"); err = bool(it.get("is_error"))
                    if tid in pending:
                        timeline[pending[tid]]["status"] = "error" if err else "ok"
                elif it.get("type") == "text" and it.get("text"):
                    timeline.append({"i": i, "ts": ts, "lane": "user", "kind": "user",
                                     "summary": _short(it["text"]), "side": side}); i += 1
        elif t == "system":
            timeline.append({"i": i, "ts": ts, "lane": "system", "kind": "system",
                             "summary": _short(str(msg.get("content") or o.get("content") or "system")),
                             "side": side}); i += 1

    sub_rows = []
    for sf in subagent_abspaths(session_file):
        li = light_parse(sf)
        sub_rows.append({"file": _ns(label, root, sf),
                         "agentId": os.path.basename(sf).replace("agent-", "").replace(".jsonl", ""),
                         "messages": li["messages"], "toolCalls": li["toolCalls"],
                         "byTool": li["byTool"], "lastTs": li["lastTs"], "durationSec": li["durationSec"],
                         "lastText": li["lastText"], "extPct": li["extPct"],
                         "internalCalls": li["internalCalls"], "externalCalls": li["externalCalls"]})

    tot, ext = _prov_rollup(prov)
    meta = {"sessionId": sid, "cwd": cwd, "file": session_file, "source": label,
            "firstTs": first_ts, "lastTs": last_ts, "durationSec": _duration(first_ts, last_ts),
            "models": sorted(models), "events": len(timeline),
            "toolCalls": sum(by_tool.values()), "subagentSpawns": len(spawns), "subagentFiles": len(sub_rows),
            "tokensIn": tin, "tokensOut": tout, "cacheRead": cread, "cacheCreate": ccreate,
            "inTotal": tin + cread + ccreate, "tokensTotal": tin + cread + ccreate + tout,
            "cacheHit": round(cread / (tin + cread + ccreate), 3) if (tin + cread + ccreate) else 0,
            "tokenTurns": tturns,
            "internalCalls": prov["local"], "externalCalls": ext, "prov": prov,
            "extPct": round(ext / tot, 3) if tot else 0,
            "skills": sorted(skills), "mcpServers": sorted(mcps)}
    flow = build_flow(meta, by_tool, spawns, sub_rows)
    return {"meta": meta, "timeline": timeline,
            "tools": [{"name": k, "count": v, "origin": tool_origin.get(k, classify_tool(k)),
                       "tokens": int(tool_tokens.get(k, 0))}
                      for k, v in sorted(by_tool.items(), key=lambda x: -x[1])],
            "spawns": spawns, "subagents": sub_rows, "flow": flow}

def build_flow(meta, by_tool, spawns, sub_rows):
    nodes = [{"id": "session", "label": (meta.get("sessionId") or "session")[:8], "type": "session",
              "tools": meta["toolCalls"]}]
    edges = []
    for idx, sp in enumerate(spawns):
        nid = f"sub{idx}"
        sub = sub_rows[idx] if idx < len(sub_rows) else None
        nodes.append({"id": nid, "type": "subagent",
                      "label": (sp.get("subagent_type") or "agent") + ": " + _short(sp.get("description", ""), 40),
                      "tools": (sub or {}).get("toolCalls", 0)})
        edges.append({"from": "session", "to": nid, "label": "spawn"})
    return {"nodes": nodes, "edges": edges}

def token_suggestions(tin, tout, cread, ccreate, rows):
    if PRO and hasattr(_pro, "token_suggestions"):
        try:
            return _pro.token_suggestions(tin, tout, cread, ccreate, rows)
        except Exception:
            pass
    out = []
    asst = sum(_int(r.get("assistantMsgs")) for r in rows) or 1
    tool_total = sum(_int(r.get("toolCalls")) for r in rows)
    cache_hit = cread / (tin + cread) if (tin + cread) > 0 else 0
    avg_in = tin / asst
    grand = tin + tout + cread
    ext = sum(_int(r.get("externalCalls")) for r in rows)
    intl = sum(_int(r.get("internalCalls")) for r in rows)
    if grand >= 30000 and cache_hit < 0.4:
        out.append({"level": "high", "text": f"Cache hit rate is only {cache_hit*100:.0f}%. Keep your system prompt / CLAUDE.md / early context stable and use --continue / --resume so prompt caching kicks in — cached input is ~10x cheaper."})
    elif cache_hit >= 0.6:
        out.append({"level": "info", "text": f"Good prompt-cache utilization ({cache_hit*100:.0f}% of input is cache reads)."})
    if avg_in >= 15000:
        out.append({"level": "high", "text": f"High context load (~{avg_in/1000:.0f}k input tokens per turn). Run /compact, prefer Grep/targeted reads, and push big exploration into sub-agents."})
    if (intl + ext) and (ext / (intl + ext)) > 0.5:
        out.append({"level": "med", "text": f"{ext/(intl+ext)*100:.0f}% of tool calls are external (web/LLM/cloud). Cache external results into the brain to cut repeat fetches and reduce dependence on the network."})
    if rows:
        top = max(rows, key=lambda r: _int(r.get("tokensTotal")))
        if _int(top.get("tokensTotal")) > 20000:
            out.append({"level": "med", "text": f"Heaviest session: '{top.get('project')}' (~{_int(top.get('tokensTotal'))/1000:.0f}k tokens). Split long sessions."})
    if tool_total and rows and tool_total / len(rows) >= 40:
        out.append({"level": "med", "text": f"~{tool_total/len(rows):.0f} tool calls per session. Batch independent calls into one turn."})
    if not out:
        out.append({"level": "info", "text": "Token usage looks healthy."})
    return out[:6]

def provenance_contributors(by_tool):
    """Group tool usage into provenance contributors for drill-down.
    by_tool: dict name->count (or list of {name,count}). Returns {cat: [{name,count,subtype}]}."""
    if isinstance(by_tool, dict):
        items = by_tool.items()
    else:
        items = [(t.get("name"), t.get("count", 0)) for t in (by_tool or [])]
    buckets = {c: {} for c in PROV_CATS}
    subtypes = {}
    for name, cnt in items:
        cat, label, sub = contributor_of(name)
        d = buckets[cat]
        d[label] = d.get(label, 0) + (cnt or 0)
        subtypes[(cat, label)] = sub
    out = {}
    for cat, d in buckets.items():
        out[cat] = sorted(
            [{"name": k, "count": v, "subtype": subtypes.get((cat, k), "")} for k, v in d.items()],
            key=lambda x: -x["count"])
    return out

# ---- user config (persisted locally; powers widget layouts + settings) ----
def _config_path():
    return os.environ.get("AGENTLENS_CONFIG", os.path.join(DASHBOARD_DIR, "config.json"))

def load_config():
    try:
        with open(_config_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg):
    try:
        with open(_config_path(), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        return True
    except Exception:
        return False

def _apply_config_sources():
    """Merge user-configured extra source roots (from config.json) into SOURCES at startup."""
    for sc in (load_config().get("sources") or []):
        lbl = (sc.get("label") or "").strip(); root = sc.get("root")
        if not lbl or not root:
            continue
        root = os.path.expanduser(root)
        found = False
        for x in SOURCES:
            if x["label"] == lbl:
                x["root"] = root; found = True
        if not found:
            SOURCES.append({"label": lbl, "root": root, "flat": bool(sc.get("flat", False))})

def _list_skill_names(d):
    out = []
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            fp = os.path.join(d, n)
            if os.path.isdir(fp) and os.path.isfile(os.path.join(fp, "SKILL.md")):
                out.append(n)
            elif n.endswith(".md"):
                out.append(n[:-3])
    return out

def topology():
    """Reflect the user's OWN environment (configurable). Nothing hardcoded."""
    cfg = load_config().get("topology", {})
    home = os.path.expanduser("~/.claude")
    skills = _list_skill_names(os.path.join(home, "skills"))
    agents = _list_skill_names(os.path.join(home, "agents"))
    commands = _list_skill_names(os.path.join(home, "commands"))
    rows = sessions_enriched()
    mcps = sorted({m for r in rows for m in (r.get("mcpServers") or [])})
    sub_agents = sorted({s for r in rows for s in (r.get("skills") or [])})
    projects = sorted({r["project"] for r in rows})
    sources = sorted({r.get("source", "?") for r in rows})
    return {
        "skills": cfg.get("skills") or skills,
        "agents": cfg.get("agents") or agents,
        "commands": cfg.get("commands") or commands,
        "mcp": [{"name": m, "subtype": mcp_subtype(m), "category": classify_tool("mcp__" + m + "__t")} for m in mcps],
        "projects": projects,
        "platforms": sources,
        "skillsUsed": sub_agents,
        "source": "live (from ~/.claude + your sessions)",
    }

# ---- datasets API (explorer + query browser) ----
def _ds_sessions():
    cols = ["project", "source", "sessionId", "lastTs", "messages", "toolCalls", "subagentFiles",
            "tokensInTotal", "tokensOut", "tokensTotal", "extPct", "durationSec", "live"]
    rows = []
    for r in sessions_enriched():
        rows.append({k: r.get(k) for k in cols} | {"file": r.get("file")})
    return {"columns": cols, "rows": rows}

def _ds_tools():
    agg = {}
    for r in sessions_enriched():
        for k, v in (r.get("byTool") or {}).items():
            cat, label, sub = contributor_of(k)
            a = agg.setdefault(k, {"tool": k, "count": 0, "category": cat, "contributor": label, "subtype": sub})
            a["count"] += v
    return {"columns": ["tool", "count", "category", "contributor", "subtype"],
            "rows": sorted(agg.values(), key=lambda x: -x["count"])}

def _ds_tokens_by_day():
    o = overview()
    return {"columns": ["date", "in", "out", "cache"], "rows": o.get("tokensByDay", [])}

def _ds_provenance():
    o = overview()
    rows = []
    for cat, lst in (o.get("provContributors") or {}).items():
        for c in lst:
            rows.append({"category": cat, "contributor": c["name"], "subtype": c.get("subtype", ""), "count": c["count"]})
    return {"columns": ["category", "contributor", "subtype", "count"],
            "rows": sorted(rows, key=lambda x: -x["count"])}

def _ds_cursor():
    try:
        import sys as _sys
        if ROOT not in _sys.path:
            _sys.path.insert(0, ROOT)
        import cursor_parser
        data = cursor_parser.summarize()
        rows = data.get("conversations", []) if isinstance(data, dict) else []
        return {"columns": ["title", "workspace", "model", "messageCount", "tools", "files", "lastTs", "agentic"],
                "rows": rows, "meta": {k: v for k, v in (data or {}).items() if k != "conversations"}}
    except Exception as e:
        return {"columns": [], "rows": [], "error": str(e)}

DATASETS = {
    "sessions": ("Sessions", _ds_sessions),
    "tools": ("Tool usage", _ds_tools),
    "tokensByDay": ("Tokens by day", _ds_tokens_by_day),
    "provenance": ("Provenance contributors", _ds_provenance),
    "cursor": ("Cursor conversations", _ds_cursor),
}

def datasets_index():
    return {"datasets": [{"name": k, "label": v[0]} for k, v in DATASETS.items()]}

def dataset(name):
    if name not in DATASETS:
        return {"error": "unknown dataset", "available": list(DATASETS)}
    return DATASETS[name][1]()

def overview():
    rows = sessions_enriched()
    total_tools = 0; by_tool = {}; subs = 0
    tin = tout = cread = ccreate = 0
    prov4 = {"local": 0, "mcp": 0, "web": 0, "llm": 0}
    by_day = {}; by_source = {}; live = 0
    for r in rows:
        if isinstance(r.get("toolCalls"), int):
            total_tools += r["toolCalls"]
        for k, v in (r.get("byTool") or {}).items():
            by_tool[k] = by_tool.get(k, 0) + v
        subs += r.get("subagentFiles", 0)
        for c in PROV_CATS:
            prov4[c] += _int((r.get("prov") or {}).get(c))
        by_source[r.get("source", "?")] = by_source.get(r.get("source", "?"), 0) + 1
        if r.get("live"):
            live += 1
        ri, ro, rc = _int(r.get("tokensIn")), _int(r.get("tokensOut")), _int(r.get("cacheRead"))
        cc = _int(r.get("cacheCreate"))
        tin += ri; tout += ro; cread += rc; ccreate += cc
        day = (r.get("lastTs") or "")[:10]
        if day:
            d = by_day.setdefault(day, {"date": day, "in": 0, "out": 0, "cache": 0})
            d["in"] += ri + rc + cc; d["out"] += ro; d["cache"] += rc
    projects = sorted({r["project"] for r in rows})
    series = sorted(by_day.values(), key=lambda x: x["date"])[-30:]
    tot = sum(prov4.values()); ext = prov4["mcp"] + prov4["web"] + prov4["llm"]
    top_sessions = sorted([r for r in rows if isinstance(r.get("tokensTotal"), int)],
                          key=lambda r: r.get("tokensTotal", 0), reverse=True)[:10]
    return {
        "sessions": len(rows), "projects": len(projects), "projectList": projects,
        "subagents": subs, "toolCalls": total_tools, "live": live, "bySource": by_source, "version": VERSION, "pro": PRO,
        "byTool": [{"name": k, "count": v, "origin": classify_tool(k)} for k, v in sorted(by_tool.items(), key=lambda x: -x[1])],
        "recent": rows[:14], "projectsDir": PROJECTS_DIR,
        "provenance": {"local": prov4["local"], "mcp": prov4["mcp"], "web": prov4["web"], "llm": prov4["llm"],
                       "external": ext, "extPct": round(ext / tot, 3) if tot else 0},
        "topSessions": [{"project": r.get("project"), "source": r.get("source"), "file": r.get("file"),
                         "sessionId": r.get("sessionId"), "tokensTotal": r.get("tokensTotal"), "tokensOut": r.get("tokensOut"),
                         "tokensInTotal": r.get("tokensInTotal"), "extPct": r.get("extPct"), "live": r.get("live"),
                         "lastTs": r.get("lastTs")} for r in top_sessions],
        "tokens": {"in": tin, "out": tout, "cacheRead": cread, "cacheCreate": ccreate,
                   "inTotal": tin + cread + ccreate, "total": tin + cread + ccreate + tout,
                   "cacheHit": round(cread / (tin + cread + ccreate), 3) if (tin + cread + ccreate) else 0},
        "tokensByDay": series,
        "provContributors": provenance_contributors(by_tool),
        "suggestions": token_suggestions(tin, tout, cread, ccreate, rows),
        "optimization": (_pro.optimization_report(rows, {"in": tin, "out": tout, "cacheRead": cread, "cacheCreate": ccreate}) if (PRO and hasattr(_pro, "optimization_report")) else None),
    }

def all_agents():
    out = []
    for s in list_main_sessions():
        _fp, root, label = resolve_file(s["file"])
        for sf in subagent_abspaths(s["file"]):
            li = light_parse(sf)
            out.append({"agentId": os.path.basename(sf).replace("agent-", "").replace(".jsonl", "")[:12],
                        "project": s["project"], "source": s.get("source"), "session": (s.get("sessionId") or "")[:12],
                        "file": _ns(label, root, sf), "messages": li["messages"],
                        "toolCalls": li["toolCalls"], "lastTs": li["lastTs"], "durationSec": li["durationSec"],
                        "lastText": li["lastText"], "extPct": li["extPct"]})
    out.sort(key=lambda x: (x["lastTs"] or ""), reverse=True)
    return out

def graph():
    rows = sessions_enriched()
    nodes = [{"id": "root", "type": "root", "label": "agentlens", "meta": {"sessions": len(rows)}}]
    edges = []; seen = set()
    for r in rows:
        p = r["project"]; pid = "p:" + p
        if pid not in seen:
            seen.add(pid)
            nodes.append({"id": pid, "type": "project", "label": p, "meta": {}})
            edges.append({"from": "root", "to": pid, "rel": "workflow"})
        sid = "s:" + r["file"]
        nodes.append({"id": sid, "type": "session", "label": (r.get("sessionId") or "")[:8], "file": r["file"],
                      "meta": {"tools": _int(r.get("toolCalls")), "subagents": r.get("subagentFiles", 0),
                               "tokens": _int(r.get("tokensInTotal")) + _int(r.get("tokensOut")),
                               "extPct": r.get("extPct", 0), "live": r.get("live", False),
                               "source": r.get("source"), "last": r.get("lastTs")}})
        edges.append({"from": pid, "to": sid, "rel": "has session"})
    return {"nodes": nodes, "edges": edges, "counts": {"projects": len(seen), "sessions": len(rows)}}

def debug_tokens(n=10):
    rows = list_main_sessions()[:n]
    grand = {"lines": 0, "assistantLines": 0, "usageLines": 0, "in": 0, "out": 0, "cacheRead": 0, "cacheCreate": 0}
    sample = None; per = []
    for s in rows:
        fp, _r, _l = resolve_file(s["file"])
        info = {"file": s["file"], "source": s.get("source"), "lines": 0, "usageLines": 0, "types": {}, "in": 0, "out": 0}
        for o in _iter_lines(fp):
            info["lines"] += 1; grand["lines"] += 1
            t = o.get("type") or "?"; info["types"][t] = info["types"].get(t, 0) + 1
            if t == "assistant":
                grand["assistantLines"] += 1
            a, b, c, d = usage_of(o)
            if a or b or c or d:
                info["usageLines"] += 1; grand["usageLines"] += 1
                info["in"] += a; info["out"] += b
                if sample is None:
                    msg = o.get("message") if isinstance(o.get("message"), dict) else {}
                    where = "message.usage" if isinstance(msg.get("usage"), dict) else ("usage" if isinstance(o.get("usage"), dict) else "?")
                    sample = {"where": where, "type": t, "topLevelKeys": sorted(list(o.keys()))[:20],
                              "usage": (msg.get("usage") if isinstance(msg.get("usage"), dict) else o.get("usage"))}
            grand["in"] += a; grand["out"] += b; grand["cacheRead"] += c; grand["cacheCreate"] += d
        per.append(info)
    return {"sources": [{"label": s["label"], "root": s["root"], "exists": os.path.isdir(s["root"])} for s in SOURCES],
            "sampledSessions": len(rows), "grand": grand, "sampleUsage": sample,
            "hint": "If grand.usageLines is 0 but assistantLines>0, the schema differs — paste sampleUsage back.",
            "perFile": per}

# ---------------- HTTP ----------------

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            u = urllib.parse.urlparse(self.path)
            if u.path == "/api/config":
                n = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(n) if n else b"{}"
                try:
                    cfg = json.loads(body or b"{}")
                except Exception:
                    return self._json({"error": "bad json"}, 400)
                ok = save_config(cfg)
                return self._json({"ok": ok})
            return self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def do_GET(self):
        try:
            u = urllib.parse.urlparse(self.path)
            p = u.path
            if p.startswith("/api/"):
                q = urllib.parse.parse_qs(u.query)
                if p == "/api/health":
                    return self._json({"status": "ok", "service": "agentlens", "version": VERSION,
                                       "time": datetime.datetime.now().isoformat(timespec="seconds"),
                                       "dashboardDir": DASHBOARD_DIR, "projectsDir": PROJECTS_DIR,
                                       "projectsExist": os.path.isdir(PROJECTS_DIR),
                                       "features": ["tokens", "provenance", "multisource", "live", "tokenAttribution", "topology", "datasets", "config"], "pro": PRO,
                                       "sources": [{"label": s["label"], "root": s["root"], "exists": os.path.isdir(s["root"])} for s in SOURCES],
                                       "liveWindowSec": LIVE_WINDOW})
                if p == "/api/overview":
                    return self._json(overview())
                if p == "/api/sessions":
                    return self._json(sessions_enriched())
                if p == "/api/session":
                    f = (q.get("file") or [""])[0]
                    if ".." in f or f.startswith("/"):
                        return self._json({"error": "bad path"}, 400)
                    return self._json(session_detail(f))
                if p == "/api/agents":
                    return self._json(all_agents())
                if p == "/api/topology":
                    return self._json(topology())
                if p == "/api/datasets":
                    return self._json(datasets_index())
                if p == "/api/dataset":
                    return self._json(dataset((q.get("name") or [""])[0]))
                if p == "/api/config":
                    return self._json(load_config())
                if p == "/api/graph":
                    return self._json(graph())
                if p == "/api/debug":
                    return self._json(debug_tokens())
                if p == "/api/cursor":
                    try:
                        import sys as _sys
                        if ROOT not in _sys.path:
                            _sys.path.insert(0, ROOT)
                        import cursor_parser
                        return self._json(cursor_parser.summarize())
                    except Exception as e:
                        return self._json({"exists": False, "error": str(e)})
                return self._json({"error": "unknown endpoint"}, 404)
            return super().do_GET()
        except Exception as e:
            self._json({"error": str(e), "trace": traceback.format_exc().splitlines()[-3:]}, 500)

    def log_message(self, fmt, *args):
        pass

_apply_config_sources()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("AGENTLENS_PORT", PORT_DEFAULT)))
    args = ap.parse_args()
    os.chdir(DASHBOARD_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    handler = functools.partial(Handler, directory=DASHBOARD_DIR)
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"agentlens → http://127.0.0.1:{args.port}/")
        print(f"  dashboard: {DASHBOARD_DIR}")
        for s in SOURCES:
            print(f"  source [{s['label']}]: {s['root']}  (exists={os.path.isdir(s['root'])})")
        print("  api: /api/health /api/overview /api/sessions /api/session?file= /api/agents /api/graph /api/topology /api/datasets /api/dataset /api/config")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")

if __name__ == "__main__":
    main()
