#!/usr/bin/env bash
# my-brain — install the always-on dashboard service.
#
# This is a thin, backward-compatible wrapper around the portable, self-locating
# installer in bootstrap.sh. It exists so older references (docs, the nightly
# dashboard-optimizer job) keep working. bootstrap.sh:
#   • generates a LaunchAgent with THIS machine's absolute path (no hard-coded user),
#   • frees port 7717 if a stale server holds it, (re)loads the service,
#   • installs the bundled skills into ~/.claude/skills, opens the dashboard.
#
# Run once on your Mac:  bash <brain>/platform/install-service.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$HERE/bootstrap.sh"
