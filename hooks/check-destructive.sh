#!/usr/bin/env bash
# PreToolUse hook for Bash: warns on destructive commands.
set -euo pipefail

# Read stdin.
INPUT=$(cat)

# Extract command.
CMD=$(printf '%s' "$INPUT" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"//;s/"$//' || true)

# Python fallback.
if [ -z "$CMD" ]; then
  CMD=$(printf '%s' "$INPUT" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("tool_input",{}).get("command",""))' 2>/dev/null || true)
fi

# If no command extracted, allow.
if [ -z "$CMD" ]; then
  echo '{}'
  exit 0
fi

CMD_LOWER=$(printf '%s' "$CMD" | tr '[:upper:]' '[:lower:]')

# Safe exceptions for build artifacts.
# Strip the rm command and its flags, then check if all remaining args are safe.
SAFE_TARGETS=$(printf '%s' "$CMD" | sed -E 's/^[[:space:]]*rm[[:space:]]+(-[a-zA-Z]+[[:space:]]+)*//;s/--recursive[[:space:]]*//;s/--force[[:space:]]*//')
if [ -n "$SAFE_TARGETS" ]; then
  SAFE_ONLY=true
  for target in $SAFE_TARGETS; do
    case "$target" in
      */node_modules|node_modules|*/dist|dist|*/__pycache__|__pycache__|*/build|build|*/coverage|coverage|*/.next|.next|*/.turbo|.turbo|*/.cache|.cache)
        ;;
      -*)
        ;;
      *)
        SAFE_ONLY=false
        break
        ;;
    esac
  done
  if [ "$SAFE_ONLY" = true ]; then
    echo '{}'
    exit 0
  fi
fi

# Destructive pattern checks.
WARN=""

if printf '%s' "$CMD" | grep -qE 'rm\s+(-[a-zA-Z]*r|--recursive)' 2>/dev/null; then
  WARN="Destructive: recursive delete (rm -r). Permanently removes files."
fi

if [ -z "$WARN" ] && printf '%s' "$CMD_LOWER" | grep -qE 'drop\s+(table|database)' 2>/dev/null; then
  WARN="Destructive: SQL DROP detected."
fi

if [ -z "$WARN" ] && printf '%s' "$CMD_LOWER" | grep -qE '\btruncate\b' 2>/dev/null; then
  WARN="Destructive: SQL TRUNCATE detected."
fi

if [ -z "$WARN" ] && printf '%s' "$CMD" | grep -qE 'git\s+push\s+.*(-f\b|--force)' 2>/dev/null; then
  WARN="Destructive: git force-push rewrites remote history."
fi

if [ -z "$WARN" ] && printf '%s' "$CMD" | grep -qE 'git\s+reset\s+--hard' 2>/dev/null; then
  WARN="Destructive: git reset --hard discards uncommitted changes."
fi

if [ -z "$WARN" ] && printf '%s' "$CMD" | grep -qE 'git\s+(checkout|restore)\s+\.' 2>/dev/null; then
  WARN="Destructive: discards all uncommitted working tree changes."
fi

if [ -z "$WARN" ] && printf '%s' "$CMD" | grep -qE 'git\s+branch\s+(-[a-zA-Z]*[dD]\b|--delete)' 2>/dev/null; then
  WARN="Destructive: branch deletion."
fi

if [ -z "$WARN" ] && printf '%s' "$CMD" | grep -qE 'git\s+(checkout|restore)\s+--\s+' 2>/dev/null; then
  WARN="Destructive: discards changes to specific files."
fi

if [ -z "$WARN" ] && printf '%s' "$CMD" | grep -qE 'git\s+clean\s+.*-f' 2>/dev/null; then
  WARN="Destructive: git clean removes untracked files."
fi

if [ -n "$WARN" ]; then
  WARN_ESCAPED=$(printf '%s' "$WARN" | sed 's/"/\\"/g')
  printf '{"permissionDecision":"ask","message":"[careful] %s"}\n' "$WARN_ESCAPED"
else
  echo '{}'
fi
exit 0
