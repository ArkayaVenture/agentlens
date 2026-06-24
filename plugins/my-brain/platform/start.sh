#!/usr/bin/env bash
# Start the my-brain dashboard on its dedicated port (default 7717).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${MYBRAIN_PORT:-7717}"

# stop a previous instance on this port (best effort)
if lsof -ti tcp:"$PORT" >/dev/null 2>&1; then
  echo "port $PORT busy — stopping previous instance"; lsof -ti tcp:"$PORT" | xargs kill -9 || true
fi

echo "starting my-brain dashboard on http://127.0.0.1:$PORT/"
exec python3 "$HERE/serve.py" --port "$PORT"
