#!/usr/bin/env python3
"""Tier 3 evaluation: contract checks not covered by tier 1.

Checks:
1. Every extension directory has a README.md.
2. CONVENTIONS.md and README Extensions section both assert manual opt-in
   and setup.sh non-inclusion.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_extension_readmes(root: Path) -> tuple[list[str], list[str]]:
    """Every subdirectory under extensions/ must have a README.md."""
    failures: list[str] = []
    warnings: list[str] = []

    extensions_dir = root / "extensions"
    if not extensions_dir.is_dir():
        return failures, warnings

    for entry in sorted(extensions_dir.iterdir()):
        if entry.is_dir():
            readme = entry / "README.md"
            if not readme.exists():
                failures.append(f"extensions/{entry.name}/ has no README.md")

    return failures, warnings


def _has_manual_opt_in(text: str) -> bool:
    """Check for manual opt-in language."""
    lower = text.lower()
    return "manual opt-in" in lower or ("manual" in lower and "opt-in" in lower)


def _has_setup_exclusion(text: str) -> bool:
    """Check for setup.sh non-inclusion language."""
    lower = text.lower()
    patterns = [
        "not included in setup",
        "not included in `setup",
        "setup.sh --profile に含めない",
        "setup.sh` profiles",
    ]
    return any(p in lower for p in patterns)


def check_conventions_readme_alignment(root: Path) -> tuple[list[str], list[str]]:
    """CONVENTIONS.md and README Extensions section both assert manual opt-in
    and setup.sh non-inclusion."""
    failures: list[str] = []
    warnings: list[str] = []

    conventions_path = root / "extensions" / "CONVENTIONS.md"
    readme_path = root / "README.md"

    if not conventions_path.exists():
        warnings.append("extensions/CONVENTIONS.md not found; skipping alignment check")
        return failures, warnings
    if not readme_path.exists():
        return failures, warnings

    conv_text = conventions_path.read_text(encoding="utf-8")
    readme_text = readme_path.read_text(encoding="utf-8")

    # Extract README Extensions section (from "## Extensions" to next "##").
    match = re.search(r"^## Extensions\s*\n(.*?)(?=^## |\Z)", readme_text, re.MULTILINE | re.DOTALL)
    if not match:
        warnings.append("README.md has no '## Extensions' section; skipping alignment check")
        return failures, warnings
    extensions_section = match.group(1)

    # Check point 1: manual opt-in
    if not _has_manual_opt_in(conv_text):
        failures.append("CONVENTIONS.md missing 'manual opt-in' language")
    if not _has_manual_opt_in(extensions_section):
        failures.append("README Extensions section missing 'manual opt-in' language")

    # Check point 2: setup.sh non-inclusion
    if not _has_setup_exclusion(conv_text):
        failures.append("CONVENTIONS.md missing setup.sh non-inclusion language")
    if not _has_setup_exclusion(extensions_section):
        failures.append("README Extensions section missing setup.sh non-inclusion language")

    return failures, warnings


CHECKS = [
    ("extension_readmes", check_extension_readmes),
    ("conventions_readme_alignment", check_conventions_readme_alignment),
]


def main() -> int:
    all_failures: list[str] = []
    all_warnings: list[str] = []
    results: list[dict[str, str]] = []

    for name, fn in CHECKS:
        failures, warnings = fn(ROOT)
        all_failures.extend(failures)
        all_warnings.extend(warnings)
        if failures:
            status = "FAIL"
        elif warnings:
            status = "WARNING"
        else:
            status = "PASS"
        results.append({"name": name, "status": status})

    # Print summary
    print("=== Tier 3: Scenario Contract Checks ===")
    print("")
    print(f"  {'Check':<40} {'Status':<10}")
    print(f"  {'-' * 40} {'-' * 10}")
    for r in results:
        print(f"  {r['name']:<40} {r['status']:<10}")

    for msg in all_failures:
        print(f"\n  FAIL: {msg}")
    for msg in all_warnings:
        print(f"\n  WARNING: {msg}")

    print("")
    if all_failures:
        print("Result: FAIL")
        return 1
    if all_warnings:
        print("Result: PASS (with warnings)")
        return 0
    print("Result: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
