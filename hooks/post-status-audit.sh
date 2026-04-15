#!/usr/bin/env bash
# PostToolUse hook for Edit/Write on STATUS.md: detects unauthorized gate advancement.
# Compares current gate_approvals against the session-start snapshot.
# If any gate advances to approved from a non-approved state, deny the edit.
#
# The hooks.template.json uses an `if` filter to limit this hook to STATUS.md edits.
# As a defense-in-depth measure (older Claude Code versions silently ignore `if`),
# this script also checks the target file path and exits early for non-STATUS.md edits.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATUS_FILE="${ROOT}/docs/STATUS.md"
SNAPSHOT_FILE="${ROOT}/.claude/.gate-snapshot"

# Load shared input extraction.
source "${SCRIPT_DIR}/lib/extract-input.sh"

# Read stdin (JSON with tool_input/tool_result).
INPUT=$(cat)

# Defense-in-depth: skip audit if the edited file is not STATUS.md.
# The `if` field in hooks config handles this for Claude Code >= v2.1.85,
# but older versions silently ignore `if` and fire this hook on all Edit/Write.
TARGET_FILE=$(extract_file_path "$INPUT")
case "$TARGET_FILE" in
  *STATUS.md) ;; # proceed with audit
  *)
    echo '{}'
    exit 0
    ;;
esac

# If snapshot or STATUS.md doesn't exist, skip audit.
if [ ! -f "$SNAPSHOT_FILE" ] || [ ! -f "$STATUS_FILE" ]; then
  echo '{}'
  exit 0
fi

# Extract gate value from a file.
extract_gate() {
  local file="$1"
  local gate="$2"
  grep -A20 "^gate_approvals:" "$file" | grep -m1 "${gate}:" | sed "s/.*${gate}:[[:space:]]*//" | sed 's/^"//;s/"$//' || true
}

# Check ALL gates for unauthorized advancement.
# Detect any transition TO approved from a non-approved state.
# This covers direct (pending→approved) and bypass (pending→blocked→approved) routes.
for gate in client_ready_for_dev brainstorm plan review qa security deploy dev_ready_for_client; do
  OLD=$(extract_gate "$SNAPSHOT_FILE" "$gate")
  NEW=$(extract_gate "$STATUS_FILE" "$gate")

  if [ "$OLD" != "approved" ] && [ "$OLD" != "" ] && [ "$NEW" = "approved" ]; then
    printf '{"permissionDecision":"deny","message":"[gate-tamper] %s gate advanced %s→approved without explicit user approval. Revert the change and request user approval via the /gate command."}\n' "$gate" "$OLD"
    exit 0
  fi
done

# No tampering detected. Update snapshot to reflect legitimate changes.
# Extract gate_approvals section for next comparison.
sed -n '/^gate_approvals:/,/^[a-z]/{ /^gate_approvals:/p; /^  /p; }' "$STATUS_FILE" > "$SNAPSHOT_FILE" 2>/dev/null || true

echo '{}'
exit 0
