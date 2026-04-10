#!/usr/bin/env bash
# PreToolUse hook for Edit/Write: blocks code edits when plan gate is not approved.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATUS_FILE="${ROOT}/docs/STATUS.md"

# Read stdin (JSON with tool_input).
INPUT=$(cat)

# If STATUS.md doesn't exist, allow.
if [ ! -f "$STATUS_FILE" ]; then
  echo '{}'
  exit 0
fi

# Extract file_path from tool_input.
TARGET_FILE=$(printf '%s' "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"//;s/"$//' || true)

# Python fallback.
if [ -z "$TARGET_FILE" ]; then
  TARGET_FILE=$(printf '%s' "$INPUT" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("tool_input",{}).get("file_path",""))' 2>/dev/null || true)
fi

# If we can't determine target, allow.
if [ -z "$TARGET_FILE" ]; then
  echo '{}'
  exit 0
fi

# Always allow edits to docs, templates, scripts, and framework control files.
# Match both absolute (*/docs/*) and repo-relative (docs/*) paths.
case "$TARGET_FILE" in
  */docs/*|docs/*|*/templates/*|templates/*|*/scripts/*|scripts/*|*/hooks/*|hooks/*|*/.claude/*|.claude/*|*CLAUDE.md|*STATUS.md|*LEARNINGS.md|*.gitkeep)
    echo '{}'
    exit 0
    ;;
esac

# Extract mode and plan gate from STATUS.md frontmatter.
MODE=$(grep -m1 "^mode:" "$STATUS_FILE" | sed "s/^mode:[[:space:]]*//" | sed 's/^"//;s/"$//' || true)
PLAN_GATE=$(grep -A20 "^gate_approvals:" "$STATUS_FILE" | grep -m1 "plan:" | sed "s/.*plan:[[:space:]]*//" | sed 's/^"//;s/"$//' || true)

# Block code edits in Client mode.
if [ "$MODE" = "Client" ]; then
  printf '{"permissionDecision":"deny","message":"[gate] Client mode: code edits are blocked. Complete Client phases and get client_ready_for_dev approval first."}\n'
  exit 0
fi

# Block code edits when plan gate is not approved.
if [ "$PLAN_GATE" != "approved" ] && [ "$PLAN_GATE" != "n/a" ]; then
  printf '{"permissionDecision":"deny","message":"[gate] Plan gate is %s. Complete brainstorm and plan phases before editing code."}\n' "$PLAN_GATE"
  exit 0
fi

echo '{}'
exit 0
