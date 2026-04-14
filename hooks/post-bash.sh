#!/usr/bin/env bash
# PostToolUse hook for Bash: detects test failures and suggests ReAct approach.
set -euo pipefail

INPUT=$(cat)

# Extract exit code from hook input.
EXIT_CODE=$(printf '%s' "$INPUT" | python3 -c '
import sys, json
data = json.loads(sys.stdin.read())
print(data.get("tool_result", {}).get("exit_code", 0))
' 2>/dev/null || echo "0")

# Extract command from hook input.
CMD=$(printf '%s' "$INPUT" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' \
  | head -1 | sed 's/.*:[[:space:]]*"//;s/"$//' || true)

# Python fallback.
if [ -z "$CMD" ]; then
  CMD=$(printf '%s' "$INPUT" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("tool_input",{}).get("command",""))' 2>/dev/null || true)
fi

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
