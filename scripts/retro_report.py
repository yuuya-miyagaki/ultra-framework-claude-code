#!/usr/bin/env python3
"""Retrospective report generator from STATUS.md + LEARNINGS.md + git log."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_status import (
    extract_approval_map,
    extract_frontmatter,
    extract_scalar_value,
    extract_session_history,
    read_text,
)
from learnings_search import parse_learnings, format_entry


def _gate_progress(approvals: dict[str, str]) -> str:
    """Format gate approvals as a progress line."""
    parts = []
    for gate, status in approvals.items():
        parts.append(f"{gate}: {status}")
    return " → ".join(parts)


def _recent_commits(root: Path, count: int = 10) -> list[str]:
    """Get recent git log --oneline."""
    try:
        result = subprocess.run(
            ["git", "log", f"--oneline", f"-{count}"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [f"  {line}" for line in result.stdout.strip().splitlines()]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


def _extract_blockers(frontmatter: str) -> list[str]:
    """Extract blockers from frontmatter."""
    blockers_val = extract_scalar_value(frontmatter, "blockers")
    if blockers_val and blockers_val.strip() == "[]":
        return []
    blockers: list[str] = []
    in_blockers = False
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if stripped.startswith("blockers:"):
            rest = stripped[len("blockers:"):].strip()
            if rest == "[]":
                return []
            in_blockers = True
            continue
        if in_blockers:
            if stripped.startswith("- "):
                blockers.append(stripped[2:].strip().strip('"'))
            elif not stripped.startswith("-") and ":" in stripped:
                break
    return blockers


def build_report(root: Path) -> str:
    """Build the retrospective report."""
    status_path = root / "docs" / "STATUS.md"
    if not status_path.exists():
        return ""

    text = read_text(status_path)
    frontmatter = extract_frontmatter(text)
    if frontmatter is None:
        return ""

    project = extract_scalar_value(frontmatter, "project_name") or "unknown"
    iteration = extract_scalar_value(frontmatter, "iteration") or "1"
    phase = extract_scalar_value(frontmatter, "phase") or "unknown"
    task_type = extract_scalar_value(frontmatter, "task_type") or "unknown"
    task_size = extract_scalar_value(frontmatter, "task_size") or "unknown"
    next_action = extract_scalar_value(frontmatter, "next_action") or "none"

    approvals = extract_approval_map(frontmatter)
    history = extract_session_history(frontmatter)
    blockers = _extract_blockers(frontmatter)

    lines: list[str] = []
    lines.append("=== Retrospective Report ===")
    lines.append(f"Project: {project} | Iteration: {iteration}")
    lines.append(f"Phase: {phase} | Task: {task_type} ({task_size})")
    lines.append(f"Next: {next_action}")
    lines.append("")

    # Session Timeline
    lines.append("--- Session Timeline ---")
    if history:
        for entry in history:
            date = entry.get("date", "?")
            mode = entry.get("mode", "?")
            ep = entry.get("phase", "?")
            note = entry.get("note", "")
            lines.append(f"  {date} {mode}/{ep}: {note}")
    else:
        lines.append("  none")
    lines.append("")

    # Gate Progress
    lines.append("--- Gate Progress ---")
    if approvals:
        lines.append(f"  {_gate_progress(approvals)}")
    else:
        lines.append("  none")
    lines.append("")

    # Learnings
    lines.append("--- Learnings ---")
    learnings_path = root / "docs" / "LEARNINGS.md"
    if learnings_path.exists():
        content = learnings_path.read_text(encoding="utf-8")
        entries = parse_learnings(content)
        if entries:
            for e in entries:
                lines.append(f"  {format_entry(e)}")
        else:
            lines.append("  none")
    else:
        lines.append("  none")
    lines.append("")

    # Recent Commits
    lines.append("--- Recent Commits ---")
    commits = _recent_commits(root)
    if commits:
        lines.extend(commits)
    else:
        lines.append("  none")
    lines.append("")

    # Blockers
    lines.append("--- Blockers & Residual Risks ---")
    if blockers:
        for b in blockers:
            lines.append(f"  - {b}")
    else:
        lines.append("  none")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate retrospective report")
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args()

    root = Path(args.root)
    status_path = root / "docs" / "STATUS.md"
    if not status_path.exists():
        print(f"ERROR: {status_path} not found", file=sys.stderr)
        return 1

    report = build_report(root)
    if report:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
