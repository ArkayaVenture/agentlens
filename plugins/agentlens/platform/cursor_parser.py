#!/usr/bin/env python3
"""
cursor_parser.py — best-effort reader for Cursor's local state.

Cursor does NOT store sessions as readable transcripts; it uses SQLite databases
(`state.vscdb`) under ~/Library/Application Support/Cursor/User/{globalStorage,workspaceStorage/*}.
The schema is undocumented and shifts between versions, so this parser is intentionally defensive:
it opens each DB read-only, walks the key/value tables, and extracts what it can —
chats/composers, message counts, models used, and MCP/tool mentions.

Run standalone to inspect what's available (paste the output back to refine the parser):
    python3 cursor_parser.py            # JSON summary
    python3 cursor_parser.py --keys     # also dump the top-level storage keys it sees

Used by serve.py to power the dashboard's Cursor panel (/api/cursor).
"""
import os, json, glob, sqlite3, re, sys, datetime

CURSOR_USER = os.path.expanduser(os.environ.get(
    "AGENTLENS_CURSOR_USER", "~/Library/Application Support/Cursor/User"))

MODEL_RE = re.compile(r"(claude[-\w.]*|gpt[-\w.]*|o[134][-\w.]*|gemini[-\w.]*|grok[-\w.]*|deepseek[-\w.]*|llama[-\w.]*|mistral[-\w.]*|cursor-\w+)", re.I)
INTEREST_KEYS = ("composer", "aichat", "aiservice", "chat", "bubble", "prompt", "generation", "mcp")


def _dbs():
    out = []
    g = os.path.join(CURSOR_USER, "globalStorage", "state.vscdb")
    if os.path.isfile(g):
        out.append(("global", g))
    for p in glob.glob(os.path.join(CURSOR_USER, "workspaceStorage", "*", "state.vscdb")):
        out.append((os.path.basename(os.path.dirname(p)), p))
    return out


def _rows(con, table):
    try:
        cur = con.execute(f"SELECT key, value FROM {table}")
        for k, v in cur:
            yield k, v
    except Exception:
        return


def _as_text(v):
    if isinstance(v, bytes):
        try:
            return v.decode("utf-8", "replace")
        except Exception:
            return ""
    return v if isinstance(v, str) else ""


def parse_db(label, path, want_keys=False):
    info = {"workspace": label, "db": path, "composers": 0, "messages": 0,
            "models": set(), "mcp": set(), "toolMentions": 0, "lastTs": None, "keys": []}
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True, timeout=2)
    except Exception:
        return info
    try:
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in ("ItemTable", "cursorDiskKV"):
            if table not in tables:
                continue
            for k, v in _rows(con, table):
                kl = (k or "").lower()
                if want_keys and any(s in kl for s in INTEREST_KEYS):
                    info["keys"].append(k)
                if "composer" in kl or kl.startswith("composerdata"):
                    info["composers"] += 1
                if "bubbleid" in kl or "messagerequest" in kl:
                    info["messages"] += 1
                if not any(s in kl for s in INTEREST_KEYS):
                    continue
                txt = _as_text(v)
                if not txt:
                    continue
                for m in MODEL_RE.findall(txt)[:50]:
                    info["models"].add(m.lower())
                if "mcp" in txt.lower():
                    for mm in re.findall(r'"(?:server|name|mcpServer)"\s*:\s*"([\w.-]{2,40})"', txt)[:50]:
                        info["mcp"].add(mm)
                    info["mcp"].add("(mcp activity)")
                info["toolMentions"] += txt.count("tool_call") + txt.count("toolCall") + txt.count('"tool"')
                # try to read message arrays for a better count + timestamp
                try:
                    obj = json.loads(txt)
                except Exception:
                    obj = None
                if isinstance(obj, dict):
                    for key in ("messages", "conversation", "bubbles", "richText"):
                        arr = obj.get(key)
                        if isinstance(arr, list):
                            info["messages"] += len(arr)
                    for tk in ("lastUpdatedAt", "updatedAt", "createdAt", "timestamp"):
                        tv = obj.get(tk)
                        if isinstance(tv, (int, float)) and tv > 1e12:
                            ts = datetime.datetime.fromtimestamp(tv / 1000).isoformat(timespec="seconds")
                            if not info["lastTs"] or ts > info["lastTs"]:
                                info["lastTs"] = ts
    except Exception:
        pass
    finally:
        con.close()
    info["models"] = sorted(info["models"])[:20]
    info["mcp"] = sorted(info["mcp"])[:20]
    return info


def summarize(want_keys=False):
    dbs = _dbs()
    per = [parse_db(l, p, want_keys) for l, p in dbs]
    agg = {"cursorUserDir": CURSOR_USER, "exists": os.path.isdir(CURSOR_USER),
           "dbCount": len(dbs), "composers": 0, "messages": 0,
           "models": set(), "mcp": set(), "toolMentions": 0, "workspaces": []}
    for i in per:
        agg["composers"] += i["composers"]; agg["messages"] += i["messages"]
        agg["toolMentions"] += i["toolMentions"]
        agg["models"].update(i["models"]); agg["mcp"].update(i["mcp"])
        agg["workspaces"].append({"workspace": i["workspace"], "composers": i["composers"],
                                  "messages": i["messages"], "models": i["models"], "mcp": i["mcp"],
                                  "lastTs": i["lastTs"], "keys": i.get("keys", [])[:40]})
    agg["models"] = sorted(agg["models"])[:30]
    agg["mcp"] = sorted(agg["mcp"])[:30]
    agg["workspaces"].sort(key=lambda w: (w.get("lastTs") or ""), reverse=True)
    agg["note"] = ("Best-effort: Cursor's SQLite schema is undocumented. Counts are heuristic. "
                   "Run `python3 cursor_parser.py --keys` and share output to sharpen extraction.")
    return agg


if __name__ == "__main__":
    print(json.dumps(summarize(want_keys=("--keys" in sys.argv)), indent=2, default=str))
