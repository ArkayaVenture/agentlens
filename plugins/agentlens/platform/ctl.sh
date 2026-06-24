#!/usr/bin/env bash
# agentlens service control — runs as a launchd user service (starts at logon, auto-restarts on crash).
#   ctl.sh start | stop | restart | status | logs
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABEL="com.agentlens.dashboard"
DEST="$HOME/Library/LaunchAgents/$LABEL.plist"
PORT="${AGENTLENS_PORT:-7717}"
U="$(id -u)"
cmd="${1:-status}"

free_port(){ lsof -ti tcp:"$PORT" 2>/dev/null | xargs kill -9 2>/dev/null || true; }

case "$cmd" in
  start|restart)
    [ -f "$DEST" ] || { echo "first run — bootstrapping…"; exec "$HERE/bootstrap.sh"; }
    launchctl bootout "gui/$U/$LABEL" 2>/dev/null || true
    free_port; sleep 1
    launchctl bootstrap "gui/$U" "$DEST" 2>/dev/null || launchctl load -w "$DEST"
    launchctl enable "gui/$U/$LABEL" 2>/dev/null || true
    sleep 1
    if curl -s "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1; then echo "✓ running → http://127.0.0.1:$PORT/"; else echo "starting… (give it a few seconds)"; fi ;;
  stop)
    launchctl bootout "gui/$U/$LABEL" 2>/dev/null || true
    free_port; echo "✓ stopped" ;;
  status)
    if launchctl print "gui/$U/$LABEL" >/dev/null 2>&1; then echo "service: loaded (starts at logon, auto-restarts)"; else echo "service: NOT loaded — run: bash ctl.sh start"; fi
    curl -s "http://127.0.0.1:$PORT/api/health" 2>/dev/null | python3 -c "import sys,json;d=json.load(sys.stdin);print('http: OK · version',d.get('version'),'· live-window',d.get('liveWindowSec'),'s · sources',[s['label'] for s in d.get('sources',[])])" 2>/dev/null || echo "http: not responding on $PORT" ;;
  logs)
    tail -n 40 "$HERE/../logs/dashboard.err.log" "$HERE/../logs/dashboard.out.log" 2>/dev/null || echo "no logs yet" ;;
  *) echo "usage: ctl.sh {start|stop|restart|status|logs}" ;;
esac
