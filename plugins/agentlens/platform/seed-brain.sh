#!/usr/bin/env bash
# Seed (or refresh) a persistent agentlens folder from the plugin bundle.
#
# The plugin install directory may be read-only or get replaced on update, so the
# live brain lives in a stable, writable location (default ~/claude-projects/agentlens).
# Code/UI are always refreshed; accumulated knowledge & logs are preserved.
#
# Usage:  bash seed-brain.sh <SRC_BUNDLE_DIR> [DEST_BRAIN_DIR]
#   SRC  = the plugin bundle root (pass ${CLAUDE_PLUGIN_ROOT})
#   DEST = where the live brain should live (default ~/claude-projects/agentlens)
set -euo pipefail
SRC="${1:?usage: seed-brain.sh <SRC> [DEST]}"
DEST="${2:-$HOME/claude-projects/agentlens}"
SRC="$(cd "$SRC" && pwd)"
mkdir -p "$DEST"

echo "→ seeding agentlens"
echo "  from: $SRC"
echo "  into: $DEST"

# 1) Always refresh code + UI + doctrine + config (these are owned by the distribution).
for d in platform dashboard doctrine config BUILD-KIT skills; do
  [ -d "$SRC/$d" ] || continue
  mkdir -p "$DEST/$d"
  cp -R "$SRC/$d/." "$DEST/$d/"
done

# 2) Seed knowledge/projects only where missing — never clobber the user's accumulated brain.
for d in knowledge projects; do
  [ -d "$SRC/$d" ] || continue
  mkdir -p "$DEST/$d"
  ( cd "$SRC/$d" && find . -type f -print0 | while IFS= read -r -d '' f; do
      if [ ! -e "$DEST/$d/$f" ]; then mkdir -p "$DEST/$d/$(dirname "$f")"; cp "$f" "$DEST/$d/$f"; fi
    done )
done

# 3) Ensure the writable runtime structure exists.
mkdir -p "$DEST/logs" "$DEST/knowledge/ai-feed" "$DEST/knowledge/best-practices" "$DEST/inbox"
[ -f "$DEST/dashboard/feed.json" ] || echo '{"updated":null,"items":[]}' > "$DEST/dashboard/feed.json"
chmod +x "$DEST/platform/"*.sh 2>/dev/null || true

echo "  ✓ brain ready at: $DEST"
echo "$DEST"
