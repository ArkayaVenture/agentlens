#!/usr/bin/env python3
"""
Rich, read-only Cursor activity reader for AgentLens.

Parses Cursor's local SQLite stores (community-reverse-engineered schema; Cursor publishes
no official schema) entirely on-device with the user's own permissions. Read-only via
SQLite immutable=1 so it never locks or mutates Cursor's DB.

  globalStorage/state.vscdb  -> cursorDiskKV: composerData:<id>, bubbleId:<id>:<bid>
  workspaceStorage/<hash>/state.vscdb + workspace.json -> workspace attribution

Model names are rarely stored per message (best-effort); token coverage is partial.
Schema is feature-detected and degrades gracefully across Cursor versions.

Config: AGENTLENS_CURSOR_USER, AGENTLENS_CURSOR_MAXCONV (default 60), AGENTLENS_LIVE_WINDOW (900s)
"""
import os, glob, json, sqlite3, time
from urllib.parse import urlparse, unquote

USER_ROOT = os.path.expanduser(os.environ.get(
    "AGENTLENS_CURSOR_USER", "~/Library/Application Support/Cursor/User"))
GLOBAL_DB = os.path.join(USER_ROOT, "globalStorage", "state.vscdb")
WS_GLOB = os.path.join(USER_ROOT, "workspaceStorage", "*", "state.vscdb")
MAX_CONV = int(os.environ.get("AGENTLENS_CURSOR_MAXCONV", "60"))
LIVE_WINDOW = int(os.environ.get("AGENTLENS_LIVE_WINDOW", "900"))
MS_MIN = 1_000_000_000_000
PATH_KEYS = ("targetFile", "path", "file", "filePath", "relativeWorkspacePath", "targetDirectory")


def _open_ro(db):
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % db, uri=True)


def _jloads(v):
    if v is None:
        return None
    if isinstance(v, (bytes, bytearray)):
        v = v.decode("utf-8", "replace")
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return v
    return v


def _table(con, name):
    return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                       (name,)).fetchone() is not None


def _ms(v):
    try:
        v = int(v)
    except Exception:
        return None
    return v if v and v > MS_MIN else None


def _uri_path(uri):
    if not uri:
        return None
    if uri.startswith("file://"):
        return unquote(urlparse(uri).path)
    return uri


def _item(con, key):
    if not _table(con, "ItemTable"):
        return None
    row = con.execute("SELECT value FROM ItemTable WHERE key=?", (key,)).fetchone()
    return _jloads(row[0]) if row else None


def _workspaces():
    out = []
    for db in glob.glob(WS_GLOB):
        wsdir = os.path.dirname(db)
        folder = None
        wj = os.path.join(wsdir, "workspace.json")
        if os.path.exists(wj):
            try:
                j = json.load(open(wj, encoding="utf-8"))
                folder = _uri_path(j.get("workspace") or j.get("folder"))
            except Exception:
                pass
        ids = []
        try:
            con = _open_ro(db)
            cd = _item(con, "composer.composerData") or {}
            arr = cd.get("allComposers") or cd.get("composers") or (cd if isinstance(cd, list) else [])
            for c in (arr or []):
                cid = (c or {}).get("composerId") or (c or {}).get("id")
                if cid:
                    ids.append(cid)
            con.close()
        except Exception:
            pass
        out.append({"hash": os.path.basename(wsdir), "folder": folder, "ids": ids})
    return out


def _composer_folder_map(wss):
    m = {}
    for w in wss:
        for cid in w["ids"]:
            m.setdefault(cid, w["folder"])
    return m


def _bubble_ts(b):
    if not isinstance(b, dict):
        return None
    t = _ms(b.get("createdAt"))
    if t:
        return t
    ti = b.get("timingInfo") or {}
    for k in ("clientRpcSendTime", "clientSettleTime", "clientEndTime", "clientStartTime"):
        t = _ms(ti.get(k))
        if t:
            return t
    return None


def _double(v):
    p = _jloads(v)
    return p if isinstance(p, dict) else {}


def _tool(b):
    tfd = b.get("toolFormerData") or {}
    name = tfd.get("name")
    if not name:
        return None
    args = _double(tfd.get("params")) or _double(tfd.get("rawArgs"))
    files = [args[k] for k in PATH_KEYS if isinstance(args.get(k), str)]
    return {"name": name, "files": files}


def summarize():
    if not os.path.isfile(GLOBAL_DB):
        return {"exists": False, "note": "Cursor global DB not found at %s" % GLOBAL_DB, "conversations": []}
    try:
        con = _open_ro(GLOBAL_DB)
    except Exception as e:
        return {"exists": False, "error": str(e), "conversations": []}
    if not _table(con, "cursorDiskKV"):
        con.close()
        return {"exists": True, "note": "No cursorDiskKV table (old/new Cursor format).", "conversations": []}

    wss = _workspaces()
    fmap = _composer_folder_map(wss)
    composers = {}
    for key, val in con.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE 'composerData:%'"):
        cid = key.split(":", 1)[1]
        d = _jloads(val)
        if isinstance(d, dict) and d.get("fullConversationHeadersOnly"):
            composers[cid] = d
    try:
        total_bubbles = con.execute("SELECT COUNT(*) FROM cursorDiskKV WHERE key LIKE 'bubbleId:%'").fetchone()[0]
    except Exception:
        total_bubbles = 0

    def _key_ts(cd):
        return _ms(cd.get("lastUpdatedAt")) or _ms(cd.get("createdAt")) or 0
    ordered = sorted(composers.items(), key=lambda kv: _key_ts(kv[1]), reverse=True)
    now = time.time()
    convs = []
    all_tools = set()
    for i, (cid, cd) in enumerate(ordered):
        headers = cd.get("fullConversationHeadersOnly") or []
        files, tools, models = set(), [], set()
        first_ts = last_ts = None
        deep = i < MAX_CONV
        if deep:
            for h in headers:
                bid = h.get("bubbleId")
                if not bid:
                    continue
                row = con.execute("SELECT value FROM cursorDiskKV WHERE key=?",
                                  ("bubbleId:%s:%s" % (cid, bid),)).fetchone()
                if not row:
                    continue
                b = _jloads(row[0])
                if not isinstance(b, dict):
                    continue
                t = _bubble_ts(b)
                if t:
                    first_ts = t if first_ts is None else min(first_ts, t)
                    last_ts = t if last_ts is None else max(last_ts, t)
                for f in (b.get("relevantFiles") or []):
                    if isinstance(f, str):
                        files.add(f)
                tc = _tool(b)
                if tc:
                    tools.append(tc["name"]); all_tools.add(tc["name"]); files.update(tc["files"])
                po = b.get("providerOptions") or {}
                mv = (po.get("cursor") or {}).get("model") if isinstance(po, dict) else None
                if mv:
                    models.add(mv)
        lt = last_ts or _ms(cd.get("lastUpdatedAt"))
        convs.append({
            "id": cid,
            "title": cd.get("name") or "(untitled)",
            "workspace": fmap.get(cid) or "-",
            "model": (sorted(models)[0] if models else None),
            "messageCount": len(headers),
            "tools": sorted(set(tools)),
            "files": sorted(files)[:25],
            "firstTs": first_ts or _ms(cd.get("createdAt")),
            "lastTs": lt,
            "agentic": bool(cd.get("isAgentic")),
            "live": bool(lt and (now - lt / 1000.0) < LIVE_WINDOW),
            "deep": deep,
        })
    con.close()
    convs.sort(key=lambda c: c["lastTs"] or 0, reverse=True)
    return {
        "exists": True,
        "dbCount": len(wss),
        "workspaces": [w["folder"] for w in wss if w["folder"]],
        "composers": len(composers),
        "messages": total_bubbles,
        "conversations": convs,
        "tools": sorted(all_tools),
        "models": sorted({c["model"] for c in convs if c["model"]}),
        "live": sum(1 for c in convs if c["live"]),
        "note": "Read-only (immutable). Model/token coverage best-effort; deep-parsed %d recent conversations." % MAX_CONV,
    }


if __name__ == "__main__":
    import sys
    json.dump(summarize(), sys.stdout, indent=2, default=str)
