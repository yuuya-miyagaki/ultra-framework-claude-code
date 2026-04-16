#!/usr/bin/env bash
# PreCompact hook: blocks compaction when STATUS.md appears stale,
# allows when state is current.
#
# Block condition: STATUS.md was not modified within the last 5 minutes
# AND next_action or phase is non-empty (active work session).
# This catches cases where compaction would discard context before
# the agent has persisted its working state to STATUS.md.
#
# Exit codes:
#   0 = allow compaction
#   2 = block compaction (Claude Code PreCompact convention)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATUS_FILE="${ROOT}/docs/STATUS.md"

# If STATUS.md doesn't exist, allow silently.
if [ ! -f "$STATUS_FILE" ]; then
  echo '{}'
  exit 0
fi

# Extract a scalar value from YAML frontmatter.
extract_value() {
  local key="$1"
  grep -m1 "^${key}:" "$STATUS_FILE" | sed "s/^${key}:[[:space:]]*//" | sed 's/^"//;s/"$//' || true
}

MODE=$(extract_value "mode")
PHASE=$(extract_value "phase")
NEXT_ACTION=$(extract_value "next_action")

# Escape for JSON.
escape_for_json() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

# Staleness check: block compaction if STATUS.md was not recently updated.
# Default: 5 minutes (300 seconds). Override with ULTRA_PRECOMPACT_INTERVAL.
STALE_THRESHOLD="${ULTRA_PRECOMPACT_INTERVAL:-300}"
# Validate: fall back to default if non-numeric, zero, or negative.
case "$STALE_THRESHOLD" in
  ''|*[!0-9]*|0) STALE_THRESHOLD=300 ;;
esac
NOW=$(date +%s)
FILE_MTIME=$(stat -f %m "$STATUS_FILE" 2>/dev/null || stat -c %Y "$STATUS_FILE" 2>/dev/null || echo "$NOW")
ELAPSED=$(( NOW - FILE_MTIME ))

if [ "$ELAPSED" -gt "$STALE_THRESHOLD" ] && [ -n "$PHASE" ] && [ "$PHASE" != "null" ]; then
  # STATUS.md is stale and there is an active phase — block compaction.
  MSG="[PreCompact BLOCKED] STATUS.md was last updated ${ELAPSED}s ago (threshold: ${STALE_THRESHOLD}s). mode=${MODE} phase=${PHASE} | Update STATUS.md before compaction to preserve working state."
  ESCAPED=$(escape_for_json "$MSG")
  printf '{"decision":"block","hookSpecificOutput":{"message":"%s"}}\n' "$ESCAPED"
  exit 2
fi

# STATUS.md is current or no active phase — allow compaction with context.
MSG="[PreCompact] mode=${MODE} phase=${PHASE} | next: ${NEXT_ACTION} | STATUS.md is current. Compaction allowed."
ESCAPED=$(escape_for_json "$MSG")

printf '{"hookSpecificOutput":{"message":"%s"}}\n' "$ESCAPED"
exit 0
