#!/usr/bin/env bash
# PostToolUse hook for Edit/Write on STATUS.md: detects unauthorized gate advancement.
# Compares current gate_approvals against the session-start snapshot.
# If any gate advances to approved from a non-approved state, deny the edit.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATUS_FILE="${ROOT}/docs/STATUS.md"
SNAPSHOT_FILE="${ROOT}/.claude/.gate-snapshot"

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
