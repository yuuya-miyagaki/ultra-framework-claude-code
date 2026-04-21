#!/usr/bin/env python3
"""Fixture-based integration tests for check_status.py routing matrix.

Tests --check-deploy-ready and --check-phase-transition via subprocess CLI,
covering task_type × task_size × phase combinations.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK_STATUS = ROOT / "scripts" / "check_status.py"

# Default gate approvals (all pending).
DEFAULT_APPROVALS = {
    "client_ready_for_dev": "approved",
    "brainstorm": "approved",
    "plan": "approved",
    "review": "pending",
    "qa": "pending",
    "security": "pending",
    "deploy": "pending",
    "dev_ready_for_client": "pending",
}


def make_status_md(
    *,
    phase: str = "implement",
    task_type: str = "feature",
    task_size: str = "L",
    approvals: dict[str, str] | None = None,
) -> str:
    """Generate a minimal STATUS.md frontmatter for testing."""
    gates = dict(DEFAULT_APPROVALS)
    if approvals:
        gates.update(approvals)
    gate_lines = "\n".join(f"  {k}: {v}" for k, v in gates.items())
    return (
        f"---\n"
        f"framework: ultra-framework-claude-code\n"
        f'framework_version: "0.11.0"\n'
        f"project_name: test\n"
        f"mode: Dev\n"
        f"phase: {phase}\n"
        f"task_type: {task_type}\n"
        f"task_size: {task_size}\n"
        f'last_updated: "2026-01-01"\n'
        f"gate_approvals:\n"
        f"{gate_lines}\n"
        f"current_refs:\n"
        f"  requirements: null\n"
        f"  plan: null\n"
        f"  spec: null\n"
        f"  review: null\n"
        f"  qa: null\n"
        f"  security: null\n"
        f"  deploy: null\n"
        f"  translation: null\n"
        f"next_action: test\n"
        f"blockers: []\n"
        f"session_history: []\n"
        f"---\n"
    )


def run_check(tmp_root: str, *args: str) -> tuple[int, str]:
    """Run check_status.py with given args against a temp project root."""
    result = subprocess.run(
        ["python3", str(CHECK_STATUS), "--root", tmp_root, *args],
        capture_output=True,
        text=True,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


class TempProject:
    """Context manager that creates a temp project with STATUS.md."""

    def __init__(self, status_content: str):
        self._content = status_content
        self._tmpdir: tempfile.TemporaryDirectory | None = None

    def __enter__(self) -> str:
        self._tmpdir = tempfile.TemporaryDirectory()
        root = self._tmpdir.name
        docs = Path(root) / "docs"
        docs.mkdir()
        (docs / "STATUS.md").write_text(self._content, encoding="utf-8")
        return root

    def __exit__(self, *args):
        if self._tmpdir:
            self._tmpdir.cleanup()


# =============================================================================
# --check-deploy-ready tests
# =============================================================================


class TestCheckDeployReady(unittest.TestCase):
    """Test deploy readiness check across task_type × task_size matrix."""

    def test_feature_L_all_approved_allows(self):
        """feature/L with review+qa+security approved → allow."""
        content = make_status_md(
            task_type="feature", task_size="L",
            approvals={"review": "approved", "qa": "approved", "security": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-deploy-ready")
            self.assertEqual(rc, 0, f"Expected allow, got: {out}")

    def test_feature_L_review_pending_denies(self):
        """feature/L with review=pending → deny."""
        content = make_status_md(
            task_type="feature", task_size="L",
            approvals={"review": "pending", "qa": "approved", "security": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-deploy-ready")
            self.assertEqual(rc, 1, f"Expected deny, got: {out}")
            self.assertIn("review", out)

    def test_feature_L_qa_pending_denies(self):
        """feature/L with qa=pending → deny."""
        content = make_status_md(
            task_type="feature", task_size="L",
            approvals={"review": "approved", "qa": "pending", "security": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-deploy-ready")
            self.assertEqual(rc, 1, f"Expected deny, got: {out}")
            self.assertIn("qa", out)

    def test_feature_S_allows_without_deploy_gates(self):
        """feature/S — deploy phase not in SIZE_ALLOWED_PHASES["S"] → allow."""
        content = make_status_md(
            task_type="feature", task_size="S",
            approvals={},  # all default (pending)
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-deploy-ready")
            self.assertEqual(rc, 0, f"Expected allow (S skips deploy), got: {out}")

    def test_feature_M_allows_without_deploy_gates(self):
        """feature/M — deploy phase not in SIZE_ALLOWED_PHASES["M"] → allow."""
        content = make_status_md(
            task_type="feature", task_size="M",
            approvals={},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-deploy-ready")
            self.assertEqual(rc, 0, f"Expected allow (M skips deploy), got: {out}")

    def test_bugfix_M_review_approved_allows(self):
        """bugfix/M — review is the only required gate → allow when approved."""
        content = make_status_md(
            task_type="bugfix", task_size="M",
            approvals={"review": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-deploy-ready")
            self.assertEqual(rc, 0, f"Expected allow, got: {out}")

    def test_feature_L_review_na_denies_strict(self):
        """feature/L with review=n/a → deny (strict enforcement)."""
        content = make_status_md(
            task_type="feature", task_size="L",
            approvals={"review": "n/a", "qa": "approved", "security": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-deploy-ready")
            self.assertEqual(rc, 1, f"Expected deny (strict), got: {out}")
            self.assertIn("n/a", out)

    def test_refactor_L_all_approved_allows(self):
        """refactor/L with all gates approved → allow."""
        content = make_status_md(
            task_type="refactor", task_size="L",
            approvals={"review": "approved", "qa": "approved", "security": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-deploy-ready")
            self.assertEqual(rc, 0, f"Expected allow, got: {out}")

    def test_hotfix_S_allows_even_pending(self):
        """hotfix/S — S size skips deploy → allow regardless of gates."""
        content = make_status_md(
            task_type="hotfix", task_size="S",
            approvals={},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-deploy-ready")
            self.assertEqual(rc, 0, f"Expected allow, got: {out}")


# =============================================================================
# --check-phase-transition tests
# =============================================================================


class TestCheckPhaseTransition(unittest.TestCase):
    """Test phase transition validation across task_size matrix."""

    def test_implement_to_review_gates_met_allows(self):
        """implement→review with brainstorm+plan approved → allow."""
        content = make_status_md(
            phase="review", task_size="L",
            approvals={"brainstorm": "approved", "plan": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "implement", "review")
            self.assertEqual(rc, 0, f"Expected allow, got: {out}")

    def test_implement_to_deploy_skips_denies(self):
        """implement→deploy without review/qa/security → deny."""
        content = make_status_md(
            phase="deploy", task_size="L",
            approvals={},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "implement", "deploy")
            self.assertEqual(rc, 1, f"Expected deny, got: {out}")
            self.assertIn("review", out)

    def test_review_to_qa_review_approved_allows(self):
        """review→qa with review approved → allow."""
        content = make_status_md(
            phase="qa", task_size="L",
            approvals={"review": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "review", "qa")
            self.assertEqual(rc, 0, f"Expected allow, got: {out}")

    def test_review_to_qa_review_pending_denies(self):
        """review→qa with review=pending → deny."""
        content = make_status_md(
            phase="qa", task_size="L",
            approvals={"review": "pending"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "review", "qa")
            self.assertEqual(rc, 1, f"Expected deny, got: {out}")

    def test_brainstorm_to_implement_S_plan_skipped_allows(self):
        """brainstorm→implement for S size (plan phase skipped) → allow."""
        content = make_status_md(
            phase="implement", task_size="S",
            approvals={"brainstorm": "approved", "plan": "n/a"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "brainstorm", "implement")
            self.assertEqual(rc, 0, f"Expected allow (S skips plan), got: {out}")

    def test_brainstorm_to_implement_L_plan_pending_denies(self):
        """brainstorm→implement for L size with plan=pending → deny."""
        content = make_status_md(
            phase="implement", task_size="L",
            approvals={"brainstorm": "approved", "plan": "pending"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "brainstorm", "implement")
            self.assertEqual(rc, 1, f"Expected deny, got: {out}")

    def test_client_phase_transition_always_allows(self):
        """Client phase transitions are not validated → allow."""
        content = make_status_md(phase="onboard", task_size="L")
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "onboard", "discovery")
            self.assertEqual(rc, 0, f"Expected allow (Client phases), got: {out}")

    def test_qa_to_security_qa_approved_allows(self):
        """qa→security with qa approved → allow."""
        content = make_status_md(
            phase="security", task_size="L",
            approvals={"review": "approved", "qa": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "qa", "security")
            self.assertEqual(rc, 0, f"Expected allow, got: {out}")

    def test_implement_to_security_skip_denies(self):
        """implement→security with review+qa approved → deny (phase skip)."""
        content = make_status_md(
            phase="security", task_size="L",
            approvals={"review": "approved", "qa": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "implement", "security")
            self.assertEqual(rc, 1, f"Expected deny (phase skip), got: {out}")
            self.assertIn("skip", out.lower())

    def test_review_to_ship_S_skips_qa_security_deploy_allows(self):
        """review→ship for S size (qa/security/deploy skipped) → allow."""
        content = make_status_md(
            phase="ship", task_size="S",
            approvals={"review": "approved"},
        )
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "review", "ship")
            self.assertEqual(rc, 0, f"Expected allow (S skips qa/security/deploy), got: {out}")

    def test_backward_transition_always_allows(self):
        """review→implement (backward/rework) → always allow."""
        content = make_status_md(phase="implement", task_size="L")
        with TempProject(content) as root:
            rc, out = run_check(root, "--check-phase-transition", "review", "implement")
            self.assertEqual(rc, 0, f"Expected allow (backward), got: {out}")


# =============================================================================
# Hook-level integration tests (shell scripts → deny JSON)
# =============================================================================


class TempProjectWithHooks(TempProject):
    """Extended temp project that copies hook scripts so ROOT resolves to temp dir.

    Hooks compute ROOT from their own filesystem location (SCRIPT_DIR/..),
    so we must place hook files inside the temp project for correct resolution.
    """

    def __enter__(self) -> str:
        root = super().__enter__()
        root_path = Path(root)

        # Symlink scripts/ so check_status.py is importable.
        (root_path / "scripts").symlink_to(ROOT / "scripts")

        # Copy hook files into temp project so ROOT resolves correctly.
        hooks_dir = root_path / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        lib_dir = hooks_dir / "lib"
        lib_dir.mkdir()
        (lib_dir / "extract-input.sh").symlink_to(
            ROOT / "hooks" / "lib" / "extract-input.sh"
        )
        # Copy each hook script (not symlink — so dirname resolves to temp).
        import shutil
        for hook_name in [
            "check-deploy-gate.sh",
            "post-status-audit.sh",
        ]:
            src = ROOT / "hooks" / hook_name
            if src.exists():
                shutil.copy2(src, hooks_dir / hook_name)
        return root


def run_hook(hook_name: str, tmp_root: str, stdin_json: str) -> tuple[int, str]:
    """Run a hook shell script (by name) from the temp project's hooks/ dir."""
    hook_path = str(Path(tmp_root) / "hooks" / hook_name)
    result = subprocess.run(
        ["bash", hook_path],
        input=stdin_json,
        capture_output=True,
        text=True,
        env={**os.environ, "HOME": tmp_root},
        cwd=tmp_root,
    )
    return result.returncode, result.stdout.strip()


class TestDeployGateHookDenyJSON(unittest.TestCase):
    """Verify check-deploy-gate.sh emits proper deny JSON (not silent exit)."""

    HOOK_NAME = "check-deploy-gate.sh"
    # Minimal PreToolUse Bash input with a deploy command.
    DEPLOY_INPUT = '{"tool_name":"Bash","tool_input":{"command":"vercel deploy --prod"}}'
    # Read-only command that contains 'deploy' as argument (should NOT trigger).
    READONLY_INPUT = '{"tool_name":"Bash","tool_input":{"command":"rg deploy docs/"}}'

    def test_deny_emits_json(self):
        """When gates not met, hook must emit permissionDecision:deny JSON."""
        content = make_status_md(
            task_type="feature", task_size="L", phase="deploy",
            approvals={"review": "pending"},
        )
        with TempProjectWithHooks(content) as root:
            rc, out = run_hook(self.HOOK_NAME, root, self.DEPLOY_INPUT)
            self.assertEqual(rc, 0, f"Hook should exit 0 even on deny, got rc={rc}")
            self.assertIn('"permissionDecision":"deny"', out,
                          f"Expected deny JSON, got: {out}")
            self.assertIn("[deploy-gate]", out)

    def test_allow_emits_empty_json(self):
        """When all gates met, hook must emit empty JSON."""
        content = make_status_md(
            task_type="feature", task_size="L", phase="deploy",
            approvals={"review": "approved", "qa": "approved", "security": "approved"},
        )
        with TempProjectWithHooks(content) as root:
            rc, out = run_hook(self.HOOK_NAME, root, self.DEPLOY_INPUT)
            self.assertEqual(rc, 0)
            self.assertEqual(out, "{}")

    def test_readonly_deploy_word_not_triggered(self):
        """Read-only command containing 'deploy' should not trigger the hook."""
        content = make_status_md(
            task_type="feature", task_size="L", phase="deploy",
            approvals={"review": "pending"},
        )
        with TempProjectWithHooks(content) as root:
            rc, out = run_hook(self.HOOK_NAME, root, self.READONLY_INPUT)
            self.assertEqual(rc, 0)
            self.assertEqual(out, "{}")


class TestPhaseSkipHookDenyJSON(unittest.TestCase):
    """Verify post-status-audit.sh emits proper deny JSON for phase skips."""

    HOOK_NAME = "post-status-audit.sh"

    def _make_snapshot(self, root: str, phase: str, gates: dict[str, str]) -> None:
        """Create .claude/.gate-snapshot with phase and gate data."""
        snapshot_dir = Path(root) / ".claude"
        snapshot_dir.mkdir(exist_ok=True)
        gate_lines = "\n".join(f"  {k}: {v}" for k, v in gates.items())
        snapshot = f"gate_approvals:\n{gate_lines}\nphase: {phase}\n"
        (snapshot_dir / ".gate-snapshot").write_text(snapshot, encoding="utf-8")

    def test_phase_skip_deny_emits_json(self):
        """implement→security skip must emit deny JSON, not silent exit."""
        # Gates in STATUS.md must MATCH snapshot gates to avoid gate-tamper
        # firing before the phase transition check.
        status_approvals = {"review": "approved", "qa": "approved"}
        content = make_status_md(
            phase="security", task_size="L",
            approvals=status_approvals,
        )
        with TempProjectWithHooks(content) as root:
            # Snapshot: same gates as STATUS.md, but phase=implement (old phase).
            self._make_snapshot(root, "implement", {
                "client_ready_for_dev": "approved",
                "brainstorm": "approved",
                "plan": "approved",
                "review": "approved",
                "qa": "approved",
                "security": "pending",
                "deploy": "pending",
                "dev_ready_for_client": "pending",
            })
            # PostToolUse input for an Edit on STATUS.md.
            stdin = '{"tool_name":"Edit","tool_input":{"file_path":"docs/STATUS.md"}}'
            rc, out = run_hook(self.HOOK_NAME, root, stdin)
            self.assertEqual(rc, 0, f"Hook should exit 0 even on deny, got rc={rc}")
            self.assertIn('"permissionDecision":"deny"', out,
                          f"Expected deny JSON for phase skip, got: {out}")
            self.assertIn("[phase-skip]", out)


if __name__ == "__main__":
    unittest.main()
