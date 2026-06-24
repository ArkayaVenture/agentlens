#!/usr/bin/env bash
# agentlens — portable, one-shot installer for team distribution.
# Self-locating: works for ANY user, wherever they unpack the folder. Run once:
#   bash <brain>/platform/bootstrap.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAIN="$(cd "$HERE/.." && pwd)"
LABEL="com.agentlens.dashboard"
PORT="${AGENTLENS_PORT:-7717}"
U="$(id -u)"
LA="$HOME/Library/LaunchAgents"
PLIST="$LA/$LABEL.plist"

echo "→ agentlens bootstrap  (brain: $BRAIN)"
mkdir -p "$LA" "$BRAIN/logs" "$BRAIN/knowledge/ai-feed" "$BRAIN/knowledge/best-practices" "$BRAIN/inbox"

# pick a working python3: prefer the system one, fall back to whatever's on PATH
PYBIN="/usr/bin/python3"
"$PYBIN" --version >/dev/null 2>&1 || PYBIN="$(command -v python3 || echo /usr/bin/python3)"
echo "  • python3: $PYBIN"

# Guard: a brain under a TCC-protected folder (~/Downloads, ~/Desktop, ~/Documents) can be read by
# Terminal but NOT by the background launchd service, which fails with EPERM. Warn loudly.
case "$BRAIN" in
  "$HOME/Downloads"/*|"$HOME/Desktop"/*|"$HOME/Documents"/*)
    echo "  ⚠ WARNING: brain is under a macOS privacy-protected folder ($BRAIN)."
    echo "    The always-on service may be denied file access there. Move it to e.g. ~/claude-projects/agentlens." ;;
esac

# 1) generate the LaunchAgent with THIS machine's absolute path (logon-start + auto-restart)
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>
    <string>$PYBIN</string><string>$BRAIN/platform/serve.py</string><string>--port</string><string>$PORT</string>
  </array>
  <key>WorkingDirectory</key><string>$BRAIN/platform</string>
  <key>EnvironmentVariables</key><dict><key>AGENTLENS_DASHBOARD</key><string>$BRAIN/dashboard</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$BRAIN/logs/dashboard.out.log</string>
  <key>StandardErrorPath</key><string>$BRAIN/logs/dashboard.err.log</string>
</dict></plist>
EOF
echo "  ✓ wrote $PLIST"

# 2) (re)load the service, freeing the port if an old instance holds it
launchctl bootout "gui/$U/$LABEL" 2>/dev/null || true
lsof -ti tcp:"$PORT" 2>/dev/null | xargs kill -9 2>/dev/null || true; sleep 1
launchctl bootstrap "gui/$U" "$PLIST" 2>/dev/null || launchctl load -w "$PLIST"
launchctl enable "gui/$U/$LABEL" 2>/dev/null || true

# 3) make the skills discoverable in Claude's slash menu
mkdir -p "$HOME/.claude/skills"
cp -R "$BRAIN/skills/." "$HOME/.claude/skills/" 2>/dev/null || true
echo "  ✓ skills installed to ~/.claude/skills"

sleep 1
if curl -s "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1; then echo "  ✓ service running → http://127.0.0.1:$PORT/"; else echo "  … service starting (check in a few seconds)"; fi
command -v open >/dev/null && open "http://127.0.0.1:$PORT/" || true

cat <<NEXT

✓ Service installed (starts at login, auto-restarts). Control it with:
    bash "$BRAIN/platform/ctl.sh" {start|stop|restart|status|logs}

NEXT — finish setup inside Claude Cowork (it can't be done from the shell):
  Open Cowork on this folder and run the "setup-agentlens" skill (or say:
  "set up the agentlens dashboard"). It will register the 3 scheduled jobs,
  initialise the second brain, and run the first enrichment + memory pass.
  Manual fallback: follow SETUP.md.
NEXT
