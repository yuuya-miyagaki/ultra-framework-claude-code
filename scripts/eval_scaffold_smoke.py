#!/usr/bin/env python3
"""Tier 2 evaluation: scaffold smoke tests.

Runs setup.sh for minimal and standard profiles, then validates each
scaffold with check_framework_contract.py.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
SETUP_SH = REPO_ROOT / "bin" / "setup.sh"
CONTRACT_PY = SCRIPTS_DIR / "check_framework_contract.py"

# full profile validates the framework repo itself (not a scaffolded project),
# so it is tested by tier 1, not scaffold smoke tests.
PROFILES = ["minimal", "standard"]


def run_scaffold_test(profile: str, target: Path) -> tuple[str, str]:
    """Scaffold with profile, then validate. Returns (status, detail)."""
    # Step 1: scaffold
    result = subprocess.run(
        ["bash", str(SETUP_SH), f"--profile={profile}", f"--target={target}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        return "FAIL", f"setup.sh --profile={profile} failed: {detail}"

    # Step 2: validate
    result = subprocess.run(
        ["python3", str(CONTRACT_PY), f"--profile={profile}", f"--root={target}"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout.strip() or result.stderr.strip()
    if result.returncode != 0:
        return "FAIL", f"contract check failed for {profile}: {output}"

    return "PASS", f"{profile} scaffold validated"


def main() -> int:
    results: list[dict[str, str]] = []
    any_fail = False

    for profile in PROFILES:
        tmpdir = tempfile.mkdtemp(prefix=f"ultra-eval-{profile}-")
        try:
            status, detail = run_scaffold_test(profile, Path(tmpdir))
            results.append({"profile": profile, "status": status, "detail": detail})
            if status == "FAIL":
                any_fail = True
        except subprocess.TimeoutExpired:
            results.append({"profile": profile, "status": "FAIL", "detail": "timeout"})
            any_fail = True
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # Print summary
    print("=== Tier 2: Scaffold Smoke Tests ===")
    print("")
    print(f"  {'Profile':<20} {'Status':<10}")
    print(f"  {'-' * 20} {'-' * 10}")
    for r in results:
        print(f"  {r['profile']:<20} {r['status']:<10}")

    for r in results:
        if r["status"] != "PASS":
            print(f"\n--- {r['profile']} ({r['status']}) ---")
            print(f"  {r['detail']}")

    print("")
    if any_fail:
        print("Result: FAIL")
        return 1
    print("Result: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
