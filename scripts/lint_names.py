#!/usr/bin/env python3
"""Cross-reference linter for skill, agent, and command names.

Checks that names referenced in check_framework_contract.py and CLAUDE.md
are consistent with the actual files in .claude/skills/, .claude/agents/,
and .claude/commands/.

Usage:
    python3 scripts/lint_names.py [--root <path>]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Filesystem extractors
# ---------------------------------------------------------------------------


def extract_skill_dirs(skills_root: Path) -> set[str]:
    """Extract skill directory names from .claude/skills/."""
    if not skills_root.is_dir():
        return set()
    return {
        d.name
        for d in skills_root.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    }


def extract_agent_files(agents_root: Path) -> set[str]:
    """Extract agent names (filename stems) from .claude/agents/."""
    if not agents_root.is_dir():
        return set()
    return {f.stem for f in agents_root.glob("*.md")}


def extract_command_files(commands_root: Path) -> set[str]:
    """Extract command names (filename stems) from .claude/commands/."""
    if not commands_root.is_dir():
        return set()
    return {f.stem for f in commands_root.glob("*.md")}


# ---------------------------------------------------------------------------
# Contract file extractors
# ---------------------------------------------------------------------------


def extract_contract_skills(contract_path: Path) -> set[str]:
    """Extract skill names from REQUIRED_SKILL_FILES in check_framework_contract.py."""
    if not contract_path.exists():
        return set()
    text = contract_path.read_text(encoding="utf-8")
    return set(re.findall(r'\.claude/skills/([a-z][\w-]*)/SKILL\.md', text))


def extract_contract_agents(contract_path: Path) -> set[str]:
    """Extract agent names from REQUIRED_AGENT_FILES in check_framework_contract.py."""
    if not contract_path.exists():
        return set()
    text = contract_path.read_text(encoding="utf-8")
    return set(re.findall(r'\.claude/agents/([a-z][\w-]*)\.md', text))


def extract_contract_commands(contract_path: Path) -> set[str]:
    """Extract command names from REQUIRED_COMMAND_FILES in check_framework_contract.py."""
    if not contract_path.exists():
        return set()
    text = contract_path.read_text(encoding="utf-8")
    return set(re.findall(r'\.claude/commands/([a-z][\w-]*)\.md', text))


# ---------------------------------------------------------------------------
# CLAUDE.md extractor
# ---------------------------------------------------------------------------


def extract_claude_md_skills(claude_md_path: Path) -> set[str]:
    """Extract skill names from CLAUDE.md ## Skills section.

    Only parses bullet-list lines (``- name, name, ...``) to avoid
    matching prose words in explanatory text.
    """
    if not claude_md_path.exists():
        return set()
    text = claude_md_path.read_text(encoding="utf-8")
    skills_section = re.search(
        r"## Skills\n(.*?)(?=\n## |\Z)", text, re.DOTALL
    )
    if not skills_section:
        return set()
    names: set[str] = set()
    for line in skills_section.group(1).splitlines():
        # Only process bullet-list lines (e.g., "- brainstorming, tdd, deploy")
        if not re.match(r"^\s*-\s+", line):
            continue
        # Strip the bullet prefix and split by comma.
        items = re.sub(r"^\s*-\s+", "", line)
        for item in items.split(","):
            token = item.strip()
            # Accept only kebab-case identifiers (skill names).
            if re.fullmatch(r"[a-z][a-z0-9-]*", token):
                names.add(token)
    return names


# ---------------------------------------------------------------------------
# Cross-check
# ---------------------------------------------------------------------------


def lint(root: Path) -> list[str]:
    """Run cross-reference lint and return sorted list of issues."""
    issues: list[str] = []

    contract_path = root / "scripts" / "check_framework_contract.py"

    # Sources of truth: actual directories.
    actual_skills = extract_skill_dirs(root / ".claude" / "skills")
    actual_agents = extract_agent_files(root / ".claude" / "agents")
    actual_commands = extract_command_files(root / ".claude" / "commands")

    # References from contract.
    contract_skills = extract_contract_skills(contract_path)
    contract_agents = extract_contract_agents(contract_path)
    contract_commands = extract_contract_commands(contract_path)

    # References from CLAUDE.md.
    claude_skills = extract_claude_md_skills(root / "CLAUDE.md")

    # --- Skills cross-check ---
    for skill in sorted(actual_skills - contract_skills):
        issues.append(
            f"skill '{skill}' exists on disk but missing from "
            f"check_framework_contract.py REQUIRED_SKILL_FILES"
        )
    for skill in sorted(contract_skills - actual_skills):
        issues.append(
            f"skill '{skill}' in check_framework_contract.py but "
            f"not found on disk (.claude/skills/{skill}/SKILL.md)"
        )

    # CLAUDE.md skills check (only if section exists).
    if claude_skills:
        for skill in sorted(actual_skills - claude_skills):
            issues.append(
                f"skill '{skill}' exists on disk but missing from "
                f"CLAUDE.md ## Skills section"
            )

    # --- Agents cross-check ---
    for agent in sorted(actual_agents - contract_agents):
        issues.append(
            f"agent '{agent}' exists on disk but missing from "
            f"check_framework_contract.py REQUIRED_AGENT_FILES"
        )
    for agent in sorted(contract_agents - actual_agents):
        issues.append(
            f"agent '{agent}' in check_framework_contract.py but "
            f"not found on disk (.claude/agents/{agent}.md)"
        )

    # --- Commands cross-check ---
    for cmd in sorted(actual_commands - contract_commands):
        issues.append(
            f"command '{cmd}' exists on disk but missing from "
            f"check_framework_contract.py REQUIRED_COMMAND_FILES"
        )
    for cmd in sorted(contract_commands - actual_commands):
        issues.append(
            f"command '{cmd}' in check_framework_contract.py but "
            f"not found on disk (.claude/commands/{cmd}.md)"
        )

    return sorted(issues)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-reference lint for skill/agent/command names",
    )
    parser.add_argument(
        "--root", type=Path, default=ROOT, help="Project root to lint",
    )
    args = parser.parse_args()

    issues = lint(args.root.resolve())
    if issues:
        for issue in issues:
            print(f"LINT: {issue}")
        return 1
    print("LINT: all names consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
