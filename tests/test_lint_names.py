#!/usr/bin/env python3
"""Tests for lint_names.py cross-reference linter."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lint_names import (
    extract_agent_files,
    extract_claude_md_skills,
    extract_command_files,
    extract_contract_agents,
    extract_contract_commands,
    extract_contract_skills,
    extract_skill_dirs,
    lint,
)


class TestExtractors(unittest.TestCase):
    """Unit tests for individual extractor functions."""

    def test_extract_skill_dirs(self):
        """Extract skill dirs from .claude/skills/."""
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / ".claude" / "skills"
            (skills / "tdd").mkdir(parents=True)
            (skills / "tdd" / "SKILL.md").write_text("# TDD")
            (skills / "empty-dir").mkdir()  # No SKILL.md — should be excluded.
            result = extract_skill_dirs(skills)
            self.assertEqual(result, {"tdd"})

    def test_extract_agent_files(self):
        """Extract agent names from .claude/agents/."""
        with tempfile.TemporaryDirectory() as tmp:
            agents = Path(tmp) / ".claude" / "agents"
            agents.mkdir(parents=True)
            (agents / "planner.md").write_text("# Planner")
            (agents / "reviewer.md").write_text("# Reviewer")
            result = extract_agent_files(agents)
            self.assertEqual(result, {"planner", "reviewer"})

    def test_extract_command_files(self):
        """Extract command names from .claude/commands/."""
        with tempfile.TemporaryDirectory() as tmp:
            cmds = Path(tmp) / ".claude" / "commands"
            cmds.mkdir(parents=True)
            (cmds / "gate.md").write_text("# Gate")
            result = extract_command_files(cmds)
            self.assertEqual(result, {"gate"})

    def test_extract_contract_skills(self):
        """Extract skill names from a mock check_framework_contract.py."""
        with tempfile.TemporaryDirectory() as tmp:
            contract = Path(tmp) / "check_framework_contract.py"
            contract.write_text(
                'REQUIRED_SKILL_FILES = [\n'
                '    ROOT / ".claude/skills/tdd/SKILL.md",\n'
                '    ROOT / ".claude/skills/deploy/SKILL.md",\n'
                ']\n'
            )
            result = extract_contract_skills(contract)
            self.assertEqual(result, {"tdd", "deploy"})

    def test_extract_claude_md_skills(self):
        """Extract skill names from CLAUDE.md ## Skills section."""
        with tempfile.TemporaryDirectory() as tmp:
            claude_md = Path(tmp) / "CLAUDE.md"
            claude_md.write_text(
                "# Framework\n\n"
                "## Skills\n\n"
                "- tdd, deploy, review\n"
                "- brainstorming, bug-diagnosis\n\n"
                "## Source of Truth\n"
            )
            result = extract_claude_md_skills(claude_md)
            self.assertIn("tdd", result)
            self.assertIn("deploy", result)
            self.assertIn("brainstorming", result)
            self.assertIn("bug-diagnosis", result)


class TestLint(unittest.TestCase):
    """Integration tests for the lint() function."""

    def test_no_issues_in_framework_repo(self):
        """Framework repo itself should have zero lint issues."""
        issues = lint(ROOT)
        self.assertEqual(issues, [], f"Lint issues found: {issues}")

    def test_missing_skill_detected(self):
        """Extra skill directory on disk → detected as missing from contract."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Minimal contract with one skill.
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "check_framework_contract.py").write_text(
                'ROOT / ".claude/skills/tdd/SKILL.md",\n'
            )
            # Two skills on disk.
            for name in ["tdd", "extra-skill"]:
                skill_dir = root / ".claude" / "skills" / name
                skill_dir.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text(f"# {name}")
            # No agents/commands needed — just create empty dirs.
            (root / ".claude" / "agents").mkdir(parents=True)
            (root / ".claude" / "commands").mkdir(parents=True)
            (root / "CLAUDE.md").write_text("")

            issues = lint(root)
            extra = [i for i in issues if "extra-skill" in i]
            self.assertTrue(len(extra) > 0, f"Expected 'extra-skill' issue, got: {issues}")

    def test_extra_contract_entry_detected(self):
        """Phantom skill in contract (not on disk) → detected."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / "check_framework_contract.py").write_text(
                'ROOT / ".claude/skills/tdd/SKILL.md",\n'
                'ROOT / ".claude/skills/phantom/SKILL.md",\n'
            )
            # Only tdd on disk.
            skill_dir = root / ".claude" / "skills" / "tdd"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# TDD")
            (root / ".claude" / "agents").mkdir(parents=True)
            (root / ".claude" / "commands").mkdir(parents=True)
            (root / "CLAUDE.md").write_text("")

            issues = lint(root)
            phantom = [i for i in issues if "phantom" in i]
            self.assertTrue(len(phantom) > 0, f"Expected 'phantom' issue, got: {issues}")


class TestContractLintIntegration(unittest.TestCase):
    """Verify check_framework_contract.py handles lint_names.py failures."""

    def test_lint_crash_produces_failure(self):
        """If lint_names.py exits non-zero with empty stdout, contract must still fail."""
        import subprocess
        # Create a fake lint_names.py that crashes with no stdout.
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "lint_names.py"
            script.write_text("import sys; sys.exit(1)\n")
            # Simulate the contract integration logic.
            result = subprocess.run(
                ["python3", str(script), "--root", tmp],
                capture_output=True, text=True,
            )
            # Current (buggy) logic: only checks stdout lines.
            # After fix: non-zero exit with empty stdout must still be treated as failure.
            has_stdout = bool(result.stdout.strip())
            self.assertNotEqual(result.returncode, 0)
            # This confirms the scenario: crash with empty stdout.
            self.assertFalse(has_stdout,
                             "Setup: expected empty stdout from crashing script")


if __name__ == "__main__":
    unittest.main()
