#!/usr/bin/env python3
"""Reference drift auto-lint for Ultra Framework Claude Code.

Detects name/count/path mismatches between documentation surfaces and
actual files.  Exits 1 on any FAIL, 0 on WARNING-only or clean.

Usage:
    python3 scripts/check_reference_drift.py [--root <framework_root>]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _glob_stems(directory: Path, pattern: str) -> set[str]:
    """Return stem names of files matching *pattern* under *directory*."""
    return {p.stem for p in directory.glob(pattern)} if directory.is_dir() else set()


def _glob_dir_names(directory: Path) -> set[str]:
    """Return names of immediate child directories that contain SKILL.md."""
    if not directory.is_dir():
        return set()
    return {d.name for d in directory.iterdir() if d.is_dir() and (d / "SKILL.md").exists()}


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------

def check_agents(root: Path) -> tuple[list[str], list[str]]:
    """#1: agent names in routing.md vs .claude/agents/*.md"""
    failures: list[str] = []
    warnings: list[str] = []

    routing_path = root / ".claude" / "rules" / "routing.md"
    agents_dir = root / ".claude" / "agents"

    if not routing_path.exists():
        failures.append("routing.md not found — cannot check agent drift")
        return failures, warnings

    text = _read(routing_path)
    # Extract backtick-quoted names.
    referenced = set(re.findall(r"`([a-z][a-z0-9_-]*)`", text))
    # "brainstorm" is main context, not a subagent.
    main_context = {"brainstorm"}
    referenced_agents = referenced - main_context

    actual_agents = _glob_stems(agents_dir, "*.md")

    missing_files = referenced_agents - actual_agents
    unreferenced = actual_agents - referenced_agents

    for name in sorted(missing_files):
        failures.append(f"agent '{name}' referenced in routing.md but no .claude/agents/{name}.md")
    for name in sorted(unreferenced):
        failures.append(f"agent file .claude/agents/{name}.md exists but not referenced in routing.md")

    return failures, warnings


def check_skills(root: Path) -> tuple[list[str], list[str]]:
    """#2: skill names in CLAUDE.md vs .claude/skills/*/SKILL.md"""
    failures: list[str] = []
    warnings: list[str] = []

    claude_md = root / "CLAUDE.md"
    skills_dir = root / ".claude" / "skills"

    if not claude_md.exists():
        failures.append("CLAUDE.md not found — cannot check skill drift")
        return failures, warnings

    text = _read(claude_md)
    # Skills section: lines starting with "- " after "## Skills" header.
    in_skills = False
    referenced: set[str] = set()
    for line in text.splitlines():
        if line.strip().startswith("## Skills"):
            in_skills = True
            continue
        if in_skills and line.strip().startswith("##"):
            break
        if in_skills and line.strip().startswith("- "):
            # Comma-separated skill names on each bullet line.
            names = line.strip().lstrip("- ").split(",")
            for name in names:
                name = name.strip()
                if name:
                    referenced.add(name)

    actual_skills = _glob_dir_names(skills_dir)

    missing_dirs = referenced - actual_skills
    unreferenced = actual_skills - referenced

    for name in sorted(missing_dirs):
        failures.append(f"skill '{name}' listed in CLAUDE.md but no .claude/skills/{name}/SKILL.md")
    for name in sorted(unreferenced):
        failures.append(f"skill directory .claude/skills/{name}/ exists but not listed in CLAUDE.md")

    return failures, warnings


def check_commands_in_readme(root: Path) -> tuple[list[str], list[str]]:
    """#3: .claude/commands/*.md vs README.md command table"""
    failures: list[str] = []
    warnings: list[str] = []

    commands_dir = root / ".claude" / "commands"
    readme_path = root / "README.md"

    if not readme_path.exists() or not commands_dir.is_dir():
        return failures, warnings

    actual_commands = _glob_stems(commands_dir, "*.md")
    readme_text = _read(readme_path)

    # README command table uses "| `/name` |" pattern.
    readme_commands = set(re.findall(r"`/([a-z][a-z0-9_-]*)`", readme_text))

    missing_in_readme = actual_commands - readme_commands
    for name in sorted(missing_in_readme):
        warnings.append(f"command '/{name}' exists as file but not in README.md command table")

    return failures, warnings


def check_hooks(root: Path) -> tuple[list[str], list[str]]:
    """#4: hooks in settings.json/settings.local.json vs hooks/*.sh"""
    failures: list[str] = []
    warnings: list[str] = []

    hooks_dir = root / "hooks"
    settings_candidates = [
        root / ".claude" / "settings.json",
        root / ".claude" / "settings.local.json",
    ]
    # Also check templates/hooks.template.json for the framework root.
    template_settings = root / "templates" / "hooks.template.json"
    if template_settings.exists():
        settings_candidates.append(template_settings)

    settings_path = None
    for candidate in settings_candidates:
        if candidate.exists():
            settings_path = candidate
            break

    if settings_path is None or not hooks_dir.is_dir():
        return failures, warnings

    try:
        settings = json.loads(_read(settings_path))
    except (json.JSONDecodeError, OSError):
        warnings.append(f"could not parse {settings_path.name}")
        return failures, warnings

    hooks_config = settings.get("hooks", {})
    referenced_scripts: set[str] = set()

    for _event, matchers in hooks_config.items():
        if not isinstance(matchers, list):
            continue
        for matcher in matchers:
            for hook in matcher.get("hooks", []):
                cmd = hook.get("command", "")
                # Extract "hooks/foo.sh" from "bash hooks/foo.sh"
                match = re.search(r"hooks/([a-z][a-z0-9_-]*\.sh)", cmd)
                if match:
                    referenced_scripts.add(match.group(1))

    actual_scripts = {p.name for p in hooks_dir.glob("*.sh")}

    missing_files = referenced_scripts - actual_scripts
    for name in sorted(missing_files):
        failures.append(f"hook script '{name}' registered in {settings_path.name} but hooks/{name} does not exist")

    return failures, warnings


def check_template_profiles(root: Path) -> tuple[list[str], list[str]]:
    """#5: template profile definitions vs actual template files"""
    failures: list[str] = []
    warnings: list[str] = []

    profiles_dir = root / "templates" / "profiles"
    if not profiles_dir.is_dir():
        return failures, warnings

    for profile_path in sorted(profiles_dir.glob("*.json")):
        try:
            profile = json.loads(_read(profile_path))
        except (json.JSONDecodeError, OSError):
            warnings.append(f"could not parse profile {profile_path.name}")
            continue

        # Drift lint checks framework-owned files only.
        # Profile 'recommended' entries are project-level guidance and may not
        # exist in the framework root, so only check 'required' paths.
        for rel_path in profile.get("required", []):
            full = root / rel_path
            if not full.exists():
                warnings.append(
                    f"profile '{profile_path.stem}' references '{rel_path}' but file does not exist"
                )

    return failures, warnings


def check_readme_counts(root: Path) -> tuple[list[str], list[str]]:
    """#6: README.md counts like '10 bounded specialist roles' vs actual"""
    failures: list[str] = []
    warnings: list[str] = []

    readme_path = root / "README.md"
    if not readme_path.exists():
        return failures, warnings

    text = _read(readme_path)

    # Agents count: "# N bounded specialist roles" or "N agents"
    agents_dir = root / ".claude" / "agents"
    agent_match = re.search(r"#\s*(\d+)\s+bounded specialist roles", text)
    if agent_match and agents_dir.is_dir():
        stated = int(agent_match.group(1))
        actual = len(list(agents_dir.glob("*.md")))
        if stated != actual:
            warnings.append(f"README says {stated} agents but found {actual}")

    return failures, warnings


def check_template_version(root: Path) -> tuple[list[str], list[str]]:
    """#7: framework_version in templates vs FRAMEWORK_VERSION in check_framework_contract.py"""
    failures: list[str] = []
    warnings: list[str] = []

    contract_path = root / "scripts" / "check_framework_contract.py"
    if not contract_path.exists():
        return failures, warnings

    contract_text = _read(contract_path)
    version_match = re.search(r'FRAMEWORK_VERSION\s*=\s*"([^"]+)"', contract_text)
    if not version_match:
        return failures, warnings

    canonical_version = version_match.group(1)

    templates_dir = root / "templates"
    if not templates_dir.is_dir():
        return failures, warnings

    for tmpl in sorted(templates_dir.glob("*.template.md")):
        tmpl_text = _read(tmpl)
        for m in re.finditer(r'framework_version:\s*"([^"]+)"', tmpl_text):
            if m.group(1) != canonical_version:
                warnings.append(
                    f"{tmpl.name} has framework_version '{m.group(1)}' "
                    f"but check_framework_contract.py says '{canonical_version}'"
                )

    return failures, warnings


def check_session_start_hints(root: Path) -> tuple[list[str], list[str]]:
    """#8: skill names in session-start.sh case statement vs actual skills"""
    failures: list[str] = []
    warnings: list[str] = []

    ss_path = root / "hooks" / "session-start.sh"
    skills_dir = root / ".claude" / "skills"

    if not ss_path.exists() or not skills_dir.is_dir():
        return failures, warnings

    text = _read(ss_path)
    actual_skills = _glob_dir_names(skills_dir)

    # Extract skill names from HINT lines: "skill: name" or "skill: name("
    hint_skills: set[str] = set()
    for m in re.finditer(r'skill:\s*([a-z][a-z0-9_-]*)', text):
        hint_skills.add(m.group(1))

    missing = hint_skills - actual_skills
    for name in sorted(missing):
        warnings.append(
            f"session-start.sh references skill '{name}' but no .claude/skills/{name}/SKILL.md"
        )

    return failures, warnings


def check_example_readme_counts(root: Path) -> tuple[list[str], list[str]]:
    """#9: examples/minimal-project/README.md counts vs actual example files"""
    failures: list[str] = []
    warnings: list[str] = []

    example_root = root / "examples" / "minimal-project"
    readme_path = example_root / "README.md"
    if not readme_path.exists():
        return failures, warnings

    text = _read(readme_path)

    # Agent count: "(N agents)"
    agents_dir = example_root / ".claude" / "agents"
    match = re.search(r"\((\d+)\s+agents?\)", text)
    if match and agents_dir.is_dir():
        stated = int(match.group(1))
        actual = len(list(agents_dir.glob("*.md")))
        if stated != actual:
            warnings.append(f"example README says {stated} agents but found {actual}")

    # Skill count: "(N skills)"
    skills_dir = example_root / ".claude" / "skills"
    match = re.search(r"\((\d+)\s+skills?\)", text)
    if match and skills_dir.is_dir():
        stated = int(match.group(1))
        actual = len([d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])
        if stated != actual:
            warnings.append(f"example README says {stated} skills but found {actual}")

    return failures, warnings


def check_example_commands(root: Path) -> tuple[list[str], list[str]]:
    """#10: example commands exist in root (excluding intentional divergence)"""
    failures: list[str] = []
    warnings: list[str] = []

    # Intentional divergence: these commands are expected to differ.
    intentional_divergence = {"validate"}

    example_commands_dir = root / "examples" / "minimal-project" / ".claude" / "commands"
    root_commands_dir = root / ".claude" / "commands"

    if not example_commands_dir.is_dir() or not root_commands_dir.is_dir():
        return failures, warnings

    example_commands = _glob_stems(example_commands_dir, "*.md") - intentional_divergence
    root_commands = _glob_stems(root_commands_dir, "*.md")

    missing_in_root = example_commands - root_commands
    for name in sorted(missing_in_root):
        warnings.append(
            f"example has command '/{name}' but root .claude/commands/{name}.md does not exist"
        )

    return failures, warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

ALL_CHECKS = [
    ("agents (routing.md ↔ agents/)", check_agents),
    ("skills (CLAUDE.md ↔ skills/)", check_skills),
    ("commands (files ↔ README)", check_commands_in_readme),
    ("hooks (settings ↔ hooks/)", check_hooks),
    ("template profiles", check_template_profiles),
    ("README counts", check_readme_counts),
    ("template version", check_template_version),
    ("session-start hints", check_session_start_hints),
    ("example README counts", check_example_readme_counts),
    ("example commands", check_example_commands),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Reference drift auto-lint")
    parser.add_argument(
        "--root",
        default=None,
        help="Framework root directory (default: parent of scripts/)",
    )
    args = parser.parse_args()

    if args.root:
        root = Path(args.root).resolve()
    else:
        root = Path(__file__).resolve().parents[1]

    all_failures: list[str] = []
    all_warnings: list[str] = []

    for label, check_fn in ALL_CHECKS:
        failures, warnings = check_fn(root)
        all_failures.extend(failures)
        all_warnings.extend(warnings)

    for w in all_warnings:
        print(f"WARNING: {w}")
    for f in all_failures:
        print(f"FAIL: {f}")

    if all_failures:
        return 1

    if not all_warnings:
        print("PASS: no reference drift detected")
    else:
        print(f"PASS (with {len(all_warnings)} warnings)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
