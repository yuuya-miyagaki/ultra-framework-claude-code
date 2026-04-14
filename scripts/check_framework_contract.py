#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path

from check_status import validate_status_file


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "CLAUDE.md",
    ROOT / "docs/STATUS.md",
    ROOT / "docs/LEARNINGS.md",
    ROOT / "docs/MIGRATION-FROM-v7.md",
    ROOT / "scripts/check_status.py",
]

REQUIRED_AGENT_FILES = [
    ROOT / ".claude/agents/planner.md",
    ROOT / ".claude/agents/implementer.md",
    ROOT / ".claude/agents/reviewer.md",
    ROOT / ".claude/agents/qa.md",
    ROOT / ".claude/agents/security.md",
    ROOT / ".claude/agents/ui.md",
    ROOT / ".claude/agents/reviewer-testing.md",
    ROOT / ".claude/agents/reviewer-performance.md",
    ROOT / ".claude/agents/reviewer-maintainability.md",
]

REQUIRED_SKILL_FILES = [
    ROOT / "docs/skills/brainstorming.md",
    ROOT / "docs/skills/test-driven-development.md",
    ROOT / "docs/skills/subagent-development.md",
    ROOT / "docs/skills/deploy.md",
    ROOT / "docs/skills/client-workflow.md",
    ROOT / "docs/skills/session-recovery.md",
    ROOT / "docs/skills/ship-and-docs.md",
]

REQUIRED_TEMPLATE_FILES = [
    ROOT / "templates/CLAUDE.template.md",
    ROOT / "templates/STATUS.template.md",
    ROOT / "templates/PRD.template.md",
    ROOT / "templates/SCOPE.template.md",
    ROOT / "templates/NFR.template.md",
    ROOT / "templates/ACCEPTANCE.template.md",
    ROOT / "templates/PLAN.template.md",
    ROOT / "templates/SPEC.template.md",
    ROOT / "templates/REVIEW.template.md",
    ROOT / "templates/QA-REPORT.template.md",
    ROOT / "templates/SECURITY-REVIEW.template.md",
    ROOT / "templates/HANDOVER-TO-DEV.template.md",
    ROOT / "templates/HANDOVER-TO-CLIENT.template.md",
    ROOT / "templates/LEARNINGS.template.md",
    ROOT / "templates/BRAINSTORM-RECORD.template.md",
    ROOT / "templates/VERIFICATION.template.md",
    ROOT / "templates/DEPLOY-CHECKLIST.template.md",
    ROOT / "templates/hooks.template.json",
]

REQUIRED_HOOK_FILES = [
    ROOT / "hooks/session-start.sh",
    ROOT / "hooks/check-gate.sh",
    ROOT / "hooks/check-destructive.sh",
    ROOT / "hooks/check-tdd.sh",
    ROOT / "hooks/post-bash.sh",
]

REQUIRED_EXAMPLE_FILES = [
    ROOT / "examples/minimal-project/CLAUDE.md",
    ROOT / "examples/minimal-project/README.md",
    ROOT / "examples/minimal-project/docs/STATUS.md",
    ROOT / "examples/minimal-project/docs/LEARNINGS.md",
    ROOT / "examples/minimal-project/docs/requirements/PRD.md",
    ROOT / "examples/minimal-project/docs/requirements/SCOPE.md",
    ROOT / "examples/minimal-project/docs/requirements/NFR.md",
    ROOT / "examples/minimal-project/docs/requirements/ACCEPTANCE.md",
    ROOT / "examples/minimal-project/docs/handover/TO-DEV.md",
    ROOT / "examples/minimal-project/docs/handover/TO-CLIENT.md",
    ROOT / "examples/minimal-project/docs/specs/search-brainstorm-record.md",
    ROOT / "examples/minimal-project/docs/specs/search-design.md",
    ROOT / "examples/minimal-project/docs/plans/search-implementation-plan.md",
    ROOT / "examples/minimal-project/docs/qa-reports/search-review.md",
    ROOT / "examples/minimal-project/docs/qa-reports/search-qa.md",
    ROOT / "examples/minimal-project/docs/qa-reports/search-security.md",
    ROOT / "examples/minimal-project/docs/qa-reports/search-verification.md",
    ROOT / "examples/minimal-project/docs/qa-reports/search-deploy-checklist.md",
]

REQUIRED_CLAUDE_HEADINGS = [
    "## Operating Contract",
    "## Session Start",
    "## State Machine",
    "## Routing",
    "## Context Budget Policy",
    "## Skills",
    "## Source of Truth",
    "## Completion Rule",
]

# Keep the kernel below 700 words (~900-1400 tokens). The budget accounts for
# the mode/phase/gate model, the deploy phase, the Skills directory listing,
# and the Project Overrides section in the template variant.
MAX_CLAUDE_WORDS = 700

# Template placeholder pattern: <記入>, <topic>, <docs/requirements/ のパス>, etc.
# Matches angle-bracket tokens that look like fill-in markers.
PLACEHOLDER_PATTERN = re.compile(r"<[A-Za-z\u3000-\u9FFF/\s\-\.,:\d_]{1,40}>")

# Placeholders that are legitimate in example files (not fill-in markers).
PLACEHOLDER_ALLOWLIST = {
    "<topic>",
    "<パス>",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def word_count(text: str) -> int:
    return len(text.split())


def main() -> int:
    failures: list[str] = []

    for path in REQUIRED_FILES + REQUIRED_AGENT_FILES + REQUIRED_SKILL_FILES + REQUIRED_TEMPLATE_FILES + REQUIRED_HOOK_FILES + REQUIRED_EXAMPLE_FILES:
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")

    for path in [
        ROOT / "CLAUDE.md",
        ROOT / "templates/CLAUDE.template.md",
        ROOT / "examples/minimal-project/CLAUDE.md",
    ]:
        if not path.exists():
            continue
        text = read_text(path)
        for heading in REQUIRED_CLAUDE_HEADINGS:
            if heading not in text:
                failures.append(f"{path.relative_to(ROOT)} is missing heading: {heading}")
        count = word_count(text)
        if count > MAX_CLAUDE_WORDS:
            failures.append(
                f"{path.relative_to(ROOT)} is too large: {count} words > {MAX_CLAUDE_WORDS}"
            )
        if path.name in {"CLAUDE.template.md", "CLAUDE.md"} and path != ROOT / "CLAUDE.md" and "## Project Overrides" not in text:
            failures.append(f"{path.relative_to(ROOT)} is missing heading: ## Project Overrides")
        # Project CLAUDE.md variants must not reference docs/skills/ file paths
        # directly. Skills are conceptual references in project contexts.
        if path != ROOT / "CLAUDE.md" and "docs/skills/" in text:
            failures.append(
                f"{path.relative_to(ROOT)} contains docs/skills/ file path reference"
                " (project CLAUDE.md should use skill names, not paths)"
            )

    for path in [ROOT / "docs/STATUS.md", ROOT / "examples/minimal-project/docs/STATUS.md"]:
        if path.exists():
            failures.extend(validate_status_file(path))

    readme_path = ROOT / "README.md"
    if readme_path.exists():
        readme = read_text(readme_path)
        for token in [
            "python3 scripts/check_framework_contract.py",
            "python3 scripts/check_status.py --root .",
        ]:
            if token not in readme:
                failures.append(f"README.md is missing validation command: {token}")
        if "/Users/" in readme:
            failures.append("README.md contains machine-specific absolute paths")

    # Hook template validation: verify that hooks.template.json registers
    # all required hook scripts in the correct event sections.
    hooks_template_path = ROOT / "templates/hooks.template.json"
    if hooks_template_path.exists():
        try:
            hooks_data = json.loads(read_text(hooks_template_path))
        except json.JSONDecodeError as e:
            failures.append(f"hooks.template.json is not valid JSON: {e}")
            hooks_data = {}
        if not isinstance(hooks_data, dict):
            failures.append("hooks.template.json top-level value is not an object")
            hooks_data = {}
        hooks_config = hooks_data.get("hooks", {})
        if not isinstance(hooks_config, dict):
            failures.append("hooks.template.json 'hooks' value is not an object")
            hooks_config = {}
        # Map: event -> list of required command substrings.
        REQUIRED_HOOK_REGISTRATIONS = {
            "SessionStart": ["hooks/session-start.sh"],
            "PreToolUse": [
                "hooks/check-gate.sh",
                "hooks/check-tdd.sh",
                "hooks/check-destructive.sh",
            ],
            "PostToolUse": ["hooks/post-bash.sh"],
        }
        for event, required_commands in REQUIRED_HOOK_REGISTRATIONS.items():
            event_entries = hooks_config.get(event, [])
            if not isinstance(event_entries, list):
                failures.append(
                    f"hooks.template.json {event} value is not an array"
                )
                continue
            # Collect all command strings registered under this event.
            registered_commands = []
            for entry in event_entries:
                if not isinstance(entry, dict):
                    failures.append(
                        f"hooks.template.json {event} contains non-object entry"
                    )
                    continue
                hooks_list = entry.get("hooks", [])
                if not isinstance(hooks_list, list):
                    failures.append(
                        f"hooks.template.json {event} entry 'hooks' is not an array"
                    )
                    continue
                for hook in hooks_list:
                    if not isinstance(hook, dict):
                        failures.append(
                            f"hooks.template.json {event} hook entry is not an object"
                        )
                        continue
                    cmd = hook.get("command", "")
                    if not isinstance(cmd, str):
                        failures.append(
                            f"hooks.template.json {event} hook command is not a string"
                        )
                        continue
                    if cmd:
                        registered_commands.append(cmd)
            for required_cmd in required_commands:
                if not any(required_cmd in cmd for cmd in registered_commands):
                    failures.append(
                        f"hooks.template.json is missing '{required_cmd}' "
                        f"registration under {event}"
                    )

    # Agent structure validation: CSO description, rationalization tables,
    # hallucination guard boundaries, and technical constraints.
    CORE_AGENT_FILES = [
        ROOT / ".claude/agents/planner.md",
        ROOT / ".claude/agents/implementer.md",
        ROOT / ".claude/agents/reviewer.md",
        ROOT / ".claude/agents/qa.md",
        ROOT / ".claude/agents/security.md",
        ROOT / ".claude/agents/ui.md",
    ]
    # Agents that must not modify files (readOnly: true in frontmatter).
    READ_ONLY_AGENT_FILES = {
        ROOT / ".claude/agents/planner.md",
        ROOT / ".claude/agents/reviewer.md",
        ROOT / ".claude/agents/qa.md",
        ROOT / ".claude/agents/security.md",
        ROOT / ".claude/agents/reviewer-testing.md",
        ROOT / ".claude/agents/reviewer-performance.md",
        ROOT / ".claude/agents/reviewer-maintainability.md",
    }
    for path in REQUIRED_AGENT_FILES:
        if not path.exists():
            continue
        text = read_text(path)
        rel = path.relative_to(ROOT)
        # All agents must have CSO-format description.
        if 'description: "Trigger:' not in text:
            failures.append(f"{rel} missing CSO description (must start with 'Trigger:')")
        # All agents must have hallucination guard boundary.
        if "do not claim completion without" not in text:
            failures.append(f"{rel} missing hallucination guard boundary")
        # Core agents must have rationalization table.
        if path in CORE_AGENT_FILES and "## Known Rationalizations" not in text:
            failures.append(f"{rel} missing rationalization table (## Known Rationalizations)")
        # All agents must have maxTurns in frontmatter with matching boundary rule.
        # Scope regex to YAML frontmatter (between first --- pair) and body respectively.
        fm_match = re.match(r"---\s*\n(.*?)\n---", text, re.DOTALL)
        frontmatter_section = fm_match.group(1) if fm_match else ""
        body_section = text[fm_match.end():] if fm_match else text
        frontmatter_turns = re.search(r"maxTurns:\s*(\d+)", frontmatter_section)
        # Scope turn-limit search to ## Boundaries section only.
        boundaries_match = re.search(
            r"## Boundaries\b(.*?)(?=\n## |\Z)", body_section, re.DOTALL
        )
        boundaries_section = boundaries_match.group(1) if boundaries_match else ""
        boundary_turns = re.search(r"complete within (\d+) turns", boundaries_section)
        if not frontmatter_turns:
            failures.append(f"{rel} missing maxTurns in frontmatter")
        if not boundary_turns:
            failures.append(f"{rel} missing turn limit boundary rule ('complete within N turns')")
        if frontmatter_turns and boundary_turns:
            fm_val = int(frontmatter_turns.group(1))
            bd_val = int(boundary_turns.group(1))
            if fm_val != bd_val:
                failures.append(
                    f"{rel} maxTurns mismatch: frontmatter={fm_val}, boundary={bd_val}"
                )
        # Read-only agents must have readOnly frontmatter and boundary rule.
        if path in READ_ONLY_AGENT_FILES:
            if "readOnly: true" not in text:
                failures.append(f"{rel} missing readOnly: true in frontmatter")
            if "do not use Edit, Write, or Bash commands that modify files" not in text:
                failures.append(f"{rel} missing read-only boundary rule")

    # Check example project files for leftover template placeholders.
    for path in REQUIRED_EXAMPLE_FILES:
        if not path.exists():
            continue
        text = read_text(path)
        for match in PLACEHOLDER_PATTERN.finditer(text):
            token = match.group(0)
            if token not in PLACEHOLDER_ALLOWLIST:
                failures.append(
                    f"{path.relative_to(ROOT)} contains template placeholder: {token}"
                )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: ultra-framework-claude-code contract is aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
