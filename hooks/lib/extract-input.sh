#!/usr/bin/env bash
# Shared input extraction library for Ultra Framework hooks.
# Source this file: source "$(dirname "$0")/lib/extract-input.sh"

# Extract file_path from Edit/Write tool_input JSON.
extract_file_path() {
  local input="$1"
  local result
  result=$(printf '%s' "$input" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"//;s/"$//' || true)
  if [ -z "$result" ]; then
    result=$(printf '%s' "$input" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("tool_input",{}).get("file_path",""))' 2>/dev/null || true)
  fi
  printf '%s' "$result"
}

# Extract command from Bash tool_input JSON.
extract_command() {
  local input="$1"
  local result
  result=$(printf '%s' "$input" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"//;s/"$//' || true)
  if [ -z "$result" ]; then
    result=$(printf '%s' "$input" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("tool_input",{}).get("command",""))' 2>/dev/null || true)
  fi
  printf '%s' "$result"
}

# Extract exit_code from PostToolUse tool_result JSON.
extract_exit_code() {
  local input="$1"
  printf '%s' "$input" | python3 -c '
import sys, json
data = json.loads(sys.stdin.read())
print(data.get("tool_result", {}).get("exit_code", 0))
' 2>/dev/null || echo "0"
}
