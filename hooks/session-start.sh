#!/usr/bin/env bash
# SessionStart hook: reads STATUS.md and injects session context.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATUS_FILE="${ROOT}/docs/STATUS.md"

# If STATUS.md doesn't exist, allow silently.
if [ ! -f "$STATUS_FILE" ]; then
  echo '{}'
  exit 0
fi

# Initialize gate snapshot for tamper detection (used by post-status-audit.sh).
SNAPSHOT_DIR="${ROOT}/.claude"
SNAPSHOT_FILE="${SNAPSHOT_DIR}/.gate-snapshot"
mkdir -p "$SNAPSHOT_DIR"
sed -n '/^gate_approvals:/,/^[a-z]/{ /^gate_approvals:/p; /^  /p; }' "$STATUS_FILE" > "$SNAPSHOT_FILE" 2>/dev/null || true

# Extract a scalar value from YAML frontmatter.
extract_value() {
  local key="$1"
  grep -m1 "^${key}:" "$STATUS_FILE" | sed "s/^${key}:[[:space:]]*//" | sed 's/^"//;s/"$//' || true
}

MODE=$(extract_value "mode")
PHASE=$(extract_value "phase")
NEXT_ACTION=$(extract_value "next_action")

# Extract blockers (all list items, stop at next top-level key).
BLOCKERS=""
if grep -q "^blockers:[[:space:]]*\[\]" "$STATUS_FILE"; then
  BLOCKERS=""
elif grep -q "^blockers:" "$STATUS_FILE"; then
  BLOCKERS=$(sed -n '/^blockers:/,/^[a-z]/{/^blockers:/d;/^[a-z]/d;s/^[[:space:]]*- //p;}' "$STATUS_FILE" | awk 'BEGIN{ORS=""} {if(NR>1) printf "; "; printf "%s",$0}' || true)
fi

# Extract gate approvals.
GATES=""
GATE_SECTION=$(grep -A20 "^gate_approvals:" "$STATUS_FILE" || true)
if [ -n "$GATE_SECTION" ]; then
  for gate_key in client_ready_for_dev brainstorm plan review qa security deploy dev_ready_for_client; do
    gate_val=$(printf '%s' "$GATE_SECTION" | grep -m1 "${gate_key}:" | sed "s/.*${gate_key}:[[:space:]]*//" | sed 's/^"//;s/"$//' || true)
    if [ -n "$gate_val" ] && [ "$gate_val" != "null" ]; then
      GATES="${GATES} ${gate_key}=${gate_val}"
    fi
  done
fi

# Extract task_size for hook profile hint.
TASK_SIZE=$(extract_value "task_size")

# Build context message.
CONTEXT="[Ultra Framework] mode=${MODE} phase=${PHASE}"
if [ -n "$TASK_SIZE" ]; then
  CONTEXT="${CONTEXT} size=${TASK_SIZE}"
fi
if [ -n "$NEXT_ACTION" ] && [ "$NEXT_ACTION" != '""' ]; then
  CONTEXT="${CONTEXT} | next: ${NEXT_ACTION}"
fi
if [ -n "$BLOCKERS" ]; then
  CONTEXT="${CONTEXT} | BLOCKERS: ${BLOCKERS}"
fi
if [ -n "$GATES" ]; then
  CONTEXT="${CONTEXT} | gates:${GATES}"
fi

# Second-opinion file detection (PaC: enforced by check_framework_contract.py).
SECOND_OPINION_FILE="${ROOT}/docs/second-opinion.md"
if [ -f "$SECOND_OPINION_FILE" ]; then
  CONTEXT="${CONTEXT} | [BLOCKER] docs/second-opinion.md exists — read before proceeding"
fi

# Failure tracking detection.
FT_COUNT=$(grep -A3 "^failure_tracking:" "$STATUS_FILE" | grep -m1 "count:" | sed 's/.*count:[[:space:]]*//' | sed 's/^"//;s/"$//' || true)
if [ -n "$FT_COUNT" ] && [ "$FT_COUNT" != "null" ] && [ "$FT_COUNT" -ge 1 ] 2>/dev/null; then
  FT_GOAL=$(grep -A3 "^failure_tracking:" "$STATUS_FILE" | grep -m1 "goal:" | sed 's/.*goal:[[:space:]]*//' | sed 's/^"//;s/"$//' || true)
  CONTEXT="${CONTEXT} | [WARNING] failure tracking active: ${FT_GOAL} (${FT_COUNT}/3)"
fi

# Stuck detection: phase stagnation (all session_history entries in same phase).
HISTORY_PHASES=$(
  sed -n '/^session_history:/,/^[a-z]/{/phase:/p;}' "$STATUS_FILE" \
    | sed 's/.*phase:[[:space:]]*//' \
    | sed 's/^"//;s/"$//'
)
HISTORY_COUNT=$(printf '%s\n' "$HISTORY_PHASES" | grep -c . || true)
if [ "$HISTORY_COUNT" -ge 2 ]; then
  UNIQUE_PHASES=$(printf '%s\n' "$HISTORY_PHASES" | sort -u | wc -l | tr -d ' ')
  if [ "$UNIQUE_PHASES" -eq 1 ]; then
    STUCK_PHASE=$(printf '%s\n' "$HISTORY_PHASES" | head -1)
    CONTEXT="${CONTEXT} | [WARNING] stuck: ${HISTORY_COUNT} sessions in '${STUCK_PHASE}' phase — consider changing approach or escalating"
  fi
fi

# Phase-aware skill and rule hints.
HINT=""
case "$PHASE" in
  onboard|discovery|requirements|scope|acceptance|handover)
    HINT="skill: client-workflow"
    ;;
  brainstorm)
    HINT="skill: brainstorming / TDD必須 / エビデンスなき完了なし"
    ;;
  plan)
    HINT="skill: subagent-dev(計画) / Boundary Map必須 / TDD必須"
    ;;
  implement)
    HINT="skill: subagent-dev / TDD必須: テストを先に書け / エビデンスなき完了なし"
    ;;
  review)
    HINT="skill: subagent-dev(レビュー) / Review Army: diff-scope分析でspecialist起動"
    ;;
  qa)
    HINT="エビデンスなき完了なし / 再現・検証を実行せよ"
    ;;
  security)
    HINT="エビデンスなき完了なし / 残留リスクを記録せよ"
    ;;
  deploy)
    HINT="skill: deploy / Security Blockers確認必須 / 3回失敗=ゴールベースカウント"
    ;;
  ship|docs)
    HINT="skill: ship-and-docs / LEARNINGS更新必須(confidence付き)"
    ;;
  *)
    if [ -n "$PHASE" ]; then
      HINT="unknown phase: ${PHASE} — docs/STATUS.md を確認"
    fi
    ;;
esac
if [ -n "$HINT" ]; then
  CONTEXT="${CONTEXT} | ${HINT}"
fi

# Extract first 3 high-confidence learnings (confidence >= 8).
# Format assumption: each learning is a single line starting with "- [confidence:N] ".
# Multi-line learnings are truncated to the first line (by design).
LEARNINGS_FILE="${ROOT}/docs/LEARNINGS.md"
if [ -f "$LEARNINGS_FILE" ]; then
  LEARNINGS=$(
    grep -E '^[[:space:]]*-[[:space:]]*\[confidence:(8|9|10)\][[:space:]]+' "$LEARNINGS_FILE" \
      | head -3 \
      | sed -E 's/^[[:space:]]*-[[:space:]]*\[confidence:[0-9]+\][[:space:]]+/- /' \
      || true
  )
  if [ -n "$LEARNINGS" ]; then
    CONTEXT="${CONTEXT} | learnings: ${LEARNINGS}"
  fi
fi

# Locale hint.
CONTEXT="${CONTEXT} / ドキュメントは日本語"

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

ESCAPED=$(escape_for_json "$CONTEXT")

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$ESCAPED"
exit 0
