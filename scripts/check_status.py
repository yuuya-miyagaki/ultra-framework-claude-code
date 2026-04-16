#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


# This validator intentionally supports a narrow YAML subset so the scaffold
# stays dependency-free. Keep STATUS.md frontmatter simple and avoid complex YAML
# features such as block scalars, inline comments in values, and nested maps
# beyond the documented schema.

REQUIRED_TOP_LEVEL_KEYS = [
    "framework",
    "framework_version",
    "project_name",
    "mode",
    "phase",
    "task_type",
    "last_updated",
    "gate_approvals",
    "current_refs",
    "next_action",
    "blockers",
    "session_history",
]

OPTIONAL_TOP_LEVEL_KEYS: set[str] = {"task_size", "task_size_rationale", "iteration", "ui_surface", "external_evidence", "failure_tracking"}

REQUIRED_APPROVAL_KEYS = [
    "client_ready_for_dev",
    "brainstorm",
    "plan",
    "review",
    "qa",
    "security",
    "deploy",
    "dev_ready_for_client",
]

ALLOWED_APPROVAL_VALUES = {"pending", "approved", "blocked", "n/a"}
ALLOWED_MODES = {"Client", "Dev"}
ALLOWED_PHASES = {
    "onboard",
    "discovery",
    "requirements",
    "scope",
    "acceptance",
    "handover",
    "brainstorm",
    "plan",
    "implement",
    "review",
    "qa",
    "security",
    "deploy",
    "ship",
    "docs",
}
MODE_PHASES = {
    "Client": {"onboard", "discovery", "requirements", "scope", "acceptance", "handover"},
    "Dev": {"brainstorm", "plan", "implement", "review", "qa", "security", "deploy", "ship", "docs"},
}
# Ordered Dev phase sequence (source of truth for phase-order checks).
DEV_PHASE_ORDER = ["brainstorm", "plan", "implement", "review", "qa", "security", "deploy", "ship", "docs"]
EXPECTED_CURRENT_REF_KEYS = {"requirements", "plan", "spec", "review", "qa", "security", "deploy"}
ALLOWED_TASK_TYPES = {"feature", "refactor", "bugfix", "hotfix", "framework"}
ALLOWED_TASK_SIZES = {"S", "M", "L"}
# Phase flow constraints by task size.
# S: minimal flow (1-file fixes). M: skip deploy. L: all phases.
SIZE_ALLOWED_PHASES = {
    "S": {"brainstorm", "implement", "review", "ship"},
    "M": {"brainstorm", "plan", "implement", "review", "qa", "security", "ship", "docs"},
    "L": {"brainstorm", "plan", "implement", "review", "qa", "security", "deploy", "ship", "docs"},
}

# Task types that require strict gate enforcement (no n/a allowed).
STRICT_GATE_TASK_TYPES = {"feature", "refactor", "framework"}
# Per-phase gates that must be approved (not n/a) for strict task types.
# At deploy: review/qa/security are prerequisites and must already be approved.
# At ship/docs: deploy must also be approved.
STRICT_GATE_BY_PHASE = {
    "deploy": ["review", "qa", "security"],
    "ship": ["review", "qa", "security", "deploy"],
    "docs": ["review", "qa", "security", "deploy"],
}
PHASE_REQUIRES_GATES = {
    "plan": ["brainstorm"],
    "implement": ["brainstorm", "plan"],
    "review": ["brainstorm", "plan"],
    "qa": ["brainstorm", "plan", "review"],
    "security": ["brainstorm", "plan", "review", "qa"],
    "deploy": ["brainstorm", "plan", "review", "qa", "security"],
    "ship": ["brainstorm", "plan", "review", "qa", "security", "deploy"],
    "docs": ["brainstorm", "plan", "review", "qa", "security", "deploy"],
}
MAX_SESSION_HISTORY_ENTRIES = 3
MAX_EXTERNAL_EVIDENCE_ENTRIES = 3
REQUIRED_BODY_HEADINGS = [
    "## Summary",
    "## Recent Decisions",
    "## Session History",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_frontmatter(text: str) -> str | None:
    match = re.search(r"\A---\n(?P<body>.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    return match.group("body")


def has_top_level_key(frontmatter: str, key: str) -> bool:
    return re.search(rf"(?m)^{re.escape(key)}:\s*", frontmatter) is not None


def extract_scalar_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf'(?m)^{re.escape(key)}:\s*"(.*)"\s*$', frontmatter)
    if match:
        return match.group(1).strip()

    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+)\s*$", frontmatter)
    if match:
        return match.group(1).strip().strip('"').strip("'")

    return None


def extract_approval_map(frontmatter: str) -> dict[str, str]:
    approvals: dict[str, str] = {}
    in_block = False

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not in_block:
            if re.match(r"^gate_approvals:\s*$", line):
                in_block = True
            continue

        if not line.strip():
            continue
        if re.match(r"^\S", line):
            break

        match = re.match(r"^\s{2}([A-Za-z0-9_]+):\s*([A-Za-z0-9_\"'\-/]+)\s*$", line)
        if match:
            approvals[match.group(1)] = match.group(2).strip("\"'")

    return approvals


def extract_current_refs(frontmatter: str) -> dict[str, list[str] | str]:
    refs: dict[str, list[str] | str] = {}
    current_key: str | None = None
    in_block = False

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not in_block:
            if re.match(r"^current_refs:\s*$", line):
                in_block = True
            continue

        if not line.strip():
            continue
        if re.match(r"^\S", line):
            break

        key_match = re.match(r"^\s{2}([A-Za-z0-9_]+):\s*(.*)$", line)
        if key_match:
            current_key = key_match.group(1)
            raw_value = key_match.group(2).strip()
            if raw_value in {"null", "[]", ""}:
                refs[current_key] = [] if raw_value == "[]" else "null"
            else:
                refs[current_key] = raw_value.strip("\"'")
            continue

        item_match = re.match(r"^\s{4}-\s*(.+)$", line)
        if item_match and current_key:
            existing = refs.get(current_key)
            value = item_match.group(1).strip().strip("\"'")
            if isinstance(existing, list):
                existing.append(value)
            else:
                refs[current_key] = [value]

    return refs


def extract_session_history(frontmatter: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_block = False

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not in_block:
            # Handle both block form and inline empty list.
            header = re.match(r"^session_history:\s*(.*)$", line)
            if header:
                inline = header.group(1).strip()
                if inline == "[]":
                    return []  # Empty list is valid.
                if inline == "":
                    in_block = True
            continue

        if not line.strip():
            continue
        if re.match(r"^\S", line):
            break

        entry_start = re.match(r"^\s{2}-\s*date:\s*(.+)$", line)
        if entry_start:
            if current:
                entries.append(current)
            current = {"date": entry_start.group(1).strip().strip('"')}
            continue

        entry_field = re.match(r"^\s{4}([A-Za-z0-9_]+):\s*(.+)$", line)
        if entry_field and current is not None:
            current[entry_field.group(1)] = entry_field.group(2).strip().strip('"')

    if current:
        entries.append(current)

    return entries


REQUIRED_FAILURE_TRACKING_FIELDS = ["goal", "count", "last_attempt"]


def extract_failure_tracking(frontmatter: str) -> dict[str, str] | None:
    """Extract failure_tracking from frontmatter.

    Expected format:
        failure_tracking:
          goal: "description"
          count: 2
          last_attempt: "what was tried"

    ``failure_tracking: null`` means no active tracking (returns None).
    """
    in_block = False
    fields: dict[str, str] = {}

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not in_block:
            header = re.match(r"^failure_tracking:\s*(.*)$", line)
            if header:
                inline = header.group(1).strip()
                if inline == "null" or inline == "":
                    if inline == "null":
                        return None
                    in_block = True
            continue

        if not line.strip():
            continue
        if re.match(r"^\S", line):
            break

        field_match = re.match(r"^\s{2}([A-Za-z0-9_]+):\s*(.+)$", line)
        if field_match:
            fields[field_match.group(1)] = field_match.group(2).strip().strip('"')

    return fields if fields else None


REQUIRED_EVIDENCE_FIELDS = ["type", "scope", "findings", "resolution"]


def extract_external_evidence(frontmatter: str) -> list[dict[str, str]]:
    """Extract external_evidence entries from frontmatter.

    Expected format (list of maps, field order independent):
        external_evidence:
          - type: "codex-review-round-1"
            scope: "v0.5.0 Phase 1-7"
            findings: "..."
            resolution: "..."

    Inline empty list (``external_evidence: []``) is valid and yields [].
    """
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_block = False

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not in_block:
            # Match both "external_evidence:" (block) and
            # "external_evidence: []" (inline empty).
            header = re.match(r"^external_evidence:\s*(.*)$", line)
            if header:
                inline = header.group(1).strip()
                if inline == "[]" or inline == "":
                    in_block = inline == ""
                    # inline [] → return empty list immediately
                    if not in_block:
                        return []
            continue

        if not line.strip():
            continue
        if re.match(r"^\S", line):
            break

        # Entry start: "  - <key>: <value>" — field-order independent.
        entry_start = re.match(r"^\s{2}-\s*([A-Za-z0-9_]+):\s*(.+)$", line)
        if entry_start:
            if current:
                entries.append(current)
            current = {entry_start.group(1): entry_start.group(2).strip().strip('"')}
            continue

        # Subsequent fields: "    <key>: <value>"
        entry_field = re.match(r"^\s{4}([A-Za-z0-9_]+):\s*(.+)$", line)
        if entry_field and current is not None:
            current[entry_field.group(1)] = entry_field.group(2).strip().strip('"')

    if current:
        entries.append(current)

    return entries


def validate_status_file(path: Path) -> list[str]:
    failures: list[str] = []

    if not path.exists():
        return [f"missing status file: {path}"]

    text = read_text(path)
    frontmatter = extract_frontmatter(text)

    if frontmatter is None:
        return [f"{path} is missing YAML frontmatter"]

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if not has_top_level_key(frontmatter, key):
            failures.append(f"{path} is missing frontmatter key: {key}")

    # Warn about unknown top-level keys (comments excluded).
    allowed_keys = set(REQUIRED_TOP_LEVEL_KEYS) | OPTIONAL_TOP_LEVEL_KEYS
    for line in frontmatter.splitlines():
        key_match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*", line)
        if key_match:
            found_key = key_match.group(1)
            if found_key not in allowed_keys:
                failures.append(f"{path} has unknown frontmatter key: {found_key}")

    mode = extract_scalar_value(frontmatter, "mode")
    phase = extract_scalar_value(frontmatter, "phase")
    if mode is None or mode not in ALLOWED_MODES:
        failures.append(f"{path} has invalid mode: {mode}")
    if phase is None or phase not in ALLOWED_PHASES:
        failures.append(f"{path} has invalid phase: {phase}")
    if mode in MODE_PHASES and phase not in MODE_PHASES[mode]:
        failures.append(f"{path} has invalid phase for mode {mode}: {phase}")

    task_type = extract_scalar_value(frontmatter, "task_type")
    if task_type and task_type not in ALLOWED_TASK_TYPES:
        failures.append(f"{path} has invalid task_type: {task_type}")

    iteration = extract_scalar_value(frontmatter, "iteration")
    if iteration is not None:
        if not iteration.isdigit() or int(iteration) < 1:
            failures.append(f"{path} has invalid iteration (must be positive integer): {iteration}")

    ui_surface = extract_scalar_value(frontmatter, "ui_surface")
    if ui_surface is not None:
        if ui_surface not in {"true", "false"}:
            failures.append(f"{path} has invalid ui_surface (must be true/false): {ui_surface}")

    task_size = extract_scalar_value(frontmatter, "task_size")
    if task_size is not None:
        if task_size not in ALLOWED_TASK_SIZES:
            failures.append(f"{path} has invalid task_size: {task_size}")
        elif mode == "Dev" and phase and phase in ALLOWED_PHASES:
            allowed = SIZE_ALLOWED_PHASES.get(task_size, ALLOWED_PHASES)
            if phase not in allowed:
                failures.append(
                    f"{path} phase '{phase}' is not allowed for task_size '{task_size}'"
                )
        elif mode == "Client":
            failures.append(
                f"{path} WARNING: task_size '{task_size}' is set in Client mode "
                "(task_size only applies to Dev phases)"
            )

    # WARNING (not FAIL) when task_size is set but rationale is missing.
    if task_size is not None:
        rationale = extract_scalar_value(frontmatter, "task_size_rationale")
        if rationale is None or rationale == "":
            print(
                f"WARNING: {path} has task_size '{task_size}' but no task_size_rationale "
                "(recommended to document sizing justification)"
            )

    approvals = extract_approval_map(frontmatter)
    for key in REQUIRED_APPROVAL_KEYS:
        if key not in approvals:
            failures.append(f"{path} is missing gate approval: {key}")
            continue
        if approvals[key] not in ALLOWED_APPROVAL_VALUES:
            failures.append(
                f"{path} has invalid approval value for {key}: {approvals[key]}"
            )

    # Phase gate check: prior gates must not be pending/blocked.
    # When task_size is set, only require gates whose phase is in the size flow.
    if phase and phase in PHASE_REQUIRES_GATES:
        required_prior = PHASE_REQUIRES_GATES[phase]
        if task_size and task_size in SIZE_ALLOWED_PHASES:
            allowed_phases = SIZE_ALLOWED_PHASES[task_size]
            required_prior = [g for g in required_prior if g in allowed_phases]
        for required_gate in required_prior:
            gate_value = approvals.get(required_gate)
            if gate_value in {"pending", "blocked"}:
                failures.append(
                    f"{path} is in phase '{phase}' but gate '{required_gate}' is '{gate_value}'"
                )

    # Dev verification by task type: feature/refactor/framework require
    # specific gates to be approved (not n/a) depending on current phase.
    # When task_size is set, only enforce gates whose phase is in the size flow.
    if task_type in STRICT_GATE_TASK_TYPES and task_size != "S" and phase in STRICT_GATE_BY_PHASE:
        strict_gates = STRICT_GATE_BY_PHASE[phase]
        if task_size and task_size in SIZE_ALLOWED_PHASES:
            allowed_phases = SIZE_ALLOWED_PHASES[task_size]
            strict_gates = [g for g in strict_gates if g in allowed_phases]
        for gate in strict_gates:
            gate_value = approvals.get(gate)
            if gate_value == "n/a":
                failures.append(
                    f"{path} task_type '{task_type}' requires gate '{gate}' "
                    f"to be approved at phase '{phase}', but it is 'n/a'"
                )

    for heading in REQUIRED_BODY_HEADINGS:
        if heading not in text:
            failures.append(f"{path} is missing body heading: {heading}")

    refs = extract_current_refs(frontmatter)
    ref_keys = set(refs.keys())
    missing_ref_keys = EXPECTED_CURRENT_REF_KEYS - ref_keys
    unknown_ref_keys = ref_keys - EXPECTED_CURRENT_REF_KEYS
    for key in sorted(missing_ref_keys):
        failures.append(f"{path} is missing current_refs key: {key}")
    for key in sorted(unknown_ref_keys):
        failures.append(f"{path} has unknown current_refs key: {key}")

    # Validate ref value types: requirements must be list, others must be scalar-or-null.
    req_value = refs.get("requirements")
    if req_value is not None and not isinstance(req_value, list):
        failures.append(f"{path} current_refs.requirements must be a list, got scalar: {req_value}")
    for scalar_key in ["plan", "spec", "review", "qa", "security", "deploy"]:
        sv = refs.get(scalar_key)
        if isinstance(sv, list):
            failures.append(f"{path} current_refs.{scalar_key} must be scalar-or-null, got list")

    # Validate gate ↔ ref consistency.
    gate_ref_mapping = {
        "plan": "plan",
        "review": "review",
        "qa": "qa",
        "security": "security",
        "deploy": "deploy",
    }
    for gate_key, ref_key in gate_ref_mapping.items():
        gate_value = approvals.get(gate_key)
        ref_value = refs.get(ref_key)
        ref_is_empty = ref_value is None or ref_value == "null" or ref_value == []
        ref_is_present = not ref_is_empty
        # Approved gate must have a ref.
        if gate_value == "approved" and ref_is_empty:
            failures.append(
                f"{path} gate '{gate_key}' is approved but current_refs.{ref_key} is empty"
            )
        # Pending or n/a gate must NOT have a ref (prevents stale refs across
        # iterations and skip-phase scenarios like bugfix/hotfix).
        if gate_value in {"pending", "n/a"} and ref_is_present:
            failures.append(
                f"{path} gate '{gate_key}' is '{gate_value}' but current_refs.{ref_key} "
                f"still has a value (stale ref: {ref_value})"
            )

    root = path.parent.parent
    for key in ["plan", "spec", "review", "qa", "security", "deploy"]:
        value = refs.get(key)
        if isinstance(value, str) and value != "null":
            ref_path = root / value
            if not ref_path.exists():
                failures.append(f"{path} points to missing {key} ref: {value}")

    requirements = refs.get("requirements")
    if isinstance(requirements, list):
        for rel_path in requirements:
            ref_path = root / rel_path
            if not ref_path.exists():
                failures.append(f"{path} points to missing requirements ref: {rel_path}")

    history = extract_session_history(frontmatter)
    if len(history) > MAX_SESSION_HISTORY_ENTRIES:
        failures.append(
            f"{path} has too many session_history entries: {len(history)} > {MAX_SESSION_HISTORY_ENTRIES}"
        )
    for index, entry in enumerate(history, start=1):
        for field in ["date", "mode", "phase", "note"]:
            if field not in entry or not entry[field]:
                failures.append(f"{path} session_history entry {index} is missing {field}")
        entry_mode = entry.get("mode")
        entry_phase = entry.get("phase")
        if entry_mode and entry_mode not in ALLOWED_MODES:
            failures.append(
                f"{path} session_history entry {index} has invalid mode: {entry_mode}"
            )
        if entry_phase and entry_phase not in ALLOWED_PHASES:
            failures.append(
                f"{path} session_history entry {index} has invalid phase: {entry_phase}"
            )
        if entry_mode in MODE_PHASES and entry_phase not in MODE_PHASES[entry_mode]:
            failures.append(
                f"{path} session_history entry {index} has invalid phase for mode {entry_mode}: {entry_phase}"
            )

    # Validate external_evidence schema (optional field).
    evidence_entries = extract_external_evidence(frontmatter)
    if len(evidence_entries) > MAX_EXTERNAL_EVIDENCE_ENTRIES:
        failures.append(
            f"{path} has too many external_evidence entries: {len(evidence_entries)} > "
            f"{MAX_EXTERNAL_EVIDENCE_ENTRIES} (archive older entries to docs/evidence-archive.md)"
        )
    allowed_evidence_fields = set(REQUIRED_EVIDENCE_FIELDS)
    for index, entry in enumerate(evidence_entries, start=1):
        for field in REQUIRED_EVIDENCE_FIELDS:
            if field not in entry or not entry[field]:
                failures.append(
                    f"{path} external_evidence entry {index} is missing required field: {field}"
                )
        for field in sorted(set(entry.keys()) - allowed_evidence_fields):
            failures.append(
                f"{path} external_evidence entry {index} has unknown field: {field}"
            )
        # WARNING (not FAIL): recommend kebab-case type naming convention.
        ev_type = entry.get("type", "")
        if ev_type and not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", ev_type):
            print(
                f"WARNING: {path} external_evidence entry {index} type '{ev_type}' "
                "does not follow kebab-case convention (e.g. 'codex-review-v071-1')"
            )

    # Validate failure_tracking (optional field).
    if has_top_level_key(frontmatter, "failure_tracking"):
        ft = extract_failure_tracking(frontmatter)
        if ft is not None:
            allowed_ft_fields = set(REQUIRED_FAILURE_TRACKING_FIELDS)
            for field in REQUIRED_FAILURE_TRACKING_FIELDS:
                if field not in ft or not ft[field]:
                    failures.append(
                        f"{path} failure_tracking is missing required field: {field}"
                    )
            for field in sorted(set(ft.keys()) - allowed_ft_fields):
                failures.append(
                    f"{path} failure_tracking has unknown field: {field}"
                )
            count_val = ft.get("count", "")
            if count_val and (not count_val.isdigit() or int(count_val) < 1):
                failures.append(
                    f"{path} failure_tracking.count must be a positive integer: {count_val}"
                )

    return failures


def validate_with_pyyaml(text: str, path: Path) -> list[str]:
    """Optional strict validation using PyYAML for cross-checking."""
    try:
        import yaml
    except ImportError:
        return [f"--strict requires PyYAML: pip install pyyaml"]

    failures: list[str] = []
    fm = extract_frontmatter(text)
    if fm is None:
        return [f"{path} missing frontmatter for PyYAML cross-check"]

    try:
        parsed = yaml.safe_load(fm)
    except yaml.YAMLError as e:
        return [f"{path} PyYAML parse error: {e}"]

    if not isinstance(parsed, dict):
        return [f"{path} PyYAML parsed frontmatter is not a dict"]

    # Cross-check key fields.
    regex_mode = extract_scalar_value(fm, "mode")
    yaml_mode = parsed.get("mode")
    if regex_mode != str(yaml_mode):
        failures.append(f"{path} mode mismatch: regex={regex_mode!r}, PyYAML={yaml_mode!r}")

    regex_phase = extract_scalar_value(fm, "phase")
    yaml_phase = parsed.get("phase")
    if regex_phase != str(yaml_phase):
        failures.append(f"{path} phase mismatch: regex={regex_phase!r}, PyYAML={yaml_phase!r}")

    regex_approvals = extract_approval_map(fm)
    yaml_approvals = parsed.get("gate_approvals", {})
    if isinstance(yaml_approvals, dict):
        for key in REQUIRED_APPROVAL_KEYS:
            rv = regex_approvals.get(key)
            yv = yaml_approvals.get(key)
            if rv != str(yv) if yv is not None else rv != yv:
                failures.append(f"{path} gate {key} mismatch: regex={rv!r}, PyYAML={yv!r}")

    return failures


def pre_approve_gate(gate_name: str, root: Path) -> int:
    """Check if a gate can be approved given current STATUS.md state.

    Returns 0 if gate can be approved, 1 otherwise.
    Uses PHASE_REQUIRES_GATES, SIZE_ALLOWED_PHASES, and gate_ref_mapping
    as the single source of truth for gate approval contracts.
    Called by update-gate.sh via --pre-approve-gate.
    """
    status_path = root / "docs" / "STATUS.md"
    if not status_path.exists():
        print("ERROR: docs/STATUS.md not found")
        return 1

    text = read_text(status_path)
    frontmatter = extract_frontmatter(text)
    if frontmatter is None:
        print("ERROR: docs/STATUS.md is missing YAML frontmatter")
        return 1

    phase = extract_scalar_value(frontmatter, "phase")
    task_type = extract_scalar_value(frontmatter, "task_type")
    task_size = extract_scalar_value(frontmatter, "task_size")
    approvals = extract_approval_map(frontmatter)
    refs = extract_current_refs(frontmatter)

    # Mode-transition gates skip context validation.
    if gate_name in ("client_ready_for_dev", "dev_ready_for_client"):
        return 0

    # --- Phase order check ---
    if gate_name in DEV_PHASE_ORDER and phase in DEV_PHASE_ORDER:
        gate_idx = DEV_PHASE_ORDER.index(gate_name)
        phase_idx = DEV_PHASE_ORDER.index(phase)
        if phase_idx < gate_idx:
            print(f"ERROR: Cannot approve '{gate_name}' — current phase is '{phase}'.")
            print(f"       This gate requires reaching at least the '{gate_name}' phase.")
            return 1

    # --- Prerequisite gates check ---
    required_prior = list(PHASE_REQUIRES_GATES.get(gate_name, []))
    if task_size and task_size in SIZE_ALLOWED_PHASES:
        allowed_phases = SIZE_ALLOWED_PHASES[task_size]
        required_prior = [g for g in required_prior if g in allowed_phases]
    for prereq in required_prior:
        prereq_val = approvals.get(prereq, "pending")
        if prereq_val not in ("approved", "n/a"):
            print(
                f"ERROR: Cannot approve '{gate_name}' — prerequisite gate "
                f"'{prereq}' is '{prereq_val}' (must be approved or n/a)."
            )
            return 1

    # --- Strict gate enforcement ---
    # feature/refactor/framework require specific prior gates to be approved
    # (not n/a) at certain phases. Uses STRICT_GATE_TASK_TYPES and
    # STRICT_GATE_BY_PHASE as source of truth (same as validate_status_file).
    if task_type in STRICT_GATE_TASK_TYPES and task_size != "S":
        strict_prereqs = list(STRICT_GATE_BY_PHASE.get(gate_name, []))
        if task_size and task_size in SIZE_ALLOWED_PHASES:
            allowed_phases = SIZE_ALLOWED_PHASES[task_size]
            strict_prereqs = [g for g in strict_prereqs if g in allowed_phases]
        for strict_gate in strict_prereqs:
            gate_val = approvals.get(strict_gate, "pending")
            if gate_val == "n/a":
                print(
                    f"ERROR: Cannot approve '{gate_name}' — task_type "
                    f"'{task_type}' requires gate '{strict_gate}' to be "
                    f"approved (not n/a)."
                )
                return 1

    # --- Gate-ref consistency (WARNING only) ---
    gate_ref_mapping = {
        "plan": "plan",
        "review": "review",
        "qa": "qa",
        "security": "security",
        "deploy": "deploy",
    }
    if gate_name in gate_ref_mapping:
        ref_key = gate_ref_mapping[gate_name]
        ref_value = refs.get(ref_key)
        ref_is_empty = ref_value is None or ref_value == "null" or ref_value == []
        if ref_is_empty:
            print(f"WARNING: Approving '{gate_name}' but current_refs.{ref_key} is empty.")
            print(
                "         Set the ref before running /validate to avoid a "
                "check_status.py failure."
            )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Project root containing docs/STATUS.md")
    parser.add_argument("--strict", action="store_true",
                        help="Enable PyYAML cross-validation (requires PyYAML)")
    parser.add_argument("--pre-approve-gate", dest="pre_approve_gate", default=None,
                        help="Check if a gate can be approved (used by update-gate.sh)")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.pre_approve_gate:
        return pre_approve_gate(args.pre_approve_gate, root)

    root = Path(args.root).resolve()
    status_path = root / "docs" / "STATUS.md"
    failures = validate_status_file(status_path)

    if args.strict and status_path.exists():
        text = read_text(status_path)
        failures.extend(validate_with_pyyaml(text, status_path))

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(f"PASS: status file is valid: {status_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
