#!/usr/bin/env python3

from __future__ import annotations

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
]

REQUIRED_EXAMPLE_FILES = [
    ROOT / "examples/minimal-project/CLAUDE.md",
    ROOT / "examples/minimal-project/README.md",
    ROOT / "examples/minimal-project/docs/STATUS.md",
    ROOT / "examples/minimal-project/docs/requirements/PRD.md",
    ROOT / "examples/minimal-project/docs/requirements/SCOPE.md",
    ROOT / "examples/minimal-project/docs/requirements/NFR.md",
    ROOT / "examples/minimal-project/docs/requirements/ACCEPTANCE.md",
    ROOT / "examples/minimal-project/docs/handover/TO-DEV.md",
    ROOT / "examples/minimal-project/docs/handover/TO-CLIENT.md",
]

REQUIRED_CLAUDE_HEADINGS = [
    "## Operating Contract",
    "## Session Start",
    "## State Machine",
    "## Routing",
    "## Context Budget Policy",
    "## Source of Truth",
    "## Completion Rule",
]

# Keep the kernel below 550 words, which approximates the original
# design target of staying comfortably under ~800-1200 tokens while leaving
# enough room to explain the mode/phase/gate model clearly.
MAX_CLAUDE_WORDS = 550


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def word_count(text: str) -> int:
    return len(text.split())


def main() -> int:
    failures: list[str] = []

    for path in REQUIRED_FILES + REQUIRED_AGENT_FILES + REQUIRED_TEMPLATE_FILES + REQUIRED_EXAMPLE_FILES:
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
        if path != ROOT / "examples/minimal-project/CLAUDE.md" and count > MAX_CLAUDE_WORDS:
            failures.append(
                f"{path.relative_to(ROOT)} is too large: {count} words > {MAX_CLAUDE_WORDS}"
            )
        if path.name in {"CLAUDE.template.md", "CLAUDE.md"} and path != ROOT / "CLAUDE.md" and "## Project Overrides" not in text:
            failures.append(f"{path.relative_to(ROOT)} is missing heading: ## Project Overrides")

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

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: ultra-framework-claude-code contract is aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
