#!/usr/bin/env bash
# PostToolUse hook for Bash: detects test failures and suggests ReAct approach.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load shared input extraction.
source "${SCRIPT_DIR}/lib/extract-input.sh"

INPUT=$(cat)

# Extract exit code from hook input.
EXIT_CODE=$(extract_exit_code "$INPUT")

# Extract command from hook input.
CMD=$(extract_command "$INPUT")

# Only act on test commands that failed.
if [ "$EXIT_CODE" = "0" ]; then
  echo '{}'
  exit 0
fi

IS_TEST=false
case "$CMD" in
  *vitest*|*jest*|*pytest*|*cargo\ test*|*go\ test*|*npm\ test*|*pnpm\ test*|*bun\ test*)
    IS_TEST=true
    ;;
esac

if [ "$IS_TEST" = true ]; then
  printf '{"hookSpecificOutput":{"message":"[ReAct] テスト失敗。Observe: エラー出力を読む → Think: 原因仮説1つ → Act: 最小変更1つ。複数変更を同時にしない。"}}\n'
else
  echo '{}'
fi
exit 0
