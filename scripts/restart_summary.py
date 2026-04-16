#!/usr/bin/env python3
"""Session restart structured summary generator.

Reads STATUS.md and produces a human-readable summary for session recovery.
Integrates status_doctor diagnostics when warnings or failures are present.

Usage:
    python3 scripts/restart_summary.py [--root <project_root>]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Import extraction utilities from check_status.py (same directory).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_status import (
    extract_approval_map,
    extract_current_refs,
    extract_frontmatter,
    extract_scalar_value,
    extract_session_history,
    read_text,
)
from status_doctor import run_doctor_collect


def build_summary(root: Path) -> str:
    """Build a structured restart summary from STATUS.md."""
    status_path = root / "docs" / "STATUS.md"
    text = read_text(status_path)
    frontmatter = extract_frontmatter(text)
    if frontmatter is None:
        return "ERROR: docs/STATUS.md is missing YAML frontmatter"

    # Core fields.
    mode = extract_scalar_value(frontmatter, "mode") or "unknown"
    phase = extract_scalar_value(frontmatter, "phase") or "unknown"
    task_type = extract_scalar_value(frontmatter, "task_type") or "unknown"
    task_size = extract_scalar_value(frontmatter, "task_size") or ""
    next_action = extract_scalar_value(frontmatter, "next_action") or "none"

    # Blockers.
    blockers = _extract_blockers(frontmatter)
    blockers_text = ", ".join(blockers) if blockers else "none"

    # Gates.
    approvals = extract_approval_map(frontmatter)
    gates_text = " ".join(
        f"{k}={v}" for k, v in approvals.items()
    ) if approvals else "none"

    # Active refs.
    refs = extract_current_refs(frontmatter)
    active_refs: list[str] = []
    for key, val in refs.items():
        if isinstance(val, list) and val:
            for item in val:
                active_refs.append(f"  - {key}: {item}")
        elif isinstance(val, str) and val != "null":
            active_refs.append(f"  - {key}: {val}")

    # Session history.
    history = extract_session_history(frontmatter)
    history_lines: list[str] = []
    for entry in history:
        date_str = entry.get("date", "?")
        h_mode = entry.get("mode", "?")
        h_phase = entry.get("phase", "?")
        h_note = entry.get("note", "")
        history_lines.append(f"  - {date_str} {h_mode}/{h_phase}: {h_note}")

    # Doctor diagnostics.
    warnings, failures = run_doctor_collect(root)
    doctor_count = len(warnings) + len(failures)

    # Build output.
    lines: list[str] = []
    lines.append("=== Session Restart Summary ===")

    task_info = f"{task_type}"
    if task_size:
        task_info += f" ({task_size})"
    lines.append(f"Mode: {mode} | Phase: {phase} | Task: {task_info}")
    lines.append(f"Next action: {next_action}")
    lines.append(f"Blockers: {blockers_text}")
    lines.append(f"Gates: {gates_text}")

    if active_refs:
        lines.append("Active refs:")
        lines.extend(active_refs)
    else:
        lines.append("Active refs: none")

    if history_lines:
        lines.append(f"Recent history (last {len(history_lines)}):")
        lines.extend(history_lines)
    else:
        lines.append("Recent history: none")

    if doctor_count > 0:
        details: list[str] = []
        for w in warnings:
            details.append(w)
        for f in failures:
            details.append(f)
        lines.append(f"Doctor warnings: {doctor_count} ({'; '.join(details)})")
    else:
        lines.append("Doctor warnings: 0")

    return "\n".join(lines)


def _extract_blockers(frontmatter: str) -> list[str]:
    """Extract blocker items from frontmatter."""
    blockers: list[str] = []
    in_block = False
    for line in frontmatter.splitlines():
        stripped = line.rstrip()
        if not in_block:
            if stripped.startswith("blockers:"):
                inline = stripped[len("blockers:"):].strip()
                if inline == "[]":
                    return []
                if inline == "":
                    in_block = True
                    continue
                # Inline non-empty value.
                blockers.append(inline)
                return blockers
            continue
        # Inside blockers block.
        s = stripped.strip()
        if s.startswith("- "):
            blockers.append(s[2:].strip().strip('"'))
        elif s and not stripped.startswith(" "):
            break
    return blockers


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Session restart summary generator"
    )
    parser.add_argument(
        "--root", default=".", help="Project root containing docs/STATUS.md"
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()

    status_path = root / "docs" / "STATUS.md"
    if not status_path.exists():
        print("ERROR: docs/STATUS.md not found")
        return 1

    summary = build_summary(root)
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
