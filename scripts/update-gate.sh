#!/usr/bin/env bash
# Gate approval script — the ONLY authorized way to approve gates.
# Called by /gate command via Bash tool. Updates STATUS.md and .gate-snapshot atomically.
# Because this runs via Bash (not Edit/Write), it naturally bypasses post-status-audit.sh.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATUS_FILE="${ROOT}/docs/STATUS.md"
SNAPSHOT_DIR="${ROOT}/.claude"
SNAPSHOT_FILE="${SNAPSHOT_DIR}/.gate-snapshot"

GATE_NAME="${1:-}"

VALID_GATES="client_ready_for_dev brainstorm plan review qa security deploy dev_ready_for_client"

# --- Argument validation ---

if [ -z "$GATE_NAME" ]; then
  echo "Usage: bash scripts/update-gate.sh <gate-name>"
  echo ""
  echo "Valid gates: $VALID_GATES"
  echo ""
  # Show current gate status if STATUS.md exists.
  if [ -f "$STATUS_FILE" ]; then
    echo "Current gate status:"
    grep -A20 "^gate_approvals:" "$STATUS_FILE" | grep "^  " | sed 's/^  /  /' || true
  fi
  exit 1
fi

VALID=false
for g in $VALID_GATES; do
  if [ "$g" = "$GATE_NAME" ]; then
    VALID=true
    break
  fi
done

if [ "$VALID" = "false" ]; then
  echo "ERROR: Invalid gate name '$GATE_NAME'"
  echo "Valid gates: $VALID_GATES"
  exit 1
fi

if [ ! -f "$STATUS_FILE" ]; then
  echo "ERROR: docs/STATUS.md not found"
  exit 1
fi

# --- Read current value ---

CURRENT=$(grep -A20 "^gate_approvals:" "$STATUS_FILE" | grep -m1 "  ${GATE_NAME}:" | sed "s/.*${GATE_NAME}:[[:space:]]*//" | sed 's/^"//;s/"$//' || true)

if [ -z "$CURRENT" ]; then
  echo "ERROR: Gate '$GATE_NAME' not found in STATUS.md gate_approvals"
  exit 1
fi

if [ "$CURRENT" = "approved" ]; then
  echo "Gate '$GATE_NAME' is already approved. No change needed."
  exit 0
fi

if [ "$CURRENT" = "n/a" ]; then
  echo "ERROR: Gate '$GATE_NAME' is marked n/a (not applicable). Cannot approve."
  echo "If this gate should be active, first change it to 'pending'."
  exit 1
fi

# --- Context validation ---
# Delegate to check_status.py (sole source of truth for gate contracts).
# Phase order, prerequisites, task_size/task_type handling, and gate-ref
# consistency are all defined in check_status.py. No duplication here.
GATE_CHECK=$(python3 "${SCRIPT_DIR}/check_status.py" --root "$ROOT" --pre-approve-gate "$GATE_NAME" 2>&1)
GATE_CHECK_RC=$?
if [ $GATE_CHECK_RC -ne 0 ]; then
  echo "$GATE_CHECK"
  exit 1
fi
# Print any warnings from the pre-approval check.
if [ -n "$GATE_CHECK" ]; then
  echo "$GATE_CHECK"
fi

# --- Update STATUS.md ---

echo "[gate-approve] $GATE_NAME: $CURRENT → approved"

TMP="${STATUS_FILE}.tmp.$$"
sed "s/\(  ${GATE_NAME}:\).*/\1 approved/" "$STATUS_FILE" > "$TMP" && mv "$TMP" "$STATUS_FILE"

# --- Update snapshot atomically ---

mkdir -p "$SNAPSHOT_DIR"
sed -n '/^gate_approvals:/,/^[a-z]/{ /^gate_approvals:/p; /^  /p; }' "$STATUS_FILE" > "$SNAPSHOT_FILE" 2>/dev/null || true
# Preserve phase in snapshot (used by post-status-audit.sh for phase transition monitoring).
grep -m1 "^phase:" "$STATUS_FILE" >> "$SNAPSHOT_FILE" 2>/dev/null || true

echo "[gate-approve] STATUS.md and .gate-snapshot updated."

# --- Show result ---

echo ""
echo "Current gate status:"
grep -A20 "^gate_approvals:" "$STATUS_FILE" | grep "^  " | sed 's/^  /  /' || true
